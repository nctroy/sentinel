# ADR-004: Agent Communication Protocol

**Status:** Accepted
**Date:** 2025-12-27
**Decision Makers:** Troy Shields (Chief Architect)
**Tags:** agents, communication, mcp, architecture, integration

---

## Context

Sentinel's multi-agent system requires agents to share information and coordinate actions. The agents need to:

1. **Share discovered bottlenecks** across domains
2. **Avoid duplicate work** when identifying similar issues
3. **Coordinate dependencies** when bottlenecks block each other
4. **Synthesize insights** from multiple perspectives
5. **Maintain audit trail** of all inter-agent communication

**Current Scale:**
- 5-10 agents initially
- Potential growth to 50+ agents
- Mix of internal and external agents (future)

**Communication Patterns Needed:**
- One-to-many (orchestrator → agents)
- Many-to-one (agents → orchestrator)
- Peer-to-peer (future: agent collaboration)
- External integrations (Notion, GitHub, Slack)

## Decision

Implement a **hybrid communication architecture**:

### Phase 1: Database State Sharing (Current)
- Agents communicate via **shared PostgreSQL database**
- Orchestrator reads all bottlenecks and synthesizes
- Simple, reliable, sufficient for current scale

### Phase 2: Model Context Protocol (Future)
- Adopt **MCP (Model Context Protocol)** for structured agent communication
- Enable Claude-native agent interactions
- Support external tool integrations
- Maintain backward compatibility with database approach

### Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    Phase 1: Current                      │
│                 Database State Sharing                   │
└─────────────────────────────────────────────────────────┘

        ┌──────────────┐
        │ Orchestrator │
        │    Agent     │
        └──────┬───────┘
               │ (reads all bottlenecks)
               ↓
    ┌──────────────────────┐
    │   PostgreSQL DB      │
    │  ┌────────────────┐  │
    │  │  bottlenecks   │  │
    │  │  decisions     │  │
    │  │  weekly_plans  │  │
    │  └────────────────┘  │
    └──────────────────────┘
               ↑
               │ (writes bottlenecks)
      ┌────────┴────────┬────────┬────────┐
      ↓                 ↓        ↓        ↓
  ┌────────┐      ┌─────────┐  ┌──────┐  ┌────────┐
  │Research│      │ GitHub  │  │ Job  │  │  ...   │
  │ Agent  │      │ Agent   │  │Agent │  │        │
  └────────┘      └─────────┘  └──────┘  └────────┘


┌─────────────────────────────────────────────────────────┐
│                    Phase 2: Future                       │
│               MCP + Database Hybrid                      │
└─────────────────────────────────────────────────────────┘

        ┌──────────────┐
        │ Orchestrator │
        │  MCP Server  │
        └──────┬───────┘
               │ (MCP protocol)
               ↓
    ┌──────────────────────┐
    │   MCP Message Bus    │
    │  ┌────────────────┐  │
    │  │ agent.message  │  │
    │  │ agent.request  │  │
    │  │ agent.response │  │
    │  └────────────────┘  │
    └──────────────────────┘
               ↑
               │ (MCP clients)
      ┌────────┴────────┬────────┬────────┐
      ↓                 ↓        ↓        ↓
  ┌────────┐      ┌─────────┐  ┌──────┐  ┌────────┐
  │Research│      │ GitHub  │  │ Job  │  │External│
  │  MCP   │      │  MCP    │  │ MCP  │  │  Tool  │
  │ Client │      │ Client  │  │Client│  │  MCP   │
  └────────┘      └─────────┘  └──────┘  └────────┘
               ↓
    ┌──────────────────────┐
    │   PostgreSQL DB      │
    │   (persistence)      │
    └──────────────────────┘
```

## Rationale

### Why Database State Sharing (Phase 1)?

**Advantages:**
1. **Simplicity** - Agents already use database for persistence
2. **Reliability** - ACID transactions guarantee consistency
3. **Auditability** - Complete history automatically stored
4. **Queryability** - SQL enables complex analysis
5. **No New Infrastructure** - Uses existing PostgreSQL

**Disadvantages:**
- ❌ Not real-time (poll-based)
- ❌ No direct peer-to-peer communication
- ❌ Doesn't scale to 100+ agents
- ❌ No support for streaming data

**When It Works:**
- ✅ Small number of agents (< 20)
- ✅ Batch/scheduled execution (not real-time)
- ✅ Centralized orchestration pattern
- ✅ Simple coordination needs

### Why MCP (Phase 2)?

**Advantages:**
1. **Native Claude Integration** - Built for AI agents
2. **Standardized Protocol** - Industry standard emerging
3. **Tool Ecosystem** - Access to MCP tool servers
4. **Real-time Communication** - Streaming support
5. **Extensibility** - Easy to add new tools/agents

**MCP Benefits for Sentinel:**
- Direct agent-to-agent messaging
- Streaming bottleneck updates
- Integration with external MCP tools (Notion, Slack, etc.)
- Better observability (message tracing)
- Support for complex workflows

**Timeline:**
- Q1 2026: Evaluate MCP maturity
- Q2 2026: Prototype MCP integration
- Q3 2026: Migrate to hybrid model
- Q4 2026: Full MCP adoption

### Why Hybrid (Not Full Migration)?

**Database Still Needed:**
- Persistence layer for audit trail
- Analytics queries (Superset dashboards)
- Historical data analysis
- Compliance requirements

**Hybrid Architecture:**
- MCP for real-time agent communication
- Database for persistence and analytics
- Best of both worlds

## Implementation

### Current: Database State Sharing

**Agent Writes Bottleneck:**
```python
# src/agents/research_agent.py
async def diagnose(self) -> Dict[str, Any]:
    bottleneck = await self.call_claude(...)

    # Write to database
    self.db.save_bottleneck(
        agent_id=self.agent_id,
        bottleneck=bottleneck
    )

    return bottleneck
