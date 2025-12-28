# CI/CD Pipeline Documentation

**Document Owner:** Troy Shields
**Last Updated:** 2025-12-27
**Status:** Planned (Implementation Pending)
**Version:** 1.0

---

## Table of Contents

1. [Overview](#overview)
2. [Pipeline Architecture](#pipeline-architecture)
3. [GitHub Actions Workflows](#github-actions-workflows)
4. [Terraform Infrastructure](#terraform-infrastructure)
5. [Ansible Configuration](#ansible-configuration)
6. [Deployment Process](#deployment-process)
7. [Monitoring & Alerts](#monitoring--alerts)
8. [Secrets Management](#secrets-management)

---

## Overview

This document describes the Continuous Integration and Continuous Deployment (CI/CD) pipeline for Sentinel. The pipeline automates testing, security scanning, building, and deployment to ensure consistent, reliable releases.

### Goals

- **Automate Testing:** Run comprehensive tests on every commit
- **Enforce Quality:** Block merges that fail quality gates
- **Secure Deployments:** Scan for vulnerabilities before deployment
- **Fast Feedback:** Provide results in < 10 minutes
- **Reproducible Builds:** Infrastructure as Code (Terraform + Ansible)

### Technology Stack

| Component | Tool | Purpose |
|-----------|------|---------|
| **CI Pipeline** | GitHub Actions | Test automation, security scans |
| **Infrastructure** | Terraform | VPS provisioning (Hostinger) |
| **Configuration** | Ansible | Server configuration, deployment |
| **Secrets** | GitHub Secrets | Encrypted credential storage |
| **Artifacts** | GitHub Packages | Docker image registry |
| **Monitoring** | SigNoz | Pipeline execution metrics |

---

## Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CI/CD Pipeline Flow                      │
└─────────────────────────────────────────────────────────────┘

  Developer
      ↓
  git push
      ↓
┌─────────────────┐
│  GitHub Actions │
│   CI Pipeline   │
└────────┬────────┘
         │
         ├─→ 1. Lint & Format (Black, Ruff, mypy)
         ├─→ 2. Security Scan (Gitleaks, Bandit, Safety)
         ├─→ 3. Unit Tests (pytest)
         ├─→ 4. Integration Tests (pytest + PostgreSQL)
         ├─→ 5. Build Docker Images
         │
         ├─→ [Quality Gate: All Pass?]
         │       ↓ NO → Fail PR, notify developer
         │       ↓ YES
         │
         ├─→ 6. Deploy to Staging
         │       ├─→ Terraform Apply (staging VPS)
         │       ├─→ Ansible Playbook (configure)
         │       └─→ System Tests
         │
         ├─→ [Manual Approval Required]
         │       ↓
         │
         └─→ 7. Deploy to Production
                 ├─→ Terraform Apply (prod VPS)
                 ├─→ Ansible Playbook (configure)
                 ├─→ Smoke Tests
                 └─→ Notify team (Slack/Email)
```

---

## GitHub Actions Workflows

### Workflow 1: Continuous Integration

**File:** `.github/workflows/ci.yml`

**Triggers:**
- Push to `main` or `develop` branches
- Pull requests to `main`

**Jobs:**

#### Job 1: Lint and Format
```yaml
name: Lint and Format
runs-on: ubuntu-latest
timeout-minutes: 5

steps:
  - uses: actions/checkout@v4

  - name: Set up Python
    uses: actions/setup-python@v5
    with:
      python-version: '3.10'

  - name: Install linting tools
    run: |
      pip install black==23.12.1 ruff==0.1.9 mypy==1.8.0

  - name: Check formatting (Black)
    run: black --check src/ tests/

  - name: Lint (Ruff)
    run: ruff check src/ tests/

  - name: Type check (mypy)
    run: mypy src/ --strict
```

#### Job 2: Security Scanning
```yaml
name: Security Scan
runs-on: ubuntu-latest
timeout-minutes: 10

steps:
  - uses: actions/checkout@v4
    with:
      fetch-depth: 0  # Full history for Gitleaks

  - name: Gitleaks Secret Scan
    uses: gitleaks/gitleaks-action@v2
    env:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  - name: Bandit Security Scan
    run: |
      pip install bandit==1.7.6
      bandit -r src/ -ll -f json -o bandit-report.json

  - name: Safety Dependency Scan
    run: |
      pip install safety==2.3.5
      safety check --json

  - name: Upload Security Reports
    if: always()
    uses: actions/upload-artifact@v4
    with:
      name: security-reports
      path: |
        bandit-report.json
        gitleaks-report.json
```

#### Job 3: Unit Tests
```yaml
name: Unit Tests
runs-on: ubuntu-latest
timeout-minutes: 10

steps:
  - uses: actions/checkout@v4

  - name: Set up Python
    uses: actions/setup-python@v5
    with:
      python-version: '3.10'
      cache: 'pip'

  - name: Install dependencies
    run: |
      pip install -r requirements.txt -r requirements-dev.txt

  - name: Run unit tests
    run: |
      pytest tests/unit/ \
        --cov=src \
        --cov-report=xml \
        --cov-report=html \
        --junitxml=junit.xml

  - name: Upload coverage to Codecov
    uses: codecov/codecov-action@v3
    with:
      files: ./coverage.xml
      flags: unittests
      fail_ci_if_error: true

  - name: Enforce coverage threshold
    run: |
      coverage report --fail-under=80
```

#### Job 4: Integration Tests
```yaml
name: Integration Tests
runs-on: ubuntu-latest
timeout-minutes: 15

services:
  postgres:
    image: postgres:15-alpine
    env:
      POSTGRES_DB: sentinel_test
      POSTGRES_USER: sentinel
      POSTGRES_PASSWORD: test_password
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5
    ports:
      - 5432:5432

steps:
  - uses: actions/checkout@v4

  - name: Set up Python
    uses: actions/setup-python@v5
    with:
      python-version: '3.10'
      cache: 'pip'

  - name: Install dependencies
    run: |
      pip install -r requirements.txt -r requirements-dev.txt

  - name: Run database migrations
    env:
      DATABASE_URL: postgresql://sentinel:test_password@localhost:5432/sentinel_test
    run: |
      alembic upgrade head

  - name: Run integration tests
    env:
      DATABASE_URL: postgresql://sentinel:test_password@localhost:5432/sentinel_test
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
    run: |
      pytest tests/integration/ -v
```

---

### Workflow 2: Continuous Deployment

**File:** `.github/workflows/deploy.yml`

**Triggers:**
- Manual workflow dispatch
- Successful merge to `main` (after CI passes)

**Jobs:**

#### Job 1: Build Docker Images
```yaml
name: Build and Push Docker Images
runs-on: ubuntu-latest
timeout-minutes: 20

steps:
  - uses: actions/checkout@v4

  - name: Set up Docker Buildx
    uses: docker/setup-buildx-action@v3

  - name: Login to GitHub Container Registry
    uses: docker/login-action@v3
    with:
      registry: ghcr.io
      username: ${{ github.actor }}
      password: ${{ secrets.GITHUB_TOKEN }}

  - name: Build and push application image
    uses: docker/build-push-action@v5
    with:
      context: .
      file: ./Dockerfile
      push: true
      tags: |
        ghcr.io/${{ github.repository }}/sentinel:latest
        ghcr.io/${{ github.repository }}/sentinel:${{ github.sha }}
      cache-from: type=registry,ref=ghcr.io/${{ github.repository }}/sentinel:latest
      cache-to: type=inline
```

#### Job 2: Deploy to Staging
```yaml
name: Deploy to Staging
runs-on: ubuntu-latest
needs: [build]
environment:
  name: staging
  url: https://staging.yourdomain.com

steps:
  - uses: actions/checkout@v4

  - name: Set up Terraform
    uses: hashicorp/setup-terraform@v3
    with:
      terraform_version: 1.6.0

  - name: Terraform Init
    working-directory: ./terraform
    run: terraform init

  - name: Terraform Plan
    working-directory: ./terraform
    env:
      TF_VAR_environment: staging
      TF_VAR_hostinger_api_key: ${{ secrets.HOSTINGER_API_KEY }}
    run: terraform plan -out=tfplan

  - name: Terraform Apply
    working-directory: ./terraform
    run: terraform apply tfplan

  - name: Set up Ansible
    run: |
      pip install ansible==9.0.0

  - name: Run Ansible Playbook
    env:
      ANSIBLE_HOST_KEY_CHECKING: False
    run: |
      ansible-playbook \
        -i inventory/staging.yml \
        playbooks/deploy.yml \
        --extra-vars "image_tag=${{ github.sha }}"

  - name: Run smoke tests
    run: |
      ./scripts/smoke-tests.sh https://staging.yourdomain.com
```

#### Job 3: Deploy to Production
```yaml
name: Deploy to Production
runs-on: ubuntu-latest
needs: [deploy-staging]
environment:
  name: production
  url: https://sentinel.yourdomain.com

steps:
  - uses: actions/checkout@v4

  - name: Terraform Apply (Production)
    working-directory: ./terraform
    env:
      TF_VAR_environment: production
      TF_VAR_hostinger_api_key: ${{ secrets.HOSTINGER_API_KEY }}
    run: |
      terraform init
      terraform apply -auto-approve

  - name: Deploy with Ansible
    run: |
      ansible-playbook \
        -i inventory/production.yml \
        playbooks/deploy.yml \
        --extra-vars "image_tag=${{ github.sha }}"

  - name: Health checks
    run: |
      ./scripts/health-check.sh https://sentinel.yourdomain.com

  - name: Notify deployment
    uses: slackapi/slack-github-action@v1
    with:
      payload: |
        {
          "text": "✅ Sentinel deployed to production",
          "blocks": [
            {
              "type": "section",
              "text": {
                "type": "mrkdwn",
                "text": "*Sentinel Production Deployment*\nVersion: `${{ github.sha }}`\nURL: https://sentinel.yourdomain.com"
              }
            }
          ]
        }
    env:
      SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK }}
```

---

## Terraform Infrastructure

### Directory Structure

```
terraform/
├── main.tf                 # Main configuration
├── variables.tf            # Input variables
├── outputs.tf              # Output values
├── providers.tf            # Provider configuration
├── modules/
│   ├── vps/               # VPS module
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── dns/               # DNS module
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
└── environments/
    ├── staging.tfvars     # Staging variables
    └── production.tfvars  # Production variables
```

### Sample Configuration

**`terraform/main.tf`:**
```hcl
terraform {
  required_version = ">= 1.6.0"

  required_providers {
    hostinger = {
      source  = "hostinger/hostinger"
      version = "~> 1.0"
    }
  }

  backend "s3" {
    bucket = "sentinel-terraform-state"
    key    = "production/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "hostinger" {
  api_key = var.hostinger_api_key
}

module "vps" {
  source = "./modules/vps"

  environment   = var.environment
  instance_type = var.instance_type
  ssh_key       = var.ssh_public_key
}

module "dns" {
  source = "./modules/dns"

  domain     = var.domain
  vps_ip     = module.vps.public_ip
  subdomain  = var.environment == "production" ? "sentinel" : "staging"
}
```

**`terraform/variables.tf`:**
```hcl
variable "environment" {
  description = "Environment name (staging/production)"
  type        = string
  validation {
    condition     = contains(["staging", "production"], var.environment)
    error_message = "Environment must be staging or production."
  }
}

variable "hostinger_api_key" {
  description = "Hostinger API key"
  type        = string
  sensitive   = true
}

variable "instance_type" {
  description = "VPS instance type"
  type        = string
  default     = "vps-4gb"
}

variable "domain" {
  description = "Root domain name"
  type        = string
}

variable "ssh_public_key" {
  description = "SSH public key for VPS access"
  type        = string
}
```

---

## Ansible Configuration

### Directory Structure

```
ansible/
├── ansible.cfg             # Ansible configuration
├── inventory/
│   ├── staging.yml        # Staging inventory
│   └── production.yml     # Production inventory
├── playbooks/
│   ├── deploy.yml         # Main deployment playbook
│   ├── setup.yml          # Initial server setup
│   └── rollback.yml       # Rollback playbook
├── roles/
│   ├── common/            # Common server configuration
│   ├── docker/            # Docker installation
│   ├── postgres/          # PostgreSQL setup
│   ├── nginx/             # Nginx configuration
│   ├── sentinel/          # Sentinel application
│   └── monitoring/        # SigNoz/Superset setup
└── group_vars/
    ├── all.yml            # Variables for all hosts
    ├── staging.yml        # Staging-specific variables
    └── production.yml     # Production-specific variables
```

### Sample Playbook

**`ansible/playbooks/deploy.yml`:**
```yaml
---
- name: Deploy Sentinel to VPS
  hosts: sentinel
  become: yes
  vars:
    app_user: sentinel
    app_dir: /home/sentinel/sentinel

  pre_tasks:
    - name: Update apt cache
      apt:
        update_cache: yes
        cache_valid_time: 3600

  roles:
    - role: common
      tags: [common]

    - role: docker
      tags: [docker]

    - role: postgres
      tags: [postgres, database]

    - role: nginx
      tags: [nginx, web]

    - role: sentinel
      tags: [sentinel, app]

    - role: monitoring
      tags: [monitoring]

  post_tasks:
    - name: Verify deployment
      uri:
        url: "https://{{ ansible_host }}/health"
        validate_certs: yes
      register: health_check
      failed_when: health_check.status != 200

    - name: Notify successful deployment
      debug:
        msg: "✅ Deployment successful! Visit https://{{ ansible_host }}"
```

**`ansible/roles/sentinel/tasks/main.yml`:**
```yaml
---
- name: Create application directory
  file:
    path: "{{ app_dir }}"
    state: directory
    owner: "{{ app_user }}"
    group: "{{ app_user }}"
    mode: '0755'

- name: Clone repository
  git:
    repo: "{{ git_repo }}"
    dest: "{{ app_dir }}"
    version: "{{ git_branch }}"
    force: yes
  become_user: "{{ app_user }}"

- name: Copy environment file
  template:
    src: env.j2
    dest: "{{ app_dir }}/.env"
    owner: "{{ app_user }}"
    group: "{{ app_user }}"
    mode: '0600'

- name: Install Python dependencies
  pip:
    requirements: "{{ app_dir }}/requirements.txt"
    virtualenv: "{{ app_dir }}/.venv"
    virtualenv_python: python3.10
  become_user: "{{ app_user }}"

- name: Run database migrations
  command: "{{ app_dir }}/.venv/bin/alembic upgrade head"
  args:
    chdir: "{{ app_dir }}"
  become_user: "{{ app_user }}"

- name: Start Docker services
  command: "./scripts/start-{{ item }}.sh"
  args:
    chdir: "{{ app_dir }}"
  become_user: "{{ app_user }}"
  loop:
    - signoz
    - superset

- name: Wait for services to be ready
  wait_for:
    host: localhost
    port: "{{ item }}"
    delay: 5
    timeout: 300
  loop:
    - 3301  # SigNoz
    - 8088  # Superset
```

---

## Deployment Process

### Manual Trigger

```bash
# Navigate to GitHub Actions
# https://github.com/nctroy/sentinel/actions

# Select "Deploy to Production" workflow
# Click "Run workflow"
# Select branch: main
# Click "Run workflow"
```

### Automated Trigger

```bash
# Merge to main automatically triggers deployment
git checkout main
git merge develop
git push origin main

# GitHub Actions will:
# 1. Run CI pipeline
# 2. If all tests pass, deploy to staging
# 3. Wait for manual approval
# 4. Deploy to production
```

---

## Monitoring & Alerts

### Pipeline Metrics

**Track in SigNoz:**
- Build duration
- Test pass/fail rates
- Deployment frequency
- Mean time to recovery (MTTR)

**Alerts:**
- Pipeline failure → Slack notification
- Deployment success → Slack notification
- Security scan findings → GitHub Issue
- Coverage drop → PR comment

### GitHub Actions Status Badge

Add to README.md:
```markdown
![CI Pipeline](https://github.com/nctroy/sentinel/workflows/CI/badge.svg)
![Deployment](https://github.com/nctroy/sentinel/workflows/Deploy/badge.svg)
```

---

## Secrets Management

### Required Secrets

**GitHub Repository Secrets:**

| Secret Name | Purpose | Where to Get |
|-------------|---------|--------------|
| `ANTHROPIC_API_KEY` | Claude API access | Anthropic Console |
| `HOSTINGER_API_KEY` | VPS provisioning | Hostinger Dashboard |
| `GITHUB_TOKEN` | Package registry | Auto-provided by GitHub |
| `DATABASE_PASSWORD` | PostgreSQL password | Generate secure password |
| `SLACK_WEBHOOK` | Deployment notifications | Slack App settings |

**Adding Secrets:**
1. Navigate to: `https://github.com/nctroy/sentinel/settings/secrets/actions`
2. Click "New repository secret"
3. Enter name and value
4. Click "Add secret"

### Secret Rotation

**Quarterly Rotation:**
```bash
# 1. Generate new secret
NEW_KEY=$(openssl rand -base64 32)

# 2. Update in GitHub Secrets
# (via UI)

# 3. Update in VPS .env
ssh sentinel@vps "sed -i 's/OLD_KEY/NEW_KEY/g' /home/sentinel/sentinel/.env"

# 4. Restart application
ssh sentinel@vps "sudo systemctl restart sentinel"

# 5. Verify
curl https://sentinel.yourdomain.com/health
```

---

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Terraform Documentation](https://www.terraform.io/docs)
- [Ansible Documentation](https://docs.ansible.com/)
- [Docker Documentation](https://docs.docker.com/)

---

**Document Version:** 1.0
**Status:** Planned (Pending Implementation)
**Next Review:** 2026-03-27
**Owner:** Troy Shields
