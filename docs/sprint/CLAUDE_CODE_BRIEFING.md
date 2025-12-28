# CLAUDE CODE BRIEFING: Sentinel Foundation Sprint (Dec 27-31, 2025)

**Project:** Sentinel - Autonomous Multi-Agent Orchestration System  
**Owner:** Troy Neff (@nctroy)  
**Repository:** https://github.com/nctroy/sentinel  
**Timeline:** 5-day sprint before 30-in-30 challenge (Jan 1-30, 2026)  
**Primary Goal:** Production-ready deployment with observability for portfolio demonstration

---

## EXECUTIVE SUMMARY

Sentinel is an autonomous multi-agent orchestration system that identifies and resolves bottlenecks across multiple business domains (job search, AI literacy business, photography, 30-in-30 challenge projects). The system uses a Chief of Staff (CoS) orchestrator with domain-specific sub-agents operating under graduated autonomy.

**Current State:** 
- ✅ Solid Python foundation (SQLAlchemy ORM, CLI, agent framework)
- ✅ PostgreSQL schema with 6 tables
- ✅ Graduated autonomy model implemented
- ✅ Working simulations ready for real API integration
- 🟡 Claude API integration stubbed but not connected
- 🟡 Notion client working but dashboards incomplete
- ❌ No production observability/monitoring yet

**Sprint Objective:** Deploy production-grade system with SigNoz + Apache Superset observability stack, Claude API integration, and portfolio-ready documentation.

---

## ARCHITECTURAL CONTEXT

### Key Architectural Decisions Already Made:

1. **Python 3.10+ Stack** - Modern Python with type hints, async/await
2. **PostgreSQL State Store** - Single source of truth for all system state
3. **Graduated Autonomy** - Diagnostic → Conditional → Full autonomy levels
4. **MCP Integration** - Planned but not yet implemented
5. **Observability Stack** - **NEW DECISION:** SigNoz + Superset (see ADR-001)

### Risk Mitigation Framework (6 Critical Risks):

**R-001: Skill Drift & Dependencies** (P1)  
**R-002: Context Loss in Upgrades** (P2)  
**R-003: Compounding Recommendations** (P2)  
**R-004: Trust Calibration Failures** (P1) - *Already partially addressed with confidence thresholds*  
**R-005: Failure Detection & Recovery** (P1)  
**R-006: Security & Attack Surface** (P1)

---

## REPOSITORY STRUCTURE (Current)

```
sentinel/
├── .github/workflows/          # CI/CD pipelines
├── config/                     # Configuration files
├── docker/                     # Docker setup
├── docs/                       # ARCHITECTURE.md, SETUP.md, AGENT_DESIGN.md
├── security-reports/           # Security analysis
├── src/
│   ├── mcp_server/            # MCP server (stubbed)
│   ├── agents/
│   │   ├── base_agent.py      # ✅ Base class with confidence thresholds
│   │   ├── sub_agent.py       # ✅ Domain agent base
│   │   ├── orchestrator.py    # ✅ Chief of Staff
│   │   ├── research_agent.py  # ✅ Research analyst
│   │   └── github_agent.py    # ✅ GitHub triage
│   ├── storage/
│   │   ├── models.py          # ✅ SQLAlchemy models (6 tables)
│   │   ├── postgres_client.py # ✅ Database client
│   │   └── notion_client.py   # ✅ Notion integration
│   ├── schemas/               # Data models
│   └── cli/
│       └── cli.py             # ✅ Working CLI with Rich output
├── tests/                     # Test suite
├── requirements.txt           # ✅ Dependencies defined
├── pyproject.toml
└── setup.py
```

---

## 5-DAY SPRINT PLAN

### DAY 1-2: Core Integration & Infrastructure

**Priority 1: Claude API Integration**
```python
# Replace simulated diagnostics in cli.py and agents
# Current: _simulate_agent_diagnostic()
# Target: Real Claude API calls using anthropic package (already in requirements.txt)

# Example integration point in research_agent.py:
async def diagnose(self) -> Dict[str, Any]:
    # TODO: Replace simulation with actual Claude API call
    # Use system prompt defining agent's domain expertise
    # Return structured JSON matching existing bottleneck schema
```

**Files to Modify:**
- `src/cli/cli.py` - Remove `_simulate_agent_diagnostic()`
- `src/agents/research_agent.py` - Implement real Claude API in `diagnose()`
- `src/agents/github_agent.py` - Implement real Claude API in `diagnose()`
- `src/agents/orchestrator.py` - Implement real Claude API in `synthesize()`

