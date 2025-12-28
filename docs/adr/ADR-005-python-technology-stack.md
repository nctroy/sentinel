# ADR-005: Python Technology Stack

**Status:** Accepted
**Date:** 2025-12-27
**Decision Makers:** Troy Shields (Chief Architect)
**Tags:** python, technology-stack, dependencies, tooling

---

## Context

Sentinel requires a technology stack that supports:

1. **AI/ML Integration** - Seamless Claude API integration
2. **Async Operations** - Concurrent agent execution
3. **Database Access** - PostgreSQL ORM and migrations
4. **API Development** - RESTful API for future web UI
5. **CLI Tooling** - Command-line interface for operations
6. **Type Safety** - Catch errors at development time
7. **Developer Experience** - Fast iteration, good tooling

**Team Context:**
- Solo developer initially (Troy)
- Potential team growth
- Need rapid prototyping capability
- Production-ready code quality

## Decision

**Primary Language:** Python 3.10+

**Core Technology Stack:**

### Application Framework
- **FastAPI** - Modern async web framework
- **Pydantic** - Data validation and settings management
- **Typer** - CLI application framework

### Database & ORM
- **PostgreSQL** - Primary database
- **SQLAlchemy** - ORM and query builder
- **Alembic** - Database migrations
- **psycopg2** - PostgreSQL adapter

### AI/ML
- **anthropic** - Official Claude API client
- **OpenAI** (future) - GPT integration if needed

### Observability
- **OpenTelemetry** - Distributed tracing
- **Python logging** - Application logging
- **Prometheus client** (future) - Metrics

### Development Tools
- **pytest** - Testing framework
- **black** - Code formatting
- **ruff** - Fast Python linter
- **mypy** - Static type checking
- **pre-commit** - Git hooks

### Security
- **python-dotenv** - Environment variable management
- **bandit** - Security linting
- **safety** - Dependency vulnerability scanning

### Utilities
- **httpx** - Async HTTP client
- **python-dateutil** - Date/time utilities
- **click** - CLI helpers (via Typer)

## Rationale

### Why Python?

**Advantages:**
1. **AI/ML Ecosystem** - Best-in-class libraries (anthropic, openai, transformers)
2. **Rapid Development** - Fast prototyping, expressive syntax
3. **Async Support** - Native async/await since 3.5
4. **Strong Typing** - Type hints + mypy provide safety
5. **Rich Ecosystem** - Mature libraries for everything
6. **Developer Pool** - Easy to hire Python developers
7. **Data Science Integration** - Natural fit for analytics

**Alternatives Considered:**

**Go:**
- ✅ Better performance, simpler concurrency
- ❌ Weaker AI/ML ecosystem
- ❌ More verbose for rapid prototyping
- **Decision:** Performance not bottleneck; AI integration more important

**TypeScript/Node:**
- ✅ Good async, strong ecosystem
- ❌ Less mature AI/ML libraries
- ❌ Not ideal for data science workflows
- **Decision:** Python's AI ecosystem decisive

**Rust:**
- ✅ Maximum performance and safety
- ❌ Slower development velocity
- ❌ Smaller AI/ML ecosystem
- ❌ Steeper learning curve
- **Decision:** Premature optimization

### Why Python 3.10+?

**Required Features:**
- Structural pattern matching (match/case)
- Better type hints (PEP 604, 612, 613)
- Better error messages
- Performance improvements

**Compatibility:**
- Widely available (2021 release)
- Supported by all major platforms
- Long-term support (until 2026)

### Why FastAPI?

**Advantages:**
1. **Native Async** - First-class async/await support
2. **Type Safety** - Pydantic validation built-in
3. **Auto Documentation** - OpenAPI/Swagger automatic
4. **Performance** - Comparable to Go/Node (Starlette + Uvicorn)
5. **Modern** - Best practices by default
6. **Developer Experience** - Excellent docs, intuitive API

**Alternatives Considered:**

**Django:**
- ✅ Batteries included, mature
- ❌ Sync-first (async support limited)
- ❌ Heavyweight for API-only service
- **Decision:** Overkill for Sentinel's needs

**Flask:**
- ✅ Lightweight, flexible
- ❌ No native async
- ❌ Manual validation/serialization
- **Decision:** FastAPI more modern

### Why SQLAlchemy?

**Advantages:**
1. **Mature** - 15+ years, battle-tested
2. **Flexible** - ORM + Core (raw SQL)
3. **Type Support** - Works with mypy
4. **Async Support** - asyncio support in 1.4+
5. **Migration Tools** - Alembic integration

**Alternatives Considered:**

**Prisma Python:**
- ✅ Modern, great DX
- ❌ Less mature in Python ecosystem
- **Decision:** SQLAlchemy more proven

**Tortoise ORM:**
- ✅ Async-first design
- ❌ Smaller community, less mature
- **Decision:** Risk vs. reward not favorable

### Why Typer?

**Advantages:**
1. **Type Hints** - Automatic CLI from type hints
2. **Modern** - Built on Click, more Pythonic
3. **Auto Help** - Help text from docstrings
4. **Testing** - Easy to test CLIs

