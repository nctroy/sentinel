# ADR-001: Observability and Analytics Stack Selection

**Status:** Accepted
**Date:** 2025-12-27
**Decision Makers:** Troy Shields (Chief Architect)
**Stakeholders:** Sentinel System, Job Search Portfolio, AI Literacy Business, Photography Business, 30-in-30 Challenge Projects

---

## Context

Sentinel requires production-grade observability and analytics to monitor:
1. **Operational Metrics**: Agent health, bottleneck detection rates, API latency, error rates, orchestration cycles
2. **Business Metrics**: Job search conversion funnel, AI business ROI, photography project status, 30-in-30 progress tracking
3. **Multi-Tenant View**: Unified single pane of glass across multiple business domains (job search, AI literacy, photography, 30n30 projects)

The system must serve two distinct audiences:
- **Technical/Operations**: Real-time monitoring, debugging, troubleshooting (developer/SRE perspective)
- **Executive/Business**: Strategic KPIs, portfolio health, business outcome tracking (business leader perspective)

Additionally, this deployment serves as a **portfolio demonstration piece** for cloud security and AI engineering roles, requiring:
- Production-quality architecture
- Industry-standard tooling and practices
- Clear decision rationale (documented via ADRs)
- Deployment patterns interviewers recognize and respect

---

## Decision

**Selected Architecture: Hybrid SigNoz + Apache Superset**

### Primary Stack Components:
1. **SigNoz** (OpenTelemetry-native observability platform)
   - Operational monitoring and observability
   - Logs, metrics, and distributed traces in unified platform
   - Real-time agent health dashboards

2. **Apache Superset** (Modern BI and data exploration platform)
   - Business intelligence and executive dashboards
   - SQL-based analytics connecting directly to PostgreSQL
   - Cross-domain business metrics and portfolio overview

3. **PostgreSQL** (Existing state store)
   - Single source of truth for all Sentinel state
   - Agents, bottlenecks, actions, orchestrator plans, decision logs
   - Both SigNoz and Superset query this database

4. **OpenTelemetry** (Instrumentation standard)
   - Industry-standard telemetry collection
   - Future-proof observability strategy
   - Vendor-neutral implementation

### Deployment Pattern:
```
┌─────────────────────────────────────────────────────────┐
│           SENTINEL PRODUCTION DEPLOYMENT                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐        ┌─────────────────┐          │
│  │   SigNoz     │◄───────┤  OpenTelemetry  │          │
│  │ Observability│        │  Instrumentation│          │
│  │  Platform    │        └─────────────────┘          │
│  │              │                                      │
│  │ - Logs       │        ┌─────────────────┐          │
│  │ - Metrics    │        │  ClickHouse     │          │
│  │ - Traces     │◄───────┤  (Time-series)  │          │
│  └──────────────┘        └─────────────────┘          │
│         │                                              │
│         │                                              │
│  ┌──────▼───────┐        ┌─────────────────┐          │
│  │   Superset   │◄───────┤   PostgreSQL    │          │
│  │   Business   │        │   State Store   │          │
│  │  Intelligence│        │                 │          │
│  │              │        │ - Agents        │          │
│  │ - Exec View  │        │ - Bottlenecks   │          │
│  │ - Portfolio  │        │ - Decisions     │          │
│  │ - Analytics  │        │ - Plans         │          │
│  └──────────────┘        └─────────────────┘          │
│         │                        │                     │
│         │                        │                     │
│  ┌──────▼────────────────────────▼──────┐             │
│  │        Nginx Reverse Proxy            │             │
│  │      your-domain.com (TBD)            │             │
│  │                                       │             │
│  │  /ops       → SigNoz (port 3301)     │             │
│  │  /executive → Superset (port 8088)   │             │
│  │  /api       → FastAPI (port 8000)    │             │
│  └───────────────────────────────────────┘             │
└─────────────────────────────────────────────────────────┘
```

---

## Alternatives Considered

