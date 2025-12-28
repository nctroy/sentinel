import json
import logging
from datetime import datetime
from typing import Dict, Any, List

from src.agents.sub_agent import SubAgent
from src.observability.telemetry import instrument_agent_method

logger = logging.getLogger(__name__)


class ResearchAnalystAgent(SubAgent):
    """
    Research & Intelligence Agent.
    Monitors domains, filters noise, and surfaces high-signal items.
    """

    def __init__(self, agent_id: str, domain: str):
        super().__init__(agent_id, domain)
        self.sources = ["arXiv", "TechCrunch", "GitHub Trending", "Hacker News"]

    @instrument_agent_method("research_agent.diagnose")
    async def diagnose(self) -> Dict[str, Any]:
        """
        Scan sources and identify high-signal items using Claude API.

        Returns:
            Dictionary containing bottleneck information with fields:
            - description: str
            - confidence: float (0.0 to 1.0)
            - impact_score: float (0.0 to 10.0)
            - blocking: List[str]
            - recommended_action: str
            - reasoning: str
        """
        # Define system prompt for Research Analyst Agent
        system_prompt = f"""You are a Research & Intelligence Agent for the domain: {self.domain}.

Your role is to monitor information sources and identify high-signal research items, papers, trends, or developments that could impact your domain. You filter noise and surface only the most relevant findings.

Your sources include: {', '.join(self.sources)}

You should identify research bottlenecks such as:
- Important new papers or research that needs review
- Emerging trends or technologies relevant to the domain
- Competitive intelligence or market movements
- New tools or frameworks worth evaluating

When you identify a bottleneck, you must respond with a JSON object (and ONLY JSON, no other text) with this exact structure:
{{
    "description": "Brief description of the research item or bottleneck",
    "confidence": 0.0-1.0 (your confidence in the importance of this finding),
    "impact_score": 0.0-10.0 (potential impact on the domain),
    "blocking": ["list", "of", "things", "this", "blocks"],
    "recommended_action": "Specific action to take",
    "reasoning": "Why this is important and relevant"
}}

If there are no significant bottlenecks or high-signal items right now, return a JSON object with confidence: 0.0 and description: "No significant bottlenecks identified"."""

        user_message = f"""Analyze the current state of {self.domain} and identify any high-signal research items, papers, or trends that represent bottlenecks to progress or knowledge gaps.

Consider:
1. Recent developments in AI/ML research relevant to {self.domain}
2. Emerging tools or frameworks
3. Competitive intelligence
4. Knowledge gaps that need filling

Return your analysis as a JSON object following the specified structure."""

        try:
            # Call Claude API
            response_text = await self.call_claude(
                system_prompt=system_prompt, user_message=user_message, max_tokens=1000
            )

            # Parse JSON response
            try:
                bottleneck = json.loads(response_text)

                # Validate required fields
                required_fields = [
                    "description",
                    "confidence",
                    "impact_score",
                    "blocking",
                    "recommended_action",
                    "reasoning",
                ]
                for field in required_fields:
                    if field not in bottleneck:
                        logger.warning(
                            f"Missing field '{field}' in Claude response, using default"
                        )
                        bottleneck[field] = (
                            ""
                            if field
                            in ["description", "recommended_action", "reasoning"]
                            else (
                                0.0 if field in ["confidence", "impact_score"] else []
                            )
                        )

                # Ensure confidence and impact_score are floats in valid ranges
                bottleneck["confidence"] = max(
                    0.0, min(1.0, float(bottleneck["confidence"]))
                )
                bottleneck["impact_score"] = max(
                    0.0, min(10.0, float(bottleneck["impact_score"]))
                )

                # Log the scan
                await self.log_decision(
                    {
                        "type": "intelligence_scan",
                        "sources": self.sources,
                        "finding": bottleneck["description"],
                        "confidence": bottleneck["confidence"],
                    }
                )

                return bottleneck

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Claude response as JSON: {e}")
                logger.error(f"Response text: {response_text}")

                # Return a default "no bottleneck" response
                return {
                    "description": "Analysis failed - unable to parse response",
                    "confidence": 0.0,
                    "impact_score": 0.0,
                    "blocking": [],
                    "recommended_action": "Retry analysis",
                    "reasoning": "JSON parsing error",
                }

        except Exception as e:
            logger.error(f"Research agent diagnose failed: {e}", exc_info=True)
            await self.log_error(e, {"domain": self.domain})

            # Return a default error response
            return {
                "description": f"Agent error: {str(e)}",
                "confidence": 0.0,
                "impact_score": 0.0,
                "blocking": [],
                "recommended_action": "Check agent logs and retry",
                "reasoning": "Exception during diagnosis",
            }

    async def execute(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute research actions.
        """
        action_type = action.get("type")

        if action_type == "summarize_paper":
            return {
                "status": "success",
                "summary": "Paper demonstrates that chain-of-thought prompting...",
                "key_takeaways": [
                    "Method A beats Method B",
                    "Latency impacts reasoning",
                ],
            }

        return {"status": "failed", "message": f"Unknown action type: {action_type}"}
