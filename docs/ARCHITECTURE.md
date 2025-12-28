# Sentinel Architecture

## Overview

Sentinel is a hierarchical, multi-agent orchestration system designed to manage autonomous agents across multiple domains while maintaining strategic coherence.

## Core Principles

1. **Bottleneck-Focused**: Attack the single highest-leverage bottleneck each cycle
2. **Graduated Autonomy**: Start read-only, progress to conditional, then full autonomy
3. **Truth-Seeking**: Access primary sources (APIs, databases, real data)
4. **Transparent Reasoning**: All decisions logged with confidence scores and assumptions

## System Architecture

### Layer 1: Domain-Specific Sub-Agents

Each sub-agent owns a specific domain:
- **Research Agent**: Market research, opportunity validation, customer discovery
- **Security Aggregator**: ESLint, ZAP, and Snyk vulnerability tracking
- **Production Agent**: Implementation, workflow automation, execution
- **Distribution Agent**: Marketing, sales, customer communication
- **Personal Development Agent**: Learning, skill acquisition, health

**Sub-Agent Responsibilities:**
- Daily diagnostic run: Identify bottleneck in your domain
- Execute assigned tasks (within autonomy constraints)
- Report state to orchestrator
- Maintain audit log of decisions

**Sub-Agent State:**
```python
{
    "agent_id": "research-001",
    "domain": "job-search",
    "last_run": "2024-12-25T08:00:00Z",
    "bottleneck": {
        "description": "Resume doesn't highlight cloud security depth",
        "confidence": 0.87,
        "impact_score": 9.2,
        "blocking": ["interview_prep"]
    },
    "actions_taken": [...],
    "next_actions": [...],
    "metrics": {...}
}
```

### Layer 2: Orchestration Agent (Chief of Staff)

The orchestrator:
- Aggregates daily reports from all sub-agents
- Identifies cross-domain bottlenecks
- Allocates resources based on impact
- Generates weekly strategic plan
- Makes final decisions (or escalates to you)

**Orchestration Logic:**
```
1. Collect daily reports from all sub-agents
2. For each bottleneck:
   - Calculate impact score (effort × impact × leverage)
   - Identify cross-domain dependencies
3. Sort by impact
4. Build weekly action plan
5. Propose resource allocation
6. Present to human (you) for approval/modification
```

### Layer 3: Persistent State

#### PostgreSQL
- Agent state (fast queries, indexing, transactions)
- Decision logs (audit trail)
- Metrics and KPIs
- Relationships between bottlenecks

**Schema:**
- `agents` — Sub-agent definitions
- `states` — Current state snapshot per agent
- `bottlenecks` — Identified bottlenecks
- `decisions` — Decisions made by orchestrator
- `actions` — Executed actions with outcomes
- `audit_log` — Complete transaction log

#### Sentinel Command Center (GUI)
- Real-time human-readable dashboard
- Built with Next.js, React, and ShadcnUI
- Direct connection to FastAPI/PostgreSQL backend
- Control center for manual agent triggers and approvals
- Actionable security and bottleneck feed

**Schema:**
- `agents` — Sub-agent definitions
- `states` — Current state snapshot per agent
- `bottlenecks` — Identified bottlenecks
- `decisions` — Decisions made by orchestrator
- `actions` — Executed actions with outcomes
- `audit_log` — Complete transaction log

## Agent Communication

Agents communicate via **MCP (Model Context Protocol)**:

```
┌──────────────┐
│ Sub-Agent 1  │
└──────┬───────┘
       │
       │ (MCP Call)
       │ "get_bottleneck_for(domain=job_search)"
       ▼
┌──────────────────────────┐
│  Orchestration Agent     │
│  (Claude via MCP)        │
└──────────────────────────┘
       │
       │ (MCP Response)
       │ {bottleneck, actions, next_steps}
       ▼
┌──────────────┐
│ Sub-Agent 1  │
└──────────────┘
```

## Execution Flow

### Daily Cycle (Sub-Agents)

```
6:00 AM
  ├─ Job Search Agent wakes up
  ├─ Queries PostgreSQL for current state
  ├─ Runs diagnosis: "What's blocking progress?"
  ├─ Returns bottleneck + recommended actions
  ├─ Writes to PostgreSQL
  ├─ Real-time update to Command Center (GUI)
  └─ Sleeps

  ├─ AI Business Agent (same)
  ├─ Photography Agent (same)
  └─ Personal Dev Agent (same)
```

### Weekly Cycle (Orchestrator)

```
Friday 5:00 PM
  ├─ Orchestrator Agent wakes up
  ├─ Queries PostgreSQL for all daily reports
  ├─ Synthesizes: "Which bottleneck has highest leverage?"
  ├─ Identifies cross-domain conflicts
  ├─ Ranks by impact score
  ├─ Generates weekly plan
  ├─ Updates Command Center (GUI)
  ├─ Presents recommendations to you
  └─ Awaits approval/modification
```

## Autonomy Levels

### Diagnostic Mode (Default)
- Agents analyze but don't execute
- Perfect for building trust
- You review daily reports
- You make all decisions

### Conditional Autonomy
- Agents execute pre-approved actions
- Example: "If interview scheduled, auto-update calendar"
- All actions logged
- You review weekly

### Full Autonomy
- Agents make independent decisions
- Within your strategic guidelines
- You review outcomes (not decisions)
- Maximum efficiency

## Data Flow

```
External Data (APIs, emails, calendar)
         │
         ▼
    Sub-Agents (Diagnose)
         │
         ▼
    PostgreSQL (Raw state)
         │
         ├──→ Orchestrator (Synthesize)
         │         │
         │         ▼
         │    Command Center GUI (Human view)
         │
         └──→ You (Strategic decisions)
```

## Safety & Constraints

1. **Action Guardrails**
   - Financial decisions require approval
   - Public communications reviewed first
   - Calendar conflicts prevented
   - No data deletion without confirmation

2. **Confidence Thresholds**
   - Agents only act if confidence > threshold
   - Low-confidence decisions escalated to you
   - All assumptions logged

3. **Audit Trail**
   - Every decision logged with reasoning
   - Complete rollback capability
   - Historical analysis for learning

## Extending Sentinel

To add a new sub-agent:

1. Define domain (e.g., "photography-business")
2. Create agent class inheriting from `SubAgent`
3. Define state schema
4. Register with orchestrator
5. Configure decision rules

See `docs/AGENT_DESIGN.md` for details.

## Performance Considerations

- Sub-agents run in parallel (4 concurrent max)
- PostgreSQL queries indexed for speed
- Notion API batched for efficiency
- MCP server handles concurrent requests
- Timeouts prevent runaway executions

## Future Enhancements

- [ ] Multi-cloud support (Azure, GCP)
- [ ] Custom metrics dashboard
- [ ] Reinforcement learning from outcomes
- [ ] Integration with more tools (Slack, email, calendar)
- [ ] Distributed agent execution
- [ ] Prediction models for bottleneck emergence