### Alternative 1: Grafana + Prometheus + Loki Stack (Classic LGTM)

**Components:**
- Grafana: Dashboarding and visualization
- Prometheus: Metrics collection and time-series database
- Loki: Log aggregation (Grafana's log solution)
- Optional: Tempo for distributed tracing

**Pros:**
- ✅ Industry standard - most recognized stack in DevOps/SRE space
- ✅ Massive ecosystem and community support
- ✅ Extensive plugin library (60+ data sources)
- ✅ Mature, battle-tested in production at scale
- ✅ Strong interview recognition (interviewers know this stack)
- ✅ Excellent documentation and tutorials
- ✅ PrometheusQueryLanguage (PromQL) is industry standard

**Cons:**
- ❌ **Three separate tools to integrate and manage** (Grafana + Prometheus + Loki)
- ❌ Operational complexity - each component needs configuration, monitoring, backup
- ❌ Loki requires separate deployment and storage management
- ❌ Tempo (tracing) is additional component if full observability needed
- ❌ No native business intelligence capabilities (limited to time-series and logs)
- ❌ Grafana dashboards optimized for operational metrics, not executive/business views
- ❌ License changed to AGPLv3 (less permissive, embedding concerns)
- ❌ Higher resource footprint (3-4 services vs. unified platform)

**Why Not Selected:**
While the Grafana stack is excellent for pure infrastructure/application monitoring, Sentinel requires **dual audiences** (technical + executive). Running Grafana for ops monitoring AND a separate BI tool (Metabase/Superset) for business analytics would result in:
1. Four total services instead of two
2. Duplicated configuration and maintenance burden
3. Two separate visualization paradigms to maintain
4. Potential confusion around "which dashboard for which question"

Additionally, the operational complexity of managing LGTM stack components individually doesn't align with the goal of showcasing **intelligent architectural choices** that balance capability with operational efficiency.

---

### Alternative 2: Commercial SaaS Solutions (Datadog, New Relic, Dynatrace)

**Representative Example: Datadog**

**Pros:**
- ✅ Fully managed - zero operational overhead
- ✅ Comprehensive all-in-one solution (APM, logs, metrics, traces, RUM, security)
- ✅ Enterprise-grade reliability and support
- ✅ Advanced ML-based anomaly detection
- ✅ Interview recognition in enterprise contexts

**Cons:**
- ❌ **Cost:** $15-100+ per host/month (prohibitive for portfolio project)
- ❌ Vendor lock-in and proprietary instrumentation
- ❌ Doesn't demonstrate infrastructure/deployment skills
- ❌ Less impressive in interviews ("you just used a SaaS tool" vs. "you architected and deployed")
- ❌ Can't showcase Docker, Kubernetes, infrastructure-as-code skills
- ❌ Limited customization compared to self-hosted solutions

**Why Not Selected:**
Commercial solutions don't achieve the portfolio objectives:
1. Cost exceeds reasonable budget for demonstration system
2. Loses opportunity to showcase deployment and operations expertise
3. Interviewers value "built and deployed" over "configured SaaS"
4. Can't demonstrate security hardening, backup strategies, scaling decisions

---

### Alternative 3: SigNoz Alone (Single Unified Platform)

**Pros:**
- ✅ Simplest deployment (single platform)
- ✅ All-in-one: logs, metrics, traces in one UI
- ✅ Lower resource requirements than Grafana stack
- ✅ OpenTelemetry-native (future-proof)
- ✅ Good operational dashboards

**Cons:**
- ❌ **Limited business intelligence capabilities**
- ❌ Dashboards optimized for time-series operational data, not business KPIs
- ❌ No SQL-based ad-hoc querying for business analysis
- ❌ Can't easily create cross-domain portfolio views
- ❌ Missing executive-friendly visualization options (Gantt charts, funnel analysis, cohort analysis)

**Why Not Selected:**
While operationally simpler, SigNoz alone cannot effectively serve the **executive/business analytics** use case. The 30-in-30 challenge, job search pipeline tracking, and multi-business portfolio management require BI capabilities that SigNoz isn't optimized for.

---

### Alternative 4: Apache Superset Alone (BI-Only Approach)

**Pros:**
- ✅ Excellent business intelligence and analytics
- ✅ Beautiful executive dashboards
- ✅ SQL-based - direct PostgreSQL integration
- ✅ Rich visualization library (50+ chart types)

**Cons:**
- ❌ **No real-time operational monitoring**
- ❌ Not designed for logs, traces, or distributed system debugging
- ❌ Lacks alerting for operational incidents
- ❌ Can't troubleshoot agent failures or API errors effectively
- ❌ No OpenTelemetry support

**Why Not Selected:**
Superset alone addresses business metrics but fails on operational observability. When an agent fails at 3 AM, you need real-time logs and traces, not a SQL-based BI dashboard refreshing every 5 minutes.

---

## Decision Rationale

### Why SigNoz + Superset Wins:

#### 1. **Separation of Concerns - Right Tool for Right Job**
- **SigNoz** → "Is the system healthy?" (Operational monitoring)
- **Superset** → "Is the business healthy?" (Strategic analytics)

Each tool optimized for its audience without compromising on either.

#### 2. **Single Shared Data Store (PostgreSQL)**
Both tools query the same PostgreSQL database:
- No data synchronization issues
- Single source of truth
- Simplified backup and disaster recovery
- Reduced infrastructure complexity vs. separate data stores

#### 3. **Lower Operational Complexity Than LGTM Stack**
```
Grafana Stack:        Hybrid Approach:
- Grafana             - SigNoz (all-in-one)
- Prometheus          - Superset (SQL-based)
- Loki                - PostgreSQL (already exists)
- (Tempo for traces)
= 3-4 services        = 2 services
```

#### 4. **Future-Proof with OpenTelemetry**
- Industry standard for observability instrumentation
- Vendor-neutral (can swap SigNoz for other OTel platforms if needed)
- Skills directly transferable to enterprise environments
- Shows knowledge of modern observability practices

#### 5. **Demonstrates Multi-Audience Architecture**
In interviews, can explain:
*"I architected separate observability layers for different stakeholders. SREs use SigNoz for real-time debugging. Executives use Superset for business KPIs. Both query the same PostgreSQL state store, ensuring consistency while optimizing UX for each audience."*

This demonstrates:
- Systems thinking
- Stakeholder management
- Appropriate technology selection
- Enterprise architecture patterns

#### 6. **Cost-Effective Production Deployment**
- Both tools are 100% open source (Apache 2.0 license)
- Self-hostable on modest infrastructure (~$40-60/month)
- No per-user licensing or data ingestion fees
- Scales as portfolio grows without exponential cost increases

#### 7. **Portfolio Differentiation**
Most candidates show:
- "I used Grafana" (common, expected)
- "I used Datadog" (just configured SaaS)

This approach shows:
- "I architected a hybrid observability strategy based on audience needs, evaluated multiple alternatives, documented the decision in an ADR, and deployed production infrastructure with proper security hardening"

**Far more impressive.**

---

## Consequences

### Positive:

1. **Dual-audience optimization**: Technical teams get real-time operational insights, executives get strategic business analytics
2. **Simplified operations**: 2 platforms instead of 3-4 (vs. Grafana stack)
3. **Cost efficiency**: Open-source stack deployable on single mid-tier VM or small K8s cluster
4. **Future flexibility**: OpenTelemetry instrumentation allows swapping SigNoz if needed
5. **Interview strength**: Demonstrates thoughtful architecture vs. "default to Grafana"
6. **Skill showcase**: Docker Compose, infrastructure-as-code, security hardening, reverse proxy configuration
7. **Unified data model**: Single PostgreSQL schema serves both operational and business analytics

### Negative:

1. **Less recognizable than Grafana**: Some interviewers may not know SigNoz (mitigated by explaining decision rationale)
2. **Two platforms to learn**: Team members need familiarity with both SigNoz and Superset UIs
3. **Smaller community than Grafana**: Fewer Stack Overflow answers, community plugins
4. **Responsibility for updates**: Self-hosted means manual security patching (vs. SaaS auto-updates)

### Mitigation Strategies:

1. **Documentation**: Comprehensive README explaining architecture and access patterns
2. **ADRs for future decisions**: Establish pattern of documenting architectural choices
3. **Automation**: Infrastructure-as-code (Terraform/Ansible) and CI/CD for updates
4. **Monitoring the monitors**: Uptime checks for SigNoz and Superset themselves
5. **Backup strategy**: Automated PostgreSQL backups, infrastructure config in Git

---

## Validation Criteria

This decision will be considered successful if:

1. ✅ **Operational visibility**: Can diagnose agent failures, API latency, bottleneck detection issues within 5 minutes
2. ✅ **Business insights**: Executive dashboards answer "How is my job search going?" and "Which 30n30 projects are on track?" at a glance
3. ✅ **Interview effectiveness**: Can demo system in 10-minute interview presentation and answer deep technical questions
4. ✅ **Cost sustainability**: Total hosting costs remain under $75/month for full portfolio (job search + 3 businesses)
5. ✅ **Deployment reliability**: System maintains >99% uptime over 30-day challenge period
6. ✅ **Skills demonstration**: Portfolio piece effectively showcases cloud security architecture, DevOps practices, and AI system operations

---

## Implementation Notes

### Deployment Timeline (Dec 27-31, 2025):

**Day 1-2: Infrastructure & Integration**
- Add OpenTelemetry instrumentation to Sentinel agents
- Configure PostgreSQL for external access (both SigNoz and Superset)
- Set up Docker Compose orchestration

**Day 3: SigNoz Deployment**
- Deploy SigNoz via Docker Compose
- Configure ClickHouse backend for time-series data
- Create operational dashboards (agent health, bottleneck detection, API metrics)
- Set up alerting rules

**Day 4: Superset Deployment**
- Deploy Apache Superset via Docker Compose
- Connect to PostgreSQL database
- Create executive dashboards (job search funnel, business portfolio, 30n30 tracker)
- Configure role-based access control

**Day 5: Production Hardening**
- Nginx reverse proxy with SSL/TLS (Let's Encrypt)
- Authentication configuration (OAuth or basic auth)
- Firewall rules and security hardening
- Backup automation for PostgreSQL
- Monitoring for the monitors (uptime checks)

### Key Configuration Files:
- `docker-compose.yml`: Full stack orchestration
- `nginx.conf`: Reverse proxy routing
- `otel-config.yaml`: OpenTelemetry collector configuration
- `postgres-backup.sh`: Automated backup script
- Infrastructure-as-code: Terraform or Ansible playbooks

---

## References

- [SigNoz Documentation](https://signoz.io/docs/)
- [Apache Superset Documentation](https://superset.apache.org/docs/intro)
- [OpenTelemetry Best Practices](https://opentelemetry.io/docs/)
- [Grafana vs. Modern Alternatives Comparison](https://signoz.io/blog/grafana-alternatives/)
- [ADR Template](https://github.com/joelparkerhenderson/architecture-decision-record)

---

## Revision History

| Date | Version | Author | Changes |
|------|---------|--------|---------|
| 2025-12-27 | 1.0 | Troy Shields | Initial decision record |

---

## Notes

This ADR establishes the foundation for Sentinel's observability strategy and serves as a template for future architectural decisions. All significant technical choices should be documented with similar rigor:

- **ADR-002**: Database schema versioning strategy
- **ADR-003**: Agent communication protocol (MCP vs. direct API)
- **ADR-004**: Graduated autonomy implementation approach
- **ADR-005**: Multi-tenancy model for business domains

Maintaining this documentation demonstrates enterprise-grade engineering practices and provides clear rationale for technical interviews.
