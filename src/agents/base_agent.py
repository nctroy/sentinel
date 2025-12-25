"""
Base agent class for all Sentinel agents.
"""

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional

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
            "confidence": decision.get("confidence", 0.0)
        }
        logger.info(f"Decision: {json.dumps(log_entry)}")
    
    async def log_error(self, error: Exception, context: Dict[str, Any] = None) -> None:
        """Log an error"""
        logger.error(
            f"Agent {self.agent_id} error: {str(error)}",
            extra={"context": context or {}},
            exc_info=True
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
