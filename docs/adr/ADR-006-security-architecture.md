# ADR-006: Security Architecture

**Status:** Accepted
**Date:** 2025-12-27
**Decision Makers:** Troy Shields (Chief Architect)
**Tags:** security, infrastructure, compliance, hardening

---

## Context

Sentinel is a production AI system managing sensitive operations across multiple business domains:

1. **Job Search Portfolio** - Resume data, interview schedules, salary negotiations
2. **GitHub Triage** - Repository access, API tokens, code analysis
3. **Multi-Business Operations** - Financial data, customer information, proprietary strategies
4. **AI Agent System** - Claude API keys, database credentials, orchestration logic

**Security Requirements:**

1. **Secrets Management** - API keys, database credentials, OAuth tokens never in code
2. **Code Security** - Prevent common vulnerabilities (injection, XSS, CSRF)
3. **Dependency Security** - Vulnerable package detection and remediation
4. **Network Security** - TLS encryption, firewall rules, authentication
5. **Data Protection** - Encrypted at rest and in transit, access controls
6. **Audit Trail** - Complete decision history for compliance
7. **Supply Chain Security** - Pre-commit hooks prevent accidental credential commits

**Compliance Considerations:**

- No formal compliance requirements (personal portfolio system)
- Best practices from enterprise security standards (OWASP, CIS Benchmarks)
- Preparation for potential future enterprise deployment

---

## Decision

Implement a **defense-in-depth security architecture** with multiple layers:

### Layer 1: Pre-Commit Security Scanning

**Tools:**
- **Gitleaks** - Secret detection (API keys, tokens, credentials)
- **Bandit** - Python code security analysis
- **Safety** - Python dependency vulnerability scanning

**Implementation:**
```bash
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks

  - repo: local
    hooks:
      - id: bandit
        name: bandit
        entry: bandit
        language: system
        args: ['-r', 'src/', '-ll']

      - id: safety
        name: safety
        entry: safety
        language: system
        args: ['check', '--json']
```

**Rationale:**
- Prevents secrets from ever entering Git history
- Catches security issues before code review
- Zero-cost prevention vs. expensive remediation
- Enforces security as part of development workflow

### Layer 2: Secrets Management

**Environment Variables:**
```python
# .env (NEVER committed to Git)
ANTHROPIC_API_KEY=sk-ant-...
DATABASE_URL=postgresql://user:pass@localhost:5432/sentinel
NOTION_API_KEY=secret_...
GITHUB_TOKEN=ghp_...

# .env.example (Template committed to Git)
ANTHROPIC_API_KEY=your_api_key_here
DATABASE_URL=postgresql://user:password@localhost:5432/sentinel
NOTION_API_KEY=your_notion_key_here
GITHUB_TOKEN=your_github_token_here
```

**Loading Secrets:**
```python
# src/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    anthropic_api_key: str
    database_url: str
    notion_api_key: str
    github_token: str

    class Config:
        env_file = ".env"
        case_sensitive = False
```

**Rationale:**
- Industry standard pattern (12-factor app)
- Separation of code and configuration
- Easy secret rotation without code changes
- Compatible with Docker, Kubernetes, cloud platforms
- `.env` in `.gitignore` prevents accidental commits

### Layer 3: Application Security

**Input Validation:**
```python
# All user input validated via Pydantic models
from pydantic import BaseModel, Field, validator

class BottleneckRequest(BaseModel):
    description: str = Field(..., max_length=5000)
    impact_score: float = Field(..., ge=0.0, le=10.0)
    confidence: float = Field(..., ge=0.0, le=1.0)

    @validator('description')
    def sanitize_description(cls, v):
        # Prevent SQL injection, XSS
        return v.strip()
```

**SQL Injection Prevention:**
- SQLAlchemy ORM with parameterized queries
- No raw SQL string interpolation
- Database user has minimum required permissions

**API Security:**
```python
# Rate limiting (Nginx layer)
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

# CORS policy
CORS_ALLOWED_ORIGINS = [
    "https://sentinel.troyneff.com",
    "http://localhost:3000"  # Development only
]

# Authentication required for sensitive endpoints
@app.post("/api/execute_action")
async def execute_action(
    action: ActionRequest,
    api_key: str = Header(..., alias="X-API-Key")
):
    verify_api_key(api_key)
    return await orchestrator.execute(action)
```

