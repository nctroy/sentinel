# Security Integration Plan

## Goal
Integrate ELLint (ESLint), OWASP ZAP, SonarQube, and Snyk into Sentinel for a unified security posture dashboard.

## Strategy
1.  **Standardization (SARIF):** Adopt SARIF (Static Analysis Results Interchange Format) as the canonical data format.
2.  **Aggregation Agent:** Develop a `SecurityAggregatorAgent` to ingest and normalize data.
3.  **Unified Dashboard:** Visualizing security metrics within the Sentinel Command Center.

## Phase 1: Standardization & Schema
- [x] **Define Unified Schema:** Create a Python Pydantic model `SecurityVulnerability` that maps fields from different tools to a common structure.
- [x] **Configure ESLint:** Update `.eslintrc.json` or CI pipeline to output results in SARIF format.
- [ ] **Configure OWASP ZAP:** Ensure ZAP scans export to JSON/SARIF.

## Phase 2: Ingestion Agents
- [x] **Create `SecurityAggregatorAgent`:**
    - Located in `src/agents/security_aggregator.py`.
    - **Capability:** `ingest_sarif(file_path)` - Parses standard SARIF files.
- [ ] **Capability:** `fetch_snyk_issues(project_id)` - Connects to Snyk API.
- [ ] **Capability:** `fetch_sonarqube_metrics(project_key)` - Connects to SonarQube API.
- [x] **Database Updates:**
    - Add `security_vulnerabilities` table to PostgreSQL schema.

## Phase 3: Dashboard Integration
- [x] **Backend API:**
    - `GET /security/summary` - Returns counts by severity and tool.
    - `GET /security/vulnerabilities` - Returns paginated list of issues.
- [x] **Frontend (Next.js):**
    - Create `SecurityDashboard` page.
    - **Components:**
        - `SeverityChart` (Pie/Bar chart of issues).
        - `VulnerabilityTable` (Sortable list of issues).
        - `ToolStatus` (Connection status for Snyk/Sonar/etc).

## Phase 4: Automation (Current Focus)
- [x] **CI/CD Integration Script:** Create `scripts/ci-security-scan.sh` to run linters and trigger ingestion via API (`POST /orchestrate`).
- [x] **Alerting Logic:** Update `SecurityAggregatorAgent` to flag Critical issues as blocking bottlenecks with high impact scores.

## Backlog / Future Enhancements
- [ ] **Dashboard Charts:** Add trend lines for vulnerability counts over time.
- [ ] **Snyk Integration:** Add API client to fetch issues directly from Snyk.
- [ ] **ZAP Integration:** Parse OWASP ZAP JSON reports.
- [ ] **Slack/Discord Webhooks:** Push notifications for critical alerts.