**Priority 2: OpenTelemetry Instrumentation**
```bash
# Add to requirements.txt:
opentelemetry-api==1.22.0
opentelemetry-sdk==1.22.0
opentelemetry-instrumentation-fastapi==0.43b0
opentelemetry-exporter-otlp==1.22.0
```

**Files to Create:**
- `src/observability/telemetry.py` - OpenTelemetry setup
- `src/observability/__init__.py`

**Instrumentation Points:**
- Every agent `diagnose()` call
- Every agent `execute()` call
- Orchestrator `synthesize()` cycle
- Database operations (query latency)
- Claude API calls (latency, token usage)

---

### DAY 3: SigNoz Deployment

**Create Infrastructure Files:**

**File:** `docker-compose.observability.yml`
```yaml
# Full SigNoz stack deployment
# Components:
# - ClickHouse (time-series database)
# - SigNoz OTel Collector
# - SigNoz Query Service
# - SigNoz Frontend
# 
# Reference: https://signoz.io/docs/install/docker/
```

**File:** `otel-collector-config.yaml`
```yaml
# OpenTelemetry Collector configuration
# - Receivers: OTLP (gRPC and HTTP)
# - Processors: Batch, memory limiter
# - Exporters: ClickHouse via SigNoz
```

**Dashboards to Create in SigNoz:**
1. **Agent Health Dashboard**
   - Agent uptime/downtime status
   - Error rate per agent
   - Average diagnosis time
   - Confidence score distribution

2. **Bottleneck Detection Dashboard**
   - Bottlenecks identified per day
   - Impact score distribution
   - Resolution time tracking
   - Top blocking issues

3. **API Performance Dashboard**
   - Claude API latency (p50, p95, p99)
   - Token usage per agent
   - API error rate
   - Cost tracking

4. **Orchestrator Dashboard**
   - Synthesis cycle duration
   - Cross-domain conflicts detected
   - Priority ranking changes
   - Weekly plan execution rate

---

### DAY 4: Apache Superset Deployment

**Create Infrastructure Files:**

**File:** `docker-compose.analytics.yml`
```yaml
# Apache Superset deployment
# - Superset application
# - Redis (for caching)
# - PostgreSQL connection (to existing Sentinel DB)
#
# Reference: https://superset.apache.org/docs/installation/installing-superset-using-docker-compose
```

**Dashboards to Create in Superset:**

**Dashboard 1: Job Search Executive View**
- Application funnel (researched → applied → interview → offer)
- Response rate trends
- Interview conversion rate
- Target company pipeline health
- Weekly application velocity

**Dashboard 2: 30-in-30 Challenge Tracker**
- Projects launched vs. target (30)
- Daily progress heatmap
- Success/failure ratio
- Time investment per project
- Revenue/traction metrics

**Dashboard 3: Multi-Business Portfolio**
- AI Literacy: Sessions delivered, revenue, client satisfaction
- Photography: Projects completed, revenue, gear utilization
- Job Search: Active applications, interviews scheduled
- Overall: Time allocation across domains

**Dashboard 4: Sentinel System Health (Business View)**
- Agent productivity score
- Bottlenecks resolved vs. identified
- Orchestration effectiveness
- System uptime and reliability

**SQL Queries to Create:**
```sql
-- Job search funnel
SELECT 
    status,
    COUNT(*) as count,
    AVG(confidence) as avg_confidence
FROM bottlenecks 
WHERE agent_id LIKE 'job-%'
GROUP BY status;

-- Agent productivity
SELECT 
    agent_id,
    COUNT(DISTINCT DATE(identified_at)) as active_days,
    COUNT(*) as bottlenecks_found,
    AVG(impact_score) as avg_impact
FROM bottlenecks
GROUP BY agent_id;
```

---

### DAY 5: Production Hardening & Documentation

**Priority 1: Reverse Proxy & Security**

**File:** `nginx/nginx.conf`
```nginx
# Reverse proxy configuration
# Routes:
# - sentinel.troyneff.com/ops → SigNoz (port 3301)
# - sentinel.troyneff.com/executive → Superset (port 8088)
# - sentinel.troyneff.com/api → FastAPI (port 8000)
#
# SSL/TLS via Let's Encrypt
# Basic auth for /ops and /executive
# Rate limiting on /api
```

**File:** `scripts/setup-ssl.sh`
```bash
#!/bin/bash
# Automated Let's Encrypt SSL certificate setup
# Uses certbot with nginx plugin
```

**Priority 2: Architecture Decision Records (ADRs)**

**Files to Create in:** `docs/adr/`

