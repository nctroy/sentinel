# Sentinel

**Production-Grade Multi-Agent AI Orchestration System**

Sentinel is a comprehensive AI orchestration platform that manages domain-specific agents across multiple business portfolios. It serves as your intelligent Chief of Staff, identifying bottlenecks, synthesizing priorities, and coordinating action across your professional and personal projects.

> **Portfolio Project** | Demonstrates cloud security architecture, AI systems engineering, and production DevOps practices

---

## 🎯 Overview

Sentinel helps you manage complex multi-domain workflows through intelligent AI agents:

- **Job Search Optimization**: Track applications, interview prep, salary research
- **GitHub Repository Management**: Issue triage, PR reviews, dependency updates
- **Multi-Business Portfolio**: AI literacy consulting, photography projects, personal development
- **30-in-30 Challenge**: Project tracking and progress monitoring

**Key Differentiators:**
- Production-ready observability (SigNoz + OpenTelemetry)
- Executive business intelligence (Apache Superset)
- Comprehensive security architecture (pre-commit scanning, TLS/SSL, audit trails)
- Graduated autonomy model (safe AI decision-making)

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                   SENTINEL PRODUCTION STACK                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Nginx Reverse Proxy (SSL/TLS)               │  │
│  │               your-domain.com (Port 443)                 │  │
│  └────┬─────────────────┬────────────────┬──────────────────┘  │
│       │                 │                │                      │
│       ▼                 ▼                ▼                      │
│  ┌─────────┐      ┌──────────┐    ┌──────────┐                │
│  │ SigNoz  │      │ Superset │    │ Next.js  │                │
│  │  Ops    │      │Executive │    │Dashboard │                │
│  │Dashboard│      │Dashboard │    │  :3000   │                │
│  │ :3301   │      │  :8088   │    │ (GUI)    │                │
│  └────┬────┘      └─────┬────┘    └────┬─────┘                │
│       │                 │              │                        │
│       ▼                 ▼              ▼                        │
│  ┌─────────────────────────────────────────────┐               │
│  │         PostgreSQL State Store              │               │
│  │  • Agents      • Decisions                  │               │
│  │  • Bottlenecks • Weekly Plans               │               │
│  │  • Audit Logs  • Security Findings          │               │
│  └──────┬───────────────────────────────┬──────┘               │
│         │                               │                      │
│         ▼                               ▼                      │
│  ┌──────────┐                    ┌─────────────┐               │
│  │ FastAPI  │                    │OpenTelemetry│               │
│  │ Sentinel │                    │   Traces    │               │
│  │ Server   │                    └─────────────┘               │
│  │  :8000   │                                                  │
│  └──────────┘                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Agent Architecture

```
┌──────────────────────────────────────────────────────────┐
│              Orchestrator Agent (Chief of Staff)         │
│  • Synthesizes bottlenecks from all sub-agents          │
│  • Creates weekly prioritized plans                     │
│  • Detects cross-domain conflicts and dependencies      │
└────┬────────────┬──────────────┬───────────────┬────────┘
     │            │              │               │
     ▼            ▼              ▼               ▼
┌─────────┐  ┌─────────┐  ┌──────────┐  ┌──────────────┐
│  Job    │  │Security │  │Research  │  │   Future     │
│ Search  │  │ Agent   │  │ Agent    │  │   Agents     │
│ Agent   │  │         │  │          │  │ (Extensible) │
└────┬────┘  └────┬────┘  └─────┬────┘  └──────┬───────┘
     │            │             │              │
     └────────────┴─────────────┴──────────────┘
                       │
                       ▼
            ┌───────────────────┐
            │ Shared PostgreSQL │
            │   State Store     │
            └───────────────────┘
```

---

## ✨ Features

### Core Capabilities

- **🤖 Multi-Agent Orchestration**: Specialized agents for job search, security posture, research, and business management
- **🛡️ Unified Security Dashboard**: Ingest and visualize findings from ESLint, ZAP, and Snyk in a single view
- **📊 Dual-Dashboard System**:
  - **SigNoz**: Real-time operational monitoring (logs, metrics, traces)
  - **Apache Superset**: Executive business intelligence (KPIs, portfolio health)
- **🔐 Production Security**: Pre-commit scanning (Gitleaks, Bandit, Safety), TLS/SSL, rate limiting, audit trails
- **📈 OpenTelemetry Integration**: Industry-standard observability and distributed tracing
- **🎛️ Graduated Autonomy**: Safe AI decision-making (diagnostic → conditional → full autonomy)
- **📝 Complete Audit Trail**: Every agent decision logged with reasoning and confidence scores

### Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Language** | Python 3.10+ | Application development |
| **API Framework** | FastAPI | Async web API |
| **Frontend** | Next.js (React) | Sentinel Command Center (GUI) |
| **UI Library** | Shadcn UI + Tailwind | Dashboard styling |
| **Database** | PostgreSQL 15 | State persistence |
| **Observability** | SigNoz + OpenTelemetry | Ops monitoring |
| **Business Intelligence** | Apache Superset | Executive dashboards |
| **Reverse Proxy** | Nginx | SSL termination, routing |
| **SSL** | Let's Encrypt | Free TLS certificates |
| **CLI** | Typer | Command-line interface |

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** (Python 3.11+ recommended)
- **Docker & Docker Compose** (for observability stack)
- **PostgreSQL 15** (local or managed)
- **Claude API key** (from Anthropic)
- **Notion API key** (optional, for dashboard integration)

### Installation

```bash
# 1. Clone repository
git clone https://github.com/yourusername/sentinel.git
cd sentinel

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your API keys and database credentials

# 5. Initialize database
python -m src.cli.cli init-db

# 6. Install pre-commit hooks (security scanning)
pre-commit install
```

### Running the System

#### 1. Start Core Sentinel Application (Backend)

```bash
source venv/bin/activate
uvicorn src.mcp_server.sentinel_server:app --reload --port 8000
```

#### 2. Start Command Center (GUI)

```bash
cd web
npm run dev
# Access at http://localhost:3000
```

#### 3. Start Observability Stack (SigNoz)

```bash
# Deploy SigNoz (ClickHouse, query service, frontend)
./scripts/start-signoz.sh

# Access SigNoz UI
open http://localhost:3301

# Stop SigNoz
./scripts/stop-signoz.sh
```

#### 3. Start Analytics Stack (Apache Superset)

```bash
# Deploy Superset (Redis, PostgreSQL metadata, Superset web/worker)
./scripts/start-superset.sh

# Access Superset UI
open http://localhost:8088

# Default credentials: admin / admin (change immediately!)

# Stop Superset
./scripts/stop-superset.sh
```

#### 4. Production Deployment (SSL/TLS)

```bash
# Set up Nginx reverse proxy with Let's Encrypt SSL
sudo ./scripts/setup-ssl.sh your-domain.com your-email@example.com

# Access production endpoints:
# https://your-domain.com/ops       → SigNoz
# https://your-domain.com/executive → Superset
# https://your-domain.com/api       → FastAPI
```

---

## 📂 Project Structure

```
sentinel/
├── src/
│   ├── agents/               # Agent implementations
│   │   ├── base_agent.py     # Abstract base agent class
│   │   ├── orchestrator.py   # Chief of Staff orchestrator
│   │   ├── security_aggregator.py # Security findings aggregator
│   │   └── research_agent.py # Research and analysis agent
│   │
│   ├── mcp_server/           # Model Context Protocol server
│   │   └── sentinel_server.py
│   │
│   ├── storage/              # Data persistence layer
│   │   ├── models.py         # SQLAlchemy ORM models
│   │   ├── postgres_client.py
│   │   └── notion_client.py
│   │
│   ├── schemas/              # Configuration schemas
│   │   └── project_schema.py
│   │
│   └── cli/                  # Command-line interface
│       └── cli.py
│
├── docs/
│   ├── adr/                  # Architecture Decision Records
│   │   ├── ADR-001-observability-stack-selection.md
│   │   ├── ADR-002-database-schema-design.md
│   │   ├── ADR-003-graduated-autonomy-model.md
│   │   ├── ADR-004-agent-communication-protocol.md
│   │   ├── ADR-005-python-technology-stack.md
│   │   └── ADR-006-security-architecture.md
│   │
│   └── sprint/               # Sprint planning and retrospectives
│       ├── CLAUDE_CODE_BRIEFING.md
│       ├── DAY_4_COMPLETION_REPORT.md
│       └── ADR-001-observability-stack-selection.md
│
├── scripts/                  # Operational scripts
│   ├── backup-db.sh          # PostgreSQL backup (with encryption)
│   ├── restore-db.sh         # Database restore
│   ├── setup-ssl.sh          # Let's Encrypt SSL automation
│   ├── start-signoz.sh       # SigNoz deployment
│   ├── stop-signoz.sh
│   ├── start-superset.sh     # Superset deployment
│   └── stop-superset.sh
│
├── nginx/
│   └── nginx.conf            # Reverse proxy configuration
│
├── superset/
│   ├── superset_config.py    # Superset configuration
│   └── dashboard_queries.sql # Pre-built SQL queries
│
├── config/                   # Agent configurations
│   ├── github-triage.json
│   └── research.json
│
├── docker-compose.signoz.yml    # SigNoz stack
├── docker-compose.analytics.yml # Superset stack
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── .gitignore
└── .pre-commit-config.yaml   # Security scanning hooks
```

---

