# Deployment Security Checklist

This document provides security guidelines for deploying Sentinel in different environments.

## Development Environment

### Network Configuration
- ✅ Use `SERVER_HOST=127.0.0.1` (localhost only)
- ✅ Keep `DEBUG=False` even in development
- ✅ Use unique, strong database passwords
- ✅ Never commit `.env` files

### Secret Management
```bash
# Good: Use .env file (gitignored)
DATABASE_URL=postgresql://sentinel:strong_password@localhost:5433/sentinel
NOTION_API_KEY=ntn_your_key_here
ANTHROPIC_API_KEY=sk-ant-your_key_here

# Bad: Hardcoded in code
db_password = "mysecret123"  # NEVER DO THIS
```

### Pre-commit Hooks
```bash
# Install hooks to prevent accidental commits
pre-commit install

# Test hooks
pre-commit run --all-files
```

---

## Production Environment

### 🔴 Critical Security Requirements

#### 1. Network Isolation
```bash
# Option A: Bind to specific internal IP
SERVER_HOST=10.0.1.100  # Internal network only

# Option B: Use reverse proxy (recommended)
SERVER_HOST=127.0.0.1  # Backend only accessible via proxy
```

#### 2. Firewall Rules
```bash
# Allow only necessary ports
# PostgreSQL: 5432 (from app server only)
# MCP Server: 8000 (from reverse proxy only)
# HTTPS: 443 (public)

# AWS Security Group Example:
# Inbound: 443 from 0.0.0.0/0
# Inbound: 8000 from <app-security-group>
# Inbound: 5432 from <app-security-group>
```

#### 3. Environment Variables
```bash
# Use secrets manager (AWS Secrets Manager, HashiCorp Vault, etc.)
# Never store production secrets in .env files on servers

# AWS Systems Manager Parameter Store example:
aws ssm put-parameter \
  --name "/sentinel/prod/anthropic-api-key" \
  --value "sk-ant-..." \
  --type "SecureString"

# Retrieve in application:
import boto3
ssm = boto3.client('ssm')
api_key = ssm.get_parameter(Name='/sentinel/prod/anthropic-api-key', WithDecryption=True)
```

#### 4. Database Security
```bash
# PostgreSQL Production Settings
# 1. Use SSL/TLS connections
DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require

# 2. Restrict network access
# Edit pg_hba.conf:
hostssl  sentinel  sentinel  10.0.0.0/24  md5

# 3. Use strong passwords (20+ characters)
# 4. Enable audit logging
# 5. Regular backups with encryption
```

#### 5. API Key Rotation
```bash
# Implement key rotation policy:
# - Anthropic API keys: Rotate every 90 days
# - Notion integration tokens: Rotate every 90 days
# - Database passwords: Rotate every 180 days

# Keep old keys active for 24 hours during rotation
# Update all services before deactivating old keys
```

---

## Docker Deployment

### Secure Docker Configuration

```dockerfile
# Use specific version tags, not 'latest'
FROM python:3.10.13-slim

# Run as non-root user
RUN useradd -m -u 1000 sentinel
USER sentinel

# Don't include secrets in image
# Use Docker secrets or environment variables
```

### Docker Secrets
```bash
# Create secrets
echo "sk-ant-your_key" | docker secret create anthropic_api_key -
echo "ntn_your_key" | docker secret create notion_api_key -

# Use in docker-compose.yml
services:
  sentinel:
    secrets:
      - anthropic_api_key
      - notion_api_key
    environment:
      ANTHROPIC_API_KEY_FILE: /run/secrets/anthropic_api_key
```

### Docker Compose Production
```yaml
version: '3.8'
services:
  sentinel:
    image: sentinel:1.0.0
    restart: unless-stopped
    networks:
      - internal
    environment:
      SERVER_HOST: "0.0.0.0"  # OK in container network
      DATABASE_URL: "postgresql://sentinel:${DB_PASSWORD}@db:5432/sentinel"
    secrets:
      - anthropic_api_key
      - notion_api_key

  db:
    image: postgres:15
    restart: unless-stopped
    networks:
      - internal
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    networks:
      - internal
      - external
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro

networks:
  internal:
    internal: true
  external:

secrets:
  anthropic_api_key:
    external: true
  notion_api_key:
    external: true
  db_password:
    external: true

volumes:
  postgres_data:
```

---

## AWS Deployment

### ECS/Fargate Security

