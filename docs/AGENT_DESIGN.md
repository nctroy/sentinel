# Agent Design Guide

## Creating a Custom Sub-Agent

### 1. Understand the Base Classes

All agents inherit from `SubAgent`:

```python
from src.agents.sub_agent import SubAgent

class MyCustomAgent(SubAgent):
    def __init__(self, agent_id: str, domain: str):
        super().__init__(agent_id, domain)
    
    async def diagnose(self) -> dict:
        """Identify bottleneck in this domain"""
        pass
    
    async def execute(self, action: dict) -> dict:
        """Execute action within guardrails"""
        pass
```

### 2. Define State Schema

Every agent tracks state:

```python
# In your agent class
STATE_SCHEMA = {
    "agent_id": str,
    "domain": str,
    "last_run": datetime,
    "bottleneck": {
        "description": str,
        "confidence": float,  # 0.0 - 1.0
        "impact_score": float,  # 0-10
        "blocking": [str]  # What's blocked by this
    },
    "metrics": {
        "tasks_completed": int,
        "blockers_resolved": int,
        "efficiency_score": float
    },
    "actions_queued": [dict]
}
```

### 3. Implement Diagnosis Logic

```python
async def diagnose(self) -> dict:
    """
    Identify the single highest-leverage bottleneck
    in this domain.
    """
    # 1. Fetch current state
    current_state = await self.get_state()
    
    # 2. Gather data (APIs, databases, external sources)
    data = await self.gather_data()
    
    # 3. Analyze for bottlenecks
    bottleneck = self.analyze(current_state, data)
    
    # 4. Score by impact
    bottleneck["impact_score"] = self.calculate_impact(bottleneck)
    bottleneck["confidence"] = self.assess_confidence(bottleneck)
    
    # 5. Log decision
    await self.log_decision({
        "type": "diagnosis",
        "bottleneck": bottleneck,
        "reasoning": "..."
    })
    
    return bottleneck
```

### 4. Implement Execution

```python
async def execute(self, action: dict) -> dict:
    """
    Execute action within autonomy constraints.
    Always verify guardrails first.
    """
    # 1. Check autonomy level
    if not self.can_execute(action):
        return {"status": "pending_approval", "action": action}
    
    # 2. Log intent
    await self.log_decision({
        "type": "execution",
        "action": action,
        "timestamp": datetime.now()
    })
    
    # 3. Execute
    try:
        result = await self.perform_action(action)
    except Exception as e:
        await self.log_error(e, action)
        raise
    
    # 4. Log outcome
    await self.log_outcome(action, result)
    
    return result
```

### 5. Register Agent

In your project config:

```json
{
  "project": "my-project",
  "sub_agents": [
    {
      "agent_id": "my-agent-001",
      "class": "src.agents.MyCustomAgent",
      "domain": "my-domain",
      "autonomy_level": "diagnostic",
      "responsibilities": [...]
    }
  ]
}
```

## Common Agent Patterns

### Pattern 1: Data-Gathering Agent

```python
class ResearchAgent(SubAgent):
    async def diagnose(self):
        # Query APIs, databases, web sources
        data = await self.gather_from_sources([
            "database_queries",
            "api_calls",
            "web_search"
        ])
        
        # Analyze for gaps/insights
        bottleneck = self.find_gaps(data)
        return bottleneck
```

### Pattern 2: Execution Agent

```python
class ProductionAgent(SubAgent):
    async def execute(self, action):
        # Check blockers first
        if self.has_blockers(action):
            return {"status": "blocked", "blockers": ...}
        
        # Execute with rollback capability
        with transaction():
            result = await self.perform_action(action)
            await self.verify_result(result)
        
        return result
```

### Pattern 3: Monitoring Agent

```python
class MonitoringAgent(SubAgent):
    async def diagnose(self):
        # Continuously monitor metrics
        metrics = await self.get_metrics()
        
        # Alert if threshold exceeded
        if metrics["error_rate"] > threshold:
            return {
                "description": f"High error rate: {metrics['error_rate']}",
                "confidence": 0.95,
                "impact_score": 9.5
            }
```

## Guardrails

Every agent action must check:

```python
def can_execute(self, action: dict) -> bool:
    """Check if action is within guardrails"""
    
    checks = {
        "financial": action.get("cost", 0) < self.financial_limit,
        "irreversible": not action.get("irreversible", False),
        "approval_required": action.get("requires_approval", False),
        "time": action.get("duration", 0) < self.time_limit
    }
    
    if not all(checks.values()):
        return False
    
    return True
```

## Testing Your Agent

```python
import pytest
from src.agents.my_agent import MyAgent

@pytest.mark.asyncio
async def test_diagnose():
    agent = MyAgent("test-001", "test-domain")
    bottleneck = await agent.diagnose()
    
    assert "description" in bottleneck
    assert "confidence" in bottleneck
    assert bottleneck["confidence"] > 0.5

@pytest.mark.asyncio
async def test_execute():
    agent = MyAgent("test-001", "test-domain")
    action = {"type": "test", "target": "value"}
    result = await agent.execute(action)
    
    assert result["status"] == "success"
```

## Debugging

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# View agent state
agent_state = await agent.get_state()
print(json.dumps(agent_state, indent=2))

# Check decision log
decisions = await agent.get_decisions(limit=10)
for decision in decisions:
    print(f"{decision['timestamp']}: {decision['reasoning']}")
```

## Next Steps

1. Choose your domain
2. Implement `SubAgent` subclass
3. Write tests
4. Register in project config
5. Run diagnostic cycle
6. Review bottleneck detection
7. Iterate based on results
