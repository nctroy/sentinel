"""
PostgreSQL client for managing Sentinel state.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import (
    Base,
    Agent,
    Bottleneck,
    Action,
    OrchestratorPlan,
    DecisionLog,
    NotionSync,
    SecurityVulnerabilityModel,
)

logger = logging.getLogger(__name__)


class PostgresClient:
    """Client for PostgreSQL operations"""

    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        if not self.db_url:
            raise ValueError("DATABASE_URL not set in environment")

        self.engine = None
        self.Session = None

    def connect(self):
        """Connect to database"""
        try:
            self.engine = create_engine(self.db_url)
            self.Session = sessionmaker(bind=self.engine)
            logger.info("Connected to PostgreSQL")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def init_db(self):
        """Initialize database schema (create all tables)"""
        try:
            Base.metadata.create_all(self.engine)
            logger.info("Database schema initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def close(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()
            logger.info("Closed PostgreSQL connection")

    def register_agent(
        self,
        agent_id: str,
        domain: str,
        name: str = None,
        responsibilities: List[str] = None,
        autonomy_level: str = "diagnostic",
    ) -> Agent:
        """Register a new agent"""
        session = self.Session()
        try:
            # Check if agent already exists
            existing = session.query(Agent).filter_by(agent_id=agent_id).first()
            if existing:
                logger.info(f"Agent {agent_id} already registered")
                return existing

            agent = Agent(
                agent_id=agent_id,
                domain=domain,
                name=name,
                responsibilities=responsibilities or [],
                autonomy_level=autonomy_level,
            )
            session.add(agent)
            session.commit()
            logger.info(f"Registered agent: {agent_id}")
            return agent
        finally:
            session.close()

    def update_agent_last_run(self, agent_id: str):
        """Update agent's last_run timestamp to now"""
        session = self.Session()
        try:
            agent = session.query(Agent).filter_by(agent_id=agent_id).first()
            if agent:
                agent.last_run = datetime.now()
                session.commit()
                logger.info(f"Updated last_run for {agent_id}")
        except Exception as e:
            logger.error(f"Failed to update last_run for {agent_id}: {e}")
        finally:
            session.close()

    def save_bottleneck(self, agent_id: str, bottleneck: Dict[str, Any]) -> Bottleneck:
        """Save bottleneck to database"""
        session = self.Session()
        try:
            bottleneck_obj = Bottleneck(
                agent_id=agent_id,
                description=bottleneck.get("description"),
                confidence=bottleneck.get("confidence", 0.0),
                impact_score=bottleneck.get("impact_score", 0.0),
                blocking=bottleneck.get("blocking", []),
                recommended_action=bottleneck.get("recommended_action"),
            )
            session.add(bottleneck_obj)
            session.commit()
            logger.info(f"Saved bottleneck for {agent_id}")
            return bottleneck_obj
        finally:
            session.close()

    def log_action(
        self,
        agent_id: str,
        action_type: str,
        description: str = None,
        parameters: Dict = None,
        status: str = "queued",
    ) -> Action:
        """Log an action"""
        session = self.Session()
        try:
            action = Action(
                agent_id=agent_id,
                action_type=action_type,
                description=description,
                parameters=parameters or {},
                status=status,
            )
            session.add(action)
            session.commit()
            logger.info(f"Logged action for {agent_id}: {action_type}")
            return action
        finally:
            session.close()

    def get_agent_state(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent state from database"""
        session = self.Session()
        try:
            agent = session.query(Agent).filter_by(agent_id=agent_id).first()
            if not agent:
                return None

            return {
                "agent_id": agent.agent_id,
                "domain": agent.domain,
                "name": agent.name,
                "last_run": agent.last_run,
                "metrics": agent.metrics or {},
            }
        finally:
            session.close()

    def get_all_agents(self) -> List[Dict[str, Any]]:
        """Get all registered agents"""
        session = self.Session()
        try:
            agents = session.query(Agent).filter_by(is_active=True).all()
            return [
                {
                    "agent_id": a.agent_id,
                    "domain": a.domain,
                    "name": a.name,
                    "last_run": a.last_run,
                    "autonomy_level": a.autonomy_level,
                }
                for a in agents
            ]
        finally:
            session.close()

    def get_all_agent_reports(self) -> List[Dict[str, Any]]:
        """Get latest reports from all agents"""
        session = self.Session()
        try:
            agents = session.query(Agent).filter_by(is_active=True).all()
            reports = []

            for agent in agents:
                # Get latest bottleneck
                latest_bottleneck = (
                    session.query(Bottleneck)
                    .filter_by(agent_id=agent.agent_id, status="open")
                    .order_by(Bottleneck.identified_at.desc())
                    .first()
                )

                reports.append(
                    {
                        "agent_id": agent.agent_id,
                        "domain": agent.domain,
                        "bottleneck": {
                            "description": latest_bottleneck.description,
                            "impact_score": latest_bottleneck.impact_score,
                            "confidence": latest_bottleneck.confidence,
                        }
                        if latest_bottleneck
                        else None,
                        "last_run": agent.last_run.isoformat() if agent.last_run else None,
                    }
                )

            return reports
        finally:
            session.close()

    def save_orchestration_result(self, plan: Dict[str, Any]) -> OrchestratorPlan:
        """Save orchestration result"""
        session = self.Session()
        try:
            plan_obj = OrchestratorPlan(
                week=plan.get("week"),
                top_bottleneck=plan.get("top_bottleneck"),
                priority_ranking=plan.get("priority_ranking", []),
                resource_allocation=plan.get("resource_allocation", {}),
                weekly_plan=plan.get("weekly_plan", []),
                cross_domain_conflicts=plan.get("cross_domain_conflicts", []),
            )
            session.add(plan_obj)
            session.commit()
            logger.info(f"Saved orchestration plan for week {plan.get('week')}")
            return plan_obj
        finally:
            session.close()

    def log_decision(
        self,
        agent_id: str,
        decision_type: str,
        reasoning: str = None,
        context: Dict = None,
        outcome: Dict = None,
    ) -> DecisionLog:
        """Log a decision to audit trail"""
        session = self.Session()
        try:
            log_entry = DecisionLog(
                agent_id=agent_id,
                decision_type=decision_type,
                reasoning=reasoning,
                context=context or {},
                outcome=outcome or {},
            )
            session.add(log_entry)
            session.commit()
            logger.info(f"Logged decision for {agent_id}: {decision_type}")
            return log_entry
        finally:
            session.close()

    def save_vulnerability(self, vulnerability: Dict[str, Any]) -> SecurityVulnerabilityModel:
        """Save or update a security vulnerability"""
        session = self.Session()
        try:
            # Basic check for existing to avoid duplicates (source + rule_id + file_path + line)
            existing = session.query(SecurityVulnerabilityModel).filter_by(
                source=vulnerability.get('source'),
                rule_id=vulnerability.get('rule_id'),
                file_path=vulnerability.get('file_path'),
                line_number=vulnerability.get('line_number')
            ).first()

            if existing:
                # Update identified_at but keep old record? 
                # For now just update description/remediation in case they changed
                existing.description = vulnerability.get('description')
                existing.remediation = vulnerability.get('remediation')
                existing.severity = vulnerability.get('severity', 'medium')
                existing.identified_at = datetime.utcnow()
                session.commit()
                return existing

            vuln_obj = SecurityVulnerabilityModel(
                source=vulnerability.get('source'),
                severity=vulnerability.get('severity', 'medium'),
                rule_id=vulnerability.get('rule_id'),
                description=vulnerability.get('description'),
                file_path=vulnerability.get('file_path'),
                line_number=vulnerability.get('line_number'),
                remediation=vulnerability.get('remediation'),
                raw_data=vulnerability.get('raw_data', {}),
                identified_at=datetime.utcnow()
            )
            session.add(vuln_obj)
            session.commit()
            logger.info(f"Saved vulnerability from {vulnerability.get('source')}: {vulnerability.get('rule_id')}")
            return vuln_obj
        finally:
            session.close()

    def get_security_summary(self) -> Dict[str, Any]:
        """Get summary of all security findings"""
        session = self.Session()
        try:
            vulns = session.query(SecurityVulnerabilityModel).filter_by(status='open').all()
            
            summary = {
                "total_findings": len(vulns),
                "counts_by_severity": {},
                "counts_by_source": {}
            }

            for v in vulns:
                summary["counts_by_severity"][v.severity] = summary["counts_by_severity"].get(v.severity, 0) + 1
                summary["counts_by_source"][v.source] = summary["counts_by_source"].get(v.source, 0) + 1
                
            return summary
        finally:
            session.close()

    def get_vulnerabilities(self, source: str = None, severity: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get list of security vulnerabilities"""
        session = self.Session()
        try:
            query = session.query(SecurityVulnerabilityModel).filter_by(status='open')
            if source:
                query = query.filter_by(source=source)
            if severity:
                query = query.filter_by(severity=severity)
            
            vulns = query.order_by(SecurityVulnerabilityModel.identified_at.desc()).limit(limit).all()
            
            return [
                {
                    "id": v.id,
                    "source": v.source,
                    "severity": v.severity,
                    "rule_id": v.rule_id,
                    "description": v.description,
                    "file_path": v.file_path,
                    "line_number": v.line_number,
                    "remediation": v.remediation,
                    "identified_at": v.identified_at
                }
                for v in vulns
            ]
        finally:
            session.close()