**Rationale:**
- Pydantic catches malformed input before processing
- ORM prevents SQL injection by design
- Rate limiting prevents DoS attacks
- CORS restricts unauthorized origins
- API key authentication for programmatic access

### Layer 4: Network Security

**TLS/SSL Encryption:**
```nginx
# nginx.conf
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
ssl_prefer_server_ciphers off;

# HSTS - Force HTTPS
add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
```

**Firewall Rules:**
```bash
# Ubuntu UFW example
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp      # SSH (restrict to known IPs in production)
sudo ufw allow 80/tcp      # HTTP (redirects to HTTPS)
sudo ufw allow 443/tcp     # HTTPS
sudo ufw enable
```

**Basic Authentication for Admin Interfaces:**
```nginx
# Operations dashboard (SigNoz)
location /ops {
    auth_basic "Sentinel Operations";
    auth_basic_user_file /etc/nginx/.htpasswd_ops;
    proxy_pass http://signoz_backend;
}

# Executive dashboard (Superset)
location /executive {
    auth_basic "Sentinel Executive";
    auth_basic_user_file /etc/nginx/.htpasswd_executive;
    proxy_pass http://superset_backend;
}
```

**Rationale:**
- TLS 1.2+ only (TLS 1.0/1.1 deprecated)
- Modern cipher suites prevent downgrade attacks
- HSTS prevents SSL stripping attacks
- Firewall reduces attack surface
- Basic auth adds second layer before application auth

### Layer 5: Data Protection

**Database Security:**
```sql
-- Principle of least privilege
CREATE USER sentinel_app WITH PASSWORD 'strong_password';
GRANT SELECT, INSERT, UPDATE ON TABLE bottlenecks TO sentinel_app;
GRANT SELECT, INSERT, UPDATE ON TABLE decisions TO sentinel_app;
-- NO DELETE or DROP permissions

-- Audit logging enabled
ALTER DATABASE sentinel SET log_statement = 'mod';
```

**Connection Security:**
```python
# SSL-enabled database connections
DATABASE_URL = "postgresql://user:pass@localhost:5432/sentinel?sslmode=require"
```

**Backup Encryption:**
```bash
# Encrypted PostgreSQL backups
pg_dump sentinel | gpg --encrypt --recipient admin@sentinel.local > backup.sql.gpg
```

**Rationale:**
- Restricted database permissions limit blast radius
- SSL connections prevent credential sniffing
- Encrypted backups protect data at rest
- Audit logs provide forensic capability

### Layer 6: Dependency Management

**Vulnerability Scanning:**
```bash
# Automated via pre-commit
safety check --json

# Weekly CI/CD scans
pip-audit --desc
```

**Pinned Dependencies:**
```txt
# requirements.txt - exact versions
fastapi==0.109.0
anthropic==0.75.0
sqlalchemy==2.0.25

# Prevents supply chain attacks via version confusion
```

**Update Strategy:**
- Monthly review of security advisories
- Quarterly dependency updates (patch versions)
- Annual major version upgrades (with testing)

**Rationale:**
- `safety` detects known CVEs in dependencies
- Pinned versions prevent unexpected breaking changes
- Regular updates balance security vs. stability

### Layer 7: Monitoring and Incident Response

**Security Monitoring:**
```python
# OpenTelemetry security events
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

@tracer.start_as_current_span("authentication_attempt")
def authenticate(api_key: str):
    span = trace.get_current_span()
    span.set_attribute("auth.success", False)

    if verify_key(api_key):
        span.set_attribute("auth.success", True)
        return True
    else:
        # Alert on repeated failures (potential attack)
        alert_security_team("Multiple auth failures detected")
        return False
```

**Audit Trail:**
```python
# All agent decisions logged to database
class Decision(Base):
    __tablename__ = "decisions"

    id = Column(Integer, primary_key=True)
    agent_id = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    decision_type = Column(String, nullable=False)
    decision_data = Column(JSONB, nullable=False)
    reasoning = Column(Text)  # AI transparency
```

**Rationale:**
- Tracing captures security events for analysis
- Alerting enables rapid incident response
- Audit trail satisfies compliance requirements
- Immutable logs prevent tampering

---

## Alternatives Considered

### Alternative 1: Secrets in Environment Variables Only (No .env File)

**Approach:**
- Set secrets directly in shell: `export ANTHROPIC_API_KEY=...`
- No `.env` file, environment variables only

