# Deployment Runbook

**Document Owner:** Troy Shields
**Last Updated:** 2025-12-27
**Status:** Active
**Version:** 1.0

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Deployment Environments](#deployment-environments)
4. [Local Deployment](#local-deployment)
5. [VPS Deployment (Hostinger)](#vps-deployment-hostinger)
6. [Post-Deployment Validation](#post-deployment-validation)
7. [Rollback Procedures](#rollback-procedures)
8. [Troubleshooting](#troubleshooting)
9. [Maintenance](#maintenance)

---

## Overview

This runbook provides step-by-step procedures for deploying Sentinel to various environments. Follow these procedures for consistent, reliable deployments.

### Deployment Strategy

Sentinel uses a **blue-green deployment** strategy with the following progression:

```
Local Development → VPS Staging → VPS Production
```

**Deployment Methods:**
- **Manual:** Step-by-step execution (this guide)
- **Automated:** Terraform + Ansible (see [CICD.md](CICD.md))

---

## Prerequisites

### Required Tools

| Tool | Version | Purpose | Installation |
|------|---------|---------|--------------|
| **Python** | 3.9+ | Application runtime | `brew install python@3.10` |
| **Docker** | 20.10+ | Container runtime | [Docker Desktop](https://www.docker.com/products/docker-desktop) |
| **Docker Compose** | 2.0+ | Stack orchestration | Included with Docker Desktop |
| **PostgreSQL** | 15+ | Database | `brew install postgresql@15` |
| **Git** | 2.30+ | Version control | `brew install git` |
| **SSH Client** | Any | VPS access | Built-in (macOS/Linux) |

### Required Credentials

- **Claude API Key:** From [Anthropic Console](https://console.anthropic.com/)
- **GitHub Token:** Personal Access Token with repo access
- **Notion API Key:** (Optional) From [Notion Integrations](https://www.notion.so/my-integrations)
- **VPS SSH Key:** For Hostinger server access
- **Domain Name:** (For production SSL)

### Required Access

- GitHub repository: `github.com/nctroy/sentinel`
- Hostinger VPS: SSH access with sudo privileges
- DNS management: Ability to configure A records

---

## Deployment Environments

### Local Development

**Purpose:** Development and testing
**Infrastructure:** Developer workstation
**Database:** Local PostgreSQL or Docker
**URL:** `http://localhost:8000`
**Cost:** $0

---

### VPS Staging (Future)

**Purpose:** Pre-production testing
**Infrastructure:** Hostinger VPS (separate instance)
**Database:** PostgreSQL on VPS
**URL:** `https://staging.yourdomain.com`
**Cost:** ~$10-20/month

---

### VPS Production

**Purpose:** Live system
**Infrastructure:** Hostinger VPS
**Database:** PostgreSQL on VPS with backups
**URL:** `https://sentinel.yourdomain.com`
**Cost:** ~$20-40/month

---

## Local Deployment

### Step 1: Clone Repository

```bash
# Clone repository
git clone https://github.com/nctroy/sentinel.git
cd sentinel

# Verify branch
git branch
# Should show: * main
```

---

### Step 2: Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file
nano .env  # or vim, code, etc.
```

**Required Variables:**
```bash
# Database
DATABASE_URL=postgresql://sentinel:your-password@localhost:5432/sentinel

# AI Services
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxx

# Optional: Notion Integration
NOTION_API_KEY=secret_xxxxxxxxxx
NOTION_WORKSPACE_ID=your-workspace-id

# Optional: GitHub Integration
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
```

---

### Step 3: Database Setup

```bash
# Start PostgreSQL (if not running)
brew services start postgresql@15

# Create database and user
psql postgres <<EOF
CREATE USER sentinel WITH PASSWORD 'your-password';
CREATE DATABASE sentinel OWNER sentinel;
GRANT ALL PRIVILEGES ON DATABASE sentinel TO sentinel;
EOF

# Verify connection
psql -U sentinel -d sentinel -c "SELECT version();"
```

---

### Step 4: Python Environment

```bash
# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate  # Windows

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Verify installation
pip list | grep fastapi
```

---

### Step 5: Database Initialization

```bash
# Run migrations
alembic upgrade head

# Verify tables created
psql -U sentinel -d sentinel -c "\dt"
# Should show: agents, bottlenecks, decisions, weekly_plans, notion_sync
```

---

### Step 6: Pre-Commit Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Test hooks
pre-commit run --all-files
```

---

### Step 7: Start Services

#### Option A: Start All Services

```bash
# Terminal 1: SigNoz Observability
./scripts/start-signoz.sh

# Terminal 2: Superset Analytics
./scripts/start-superset.sh

# Terminal 3: Sentinel Application (future)
python -m src.cli.cli run-server
```

#### Option B: Start Individual Services

```bash
# SigNoz only
./scripts/start-signoz.sh

# Superset only
./scripts/start-superset.sh
```

---

### Step 8: Verification

```bash
# Run local test suite
./scripts/test-local-deployment.sh

# Check service health
curl http://localhost:3301  # SigNoz
curl http://localhost:8088  # Superset

# Access dashboards
open http://localhost:3301      # SigNoz
open http://localhost:8088      # Superset (admin/admin)
```

---

## VPS Deployment (Hostinger)

### Architecture

```
┌─────────────────────────────────────────────┐
│         Hostinger VPS (Ubuntu 22.04)        │
├─────────────────────────────────────────────┤
│  ┌───────────────────────────────────────┐  │
│  │  Nginx (Port 80/443)                  │  │
│  │  - SSL Termination (Let's Encrypt)    │  │
│  │  - Reverse Proxy                      │  │
│  │  - Rate Limiting                      │  │
│  └──────┬───────┬───────┬────────────────┘  │
│         │       │       │                    │
│    ┌────▼──┐ ┌──▼───┐ ┌▼─────┐             │
│    │SigNoz │ │Super │ │FastAPI│             │
│    │:3301  │ │:8088 │ │:8000  │             │
│    └───────┘ └──────┘ └───────┘             │
│         │       │       │                    │
│    ┌────▼───────▼───────▼────┐              │
│    │   PostgreSQL :5432       │              │
│    └──────────────────────────┘              │
└─────────────────────────────────────────────┘
```

---

### Step 1: VPS Provisioning

#### Manual Provisioning

1. **Log into Hostinger**
   - Navigate to VPS section
   - Select plan (recommended: 4GB RAM, 2 vCPUs)

2. **Configure VPS**
   - OS: Ubuntu 22.04 LTS
   - Location: Closest to users
   - Hostname: `sentinel-prod`

3. **Note Credentials**
   - IP Address: `xxx.xxx.xxx.xxx`
   - Root password: (provided by Hostinger)

#### Automated Provisioning (Terraform)

```bash
# Initialize Terraform
cd terraform/
terraform init

# Plan deployment
terraform plan \
  -var="hostinger_api_key=$HOSTINGER_API_KEY" \
  -var="vps_plan=vps-4gb"

# Apply configuration
terraform apply

# Note outputs
terraform output vps_ip_address
```

---

### Step 2: Initial Server Setup

```bash
# SSH into VPS
ssh root@xxx.xxx.xxx.xxx

# Update system
apt update && apt upgrade -y

# Install prerequisites
apt install -y \
  python3.10 \
  python3.10-venv \
  python3-pip \
  postgresql-15 \
  nginx \
  certbot \
  python3-certbot-nginx \
  docker.io \
  docker-compose \
  git \
  ufw

# Create sentinel user
adduser --disabled-password --gecos "" sentinel
usermod -aG sudo,docker sentinel

# Configure SSH key
mkdir -p /home/sentinel/.ssh
cp ~/.ssh/authorized_keys /home/sentinel/.ssh/
chown -R sentinel:sentinel /home/sentinel/.ssh
chmod 700 /home/sentinel/.ssh
chmod 600 /home/sentinel/.ssh/authorized_keys

# Switch to sentinel user
su - sentinel
```

---

### Step 3: Firewall Configuration

```bash
# Configure UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# Verify firewall
sudo ufw status
```

---

### Step 4: Clone Repository

```bash
# Clone as sentinel user
cd /home/sentinel
git clone https://github.com/nctroy/sentinel.git
cd sentinel

# Verify
git log -1 --oneline
```

---

### Step 5: Environment Configuration

```bash
# Create .env from template
cp .env.example .env

# Edit with VPS-specific values
nano .env
```

**Production .env:**
```bash
# Database (local PostgreSQL)
DATABASE_URL=postgresql://sentinel:STRONG_PASSWORD@localhost:5432/sentinel

# AI Services
ANTHROPIC_API_KEY=sk-ant-api03-your-real-key

# Notion Integration
NOTION_API_KEY=secret_your-real-key
NOTION_WORKSPACE_ID=your-workspace-id

# GitHub Integration
GITHUB_TOKEN=ghp_your-real-token

# Environment
ENVIRONMENT=production
LOG_LEVEL=INFO
```

**Security:**
```bash
# Restrict .env permissions
chmod 600 .env

# Verify
ls -la .env
# Should show: -rw------- 1 sentinel sentinel
```

---

### Step 6: Database Setup

```bash
# Configure PostgreSQL
sudo -u postgres psql <<EOF
CREATE USER sentinel WITH PASSWORD 'STRONG_PASSWORD';
CREATE DATABASE sentinel OWNER sentinel;
GRANT ALL PRIVILEGES ON DATABASE sentinel TO sentinel;
\q
EOF

# Test connection
psql -U sentinel -d sentinel -c "SELECT version();"

# Configure PostgreSQL for network access (if needed)
sudo nano /etc/postgresql/15/main/postgresql.conf
# Set: listen_addresses = 'localhost'

sudo nano /etc/postgresql/15/main/pg_hba.conf
# Add: local   sentinel   sentinel   md5

# Restart PostgreSQL
sudo systemctl restart postgresql
```

---

### Step 7: Python Application

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run database migrations
alembic upgrade head

# Verify
psql -U sentinel -d sentinel -c "\dt"
```

---

### Step 8: Docker Services

```bash
# Start Docker daemon
sudo systemctl start docker
sudo systemctl enable docker

# Add sentinel to docker group (if not already)
sudo usermod -aG docker sentinel
# Log out and back in for group changes

# Start SigNoz
./scripts/start-signoz.sh

# Start Superset
./scripts/start-superset.sh

# Verify containers running
docker ps
```

---

### Step 9: SSL/TLS Configuration

**Prerequisites:**
- Domain DNS A record points to VPS IP
- Domain propagated (check with `dig yourdomain.com`)

```bash
# Run SSL setup script
sudo ./scripts/setup-ssl.sh sentinel.yourdomain.com admin@yourdomain.com

# Verify SSL certificate
sudo certbot certificates

# Test auto-renewal
sudo certbot renew --dry-run
```

**Manual Nginx Configuration:**

```bash
# Copy nginx config
sudo cp nginx/nginx.conf /etc/nginx/sites-available/sentinel

# Update domain in config
sudo sed -i 's/your-domain.com/sentinel.yourdomain.com/g' /etc/nginx/sites-available/sentinel

# Enable site
sudo ln -s /etc/nginx/sites-available/sentinel /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

---

### Step 10: Production Validation

```bash
# Run deployment tests
./scripts/test-local-deployment.sh

# Check HTTPS access
curl https://sentinel.yourdomain.com/health

# Verify dashboards
curl -u admin:password https://sentinel.yourdomain.com/ops
curl -u admin:password https://sentinel.yourdomain.com/executive
```

---

## Post-Deployment Validation

### Health Checks

```bash
# 1. Database connectivity
psql -U sentinel -d sentinel -c "SELECT COUNT(*) FROM agents;"

# 2. API health
curl https://sentinel.yourdomain.com/health

# 3. SigNoz
curl https://sentinel.yourdomain.com/ops

# 4. Superset
curl https://sentinel.yourdomain.com/executive

# 5. SSL certificate
openssl s_client -connect sentinel.yourdomain.com:443 -servername sentinel.yourdomain.com < /dev/null
```

---

### Smoke Tests

**Test 1: Database Operations**
```bash
# Run test query
psql -U sentinel -d sentinel <<EOF
INSERT INTO agents (agent_id, agent_type, domain)
VALUES ('smoke-test', 'test', 'testing');

SELECT * FROM agents WHERE agent_id = 'smoke-test';

DELETE FROM agents WHERE agent_id = 'smoke-test';
EOF
```

**Test 2: Agent Execution**
```bash
# Run diagnostic cycle
python -m src.cli.cli run-cycle --mode diagnostic

# Check for errors
echo $?
# Should return 0
```

**Test 3: Backup Creation**
```bash
# Create test backup
./scripts/backup-db.sh

# Verify backup exists
ls -lh backups/postgres/
```

---

## Rollback Procedures

### Application Rollback

```bash
# 1. Identify previous stable version
git tag -l
# Example output: v1.0.0, v1.0.1, v1.1.0

# 2. Checkout previous version
git checkout v1.0.0

# 3. Reinstall dependencies
source .venv/bin/activate
pip install -r requirements.txt

# 4. Restart services
sudo systemctl restart sentinel

# 5. Verify
curl https://sentinel.yourdomain.com/health
```

---

### Database Rollback

```bash
# 1. Stop application
sudo systemctl stop sentinel

# 2. Restore from backup
./scripts/restore-db.sh backups/postgres/sentinel_YYYYMMDD_HHMMSS.sql.gz

# 3. Verify data
psql -U sentinel -d sentinel -c "SELECT COUNT(*) FROM agents;"

# 4. Restart application
sudo systemctl start sentinel
```

---

## Troubleshooting

### Common Issues

#### Issue: Port Already in Use

**Symptoms:**
```
Error: bind: address already in use
```

**Solution:**
```bash
# Find process using port
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>

# Or use fuser
sudo fuser -k 8000/tcp
```

---

#### Issue: Database Connection Failed

**Symptoms:**
```
psycopg2.OperationalError: could not connect to server
```

**Solution:**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Start if stopped
sudo systemctl start postgresql

# Check logs
sudo tail -f /var/log/postgresql/postgresql-15-main.log

# Verify connection string
cat .env | grep DATABASE_URL
```

---

#### Issue: SSL Certificate Not Found

**Symptoms:**
```
nginx: [emerg] cannot load certificate
```

**Solution:**
```bash
# Verify certificate exists
sudo ls -la /etc/letsencrypt/live/sentinel.yourdomain.com/

# Re-run certbot
sudo certbot --nginx -d sentinel.yourdomain.com

# Check Nginx config
sudo nginx -t
```

---

#### Issue: Docker Container Not Starting

**Symptoms:**
```
Error: container exited with code 137
```

**Solution:**
```bash
# Check container logs
docker logs <container-name>

# Check system resources
free -h
df -h

# Restart Docker daemon
sudo systemctl restart docker

# Recreate container
docker-compose down
docker-compose up -d
```

---

## Maintenance

### Daily Tasks

- Monitor dashboard health (automated alerts)
- Review error logs
- Check disk space

```bash
# Automated health check script
./scripts/health-check.sh
```

---

### Weekly Tasks

- Review security scan results
- Update dependencies (patch versions)
- Backup verification

```bash
# Update dependencies
pip list --outdated
pip install -U package-name

# Test backup restore
./scripts/restore-db.sh --test
```

---

### Monthly Tasks

- SSL certificate check (auto-renews, but verify)
- Full system backup
- Performance review
- Security audit

```bash
# Certificate expiry
sudo certbot certificates

# Full backup
./scripts/backup-db.sh --encrypt

# Security scan
pre-commit run --all-files
```

---

## References

- [Hostinger VPS Documentation](https://www.hostinger.com/tutorials/vps)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Docker Documentation](https://docs.docker.com/)

---

**Document Version:** 1.0
**Next Review:** 2026-03-27
**Owner:** Troy Shields
