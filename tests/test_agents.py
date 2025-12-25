"""
Tests for agent implementations
"""

import pytest
import asyncio
from src.agents.sub_agent import SubAgent


@pytest.fixture
def sample_agent():
    """Create a sample sub-agent for testing"""
    agent = SubAgent("test-001", "test-domain")
    return agent


@pytest.mark.asyncio
async def test_agent_initialization(sample_agent):
    """Test agent initialization"""
    assert sample_agent.agent_id == "test-001"
    assert sample_agent.domain == "test-domain"
    assert sample_agent.metrics["diagnoses_run"] == 0


@pytest.mark.asyncio
async def test_agent_state(sample_agent):
    """Test getting agent state"""
    state = await sample_agent.get_state()
    
    assert "agent_id" in state
    assert "domain" in state
    assert "metrics" in state


@pytest.mark.asyncio
async def test_confidence_assessment(sample_agent):
    """Test confidence assessment"""
    confidence = sample_agent.assess_confidence({
        "confidence": 0.85
    })
    
    assert confidence == 0.85


def test_execute_guardrails(sample_agent):
    """Test that guardrails are enforced"""
    action = {
        "type": "test",
        "confidence": 0.3  # Below threshold
    }
    
    can_execute = sample_agent.can_execute(action)
    assert not can_execute