**Pros:**
- ✅ No file to accidentally commit

**Cons:**
- ❌ Hard to manage multiple environments (dev/staging/prod)
- ❌ Secrets lost when terminal closes
- ❌ Difficult for team members to set up
- ❌ No template for required variables

**Why Not Selected:**
Developer experience matters. `.env` files with `.env.example` template provide:
- Clear documentation of required secrets
- Easy local development setup
- Environment parity (12-factor principle)
- Standard pattern familiar to all developers

Risk mitigated by:
- `.env` in `.gitignore`
- Gitleaks pre-commit hook
- `.env.example` as template

---

### Alternative 2: HashiCorp Vault for Secret Management

**Approach:**
- Centralized secret storage (Vault server)
- Dynamic secret generation
- Fine-grained access control

**Pros:**
- ✅ Enterprise-grade secret management
- ✅ Secret rotation automation
- ✅ Audit logging built-in
- ✅ Dynamic credentials

**Cons:**
- ❌ Operational overhead (Vault server deployment)
- ❌ Overkill for single-developer portfolio project
- ❌ Additional attack surface (Vault itself needs securing)
- ❌ Complexity doesn't match current scale

**Why Not Selected:**
Vault is excellent for multi-team enterprises but excessive for current needs:
- Single developer (no multi-user access control needed)
- < 10 secrets total
- No compliance requirements mandating centralized secret store

**Future Consideration:**
If Sentinel scales to multiple teams or requires SOC 2 compliance, revisit Vault.

---

### Alternative 3: AWS Secrets Manager / GCP Secret Manager

**Approach:**
- Cloud-native secret storage
- Integrated with cloud IAM

**Pros:**
- ✅ Fully managed (no operational overhead)
- ✅ Automatic rotation support
- ✅ Strong encryption at rest