**Alternative:** Click (lower-level, more manual)

### Dependency Management

**Tool:** pip + requirements.txt

**Why Not Poetry/PDM?**
- Requirements.txt simpler for single-developer project
- Docker compatibility straightforward
- Can migrate to Poetry later if needed

**Current Structure:**
```
requirements.txt          # Production dependencies
requirements-dev.txt      # Development dependencies
```

## Technology Stack Details

### Production Dependencies

```txt
# requirements.txt
fastapi==0.109.0          # Web framework
uvicorn[standard]==0.27.0 # ASGI server
pydantic==2.5.3           # Data validation
pydantic-settings==2.1.0  # Settings management

sqlalchemy==2.0.25        # ORM
alembic==1.13.1           # Migrations
psycopg2-binary==2.9.9    # PostgreSQL driver

anthropic==0.75.0         # Claude API
httpx==0.28.1             # Async HTTP

opentelemetry-api==1.22.0              # Tracing API
opentelemetry-sdk==1.22.0              # Tracing SDK
opentelemetry-exporter-otlp==1.22.0    # OTLP exporter
opentelemetry-instrumentation-fastapi==0.43b0  # FastAPI instrumentation

typer==0.9.0              # CLI framework
python-dotenv==1.0.0      # Environment variables
python-dateutil==2.8.2    # Date utilities
```

### Development Dependencies

```txt
# requirements-dev.txt
pytest==7.4.3             # Testing
pytest-asyncio==0.21.1    # Async test support
pytest-cov==4.1.0         # Coverage

black==23.12.1            # Code formatting
ruff==0.1.9               # Linting
mypy==1.8.0               # Type checking
pre-commit==3.6.0         # Git hooks

bandit==1.7.6             # Security linting
safety==2.3.5             # Dependency scanning
```

## Code Style and Standards

### Formatting
- **Tool:** Black (line length: 100)
- **Config:** `pyproject.toml`

### Linting
- **Tool:** Ruff (faster than flake8+pylint)
- **Rules:** Select = ["E", "F", "I", "N", "W"]

### Type Checking
- **Tool:** mypy
- **Strictness:** `--strict` mode
- **Coverage:** 100% type coverage goal

### Testing
- **Framework:** pytest
- **Coverage:** 80% minimum
- **Async:** pytest-asyncio for async tests

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
```

## Consequences

### Positive

✅ **Rapid Development** - Python's expressiveness enables fast iteration
✅ **Type Safety** - mypy + Pydantic catch errors early
✅ **AI Integration** - First-class Claude API support
✅ **Async Performance** - FastAPI comparable to Node/Go
✅ **Ecosystem** - Rich library availability
✅ **Hiring** - Large Python developer pool

### Negative

⚠️ **Performance Ceiling** - Python slower than compiled languages
⚠️ **Deployment Size** - Larger than Go/Rust binaries
⚠️ **GIL Limitations** - Multi-threading limited (async mitigates)
⚠️ **Dependency Management** - pip less sophisticated than Cargo/npm

### Mitigations

**Performance:**
- Async I/O for concurrency
- PostgreSQL handles data processing
- Can rewrite hot paths in Rust (via PyO3) if needed

**Dependencies:**
- Pin exact versions for reproducibility
- Regular `safety` scans for vulnerabilities
- Can migrate to Poetry if complexity grows

## Future Considerations

### Potential Additions

**When to Add:**

1. **Celery** - If need distributed task queue
2. **Redis** - If need caching beyond Superset
3. **NumPy/Pandas** - If complex data analysis in-process
4. **Polars** - If DataFrame operations needed (faster than Pandas)
5. **Streamlit** - If need quick internal dashboards

**When to Replace:**

1. **Rust for Performance** - Only if Python proven bottleneck
2. **Poetry** - If dependency management becomes complex
3. **Alternative ORM** - Only if SQLAlchemy insufficient

### Version Upgrade Strategy

**Python Version:**
- Upgrade to latest Python annually
- Test compatibility in CI/CD
- Target: Python 3.11 (Q2 2026) for performance gains

**Dependencies:**
- Update quarterly for security patches
- Review breaking changes carefully
- Test in staging before production

## Development Workflow

### Local Setup
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Type check
mypy src/

# Lint
ruff check src/
```

### CI/CD Pipeline
```yaml
# GitHub Actions
- name: Test
  run: |
    pytest --cov=src --cov-report=xml

- name: Type Check
  run: mypy src/

- name: Lint
  run: ruff check src/

- name: Security Scan
  run: |
    bandit -r src/
    safety check
```

## References

- FastAPI: https://fastapi.tiangolo.com/
- SQLAlchemy: https://www.sqlalchemy.org/
- Pydantic: https://docs.pydantic.dev/
- Typer: https://typer.tiangolo.com/
- Python Typing: https://docs.python.org/3/library/typing.html

---

**Supersedes:** None
**Superseded By:** None
**Related:** ADR-002 (Database Schema), ADR-006 (Security Architecture)
