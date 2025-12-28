"""
SQLAlchemy database models for Sentinel.
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    JSON,
    Text,
    Boolean,
    ForeignKey,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Agent(Base):
    """Agent registration and state"""

    __tablename__ = "agents"

    id = Column(Integer, primary_key=True)
    agent_id = Column(String(100), unique=True, nullable=False, index=True)
    domain = Column(String(100), nullable=False)
    name = Column(String(200))
    responsibilities = Column(JSON)
    autonomy_level = Column(String(50), default="diagnostic")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_run = Column(DateTime)
    is_active = Column(Boolean, default=True)
    metrics = Column(JSON)

    # Relationships
    bottlenecks = relationship(
        "Bottleneck", back_populates="agent", cascade="all, delete-orphan"
    )
    actions = relationship(
        "Action", back_populates="agent", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Agent(agent_id='{self.agent_id}', domain='{self.domain}')>"


class Bottleneck(Base):
    """Bottlenecks identified by agents"""

    __tablename__ = "bottlenecks"

    id = Column(Integer, primary_key=True)
    agent_id = Column(
        String(100), ForeignKey("agents.agent_id"), nullable=False, index=True
    )
    description = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False)  # 0.0 - 1.0
    impact_score = Column(Float, nullable=False)  # 0-10
    blocking = Column(JSON)  # List of what's blocked
    recommended_action = Column(Text)
    status = Column(String(50), default="open")  # open, in_progress, resolved
    identified_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)

    # Relationships
    agent = relationship("Agent", back_populates="bottlenecks")

    def __repr__(self):
        return f"<Bottleneck(agent_id='{self.agent_id}', impact={self.impact_score})>"


class Action(Base):
    """Actions queued and executed by agents"""

    __tablename__ = "actions"

    id = Column(Integer, primary_key=True)
    agent_id = Column(
        String(100), ForeignKey("agents.agent_id"), nullable=False, index=True
    )
    action_type = Column(String(100), nullable=False)
    description = Column(Text)
    parameters = Column(JSON)
    status = Column(
        String(50), default="queued"
    )  # queued, executing, completed, failed
    priority = Column(Integer, default=5)  # 1-10
    queued_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    result = Column(JSON)
    error = Column(Text)

    # Relationships
    agent = relationship("Agent", back_populates="actions")

    def __repr__(self):
        return f"<Action(agent_id='{self.agent_id}', type='{self.action_type}', status='{self.status}')>"


class OrchestratorPlan(Base):
    """Weekly orchestration plans"""

    __tablename__ = "orchestrator_plans"

    id = Column(Integer, primary_key=True)
    week = Column(
        String(100), unique=True, nullable=False, index=True
    )  # e.g., "2024-W52"
    top_bottleneck = Column(JSON, nullable=False)
    priority_ranking = Column(JSON)
    resource_allocation = Column(JSON)
    weekly_plan = Column(JSON)
    cross_domain_conflicts = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<OrchestratorPlan(week='{self.week}')>"


class DecisionLog(Base):
    """Audit trail of all agent decisions and reasoning"""

    __tablename__ = "decision_log"

    id = Column(Integer, primary_key=True)
    agent_id = Column(String(100), nullable=False, index=True)
    decision_type = Column(
        String(100), nullable=False
    )  # bottleneck_identified, action_executed, etc.
    reasoning = Column(Text)
    context = Column(JSON)
    outcome = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<DecisionLog(agent_id='{self.agent_id}', type='{self.decision_type}')>"


class NotionSync(Base):
    """Track Notion synchronization state"""

    __tablename__ = "notion_sync"

    id = Column(Integer, primary_key=True)
    entity_type = Column(String(50), nullable=False)  # agent, bottleneck, plan
    entity_id = Column(String(100), nullable=False)
    notion_page_id = Column(String(100))
    last_synced = Column(DateTime)
    sync_status = Column(String(50), default="pending")  # pending, synced, error
    error_message = Column(Text)

    def __repr__(self):
        return f"<NotionSync(entity_type='{self.entity_type}', status='{self.sync_status}')>"


class SecurityVulnerabilityModel(Base):
    """Storage for aggregated security findings"""
    __tablename__ = 'security_vulnerabilities'

    id = Column(Integer, primary_key=True)
    source = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), nullable=False, index=True)
    rule_id = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    file_path = Column(Text)
    line_number = Column(Integer)
    remediation = Column(Text)
    raw_data = Column(JSON)
    identified_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default='open')  # open, false_positive, resolved

    def __repr__(self):
        return f"<SecurityVulnerability(source='{self.source}', severity='{self.severity}', rule='{self.rule_id}')>"