1. ✅ **ADR-001: Observability Stack Selection** (already created)
   - Documents SigNoz + Superset decision
   - Evaluates Grafana/Prometheus/Loki alternative
   - Rationale for hybrid approach

2. **ADR-002: Database Schema Design**
   - Why PostgreSQL over NoSQL
   - Table structure rationale
   - SQLAlchemy ORM choice

3. **ADR-003: Graduated Autonomy Model**
   - Three-tier autonomy levels
   - Trust calibration mechanism
   - Safety rails and guardrails

4. **ADR-004: Agent Communication Protocol**
   - Current: Direct database state sharing
   - Future: MCP integration roadmap
   - Trade-offs and timeline

5. **ADR-005: Python Technology Stack**
   - Python 3.10+ choice
   - Key libraries (FastAPI, SQLAlchemy, Typer)
   - Why not Go/Rust/Node.js

6. **ADR-006: Security Architecture**
   - Secret management (.env, never committed)
   - Gitleaks integration
   - API authentication strategy
   - Audit logging approach

**Priority 3: README & Documentation Updates**

**File:** `README.md` (major overhaul)
```markdown
# Sentinel: Autonomous Multi-Agent Orchestration

[Badges: Build status, test coverage, license]

## Live Demo
🔗 **Production Instance:** https://sentinel.troyneff.com
- Operations Dashboard: /ops (SigNoz)
- Executive Analytics: /executive (Superset)

## Architecture
[High-level architecture diagram]
- Multi-agent system with graduated autonomy
- PostgreSQL state store
- OpenTelemetry observability
- Production-grade monitoring

## Quick Start
[Docker Compose commands]

## Documentation
- [Architecture Overview](docs/ARCHITECTURE.md)
- [Setup Guide](docs/SETUP.md)
- [Agent Design](docs/AGENT_DESIGN.md)
- [Architecture Decisions](docs/adr/)

## Portfolio Context
This system demonstrates cloud security architecture, DevOps practices,
and AI system operations for interview purposes. See [PORTFOLIO.md](docs/PORTFOLIO.md)
for interview talking points.
```

**File:** `docs/PORTFOLIO.md` (NEW)
```markdown
# Sentinel as Portfolio Demonstration

## Interview Narrative

"I built Sentinel as an autonomous multi-agent orchestration system 
where I maintain architectural control without micromanaging execution..."

## Technical Highlights
- Multi-agent architecture with graduated autonomy
- Production observability (OpenTelemetry + SigNoz)
- Business intelligence layer (Apache Superset)
- Security-first design (ADR-006)

## Demo Script (10-minute presentation)
[Step-by-step demo flow]

## Deep-Dive Topics
- Systems thinking and bottleneck analysis
- Trust calibration in autonomous systems
- Multi-audience dashboard design
- Cost-effective production deployment

## Questions I Can Answer
[Anticipated interview questions with talking points]
```

**Priority 4: Backup & Recovery**

**File:** `scripts/backup-postgres.sh`
```bash
#!/bin/bash
# Automated PostgreSQL backup
# Daily snapshots to S3/Digital Ocean Spaces
# 7-day retention
```

**File:** `scripts/restore-postgres.sh`
```bash
#!/bin/bash
# PostgreSQL restore from backup
# Validates backup integrity before restore
```

**Priority 5: Monitoring the Monitors**

**File:** `docker-compose.monitoring.yml`
```yaml
# Uptime monitoring for SigNoz and Superset themselves
# Simple healthcheck endpoints
# Alert on dashboard downtime
```

---

## DEPLOYMENT ARCHITECTURE

**Recommended Hosting:** Digital Ocean Droplet (4GB RAM / 2 vCPUs) - $24/month

```
┌─────────────────────────────────────────────────┐
│   Digital Ocean Droplet (Ubuntu 24.04)          │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌─────────────────────────────────────┐       │
│  │   Docker Compose Services           │       │
│  ├─────────────────────────────────────┤       │
│  │                                     │       │
│  │  Sentinel App (FastAPI)             │       │
│  │  PostgreSQL                         │       │
│  │  SigNoz (+ ClickHouse)             │       │
│  │  Apache Superset (+ Redis)         │       │
│  │  Nginx Reverse Proxy               │       │
│  │                                     │       │
│  └─────────────────────────────────────┘       │
│                                                 │
│  Ports:                                         │
│  - 80/443 (Nginx - public)                     │
│  - 5432 (PostgreSQL - internal only)           │
│  - 3301 (SigNoz - via Nginx)                   │
│  - 8088 (Superset - via Nginx)                 │
│  - 8000 (FastAPI - via Nginx)                  │
│                                                 │
└─────────────────────────────────────────────────┘
```

