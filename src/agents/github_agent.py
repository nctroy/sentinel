import json
import logging
from datetime import datetime
from typing import Dict, Any, List

from src.agents.sub_agent import SubAgent
from src.observability.telemetry import instrument_agent_method

logger = logging.getLogger(__name__)


class GitHubTriageAgent(SubAgent):
    """
    Agent responsible for scanning GitHub repositories for issues
    and pull requests that need attention.
    """

    def __init__(self, agent_id: str, domain: str):
        super().__init__(agent_id, domain)

    @instrument_agent_method("github_agent.diagnose")
    async def diagnose(self) -> Dict[str, Any]:
        """
        Diagnose the state of the GitHub repository using Claude API.

        Returns:
            Dictionary containing bottleneck information with fields:
            - description: str
            - confidence: float (0.0 to 1.0)
            - impact_score: float (0.0 to 10.0)
            - blocking: List[str]
            - recommended_action: str
            - reasoning: str
        """
        # Define system prompt for GitHub Triage Agent
        system_prompt = f"""You are a GitHub Triage Agent for the domain: {self.domain}.

Your role is to monitor GitHub repositories and identify issues, pull requests, or repository health problems that need attention. You analyze:
- Unassigned high-priority bugs
- Stale issues and PRs
- Code review bottlenecks
- Release blockers
- Repository health metrics

When you identify a bottleneck, you must respond with a JSON object (and ONLY JSON, no other text) with this exact structure:
{{
    "description": "Brief description of the GitHub bottleneck",
    "confidence": 0.0-1.0 (your confidence in this being a real bottleneck),
    "impact_score": 0.0-10.0 (potential impact on development velocity),
    "blocking": ["list", "of", "things", "this", "blocks"],
    "recommended_action": "Specific action to take",
    "reasoning": "Why this is a bottleneck and needs attention"
}}

If there are no significant bottlenecks, return a JSON object with confidence: 0.0 and description: "No significant bottlenecks identified"."""

        user_message = f"""Analyze the current state of GitHub repositories in the {self.domain} domain and identify any bottlenecks.

Consider typical bottlenecks such as:
1. Unassigned high-priority bugs or issues
2. Stale issues or pull requests (no activity for 30+ days)
3. Pull requests awaiting review for extended periods
4. Release blockers or critical bugs
5. Repository backlog health

Since you don't have direct GitHub API access, simulate a realistic bottleneck that a GitHub repository in the {self.domain} domain might face.

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
                        "type": "github_triage_scan",
                        "domain": self.domain,
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
            logger.error(f"GitHub agent diagnose failed: {e}", exc_info=True)
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
        Execute actions on GitHub.
        """
        action_type = action.get("type")

        if action_type == "assign_issue":
            # Simulate assigning
            return {
                "status": "success",
                "message": f"Assigned issue {action.get('issue_id')} to {action.get('user')}",
            }

        elif action_type == "close_issue":
            # Simulate closing
            return {
                "status": "success",
                "message": f"Closed issue {action.get('issue_id')}",
            }

        return {"status": "failed", "message": f"Unknown action type: {action_type}"}
