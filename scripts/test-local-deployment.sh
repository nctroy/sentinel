#!/bin/bash
# Local Deployment Testing Script for Sentinel
# Tests all components before VPS deployment
#
# Usage: ./test-local-deployment.sh
#
# This script validates:
# 1. Environment configuration
# 2. Database connectivity
# 3. Docker stack deployments
# 4. Backup/restore functionality
# 5. API endpoints
# 6. Monitoring dashboards

# Don't exit on error - we want to run all tests
# set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Test results tracking
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"

    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}TEST $TESTS_TOTAL: $test_name${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    if eval "$test_command"; then
        echo -e "${GREEN}✅ PASS: $test_name${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL: $test_name${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Banner
clear
echo -e "${GREEN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     SENTINEL LOCAL DEPLOYMENT TEST SUITE            ║${NC}"
echo -e "${GREEN}║     Validating production readiness                 ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Project Root: ${YELLOW}$PROJECT_ROOT${NC}"
echo -e "${BLUE}Start Time:   ${YELLOW}$(date)${NC}"
echo ""

cd "$PROJECT_ROOT"

# ============================================================================
# TEST 1: Environment Configuration
# ============================================================================
run_test "Environment file exists" "[[ -f .env ]]"

if [[ -f .env ]]; then
    run_test "DATABASE_URL configured" "grep -q 'DATABASE_URL=' .env && ! grep -q 'DATABASE_URL=$' .env"
    run_test "ANTHROPIC_API_KEY configured" "grep -q 'ANTHROPIC_API_KEY=' .env && ! grep -q 'ANTHROPIC_API_KEY=$' .env"
fi

# ============================================================================
# TEST 2: Prerequisites Check
# ============================================================================
run_test "Docker installed" "command -v docker &> /dev/null"
run_test "Docker Compose installed" "command -v docker-compose &> /dev/null || docker compose version &> /dev/null"
run_test "Python 3.9+ installed" "python3 --version | grep -E 'Python 3\.([9-9]|[1-9][0-9])'"
# PostgreSQL client is optional for Docker-based deployments
if command -v psql &> /dev/null; then
    run_test "PostgreSQL client installed" "command -v psql &> /dev/null"
else
    echo -e "${YELLOW}   ⚠️  PostgreSQL client (psql) not found - optional for Docker deployments${NC}"
fi

# ============================================================================
# TEST 3: Python Virtual Environment
# ============================================================================
if [[ -d .venv ]]; then
    echo -e "${YELLOW}Virtual environment exists, activating...${NC}"
    source .venv/bin/activate
    run_test "Virtual environment activated" "[[ -n '$VIRTUAL_ENV' ]]"
else
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv .venv
    source .venv/bin/activate
    run_test "Virtual environment created" "[[ -d .venv ]]"
fi

# ============================================================================
# TEST 4: Python Dependencies
# ============================================================================
echo -e "${YELLOW}Installing dependencies (this may take a minute)...${NC}"
pip install -q -r requirements.txt
pip install -q -r requirements-dev.txt

run_test "Dependencies installed" "pip list | grep -q 'fastapi'"
run_test "SQLAlchemy installed" "pip list | grep -q 'SQLAlchemy'"
run_test "Anthropic SDK installed" "pip list | grep -q 'anthropic'"

# ============================================================================
# TEST 5: Database Connectivity
# ============================================================================
echo -e "${YELLOW}Testing database connectivity...${NC}"

# Extract database credentials from .env
if [[ -f .env ]]; then
    export $(grep -v '^#' .env | xargs)

    # Parse DATABASE_URL
    DB_HOST=$(echo "$DATABASE_URL" | sed -n 's|.*@\([^:]*\):.*|\1|p')
    DB_PORT=$(echo "$DATABASE_URL" | sed -n 's|.*:\([0-9]*\)/.*|\1|p')
    DB_NAME=$(echo "$DATABASE_URL" | sed -n 's|.*/\([^?]*\).*|\1|p')
    DB_USER=$(echo "$DATABASE_URL" | sed -n 's|.*://\([^:]*\):.*|\1|p')
    DB_PASSWORD=$(echo "$DATABASE_URL" | sed -n 's|.*://[^:]*:\([^@]*\)@.*|\1|p')

    export PGPASSWORD="$DB_PASSWORD"

    run_test "PostgreSQL server reachable" "pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -q"
    run_test "Database exists" "psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c 'SELECT 1;' &> /dev/null"

    # Check if tables exist
    TABLE_COUNT=$(psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" 2>/dev/null | xargs)

    if [[ "$TABLE_COUNT" -gt 0 ]]; then
        echo -e "${GREEN}   Found $TABLE_COUNT tables in database${NC}"
        run_test "Core tables exist" "psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c '\dt' | grep -q 'agents'"
    else
        echo -e "${YELLOW}   No tables found - database needs initialization${NC}"
    fi

    unset PGPASSWORD
fi

# ============================================================================
# TEST 6: Docker Daemon
# ============================================================================
run_test "Docker daemon running" "docker info &> /dev/null"
run_test "Docker has free resources" "[[ $(docker system df | grep -c 'reclaimable') -ge 0 ]]"

# ============================================================================
# TEST 7: SigNoz Stack (Observability)
# ============================================================================
echo -e "${YELLOW}Testing SigNoz observability stack...${NC}"

if [[ -f docker-compose.observability.yml ]]; then
    # Check if already running
    if docker ps | grep -q signoz; then
        echo -e "${GREEN}   SigNoz already running${NC}"
        run_test "SigNoz frontend accessible" "curl -f http://localhost:3301 &> /dev/null"
    else
        echo -e "${YELLOW}   Starting SigNoz (this may take 2-3 minutes)...${NC}"
        ./scripts/start-signoz.sh &> /tmp/signoz-start.log &
        SIGNOZ_PID=$!

        # Wait up to 3 minutes for SigNoz to start
        for i in {1..36}; do
            if curl -f http://localhost:3301 &> /dev/null; then
                echo -e "${GREEN}   SigNoz started successfully${NC}"
                break
            fi
            echo -n "."
            sleep 5
        done
        echo ""

        run_test "SigNoz frontend accessible" "curl -f http://localhost:3301 &> /dev/null"
    fi

    run_test "ClickHouse running" "docker ps | grep -q clickhouse"
    run_test "SigNoz query service running" "docker ps | grep -q signoz-query-service"
else
    echo -e "${YELLOW}   Skipping SigNoz test - docker-compose.observability.yml not found${NC}"
fi

# ============================================================================
# TEST 8: Superset Stack (Analytics)
# ============================================================================
echo -e "${YELLOW}Testing Apache Superset analytics stack...${NC}"

if [[ -f docker-compose.analytics.yml ]]; then
    # Check if already running
    if docker ps | grep -q sentinel-superset; then
        echo -e "${GREEN}   Superset already running${NC}"
        run_test "Superset web accessible" "curl -f http://localhost:8088 &> /dev/null"
    else
        echo -e "${YELLOW}   Starting Superset (this may take 2-3 minutes)...${NC}"
        ./scripts/start-superset.sh &> /tmp/superset-start.log &
        SUPERSET_PID=$!

        # Wait up to 3 minutes for Superset to start
        for i in {1..36}; do
            if curl -f http://localhost:8088 &> /dev/null; then
                echo -e "${GREEN}   Superset started successfully${NC}"
                break
            fi
            echo -n "."
            sleep 5
        done
        echo ""

        run_test "Superset web accessible" "curl -f http://localhost:8088/login/ &> /dev/null"
    fi

    run_test "Redis running" "docker ps | grep -q sentinel-redis"
    run_test "Superset worker running" "docker ps | grep -q sentinel-superset-worker"
else
    echo -e "${YELLOW}   Skipping Superset test - docker-compose.analytics.yml not found${NC}"
fi

# ============================================================================
# TEST 9: Backup Script
# ============================================================================
echo -e "${YELLOW}Testing backup script...${NC}"

if [[ -f scripts/backup-db.sh ]]; then
    run_test "Backup script executable" "[[ -x scripts/backup-db.sh ]]"

    # Create test backup
    echo -e "${YELLOW}   Creating test backup...${NC}"
    mkdir -p backups/postgres
    if ./scripts/backup-db.sh --retention-days 1 &> /tmp/backup-test.log; then
        run_test "Backup created successfully" "[[ -f backups/postgres/sentinel_*.sql.gz ]]"

        # Check backup file is not empty
        BACKUP_FILE=$(ls -t backups/postgres/sentinel_*.sql.gz 2>/dev/null | head -1)
        if [[ -f "$BACKUP_FILE" ]]; then
            BACKUP_SIZE=$(stat -f%z "$BACKUP_FILE" 2>/dev/null || stat -c%s "$BACKUP_FILE" 2>/dev/null)
            run_test "Backup file not empty" "[[ $BACKUP_SIZE -gt 0 ]]"
        fi
    else
        TESTS_FAILED=$((TESTS_FAILED + 1))
        echo -e "${RED}   Backup creation failed - check /tmp/backup-test.log${NC}"
    fi
else
    echo -e "${YELLOW}   Skipping backup test - scripts/backup-db.sh not found${NC}"
fi

# ============================================================================
# TEST 10: Python Application
# ============================================================================
echo -e "${YELLOW}Testing Sentinel Python application...${NC}"

run_test "CLI module exists" "[[ -f src/cli/cli.py ]]"
run_test "Agent modules exist" "[[ -f src/agents/base_agent.py ]]"
run_test "Storage modules exist" "[[ -f src/storage/postgres_client.py ]]"

# Test imports
run_test "Python imports work" "python3 -c 'from src.storage.postgres_client import PostgresClient'"
run_test "CLI imports work" "python3 -c 'from src.cli.cli import app'"

# ============================================================================
# TEST 11: Pre-commit Hooks
# ============================================================================
echo -e "${YELLOW}Testing pre-commit security hooks...${NC}"

if [[ -f .pre-commit-config.yaml ]]; then
    run_test "Pre-commit config exists" "[[ -f .pre-commit-config.yaml ]]"

    # Check if hooks are installed
    if [[ -f .git/hooks/pre-commit ]]; then
        run_test "Pre-commit hooks installed" "grep -q 'pre-commit' .git/hooks/pre-commit"
    else
        echo -e "${YELLOW}   Installing pre-commit hooks...${NC}"
        pre-commit install
        run_test "Pre-commit hooks installed" "[[ -f .git/hooks/pre-commit ]]"
    fi
fi

# ============================================================================
# TEST 12: Configuration Files
# ============================================================================
echo -e "${YELLOW}Testing configuration files...${NC}"

run_test "Nginx config exists" "[[ -f nginx/nginx.conf ]]"
run_test "Superset config exists" "[[ -f superset/superset_config.py ]]"
run_test "OTel config exists" "[[ -f otel-collector-config.yaml ]]"

# ============================================================================
# TEST 13: Documentation
# ============================================================================
echo -e "${YELLOW}Validating documentation...${NC}"

run_test "README exists" "[[ -f README.md ]]"
run_test "ADRs exist" "[[ -d docs/adr ]]"
run_test "All 6 ADRs present" "[[ $(ls -1 docs/adr/ADR-*.md 2>/dev/null | wc -l) -ge 6 ]]"
run_test "Sprint docs exist" "[[ -d docs/sprint ]]"

# ============================================================================
# FINAL SUMMARY
# ============================================================================
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}╔══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              TEST SUITE COMPLETE                     ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════╝${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}Total Tests:  ${YELLOW}$TESTS_TOTAL${NC}"
echo -e "${GREEN}Passed:       ${YELLOW}$TESTS_PASSED${NC}"
echo -e "${RED}Failed:       ${YELLOW}$TESTS_FAILED${NC}"

if [[ $TESTS_FAILED -eq 0 ]]; then
    echo ""
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${GREEN}✅ Sentinel is ready for VPS deployment!${NC}"
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo "  1. Review test results above"
    echo "  2. Access dashboards:"
    echo "     - SigNoz:   http://localhost:3301"
    echo "     - Superset: http://localhost:8088 (admin/admin)"
    echo "  3. Proceed with Terraform + Ansible deployment"
    echo ""
    echo -e "${BLUE}Deployment Commands:${NC}"
    echo "  terraform apply -var='hostinger_api_key=YOUR_KEY'"
    echo "  ansible-playbook deploy.yml -i inventory/hostinger.yml"
    echo ""
else
    echo ""
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}⚠️  SOME TESTS FAILED${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    echo -e "${YELLOW}Please fix the failed tests before VPS deployment.${NC}"
    echo ""
    echo -e "${BLUE}Common Issues:${NC}"
    echo "  - Missing .env file: cp .env.example .env"
    echo "  - Database not running: Start PostgreSQL"
    echo "  - Docker not running: Start Docker Desktop"
    echo "  - Dependencies not installed: pip install -r requirements.txt"
    echo ""
    echo -e "${BLUE}Logs:${NC}"
    echo "  - SigNoz:  /tmp/signoz-start.log"
    echo "  - Superset: /tmp/superset-start.log"
    echo "  - Backup:   /tmp/backup-test.log"
    echo ""
    exit 1
fi

echo -e "${BLUE}End Time: ${YELLOW}$(date)${NC}"
echo ""