## 🔒 Security

Sentinel implements defense-in-depth security architecture:

### Pre-Commit Security Scanning

```bash
# Automatically runs on every commit:
# ✓ Gitleaks   - Detect secrets in code
# ✓ Bandit     - Python security analysis
# ✓ Safety     - Dependency vulnerability scanning
```

### Secrets Management

- **Never commit secrets** - `.env` file for all credentials
- **Environment variables** - 12-factor app methodology
- **GPG encryption** - Optional backup encryption

### Network Security

- **TLS 1.2+** - Modern SSL/TLS only
- **Let's Encrypt** - Free automated certificates
- **Rate limiting** - API protection (10 req/s, 5 req/s admin)
- **Basic auth** - Dashboard access control
- **Firewall rules** - Ports 80/443 only

### Database Security

- **Least privilege** - Application user has minimal permissions
- **SSL connections** - Encrypted database connections
- **Audit logging** - Complete decision history

See [ADR-006: Security Architecture](docs/adr/ADR-006-security-architecture.md) for complete details.

---

## 📊 Dashboards

### SigNoz Operations Dashboard

**Purpose:** Real-time operational monitoring for technical teams

**Access:** `https://your-domain.com/ops` (basic auth required)

**Features:**
- Live agent health monitoring
- API latency and error rates
- Distributed traces for debugging
- Log aggregation and search
- Custom alerts and notifications

### Apache Superset Executive Dashboard

**Purpose:** Strategic business intelligence for decision-makers

**Access:** `https://your-domain.com/executive` (basic auth required)

**Pre-built Dashboards:**

1. **Job Search Executive View**
   - Application conversion funnel
   - Interview pipeline
   - Salary research progress
   - Time-to-offer tracking

2. **30-in-30 Challenge Tracker**
   - Daily project completion rate
   - Velocity trends
   - Bottleneck identification

3. **Multi-Business Portfolio**
   - Revenue across business lines
   - Active project counts
   - Resource allocation

4. **Sentinel System Health**
   - Agent productivity scores
   - Bottleneck resolution rates
   - Decision confidence trends

**SQL Queries:** See `superset/dashboard_queries.sql` for all queries

---

## 🛠️ Operations

### CI/CD Security Scanning

```bash
# Run local security scan and trigger Sentinel ingestion
./scripts/ci-security-scan.sh
```

### Database Backup & Restore

```bash
# Create backup (compressed)
./scripts/backup-db.sh

# Create encrypted backup
./scripts/backup-db.sh --encrypt

# Restore from backup
./scripts/restore-db.sh backups/postgres/sentinel_20251227_140530.sql.gz

# Force restore (skip confirmation)
./scripts/restore-db.sh backup.sql.gz --force
```

**Automated Backups (Cron):**
```bash
# Add to crontab (daily at 2 AM):
0 2 * * * cd /path/to/sentinel && ./scripts/backup-db.sh --encrypt
```

### SSL Certificate Management

```bash
# Initial setup
sudo ./scripts/setup-ssl.sh your-domain.com admin@example.com

# Auto-renewal (configured automatically)
# Certificates renew daily at 3:00 AM via cron

# Test renewal manually
sudo certbot renew --dry-run
```

### Monitoring and Logs

```bash
# View Sentinel application logs
docker logs sentinel-app

# View SigNoz logs
docker logs signoz-frontend
docker logs signoz-query-service

# View Superset logs
docker logs sentinel-superset
docker logs sentinel-superset-worker

# View Nginx access logs
sudo tail -f /var/log/nginx/sentinel_access.log

# View Nginx error logs
sudo tail -f /var/log/nginx/sentinel_error.log
```

---

## 🧪 Development

### Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Specific test file
pytest tests/test_agents.py -v
```

### Code Quality

```bash
# Format code (Black)
black src/ tests/

# Lint code (Ruff)
ruff check src/ tests/

# Type checking (mypy)
mypy src/

# Run all pre-commit hooks manually
pre-commit run --all-files
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

---

## 📖 Architecture Decision Records (ADRs)

Comprehensive documentation of all significant architectural decisions:

1. **[ADR-001: Observability Stack Selection](docs/adr/ADR-001-observability-stack-selection.md)**
   - Why SigNoz + Superset over Grafana
   - Rationale for dual-dashboard approach
   - OpenTelemetry integration strategy

2. **[ADR-002: Database Schema Design](docs/adr/ADR-002-database-schema-design.md)**
   - PostgreSQL schema structure
   - SQLAlchemy ORM justification
   - Audit trail requirements

3. **[ADR-003: Graduated Autonomy Model](docs/adr/ADR-003-graduated-autonomy-model.md)**
   - Three-tier autonomy framework
   - Safety guardrails and circuit breakers
   - Trust calibration mechanisms

