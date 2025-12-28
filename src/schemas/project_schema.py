from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class ProjectMilestone(BaseModel):
    name: str
    deadline: Optional[str] = None
    status: str = "pending"  # pending, in-progress, done


class ProjectRisk(BaseModel):
    description: str
    mitigation: str
    probability: str = "medium"  # low, medium, high


class ProjectConfig(BaseModel):
    """
    Project definition strictly adhering to CoS Protocol v2.3
    """

    project: str
    description: str

    # CoS Framework Requirements
    outcome_metrics: Dict[str, str] = Field(
        ..., description="Measurable success metrics"
    )
    definition_of_done: List[str] = Field(..., description="Acceptance criteria")
    milestones: List[ProjectMilestone] = Field(
        ..., max_items=7, description="3-7 milestones max"
    )
    risks: List[ProjectRisk] = Field(
        ..., max_items=3, description="Top 3 risks + mitigations"
    )
    dependencies: List[str] = []
    required_artifacts: List[str] = []

    # Agent Configuration
    sub_agents: List[Dict] = []

    class Config:
        extra = "ignore"