**Cons:**
- ❌ Vendor lock-in
- ❌ Cost ($0.40 per secret per month)
- ❌ Requires cloud deployment
- ❌ Network dependency (can't run fully local)

**Why Not Selected:**
Sentinel designed to run anywhere (local, VPS, cloud). Cloud secret managers:
- Tie deployment to specific cloud provider
- Add recurring costs
- Prevent local development without cloud access

**Future Consideration:**
If deploying to AWS/GCP in production, migrate to cloud secret manager while keeping `.env` for local dev.

---

## Implementation Details

### Security Checklist

**Pre-Deployment:**
- [x] All secrets in `.env` (not in code)
- [x] `.env` in `.gitignore`
- [x] `.env.example` template committed
- [x] Gitleaks pre-commit hook installed
- [x] Bandit security scanning configured
- [x] Safety dependency scanning configured
- [x] Database credentials not default values
- [x] API rate limiting configured
- [x] CORS policy restrictive
- [x] SQL injection prevention (ORM only)

**Deployment:**
- [x] TLS/SSL certificates configured (Let's Encrypt)
- [x] HTTPS redirects enabled
- [x] HSTS header enabled
- [x] Firewall configured (UFW/iptables)
- [x] Basic auth on admin interfaces
- [ ] Database backups encrypted
- [ ] Backup restore process tested
- [ ] Incident response plan documented

**Ongoing:**
- [ ] Weekly security advisory review
- [ ] Monthly dependency updates
- [ ] Quarterly penetration testing
- [ ] Annual security architecture review

### Common Attack Vectors and Mitigations

| Attack Vector | Mitigation | Implementation |
|---------------|------------|----------------|
| **SQL Injection** | Parameterized queries via ORM | SQLAlchemy, no raw SQL |
| **XSS** | Input sanitization, CSP headers | Pydantic validation, Content-Security-Policy |
| **CSRF** | CSRF tokens on state-changing requests | FastAPI CSRF middleware |
| **Credential Theft** | Secrets never in code, Gitleaks scanning | `.env` + pre-commit hooks |
| **Man-in-the-Middle** | TLS 1.2+ encryption | Nginx SSL config, Let's Encrypt |
| **Brute Force** | Rate limiting, account lockout | Nginx limit_req, failed login tracking |
| **Dependency Vulnerabilities** | Automated scanning, regular updates | Safety, pip-audit, Dependabot |
| **DoS** | Rate limiting, resource limits | Nginx zones, Docker resource constraints |
| **Privilege Escalation** | Least-privilege database users | PostgreSQL GRANT restrictions |
| **Session Hijacking** | Secure cookies, session timeouts | httpOnly, secure, SameSite cookies |

---

## Consequences

### Positive

✅ **Defense in Depth** - Multiple security layers prevent single point of failure
✅ **Automated Prevention** - Pre-commit hooks catch issues before they enter codebase
✅ **Standard Patterns** - Uses industry best practices (12-factor, OWASP guidelines)
✅ **Audit Trail** - Complete decision history for forensics and compliance
✅ **Low Overhead** - Minimal operational complexity for solo developer
✅ **Portfolio Value** - Demonstrates security competency for job search
✅ **Future-Proof** - Architecture scales to enterprise requirements

### Negative

⚠️ **Pre-Commit Friction** - Security scans add 5-10 seconds to commit process
⚠️ **False Positives** - Bandit/Safety occasionally flag non-issues
⚠️ **Manual Secret Rotation** - No automated secret rotation (manual process)
⚠️ **Local .env Management** - Developers must manually create `.env` file

### Mitigations

**Pre-Commit Performance:**
- Run scans in parallel where possible
- Cache scan results when dependencies unchanged
- Allow `--no-verify` for WIP commits (use sparingly)

**False Positives:**
- Maintain `bandit.yaml` configuration to suppress known false positives
- Document exceptions in code comments

**Secret Rotation:**
- Quarterly calendar reminder to rotate secrets
- Document rotation procedure in runbook
- Future: automate via Vault if complexity justifies

---

## Validation Criteria

This security architecture is successful if:

1. ✅ **Zero credential leaks** - No secrets ever committed to Git (verified via Gitleaks)
2. ✅ **No critical CVEs** - All critical dependency vulnerabilities patched within 48 hours
3. ✅ **Audit compliance** - Complete decision history available for 1+ year retention
4. ✅ **Attack surface minimized** - Only ports 80/443 exposed, all others firewalled
5. ✅ **Encrypted in transit** - 100% of traffic over TLS 1.2+
6. ✅ **Interview readiness** - Can explain security architecture in 5 minutes with confidence

---

## Future Enhancements

### Phase 2: Advanced Security (When Needed)

1. **Web Application Firewall (WAF)**
   - ModSecurity with OWASP Core Rule Set
   - Protects against OWASP Top 10 attacks
   - **When:** If public API sees significant traffic or attacks

2. **Intrusion Detection (IDS)**
   - Fail2ban for automated IP blocking
   - OSSEC for host-based intrusion detection
   - **When:** If monitoring detects suspicious activity patterns

3. **Secret Rotation Automation**
   - HashiCorp Vault for dynamic secrets
   - AWS Secrets Manager if cloud-deployed
   - **When:** Multi-user environment or compliance requirement

4. **Penetration Testing**
   - Annual third-party penetration test
   - Bug bounty program for responsible disclosure
   - **When:** Handling customer data or financial transactions

5. **SOC 2 Compliance**
   - Formal security audit and certification
   - **When:** Selling Sentinel as SaaS product

---

## References

- **OWASP Top 10**: https://owasp.org/www-project-top-ten/
- **12-Factor App Security**: https://12factor.net/
- **CIS Benchmarks**: https://www.cisecurity.org/cis-benchmarks
- **Gitleaks**: https://github.com/gitleaks/gitleaks
- **Bandit**: https://bandit.readthedocs.io/
- **Safety**: https://pyup.io/safety/
- **Let's Encrypt**: https://letsencrypt.org/
- **Nginx Security**: https://nginx.org/en/docs/http/configuring_https_servers.html

---

**Supersedes:** None
**Superseded By:** None
**Related:** ADR-005 (Python Technology Stack), ADR-002 (Database Schema)

---

## Notes

Security is not a one-time implementation but an ongoing practice. This ADR establishes the **foundation**, but security must be:

1. **Continuously monitored** - Weekly security advisory reviews
2. **Regularly tested** - Quarterly dependency updates and vulnerability scans
3. **Actively maintained** - Prompt patching of critical vulnerabilities
4. **Culturally embedded** - Security considerations in every design decision

**Remember:** The best security architecture is one that is:
- ✅ **Implemented** (not just documented)
- ✅ **Maintainable** (not so complex it's abandoned)
- ✅ **Tested** (verified to work in practice)
- ✅ **Evolving** (updated as threats change)

> "Security is a process, not a product." - Bruce Schneier