```

**Orchestrator Reads All:**
```python
# src/agents/orchestrator.py
async def synthesize(self) -> Dict[str, Any]:
    # Read all recent bottlenecks
    bottlenecks = self.db.get_recent_bottlenecks(days=7)

    # Group by agent/domain
    by_domain = self._group_by_domain(bottlenecks)

    # Synthesize with Claude
    synthesis = await self.call_claude(
        system_prompt="Synthesize bottlenecks...",
        user_message=json.dumps(by_domain)
    )

    return synthesis
```

### Future: MCP Integration

**MCP Server Setup:**
```python
# src/mcp_server/sentinel_server.py
from mcp.server import Server
from mcp.types import Tool, Resource

server = Server("sentinel")

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="report_bottleneck",
            description="Report a discovered bottleneck",
            inputSchema={
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "impact_score": {"type": "number"},
                    "confidence": {"type": "number"},
                },
                "required": ["description"]
            }
        ),
        Tool(
            name="get_bottlenecks",
            description="Retrieve bottlenecks from other agents",
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {"type": "string"},
                    "status": {"type": "string"},
                }
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> str:
    if name == "report_bottleneck":
        # Save to database
        bottleneck_id = db.save_bottleneck(arguments)

        # Broadcast to other agents via MCP
        await mcp_bus.publish(
            topic="bottleneck.identified",
            message=arguments
        )

        return f"Bottleneck {bottleneck_id} reported"

    elif name == "get_bottlenecks":
        bottlenecks = db.query_bottlenecks(arguments)
        return json.dumps(bottlenecks)
```

**Agent MCP Client:**
```python
# src/agents/base_agent.py (future)
from mcp import ClientSession

class BaseAgent:
    async def initialize_mcp(self):
        self.mcp_session = ClientSession()
        await self.mcp_session.connect("sentinel-mcp-server")

    async def report_bottleneck(self, bottleneck: dict):
        # Use MCP tool
        result = await self.mcp_session.call_tool(
            "report_bottleneck",
            bottleneck
        )
        return result

    async def subscribe_to_bottlenecks(self):
        # Subscribe to real-time updates
        async for message in self.mcp_session.subscribe("bottleneck.*"):
            await self.handle_bottleneck_update(message)
```

## Consequences

### Positive

✅ **Immediate Value** - Database approach works today
✅ **Future-Proof** - Clear path to MCP adoption
✅ **Low Risk** - Phased migration, no big-bang cutover
✅ **Standards-Based** - MCP is emerging industry standard
✅ **Flexibility** - Hybrid model supports various patterns

### Negative

⚠️ **Technical Debt** - Will maintain both protocols temporarily
⚠️ **Migration Effort** - Requires agent refactoring for MCP
⚠️ **MCP Maturity Risk** - Protocol still evolving
⚠️ **Complexity** - Two communication paths to maintain

### Trade-offs

**Database State Sharing:**
- ✅ Simple, reliable, auditable
- ❌ Not real-time, limited scalability

**MCP:**
- ✅ Real-time, scalable, extensible
- ❌ More complex, requires infrastructure

**Hybrid:**
- ✅ Best of both worlds
- ❌ Operational overhead

## Migration Plan

### Phase 1: Current (2025 Q4)
- ✅ All agents use database
- ✅ Orchestrator polls database
- ✅ Simple, working solution

### Phase 2: MCP Prototype (2026 Q1-Q2)
- [ ] Evaluate MCP maturity
- [ ] Build MCP server for Sentinel
- [ ] Migrate 1-2 agents to MCP
- [ ] Test hybrid architecture

### Phase 3: Gradual Migration (2026 Q3)
- [ ] Migrate remaining agents
- [ ] Database becomes persistence layer
- [ ] MCP becomes communication layer

### Phase 4: Full MCP (2026 Q4)
- [ ] All real-time communication via MCP
- [ ] Database for persistence only
- [ ] Integrate external MCP tools

## Alternative Considered: Message Queue

**Option: RabbitMQ / Redis Pub/Sub**

**Pros:**
- Mature, battle-tested
- High performance
- Rich ecosystem

**Cons:**
- Not AI-native
- Requires separate infrastructure
- No standardized agent protocol
- Vendor lock-in risk

**Decision:** Rejected in favor of MCP for AI-first design

## References

- MCP Specification: https://modelcontextprotocol.io/
- Anthropic MCP Docs: https://docs.anthropic.com/claude/docs/mcp
- Agent Communication: https://arxiv.org/abs/2308.08155

---

**Supersedes:** None
**Superseded By:** None
**Related:** ADR-003 (Graduated Autonomy), ADR-005 (Python Technology Stack)
