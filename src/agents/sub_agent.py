"""
Sub-agent base class for domain-specific agents.
"""

import json
import logging
from abc import abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional, List

from src.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class SubAgent(BaseAgent):
    """Base class for domain-specific sub-agents"""
    
    def __init__(self, agent_id: str, domain: str):
        super().__init__(agent_id, agent_type="sub_agent")
        self.domain = domain
        self.bottleneck = None
        self.last_diagnosis = None
        self.actions_queued = []
        self.metrics = {
            "diagnoses_run": 0,
            "actions_executed": 0,
            "errors": 0
        }
    
    @abstractmethod
    async def diagnose(self) -> Dict[str, Any]:
        """
        Identify the bottleneck in this domain.
        
        Returns:
            {
                "description": str,
                "confidence": float (0-1),
                "impact_score": float (0-10),
                "blocking": [str],  # What's blocked by this
                "recommended_action": str
            }
        """
        pass
    
    async def execute(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute action within guardrails.
        Override in subclasses for domain-specific logic.
        """
        if not self.can_execute(action):
            logger.warning(f"Action blocked: {action}")
            return {"status": "blocked", "reason": "Failed confidence threshold"}
        
        try:
            result = await self._perform_action(action)
            self.metrics["actions_executed"] += 1
            return result
        except Exception as e:
            self.metrics["errors"] += 1
            await self.log_error(e, {"action": action})
            raise
    
    async def _perform_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Override in subclasses"""
        return {"status": "not_implemented"}
    
    async def get_state(self) -> Dict[str, Any]:
        """Get current agent state"""
        return {
            "agent_id": self.agent_id,
            "domain": self.domain,
            "created_at": self.created_at.isoformat(),
            "last_diagnosis": self.last_diagnosis,
            "bottleneck": self.bottleneck,
            "actions_queued": self.actions_queued,
            "metrics": self.metrics
        }
    
    async def run(self) -> Dict[str, Any]:
        """Run daily diagnostic"""
        try:
            logger.info(f"Running {self.agent_id} diagnostic")
            
            bottleneck = await self.diagnose()
            self.bottleneck = bottleneck
            self.last_diagnosis = datetime.now().isoformat()
            self.metrics["diagnoses_run"] += 1
            
            await self.log_decision({
                "type": "diagnosis",
                "bottleneck": bottleneck,
                "confidence": bottleneck.get("confidence", 0)
            })
            
            return {
                "agent_id": self.agent_id,
                "status": "success",
                "bottleneck": bottleneck
            }
        
        except Exception as e:
            self.metrics["errors"] += 1
            await self.log_error(e)
            return {
                "agent_id": self.agent_id,
                "status": "error",
                "error": str(e)
            }
