"""
Orchestration agent (Chief of Staff).
Synthesizes sub-agent reports and generates weekly priorities.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List

from src.agents.base_agent import BaseAgent
from src.observability.telemetry import instrument_agent_method

logger = logging.getLogger(__name__)


class OrchestratorAgent(BaseAgent):
    """
    Orchestration agent that coordinates all sub-agents.
    Runs weekly to synthesize findings and route priorities.
    """
    
    def __init__(self):
        super().__init__("orchestrator", agent_type="orchestrator")
        self.last_synthesis = None
        self.current_plan = None
    
    async def run(self) -> Dict[str, Any]:
        """Run weekly orchestration"""
        logger.info("Starting orchestration cycle")
        # Implementation in subclass
        return {"status": "not_implemented"}
    
    @instrument_agent_method("orchestrator.synthesize")
    async def synthesize(self, sub_agent_reports: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Synthesize all sub-agent reports into weekly priorities using Claude API.

        Args:
            sub_agent_reports: List of bottleneck reports from sub-agents

        Returns:
            {
                "top_bottleneck": {...},
                "priority_ranking": [...],
                "resource_allocation": {...},
                "weekly_plan": [...],
                "cross_domain_conflicts": [...]
            }
        """
        try:
            logger.info(f"Synthesizing {len(sub_agent_reports)} reports")

            if not sub_agent_reports:
                logger.warning("No sub-agent reports to synthesize")
                return {
                    "week": datetime.now().isoformat(),
                    "top_bottleneck": {},
                    "priority_ranking": [],
                    "resource_allocation": {},
                    "weekly_plan": [],
                    "cross_domain_conflicts": []
                }

            # Rank by impact (preliminary ranking)
            ranked = self._rank_by_impact(sub_agent_reports)

            # Use Claude to intelligently synthesize the reports
            system_prompt = """You are the Chief of Staff (Orchestrator) in a multi-agent system.

Your role is to synthesize reports from multiple domain-specific agents and create a coherent weekly action plan. You must:
1. Identify the highest-impact bottleneck across all domains
2. Rank all bottlenecks by priority (considering both impact and confidence)
3. Detect cross-domain conflicts (when resources or attention are needed in multiple domains)
4. Generate a clear, actionable weekly plan

You will receive a JSON array of bottleneck reports, each with:
- description: What the bottleneck is
- confidence: Agent's confidence (0.0-1.0)
- impact_score: Estimated impact (0.0-10.0)
- blocking: What this bottleneck blocks
- recommended_action: Suggested next step
- reasoning: Why this matters
- agent_id: Which agent reported it
- domain: Which domain it affects

Respond with a JSON object (and ONLY JSON, no other text) with this structure:
{
    "top_bottleneck": {the single highest-priority bottleneck object},
    "priority_ranking": [array of all bottlenecks sorted by priority],
    "cross_domain_conflicts": [
        {"description": "conflict description", "affected_domains": ["domain1", "domain2"], "resolution_strategy": "how to resolve"}
    ],
    "weekly_plan": [
        {"action": "specific action", "domain": "domain", "priority": 1-10, "rationale": "why this matters"}
    ],
    "synthesis_reasoning": "Your overall strategic reasoning for these priorities"
}"""

            # Prepare reports with agent context
            reports_with_context = []
            for report in ranked:
                # Add agent_id and domain if not present
                if 'agent_id' not in report and hasattr(self, '_report_sources'):
                    # This would be set by the caller
                    pass
                reports_with_context.append(report)

            user_message = f"""Here are the bottleneck reports from all sub-agents:

{json.dumps(reports_with_context, indent=2)}

Synthesize these reports into a coherent weekly action plan. Consider:
1. Which bottleneck has the highest real impact (not just highest score)?
2. Are there dependencies or conflicts between domains?
3. What's the most strategic sequence of actions?
4. What can be parallelized vs. what must be sequential?

Return your synthesis as a JSON object following the specified structure."""

            # Call Claude API for intelligent synthesis
            response_text = await self.call_claude(
                system_prompt=system_prompt,
                user_message=user_message,
                max_tokens=2000
            )

            # Parse JSON response
            try:
                plan = json.loads(response_text)

                # Ensure required fields exist
                required_fields = ["top_bottleneck", "priority_ranking", "cross_domain_conflicts", "weekly_plan"]
                for field in required_fields:
                    if field not in plan:
                        logger.warning(f"Missing field '{field}' in orchestrator response")
                        plan[field] = {} if field == "top_bottleneck" else []

                # Add metadata
                plan["week"] = datetime.now().isoformat()
                plan["resource_allocation"] = {}  # Can be enhanced later

                self.current_plan = plan
                self.last_synthesis = datetime.now().isoformat()

                await self.log_decision({
                    "type": "orchestration",
                    "reports_synthesized": len(sub_agent_reports),
                    "top_bottleneck": plan.get("top_bottleneck", {}).get("description", "None"),
                    "weekly_plan_items": len(plan.get("weekly_plan", []))
                })

                return plan

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse orchestrator Claude response as JSON: {e}")
                logger.error(f"Response text: {response_text}")

                # Fallback to simple ranking
                return self._generate_plan(ranked, self._find_conflicts(ranked))

        except Exception as e:
            logger.error(f"Orchestrator synthesis failed: {e}", exc_info=True)
            await self.log_error(e, {"reports": len(sub_agent_reports)})
            raise
    
    def _rank_by_impact(self, reports: List[Dict]) -> List[Dict]:
        """Rank bottlenecks by impact score"""
        return sorted(
            reports,
            key=lambda x: x.get("impact_score", 0) * x.get("confidence", 0.5),
            reverse=True
        )
    
    def _find_conflicts(self, ranked_reports: List[Dict]) -> List[Dict]:
        """Identify resource conflicts between agents"""
        conflicts = []
        # Implementation would detect when multiple agents
        # need the same resources
        return conflicts
    
    def _generate_plan(self, ranked: List[Dict], conflicts: List[Dict]) -> Dict[str, Any]:
        """Generate weekly action plan"""
        plan = {
            "week": datetime.now().isoformat(),
            "top_bottleneck": ranked[0] if ranked else {},
            "priority_ranking": ranked,
            "resource_allocation": {},
            "weekly_plan": [],
            "cross_domain_conflicts": conflicts
        }
        return plan
