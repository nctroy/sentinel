# ADR-002: Database Schema Design

**Status:** Accepted
**Date:** 2025-12-27
**Decision Makers:** Troy Shields (Chief Architect)
**Tags:** database, postgresql, schema, architecture

---

## Context

Sentinel requires a robust database schema to store agent configurations, execution history, identified bottlenecks, decisions, and system metrics. The schema must support:

1. **Multi-agent tracking** - Multiple agents with different types and domains
2. **Bottleneck management** - Storing, prioritizing, and resolving bottlenecks
3. **Decision audit trail** - Complete history of agent decisions
4. **Performance analytics** - Metrics for business intelligence dashboards
5. **Scalability** - Support for growing number of agents and data volume

## Decision

We will use **PostgreSQL** with a relational schema consisting of five core tables:

1. **`agents`** - Agent registry and configuration
2. **`bottlenecks`** - Identified bottlenecks with metadata
3. **`decisions`** - Agent decision audit log
4. **`weekly_plans`** - Orchestrator weekly plan generation
5. **`notion_sync`** - Notion integration tracking

**ORM Choice:** SQLAlchemy for Python compatibility and type safety

### Schema Design

```sql
-- Agent Registry
CREATE TABLE agents (
    agent_id VARCHAR(255) PRIMARY KEY,
    agent_type VARCHAR(50) NOT NULL,  -- 'research', 'github', 'orchestrator'
    domain VARCHAR(255),
    config JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_run TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active'
);

-- Bottleneck Tracking
CREATE TABLE bottlenecks (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(255) REFERENCES agents(agent_id),
    description TEXT NOT NULL,
    impact_score REAL CHECK (impact_score BETWEEN 0 AND 10),
    confidence REAL CHECK (confidence BETWEEN 0 AND 1),
    blocking JSONB DEFAULT '[]',
    recommended_action TEXT,
    reasoning TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    identified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    notion_page_id VARCHAR(255)
);

-- Decision Audit Log
CREATE TABLE decisions (
    id SERIAL PRIMARY KEY,
    agent_id VARCHAR(255) REFERENCES agents(agent_id),
    decision_type VARCHAR(100) NOT NULL,
    decision_data JSONB NOT NULL,
    reasoning TEXT,
    confidence REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Weekly Plans
CREATE TABLE weekly_plans (
    id SERIAL PRIMARY KEY,
    week_start DATE NOT NULL,
    week_end DATE NOT NULL,
    priorities JSONB NOT NULL,
    conflicts JSONB DEFAULT '[]',
    synthesis_reasoning TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notion Sync Tracking
CREATE TABLE notion_sync (
    id SERIAL PRIMARY KEY,
    bottleneck_id INTEGER REFERENCES bottlenecks(id),
    notion_page_id VARCHAR(255) NOT NULL,
    synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sync_status VARCHAR(50)
);

-- Indexes for performance
CREATE INDEX idx_bottlenecks_agent_id ON bottlenecks(agent_id);
CREATE INDEX idx_bottlenecks_status ON bottlenecks(status);
CREATE INDEX idx_bottlenecks_impact ON bottlenecks(impact_score DESC);
CREATE INDEX idx_bottlenecks_identified_at ON bottlenecks(identified_at DESC);
CREATE INDEX idx_decisions_agent_id ON decisions(agent_id);
CREATE INDEX idx_decisions_timestamp ON decisions(timestamp DESC);
CREATE INDEX idx_agents_type ON agents(agent_type);
```

## Rationale

### Why PostgreSQL over NoSQL?

**PostgreSQL Advantages:**
1. **ACID Compliance** - Critical for audit trail integrity
2. **Complex Queries** - SQL Lab in Superset requires SQL database
3. **JSONB Support** - Flexibility of document storage where needed
4. **Mature Ecosystem** - Strong Python support via psycopg2/SQLAlchemy
5. **Analytics Performance** - Excellent for aggregation queries in dashboards

**NoSQL Considered But Rejected:**
- MongoDB: Lacks strong consistency guarantees for audit logs
- Redis: In-memory limitations for historical data
- DynamoDB: Query limitations, cost concerns