4. **[ADR-004: Agent Communication Protocol](docs/adr/ADR-004-agent-communication-protocol.md)**
   - Current: Database state sharing
   - Future: Model Context Protocol (MCP)
   - Hybrid architecture approach

5. **[ADR-005: Python Technology Stack](docs/adr/ADR-005-python-technology-stack.md)**
   - Python 3.10+ justification
   - FastAPI, SQLAlchemy, Typer choices
   - Dependency management strategy

6. **[ADR-006: Security Architecture](docs/adr/ADR-006-security-architecture.md)**
   - Defense-in-depth layers
   - Secrets management approach
   - Compliance and audit requirements

---

## 🎓 Learning Resources

### For Interviewers

**This project demonstrates:**
- ✅ **Cloud Security Architecture** - SSL/TLS, secrets management, defense-in-depth
- ✅ **AI Systems Engineering** - Multi-agent orchestration, graduated autonomy, safety
- ✅ **Production DevOps** - Docker Compose, Nginx, monitoring, backup/restore
- ✅ **Database Design** - PostgreSQL schema, migrations, audit trails
- ✅ **API Development** - FastAPI, OpenAPI, async/await patterns
- ✅ **Observability** - OpenTelemetry, SigNoz, distributed tracing
- ✅ **Business Intelligence** - Superset dashboards, SQL analytics
- ✅ **Documentation** - ADRs, comprehensive README, code comments

**Interview Talking Points:**
1. Why hybrid SigNoz + Superset vs. monolithic Grafana
2. Security scanning automation via pre-commit hooks
3. Graduated autonomy model for safe AI decision-making
4. OpenTelemetry instrumentation for vendor-neutral observability
5. Database state sharing vs. MCP for agent communication

### For Contributors

1. Read [CLAUDE_CODE_BRIEFING.md](docs/sprint/CLAUDE_CODE_BRIEFING.md) for project context
2. Review all ADRs in `docs/adr/` to understand design decisions
3. Check [Sprint Documentation](docs/sprint/) for implementation history
4. Run `pre-commit install` to enable security scanning
5. Write tests for all new features (80% coverage minimum)

---

## 🚦 Deployment Checklist

Before production deployment:

**Security:**
- [ ] All secrets in `.env` (not in code)
- [ ] Pre-commit hooks installed and passing
- [ ] SSL/TLS certificates configured
- [ ] Firewall rules applied (ports 80/443 only)
- [ ] Basic auth configured for admin dashboards
- [ ] Database backups automated (cron job)
- [ ] Database user has minimum required permissions

**Monitoring:**
- [ ] SigNoz deployed and accessible
- [ ] Superset deployed with Sentinel database connection
- [ ] OpenTelemetry instrumentation enabled
- [ ] Alert rules configured (uptime, error rates)
- [ ] Log aggregation working

**Infrastructure:**
- [ ] PostgreSQL backups tested (backup + restore)
- [ ] Nginx reverse proxy configured
- [ ] Domain DNS pointed to server
- [ ] Let's Encrypt auto-renewal configured
- [ ] Resource limits set (Docker memory/CPU)

**Application:**
- [ ] All agents registered in database
- [ ] Configuration files validated
- [ ] API health check endpoint responding
- [ ] Notion integration tested (if using)

---

## 📜 License

MIT License - See [LICENSE](LICENSE) file for details.

This is a personal portfolio project demonstrating production-grade AI systems engineering.

---

## 🤖 Contributors & Agent History

Sentinel is a multi-agent system built by multi-agent collaboration.

| Agent | Era | Primary Contributions |
|-------|-----|-----------------------|
| **Claude** (Anthropic) | *Foundation Era* | System architecture, enterprise documentation (ADRs), graduated autonomy model, observability stack (SigNoz/Superset). |
| **Gemini** (Google) | *Execution Era* | Sentinel Command Center (Next.js), Security Integration (SARIF/Alerting), backend stabilization, CI/CD automation. |

> **Policy Enacted:** 2025-12-28 (v1.1.0)
> *All future commits and documentation updates must explicitly attribute significant architectural changes to the acting agent to maintain traceability.*

---

## 👤 Author

**Troy Shields**
- Cloud Security Architect
- AI Systems Builder
- Multi-Domain Portfolio Manager

**Contact:** Available for cloud security, AI engineering, and DevOps consulting opportunities.

---

## 🙏 Acknowledgments

- **Anthropic** - Claude API for agent intelligence
- **SigNoz Team** - OpenTelemetry-native observability platform
- **Apache Software Foundation** - Superset business intelligence platform
- **Let's Encrypt** - Free SSL/TLS certificates

---

**Last Updated:** 2025-12-28
**Version:** 1.1.0
**Status:** Production-Ready Foundation (Security Integration Complete)
