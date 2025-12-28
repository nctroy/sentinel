# Testing Strategy and Procedures

**Document Owner:** Troy Shields
**Last Updated:** 2025-12-27
**Status:** Active
**Applies To:** Sentinel v1.0.0+

---

## Table of Contents

1. [Overview](#overview)
2. [Testing Philosophy](#testing-philosophy)
3. [Test Levels](#test-levels)
4. [Test Environments](#test-environments)
5. [Test Automation](#test-automation)
6. [Manual Testing Procedures](#manual-testing-procedures)
7. [Quality Gates](#quality-gates)
8. [Continuous Integration](#continuous-integration)
9. [Bug Reporting](#bug-reporting)
10. [Test Metrics](#test-metrics)

---

## Overview

This document defines the testing strategy for Sentinel, a production-grade multi-agent AI orchestration platform. Our testing approach follows industry best practices to ensure reliability, security, and performance.

### Goals

- **Prevent Production Defects:** Catch issues before deployment
- **Enable Confident Refactoring:** Comprehensive test coverage allows safe code changes
- **Document System Behavior:** Tests serve as executable documentation
- **Maintain Quality:** Enforce quality gates throughout the development lifecycle

### Scope

This testing strategy covers:
- Unit testing (Python code)
- Integration testing (database, API, external services)
- System testing (Docker stacks, end-to-end workflows)
- Security testing (vulnerability scanning, secret detection)
- Performance testing (load testing, stress testing)
- Deployment testing (local, staging, production validation)

---

## Testing Philosophy

### Principles

1. **Test Early, Test Often**
   - Write tests alongside code (TDD encouraged)
   - Run tests locally before committing
   - Automated tests run on every commit (CI/CD)

2. **Comprehensive Coverage**
   - Minimum 80% code coverage
   - Critical paths have 100% coverage
   - Edge cases explicitly tested

3. **Fast Feedback**
   - Unit tests complete in < 5 seconds
   - Integration tests complete in < 30 seconds
   - Full test suite completes in < 5 minutes

4. **Realistic Testing**
   - Use production-like data (anonymized)
   - Test with real external dependencies where possible
   - Mock only when necessary (cost, latency, availability)

5. **Security First**
   - Pre-commit hooks scan for secrets and vulnerabilities
   - Dependency scanning on every build
   - Security tests in CI/CD pipeline

---

## Test Levels

### 1. Unit Tests

**Purpose:** Validate individual functions/classes in isolation

**Scope:**
- Agent logic (bottleneck detection, decision making)
- Database models (ORM operations)
- Utility functions (data parsing, formatting)
- Configuration validation

**Tools:**
- `pytest` - Test framework
- `pytest-cov` - Coverage reporting
- `pytest-mock` - Mocking framework

**Location:** `tests/unit/`

**Example:**
```python
# tests/unit/test_base_agent.py
import pytest
from src.agents.base_agent import BaseAgent

def test_agent_initialization():
    """Test agent initializes with correct configuration."""
    agent = BaseAgent(agent_id="test-001", config={"domain": "testing"})
    assert agent.agent_id == "test-001"
    assert agent.config["domain"] == "testing"

def test_bottleneck_validation():
    """Test bottleneck validation rejects invalid data."""
    agent = BaseAgent(agent_id="test-001")

    # Invalid impact score (> 10)
    with pytest.raises(ValueError):
        agent.validate_bottleneck({"impact_score": 15})

    # Valid bottleneck
    result = agent.validate_bottleneck({"impact_score": 8.5})
    assert result is True
```

**Running:**
```bash
# All unit tests
pytest tests/unit/ -v

# With coverage
pytest tests/unit/ --cov=src --cov-report=html

# Specific test file
pytest tests/unit/test_base_agent.py -v
```

**Coverage Target:** 85%

---

### 2. Integration Tests

**Purpose:** Validate components working together

**Scope:**
- Database operations (CRUD, transactions)
- API endpoints (FastAPI routes)
- External API integrations (Claude, Notion, GitHub)
- Agent orchestration workflows

**Tools:**
- `pytest` - Test framework
- `pytest-asyncio` - Async test support
- `httpx` - Async HTTP client for API testing
- `testcontainers` - Docker-based test dependencies

**Location:** `tests/integration/`

**Example:**
```python
# tests/integration/test_database.py
import pytest
from src.storage.postgres_client import PostgresClient
from src.storage.models import Bottleneck

@pytest.mark.asyncio
async def test_bottleneck_crud():
    """Test complete CRUD cycle for bottlenecks."""
    db = PostgresClient()

    # Create
    bottleneck = await db.save_bottleneck(
        agent_id="test-agent",
        description="Test bottleneck",
        impact_score=7.5,
        confidence=0.9
    )
    assert bottleneck.id is not None

    # Read
    retrieved = await db.get_bottleneck(bottleneck.id)
    assert retrieved.description == "Test bottleneck"

    # Update
    await db.update_bottleneck(bottleneck.id, status="resolved")
    updated = await db.get_bottleneck(bottleneck.id)
    assert updated.status == "resolved"

    # Delete
    await db.delete_bottleneck(bottleneck.id)
    deleted = await db.get_bottleneck(bottleneck.id)
    assert deleted is None
```

**Running:**
```bash
# All integration tests
pytest tests/integration/ -v

# Skip slow tests
pytest tests/integration/ -m "not slow"

# Run only database tests
pytest tests/integration/test_database.py -v
```

**Coverage Target:** 75%

---

### 3. System Tests (End-to-End)

**Purpose:** Validate complete system workflows

**Scope:**
- Full agent execution cycles
- Multi-agent orchestration
- Dashboard data flow (SigNoz, Superset)
- Backup/restore procedures
- Deployment workflows

**Tools:**
- `pytest` - Test framework
- `docker-compose` - Stack orchestration
- `selenium` (future) - UI testing

**Location:** `tests/system/`

**Example:**
```python
# tests/system/test_agent_workflow.py
import pytest
from src.cli.cli import run_agent

@pytest.mark.system
@pytest.mark.slow
async def test_full_agent_cycle():
    """Test complete agent diagnostic cycle."""

    # Run research agent
    result = await run_agent("research", mode="diagnostic")

    # Validate bottleneck identified
    assert result["status"] == "success"
    assert "bottleneck" in result
    assert result["bottleneck"]["impact_score"] > 0

    # Validate database persistence
    db = PostgresClient()
    bottlenecks = await db.get_recent_bottlenecks(agent_id="research")
    assert len(bottlenecks) > 0
```

**Running:**
```bash
# All system tests (requires Docker)
pytest tests/system/ -v

# Skip slow tests
pytest tests/system/ -m "not slow"
```

**Coverage Target:** N/A (end-to-end validation, not code coverage)

---

### 4. Security Tests

**Purpose:** Identify vulnerabilities and security issues

**Scope:**
- Secret detection (API keys, credentials)
- Dependency vulnerabilities
- Code security issues (SQL injection, XSS)
- Container security

**Tools:**
- `gitleaks` - Secret scanning
- `bandit` - Python security linter
- `safety` - Dependency vulnerability scanner
- `trivy` (future) - Container vulnerability scanner

**Location:** Pre-commit hooks, CI/CD pipeline

**Running:**
```bash
# Pre-commit hooks (automatic)
pre-commit run --all-files

# Manual security scan
gitleaks detect --source . --verbose
bandit -r src/ -ll
safety check --json
```

**Quality Gate:** Zero high/critical vulnerabilities

---

### 5. Performance Tests

**Purpose:** Validate system performance under load

**Scope:**
- API response times (< 200ms p95)
- Database query performance
- Agent execution time
- Dashboard load times

**Tools:**
- `pytest-benchmark` - Python performance testing
- `locust` (future) - Load testing
- `pgbench` (future) - Database performance testing

**Location:** `tests/performance/`

**Running:**
```bash
# Benchmark tests
pytest tests/performance/ --benchmark-only

# Load testing (future)
locust -f tests/performance/locustfile.py
```

**Performance Targets:**
- API p95 latency: < 200ms
- Database query p95: < 50ms
- Agent cycle time: < 30 seconds
- Dashboard load time: < 3 seconds

---

## Test Environments

### Local Development

**Purpose:** Developer testing during development

**Configuration:**
- PostgreSQL: Local instance or Docker
- Docker Compose: SigNoz, Superset stacks
- .env: Local credentials

**Access:**
- Database: `localhost:5432`
- SigNoz: `http://localhost:3301`
- Superset: `http://localhost:8088`

**Data:** Anonymized production-like data

---

### Staging (Future)

**Purpose:** Pre-production validation

**Configuration:**
- VPS: Staging environment (separate from production)
- PostgreSQL: Dedicated staging database
- Domain: `staging.sentinel.yourdomain.com`

**Access:** Restricted to development team

**Data:** Anonymized production data snapshot

---

### Production

**Purpose:** Live system serving real users

**Configuration:**
- VPS: Production Hostinger server
- PostgreSQL: Production database with backups
- Domain: `sentinel.yourdomain.com`

**Access:** Role-based access control (RBAC)

**Data:** Real production data

---

## Test Automation

### Pre-Commit Hooks

**Trigger:** Before `git commit`

**Tests:**
- Trailing whitespace removal
- YAML syntax validation
- Secret detection (Gitleaks)
- Python code formatting (Black)
- Python linting (Ruff)
- Security scanning (Bandit)

**Configuration:** `.pre-commit-config.yaml`

**Bypass:** `git commit --no-verify` (use sparingly!)

---

### Local Test Suite

**Trigger:** Manual execution

**Script:** `scripts/test-local-deployment.sh`

**Tests:**
- Environment configuration
- Prerequisite validation
- Database connectivity
- Docker stack health
- Backup/restore functionality
- Application imports

**Usage:**
```bash
./scripts/test-local-deployment.sh
```

---

### CI/CD Pipeline (Future)

**Trigger:** `git push` to GitHub

**Pipeline Stages:**
1. **Lint & Format** (< 1 min)
   - Black, Ruff, mypy
2. **Security Scan** (< 2 min)
   - Gitleaks, Bandit, Safety
3. **Unit Tests** (< 3 min)
   - pytest unit tests
   - Coverage report
4. **Integration Tests** (< 5 min)
   - Database tests
   - API tests
5. **Build Docker Images** (< 5 min)
   - Application image
   - Test image
6. **Deploy to Staging** (< 3 min)
   - Terraform apply (staging)
   - Ansible playbook (staging)
7. **System Tests** (< 10 min)
   - End-to-end workflows
   - Smoke tests
8. **Deploy to Production** (Manual approval)
   - Terraform apply (production)
   - Ansible playbook (production)

**Tools:** GitHub Actions

**Configuration:** `.github/workflows/ci-cd.yml` (to be created)

---

## Manual Testing Procedures

### Pre-Release Checklist

Before deploying to production, manually verify:

- [ ] All automated tests pass
- [ ] Security scan shows no high/critical issues
- [ ] Database migrations tested (up and down)
- [ ] Backup/restore procedure tested
- [ ] All dashboards accessible (SigNoz, Superset)
- [ ] SSL certificates valid and auto-renewal configured
- [ ] Monitoring alerts configured
- [ ] Documentation up-to-date
- [ ] Changelog updated

---

### Smoke Testing

After deployment, verify critical paths:

1. **Database Connectivity**
   ```bash
   psql -h localhost -U sentinel -d sentinel -c "SELECT COUNT(*) FROM agents;"
   ```

2. **API Health Check**
   ```bash
   curl https://your-domain.com/health
   ```

3. **SigNoz Dashboard**
   - Navigate to `https://your-domain.com/ops`
   - Verify metrics visible

4. **Superset Dashboard**
   - Navigate to `https://your-domain.com/executive`
   - Verify database connection active
   - Run sample query

5. **Agent Execution**
   ```bash
   python -m src.cli.cli run-cycle --mode diagnostic
   ```

---

## Quality Gates

### Code Merge Requirements

Pull requests must meet these criteria before merging:

1. **Tests Pass**
   - All unit tests pass
   - All integration tests pass
   - No security vulnerabilities

2. **Coverage**
   - Overall coverage ≥ 80%
   - Changed files coverage ≥ 85%

3. **Code Quality**
   - Black formatting applied
   - Ruff linting passes
   - mypy type checking passes (strict mode)

4. **Documentation**
   - Public APIs documented
   - ADR created for architectural changes
   - Changelog updated

5. **Review**
   - At least 1 code review approval
   - All review comments addressed

---

### Deployment Requirements

Deployments to production require:

1. **All Quality Gates Pass**
2. **Staging Validation**
   - System tests pass in staging
   - Smoke tests pass in staging
   - Performance benchmarks met
3. **Approval**
   - Technical lead approval
   - Product owner approval (for feature releases)
4. **Rollback Plan**
   - Database rollback tested
   - Application rollback procedure documented
5. **Monitoring**
   - Alerts configured
   - On-call rotation assigned

---

## Continuous Integration

### GitHub Actions Workflow (Future)

**File:** `.github/workflows/ci.yml`

```yaml
name: CI Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install black ruff mypy
      - run: black --check src/ tests/
      - run: ruff check src/ tests/
      - run: mypy src/

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: gitleaks/gitleaks-action@v2
      - run: pip install bandit safety
      - run: bandit -r src/ -ll
      - run: safety check

  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt -r requirements-dev.txt
      - run: pytest tests/ --cov=src --cov-report=xml
      - uses: codecov/codecov-action@v3
```

---

## Bug Reporting

### Issue Template

When reporting bugs, include:

1. **Description:** Clear summary of the issue
2. **Steps to Reproduce:** Exact steps to trigger the bug
3. **Expected Behavior:** What should happen
4. **Actual Behavior:** What actually happens
5. **Environment:**
   - OS: `uname -a`
   - Python: `python3 --version`
   - Docker: `docker --version`
6. **Logs:** Relevant error messages/stack traces
7. **Screenshots:** If UI-related

### Severity Levels

- **Critical:** System down, data loss risk
- **High:** Major feature broken, security vulnerability
- **Medium:** Feature partially broken, workaround exists
- **Low:** Minor issue, cosmetic problem

---

## Test Metrics

### Key Performance Indicators (KPIs)

**Test Coverage:**
- Target: 80% overall, 85% for new code
- Measured by: `pytest --cov`

**Test Execution Time:**
- Unit tests: < 5 seconds
- Integration tests: < 30 seconds
- Full suite: < 5 minutes

**Defect Escape Rate:**
- Target: < 5% of bugs found in production
- Measured by: Production incidents / Total bugs found

**Mean Time to Detect (MTTD):**
- Target: < 5 minutes
- Measured by: Time from bug introduction to detection

**Mean Time to Resolve (MTTR):**
- Target: < 2 hours (critical), < 1 day (high)
- Measured by: Time from bug report to fix deployed

---

## References

- [pytest Documentation](https://docs.pytest.org/)
- [Python Testing Best Practices](https://realpython.com/python-testing/)
- [Testing Microservices](https://martinfowler.com/articles/microservice-testing/)
- [Google Testing Blog](https://testing.googleblog.com/)

---

**Document Version:** 1.0
**Next Review:** 2026-03-27
**Owner:** Troy Shields