**Alternative:** AWS (for interview cred)
- EC2 t3.medium: ~$30/month
- RDS PostgreSQL t3.micro: ~$15/month
- ALB: ~$16/month
- Total: ~$61/month + demonstrates AWS expertise

---

## CRITICAL FILES REFERENCE

**Already Uploaded (Available in Context):**
- ✅ requirements.txt
- ✅ cli.py
- ✅ research_agent.py
- ✅ github_agent.py
- ✅ sub_agent.py
- ✅ orchestrator.py
- ✅ base_agent.py
- ✅ notion_client.py
- ✅ postgres_client.py
- ✅ models.py
- ✅ state_schema.py
- ✅ Config files: research.json, github-triage.json, job-search.json

**Already Created in This Session:**
- ✅ ADR-001: Observability Stack Selection
- ✅ Sentinel Risk Analysis & Mitigation Framework
- ✅ CoS Briefing for Risk Mitigation
- ✅ Sentinel Architectural Philosophy Document

---

## INTEGRATION PATTERNS

### Claude API Integration Pattern:

```python
# src/agents/base_agent.py - Add Claude client

import anthropic
import os

class BaseAgent(ABC):
    def __init__(self, agent_id: str, agent_type: str = "base"):
        # ... existing code ...
        self.claude_client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
    
    async def call_claude(self, system_prompt: str, user_message: str) -> str:
        """Make Claude API call with observability"""
        with tracer.start_as_current_span("claude_api_call") as span:
            span.set_attribute("agent.id", self.agent_id)
            span.set_attribute("prompt.length", len(user_message))
            
            response = self.claude_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )
            
            # Track usage
            span.set_attribute("tokens.input", response.usage.input_tokens)
            span.set_attribute("tokens.output", response.usage.output_tokens)
            
            return response.content[0].text
```

### OpenTelemetry Integration Pattern:

```python
# src/observability/telemetry.py

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

def setup_telemetry():
    """Initialize OpenTelemetry with SigNoz backend"""
    provider = TracerProvider()
    
    # SigNoz OTLP endpoint
    otlp_exporter = OTLPSpanExporter(
        endpoint="http://localhost:4317",
        insecure=True
    )
    
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    trace.set_tracer_provider(provider)
    
    return trace.get_tracer(__name__)

# Global tracer
tracer = setup_telemetry()
```

---

## ENVIRONMENT VARIABLES REQUIRED

**File:** `.env.example` (create for reference)
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/sentinel

# Claude API
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Notion (optional - being replaced)
NOTION_API_KEY=secret_xxxxx
NOTION_WORKSPACE_ID=xxxxx

# OpenTelemetry
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
OTEL_SERVICE_NAME=sentinel

# Production
DOMAIN=sentinel.troyneff.com
SSL_EMAIL=troy@example.com

# Security
SECRET_KEY=generate-random-secret-here
ADMIN_PASSWORD=generate-strong-password
```

---

## TESTING STRATEGY

**Priority Tests for Sprint:**

1. **Agent Integration Tests**
```python
# tests/test_claude_integration.py
async def test_research_agent_real_diagnosis():
    """Test ResearchAnalystAgent with real Claude API"""
    agent = ResearchAnalystAgent("research-01", "ai-research")
    result = await agent.diagnose()
    
    assert "description" in result
    assert 0 <= result["confidence"] <= 1.0
    assert 0 <= result["impact_score"] <= 10
```

2. **Observability Tests**
```python
# tests/test_telemetry.py
def test_spans_exported_to_signoz():
    """Verify OpenTelemetry spans are exported"""
    # Run agent diagnosis
    # Check SigNoz API for spans
```

3. **Database Migration Tests**
```python
# tests/test_migrations.py
def test_schema_up_to_date():
    """Ensure all migrations applied"""
```

---

## SUCCESS CRITERIA (End of Day 5)

**Must Have (Blocking for Jan 1 launch):**
- ✅ Claude API integrated and working in at least 2 agents
- ✅ OpenTelemetry spans visible in SigNoz
- ✅ SigNoz operational dashboard accessible at /ops
- ✅ Superset executive dashboard accessible at /executive
- ✅ SSL/TLS configured with Let's Encrypt
- ✅ PostgreSQL backups automated
- ✅ ADR-001 through ADR-006 documented
- ✅ README.md updated with live demo link

**Nice to Have (Can defer to Week 1 of challenge):**
- Database query performance optimization
- Advanced SigNoz alerting rules
- Superset email reports
- Load testing results
- Full test coverage (>80%)

**Validation Commands:**
```bash
# Verify all services running
docker-compose ps

