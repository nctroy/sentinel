"""
Base agent class for all Sentinel agents.
"""

import os
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional

import anthropic
from opentelemetry import trace

from src.observability.telemetry import get_tracer, instrument_claude_call

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Abstract base class for all agents"""

    def __init__(self, agent_id: str, agent_type: str = "base"):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.created_at = datetime.now()
        self.last_run = None
        self.confidence_threshold = 0.5
        self.max_retries = 3
        self.timeout = 3600  # 1 hour

        # Initialize Claude API client
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key:
            self.claude_client = anthropic.Anthropic(api_key=api_key)
        else:
            logger.warning(f"ANTHROPIC_API_KEY not set for agent {agent_id}")
            self.claude_client = None

        # Get OpenTelemetry tracer
        self.tracer = get_tracer()

    @abstractmethod
    async def run(self) -> Dict[str, Any]:
        """Main execution method"""
        pass

    async def log_decision(self, decision: Dict[str, Any]) -> None:
        """Log a decision made by this agent"""
        log_entry = {
            "agent_id": self.agent_id,
            "timestamp": datetime.now().isoformat(),
            "type": decision.get("type"),
            "reasoning": decision.get("reasoning", ""),
            "confidence": decision.get("confidence", 0.0),
        }
        logger.info(f"Decision: {json.dumps(log_entry)}")

    async def log_error(self, error: Exception, context: Dict[str, Any] = None) -> None:
        """Log an error"""
        logger.error(
            f"Agent {self.agent_id} error: {str(error)}",
            extra={"context": context or {}},
            exc_info=True,
        )

    def assess_confidence(self, data: Dict[str, Any]) -> float:
        """
        Assess confidence in a decision.
        Override in subclasses for domain-specific logic.
        """
        if "confidence" in data:
            return data["confidence"]
        return 0.5

    def can_execute(self, action: Dict[str, Any]) -> bool:
        """Check if action meets confidence threshold"""
        confidence = action.get("confidence", 0.0)
        return confidence >= self.confidence_threshold

    @instrument_claude_call
    async def call_claude(
        self,
        system_prompt: str,
        user_message: str,
        model: str = "claude-sonnet-4-20250514",
        max_tokens: int = 2000,
    ) -> str:
        """
        Make a Claude API call with observability instrumentation.

        Args:
            system_prompt: System prompt defining agent's role and context
            user_message: User message containing the task/question
            model: Claude model to use
            max_tokens: Maximum tokens in response

        Returns:
            Response text from Claude

        Raises:
            Exception: If Claude API client is not initialized or API call fails
        """
        if not self.claude_client:
            raise Exception(
                f"Claude API client not initialized for agent {self.agent_id}"
            )

        with self.tracer.start_as_current_span("claude_api_call") as span:
            # Add span attributes
            span.set_attribute("agent.id", self.agent_id)
            span.set_attribute("agent.type", self.agent_type)
            span.set_attribute("model", model)
            span.set_attribute("prompt.system.length", len(system_prompt))
            span.set_attribute("prompt.user.length", len(user_message))

            try:
                # Make Claude API call
                response = self.claude_client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_message}],
                )

                # Track token usage
                span.set_attribute("tokens.input", response.usage.input_tokens)
                span.set_attribute("tokens.output", response.usage.output_tokens)
                span.set_attribute(
                    "tokens.total",
                    response.usage.input_tokens + response.usage.output_tokens,
                )

                # Extract and return text content
                response_text = response.content[0].text

                span.set_attribute("response.length", len(response_text))
                span.set_attribute("success", True)

                logger.debug(
                    f"Claude API call successful for agent {self.agent_id}: "
                    f"{response.usage.input_tokens} input tokens, "
                    f"{response.usage.output_tokens} output tokens"
                )

                return response_text

            except Exception as e:
                span.set_attribute("success", False)
                span.set_attribute("error.type", type(e).__name__)
                span.set_attribute("error.message", str(e))
                span.record_exception(e)

                logger.error(
                    f"Claude API call failed for agent {self.agent_id}: {e}",
                    exc_info=True,
                )
                raise