### Why SQLAlchemy ORM?

**Advantages:**
1. **Type Safety** - Pydantic models integrate seamlessly
2. **Migration Management** - Alembic for schema versioning
3. **Python Native** - Idiomatic Python code
4. **Query Builder** - Complex queries without raw SQL
5. **Connection Pooling** - Built-in performance optimization

**Alternatives Considered:**
- Raw SQL: More verbose, error-prone, harder to maintain
- Django ORM: Too heavyweight for FastAPI project
- Peewee: Less mature, smaller ecosystem

### Schema Design Principles

**1. Normalization**
- Agents table as single source of truth
- Foreign keys ensure referential integrity
- Avoids data duplication

**2. JSONB for Flexibility**
- `config` field allows agent-specific settings
- `blocking` array stores dynamic dependencies
- `decision_data` captures varied decision structures

**3. Audit Trail**
- `identified_at` and `resolved_at` for time tracking
- `decisions` table never deletes records
- `reasoning` fields capture AI decision context

**4. Performance Optimization**
- Indexes on frequently queried columns
- Timestamp indexes for time-series queries
- Compound indexes for dashboard queries

**5. Status Management**
- Enum-like VARCHAR fields with CHECK constraints
- Statuses: 'pending', 'in_progress', 'resolved', 'ignored'
- Enables workflow management

## Consequences

### Positive

✅ **Strong Data Integrity** - ACID transactions prevent data corruption
✅ **Rich Query Capabilities** - SQL enables complex analytics
✅ **Industry Standard** - Well-documented, widely supported
✅ **Scalability** - PostgreSQL handles millions of rows efficiently
✅ **Backup/Restore** - Mature tooling (pg_dump, WAL archiving)
✅ **Cost Effective** - Free, open-source, runs anywhere

### Negative

⚠️ **Vertical Scaling** - Eventually requires larger machines
⚠️ **Schema Migrations** - Changes require careful planning
⚠️ **Learning Curve** - Team must understand SQL and ORMs

### Neutral

ℹ️ **JSONB Trade-off** - Flexibility vs. schema enforcement balance
ℹ️ **Index Maintenance** - Requires monitoring and optimization
ℹ️ **Backup Strategy** - Need automated backup procedures

## Implementation Notes

### Connection Management
```python
# src/storage/postgres_client.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

### Model Example
```python
# src/storage/models.py
class Bottleneck(Base):
    __tablename__ = "bottlenecks"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String, ForeignKey("agents.agent_id"))
    description = Column(Text, nullable=False)
    impact_score = Column(Float)
    confidence = Column(Float)
    status = Column(String, default="pending")
```

### Migration Strategy
```bash
# Using Alembic for schema versioning
alembic revision --autogenerate -m "Add bottleneck_priority column"
alembic upgrade head
```

## Compliance and Security

**Data Protection:**
- No PII stored without encryption
- Sensitive config values stored in environment variables
- Database credentials never committed to git

**Audit Requirements:**
- All decision records timestamped
- No deletion of historical data
- Reasoning fields maintain AI transparency

## Future Considerations

**Potential Enhancements:**
1. **Partitioning** - Table partitioning by date for very large datasets
2. **Read Replicas** - Separate read replica for analytics queries
3. **TimescaleDB Extension** - Time-series optimization if needed
4. **Full-Text Search** - PostgreSQL FTS for bottleneck descriptions
5. **GraphQL** - Consider Hasura/Postgraphile for API layer

**Migration Path:**
- Current schema supports 1M+ bottlenecks
- If scaling beyond, consider time-series database for metrics
- Main transactional data stays in PostgreSQL

## References

- PostgreSQL Documentation: https://www.postgresql.org/docs/
- SQLAlchemy ORM: https://docs.sqlalchemy.org/
- Alembic Migrations: https://alembic.sqlalchemy.org/
- JSONB Performance: https://www.postgresql.org/docs/current/datatype-json.html

---

**Supersedes:** None (first database ADR)
**Superseded By:** None
**Related:** ADR-005 (Python Technology Stack), ADR-006 (Security Architecture)