# Check SigNoz health
curl http://localhost:3301/api/v1/version

# Check Superset health
curl http://localhost:8088/health

# Run CLI diagnostic
python -m src.cli.cli run-cycle --mode diagnostic --verbose

# Check OpenTelemetry traces
# Visit https://sentinel.troyneff.com/ops
```

---

## IMPORTANT NOTES FOR CLAUDE CODE

### Existing Code Quality:
- **HIGH QUALITY** - Clean architecture, proper separation of concerns
- **SECURITY-CONSCIOUS** - Gitleaks, pre-commit hooks already configured
- **WELL-STRUCTURED** - SQLAlchemy models, CLI with Rich, proper logging
- **NOT VIBE CODING** - Thoughtful design decisions evident throughout

### What NOT to Rebuild:
- ❌ Don't rewrite the agent framework - it's solid
- ❌ Don't change the database schema without migration
- ❌ Don't replace PostgreSQL with another database
- ❌ Don't remove existing CLI commands

### What TO Build:
- ✅ Connect Claude API to existing agent methods
- ✅ Add OpenTelemetry instrumentation (non-invasive)
- ✅ Deploy observability stack (separate docker-compose files)
- ✅ Create documentation (ADRs, README updates)
- ✅ Production hardening (nginx, SSL, backups)

### Coding Standards:
- Type hints on all functions
- Docstrings in Google style
- Use existing logging framework
- Follow existing error handling patterns
- Add tests for new functionality

### Git Workflow:
```bash
# Feature branches for each major component
git checkout -b feature/claude-api-integration
git checkout -b feature/opentelemetry-instrumentation
git checkout -b feature/signoz-deployment
git checkout -b feature/superset-deployment
git checkout -b feature/production-hardening

# ADRs can go directly to main
git checkout -b docs/adr-002-through-006
```

---

## RISK MITIGATION CHECKPOINTS

**Daily Check-ins (End of Each Day):**

**Day 1 Checkpoint:**
- [ ] Claude API successfully returns structured bottleneck JSON
- [ ] At least 1 agent (research or github) working with real API
- [ ] OpenTelemetry dependencies installed and tracer initialized

**Day 2 Checkpoint:**
- [ ] All agents using real Claude API (no simulations)
- [ ] OpenTelemetry spans visible in logs
- [ ] Docker compose file for SigNoz ready

**Day 3 Checkpoint:**
- [ ] SigNoz running locally
- [ ] At least 1 operational dashboard created
- [ ] Spans from agents appearing in SigNoz UI

**Day 4 Checkpoint:**
- [ ] Superset running locally
- [ ] Connected to PostgreSQL
- [ ] At least 1 executive dashboard created

**Day 5 Checkpoint:**
- [ ] Nginx reverse proxy working
- [ ] SSL/TLS configured
- [ ] All 6 ADRs documented
- [ ] README updated with deployment instructions

---

## CONTACT & ESCALATION

**If Blocked:**
- Check existing code patterns first (they're good!)
- Review ADR-001 for architectural guidance
- Reference uploaded files for schema/structure
- Troy available for architectural decisions (not implementation details)

**Decision Authority:**
- **Troy decides:** Architecture, tool selection, deployment targets
- **Claude Code implements:** Following established patterns, adding integrations, creating docs

**Philosophy:**
This is NOT vibe coding. This is **architectural delegation** - Troy owns the "what" and "why," Claude Code handles the "how" within established guardrails.

---

## FINAL NOTES

This sprint transforms Sentinel from "working prototype" to "production-ready portfolio piece." Every decision is documented, every integration is observable, and the result showcases enterprise-grade engineering practices.

**The bar for "impressive interview demo" is:**
1. Live, accessible deployment (https://sentinel.troyneff.com)
2. Real-time operational dashboards showing system health
3. Executive analytics proving business value
4. Clean, documented codebase with ADRs
5. Ability to explain architectural decisions in depth

By end of Day 5, you'll have all of this.

**LFG! 🚀**

---

## APPENDIX: Quick Reference Commands

**Start Full Stack:**
```bash
docker-compose -f docker-compose.yml \
               -f docker-compose.observability.yml \
               -f docker-compose.analytics.yml up -d
```

**View Logs:**
```bash
docker-compose logs -f sentinel-app
docker-compose logs -f signoz
docker-compose logs -f superset
```

**Database Backup:**
```bash
./scripts/backup-postgres.sh
```

**Deploy to Production:**
```bash
./scripts/deploy.sh
```

**Run Tests:**
```bash
pytest -v --cov=src tests/
```
