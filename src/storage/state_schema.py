"""
Unified state schema for agents.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import json


@dataclass
class Bottleneck:
    """Represents a bottleneck identified by an agent"""
    description: str
    confidence: float  # 0.0 - 1.0
    impact_score: float  # 0-10
    blocking: List[str]  # What's blocked by this
    recommended_action: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AgentState:
    """Complete state for an agent"""
    agent_id: str
    domain: str
    last_run: Optional[datetime]
    bottleneck: Optional[Bottleneck]
    actions_queued: List[Dict[str, Any]]
    metrics: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        state = asdict(self)
        state["last_run"] = self.last_run.isoformat() if self.last_run else None
        if self.bottleneck:
            state["bottleneck"] = self.bottleneck.to_dict()
        return state
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class OrchestratorPlan:
    """Weekly orchestration plan"""
    week: str
    top_bottleneck: Dict[str, Any]
    priority_ranking: List[Dict[str, Any]]
    resource_allocation: Dict[str, Any]
    weekly_plan: List[Dict[str, Any]]
    cross_domain_conflicts: List[Dict[str, Any]]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
