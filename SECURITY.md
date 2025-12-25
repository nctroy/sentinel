# Security Policy

## Overview

Sentinel takes security seriously. This document outlines our security practices, vulnerability reporting process, and security scanning setup.

## Security Scanning

This project uses multiple automated security scanning tools:

### Secret Detection
- **Gitleaks**: Scans for hardcoded secrets and credentials
- **TruffleHog**: Detects secrets in git history
- **Pre-commit hooks**: Prevents committing sensitive files

### Code Security Analysis
- **CodeQL**: GitHub's semantic code analysis
- **Bandit**: Python security linter
- **Semgrep**: Static analysis security testing (SAST)

### Dependency Scanning
- **Safety**: Python dependency vulnerability scanner
- **Dependabot**: Automated dependency updates (GitHub)

### Container Security
- **Trivy**: Docker image vulnerability scanner
- **Hadolint**: Dockerfile linter

## Protected Secrets

The following secrets must NEVER be committed to the repository:

- **API Keys**: Anthropic API keys, Notion integration tokens
- **Database Credentials**: PostgreSQL passwords, connection strings
- **Environment Files**: `.env` files containing real credentials
- **Private Keys**: SSH keys, GPG keys, service account keys

## Environment Variables

All sensitive configuration should be stored in `.env` files:

```bash
# Required environment variables
DATABASE_URL=postgresql://user:password@host:port/database
NOTION_API_KEY=ntn_xxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx
```

**Never commit `.env` files to version control.**

## Security Best Practices

1. **Use `.env.example` for templates**: Commit example files with placeholder values
2. **Rotate credentials regularly**: Update API keys and passwords periodically
3. **Principle of least privilege**: Grant minimal necessary permissions
4. **Enable GitHub security features**:
   - Secret scanning
   - Dependabot alerts
   - Code scanning with CodeQL
5. **Review security reports**: Check GitHub Security tab regularly

## Reporting Vulnerabilities

If you discover a security vulnerability, please:

1. **Do NOT open a public issue**
2. Email: [your-security-email]
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will respond within 48 hours and work with you to address the issue.

## Security Scanning Reports

Security scan reports are generated automatically on:
- Every push to `main` or `develop`
- Every pull request
- Weekly schedule (Sundays and Mondays)

Reports are available in:
- GitHub Actions artifacts
- GitHub Security tab (for CodeQL)
- Pull request comments (for critical findings)

## Incident Response

In case of a security incident:

1. **Immediately rotate compromised credentials**
2. **Assess impact**: Determine what was exposed
3. **Notify affected parties** if user data was compromised
4. **Document the incident**: Create timeline and lessons learned
5. **Implement fixes**: Update code and security controls

## Compliance

This project follows:
- OWASP Top 10 security best practices
- GitHub Security Best Practices
- Python security guidelines (PEP 594, Bandit rules)

## Security Checklist

- [x] `.env` files excluded from git
- [x] Secret scanning enabled (Gitleaks, TruffleHog)
- [x] Pre-commit hooks configured
- [x] CodeQL analysis enabled
- [x] Dependency scanning enabled
- [x] Docker image scanning enabled
- [ ] API key rotation policy established
- [ ] Security contact email configured
- [ ] Incident response plan documented

## Updates

This security policy is reviewed quarterly and updated as needed.

Last updated: 2024-12-25