```json
{
  "taskDefinition": {
    "family": "sentinel",
    "networkMode": "awsvpc",
    "requiresCompatibilities": ["FARGATE"],
    "containerDefinitions": [
      {
        "name": "sentinel",
        "image": "sentinel:1.0.0",
        "secrets": [
          {
            "name": "ANTHROPIC_API_KEY",
            "valueFrom": "arn:aws:secretsmanager:region:account:secret:sentinel/anthropic"
          },
          {
            "name": "NOTION_API_KEY",
            "valueFrom": "arn:aws:secretsmanager:region:account:secret:sentinel/notion"
          }
        ],
        "logConfiguration": {
          "logDriver": "awslogs",
          "options": {
            "awslogs-group": "/ecs/sentinel",
            "awslogs-region": "us-east-1"
          }
        }
      }
    ]
  }
}
```

### IAM Permissions (Least Privilege)
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "secretsmanager:GetSecretValue"
      ],
      "Resource": [
        "arn:aws:secretsmanager:region:account:secret:sentinel/*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "rds:DescribeDBInstances"
      ],
      "Resource": "arn:aws:rds:region:account:db:sentinel-db"
    }
  ]
}
```

---

## Monitoring & Incident Response

### Security Monitoring
```bash
# Log all authentication attempts
# Monitor for:
# - Failed login attempts (>5 in 5 minutes)
# - Unusual API usage patterns
# - Database connection errors
# - Unauthorized access attempts

# CloudWatch Alarms example:
aws cloudwatch put-metric-alarm \
  --alarm-name sentinel-failed-auth \
  --metric-name FailedAuthentication \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1 \
  --period 300
```

### Incident Response Plan
1. **Detection**: Automated alerts via CloudWatch/PagerDuty
2. **Containment**: Rotate compromised credentials immediately
3. **Investigation**: Review audit logs, access patterns
4. **Recovery**: Deploy clean configuration, update secrets
5. **Post-mortem**: Document incident, update procedures

---

## Pre-Deployment Checklist

### Before Going Live

- [ ] All secrets stored in secrets manager (not .env files)
- [ ] Database uses SSL/TLS connections
- [ ] Firewall rules configured (whitelist only)
- [ ] Server binds to internal IP or uses reverse proxy
- [ ] API rate limiting enabled
- [ ] Logging and monitoring configured
- [ ] Backup and recovery tested
- [ ] Incident response plan documented
- [ ] Security scanning passed (no HIGH/CRITICAL issues)
- [ ] Dependencies updated and scanned
- [ ] Pre-commit hooks installed
- [ ] CORS policies configured
- [ ] HTTPS enforced (no HTTP)
- [ ] Security headers configured (HSTS, CSP, etc.)

### Security Testing
```bash
# Before deployment, run full security scan:
pre-commit run --all-files
gitleaks detect
bandit -r src/
safety check
docker scan sentinel:latest  # If using Docker

# Verify no secrets in environment
env | grep -i "key\|token\|password"  # Should show nothing

# Test with security headers
curl -I https://your-domain.com
# Should include:
# Strict-Transport-Security
# X-Content-Type-Options
# X-Frame-Options
```

---

## Compliance & Auditing

### Audit Logging
```python
# Log all security-relevant events
import logging

security_logger = logging.getLogger('sentinel.security')

# Log authentication
security_logger.info(f"API key authentication: {key_id} from {ip_address}")

# Log data access
security_logger.info(f"Database query: {user} accessed {table}")

# Log configuration changes
security_logger.warning(f"Config changed: {setting} by {user}")
```

### Regular Security Reviews
- **Daily**: Monitor security alerts and logs
- **Weekly**: Review access logs, failed authentications
- **Monthly**: Dependency vulnerability scan, update packages
- **Quarterly**: Full security audit, penetration testing
- **Annually**: Security policy review, key rotation verification

---

## Emergency Procedures

### Compromised API Key
```bash
# 1. Immediately deactivate old key (Anthropic/Notion dashboard)
# 2. Generate new key
# 3. Update secrets manager
# 4. Restart application with new key
# 5. Review audit logs for unauthorized usage
# 6. Report to security team

# Automation script:
./scripts/rotate-api-key.sh --service anthropic --environment prod
```

### Database Breach
```bash
# 1. Isolate database (security group rules)
# 2. Take snapshot
# 3. Review access logs
# 4. Rotate database credentials
# 5. Restore from clean backup if compromised
# 6. Notify affected parties
```

---

## Security Contacts

- **Security Team**: security@yourcompany.com
- **On-Call**: PagerDuty rotation
- **Anthropic Support**: support@anthropic.com
- **Notion Security**: security@notion.so

---

**Last Updated**: 2025-12-25
**Next Review**: 2026-03-25
**Owner**: Security Team
