"""
Tests for orchestration logic
"""

import pytest
from src.agents.orchestrator import OrchestratorAgent


@pytest.fixture
def orchestrator():
    """Create orchestrator for testing"""
    return OrchestratorAgent()


@pytest.mark.asyncio
async def test_orchestrator_initialization(orchestrator):
    """Test orchestrator initialization"""
    assert orchestrator.agent_id == "orchestrator"
    assert orchestrator.agent_type == "orchestrator"


@pytest.mark.asyncio
async def test_rank_by_impact(orchestrator):
    """Test ranking bottlenecks by impact"""
    reports = [
        {"impact_score": 5, "confidence": 0.8},
        {"impact_score": 8, "confidence": 0.9},
        {"impact_score": 3, "confidence": 0.7}
    ]
    
    ranked = orchestrator._rank_by_impact(reports)
    
    assert ranked[0]["impact_score"] == 8  # Highest impact first
    assert ranked[-1]["impact_score"] == 3  # Lowest impact last
