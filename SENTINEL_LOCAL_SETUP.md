# Sentinel Setup & Deployment Guide

This guide walks you through setting up Sentinel on **your local machine** (not on the remote server).

## What You Have

You've been given:
1. **sentinel-project.zip** — Complete project structure with all code
2. **This guide** — Step-by-step instructions

## Step 1: Extract & Initialize

### On Your Local Machine:

```bash
# Extract the zip file
unzip sentinel-project.zip
cd sentinel

# Initialize git (if you want version control)
git init
git add .
git commit -m "Initial commit: Sentinel scaffold"
```

## Step 2: Create Private GitHub Repository

### Create Repo on GitHub.com:

1. Go to **https://github.com/new**
2. **Repository name**: `sentinel`
3. **Description**: "Multi-agent orchestration system for autonomous project management"
4. **Privacy**: Select **Private**
5. **Initialize this repository**: Leave unchecked (you already have code)
6. Click **Create repository**

### Connect Local to GitHub:

After creating the repo, GitHub will show you commands. Run these:

```bash
git remote add origin https://github.com/nctroy/sentinel.git
git branch -M main
git push -u origin main
```

When prompted:
- **Username**: `your-github-username`
- **Password**: Use your GitHub token: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

(Or configure SSH if you prefer)

---

## Step 3: Python & Dependencies

### Create Virtual Environment:

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### Install Requirements:

```bash
pip install -r requirements.txt
```

---

## Step 4: Set Up Environment Variables

### Copy & Edit .env:

```bash
# Copy the example
cp .env.example .env

# Edit .env with your values
nano .env
```

Fill in:

```bash
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/sentinel

# Notion Configuration (YOUR WORKSPACE)
NOTION_API_KEY=ntn_xxxxxxxxxxxxxxxxxxxxx  # Get this from Notion
NOTION_WORKSPACE_ID=38d5edab-553a-4fe3-9a5a-fe188a4c210c
NOTION_WORKSPACE_NAME=superonyx

# Claude/Anthropic
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxx

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=False
LOG_LEVEL=INFO
```

---

## Step 5: Set Up PostgreSQL

### Option A: Local PostgreSQL (Easiest for Development)

**macOS (with Homebrew):**
```bash
brew install postgresql
brew services start postgresql
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install postgresql postgresql-contrib
sudo service postgresql start
```

**Windows:**
Download and install from https://www.postgresql.org/download/windows/

### Create Database:

Once PostgreSQL is running:

```bash
# Create database and user
psql postgres

# In the psql prompt:
CREATE USER sentinel WITH PASSWORD 'your-secure-password';
CREATE DATABASE sentinel OWNER sentinel;
GRANT ALL PRIVILEGES ON DATABASE sentinel TO sentinel;
\q
```

Update your `.env`:
```bash
DATABASE_URL=postgresql://sentinel:your-secure-password@localhost:5432/sentinel
```

### Option B: PostgreSQL via Docker

If you prefer Docker:

```bash
docker run --name sentinel-postgres \
  -e POSTGRES_USER=sentinel \
  -e POSTGRES_PASSWORD=your-password \
  -e POSTGRES_DB=sentinel \
  -p 5432:5432 \
  -d postgres:15
```

---

## Step 6: Set Up Notion Integration

### Create Notion Integration:

1. Go to **https://www.notion.so/my-integrations**
2. Click **New integration**
3. Fill in:
   - **Name**: Sentinel
   - **Description**: Multi-agent orchestration dashboard
4. Under **Capabilities**, check:
   - ✅ Read content
   - ✅ Update content
   - ✅ Insert content
5. Click **Submit**

### Get API Key:

1. On the integration page, find **Internal Integration Token**
2. Click **Show** to reveal the token
3. Copy it (starts with `ntn_`)
4. Add to `.env`: `NOTION_API_KEY=ntn_xxxxxxxxxxxxxxxxxxxxx`

### Share Workspace:

1. In your Notion workspace, click **Share** (top right)
2. Click **Invite**
3. Search for "Sentinel" (your integration)
4. Click to add it
5. Grant **Edit** permissions

---

## Step 7: Get Your Anthropic API Key

1. Go to **https://console.anthropic.com/account/keys**
2. Create a new API key
3. Copy it
4. Add to `.env`: `ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxx`

---

## Step 8: Initialize Database Schema

```bash
# Make sure you're in the project directory with venv activated
python -m src.cli.cli init-db

# You should see: "✓ Database initialized"
```

---

## Step 9: Test the System

### Run First Diagnostic Cycle:

```bash
python -m src.cli.cli run-cycle --mode diagnostic --verbose
```

This will:
1. ✅ Connect to PostgreSQL
2. ✅ Connect to Notion
3. ✅ Run diagnostic (read-only, no actions)
4. ✅ Write results to Notion dashboard

### Check Your Notion Workspace:

After running the diagnostic, go to your Notion workspace. You should see new databases created:
- **Agent Daily Reports**
- **Weekly Priorities**
- **Decision Log**

---

## Step 10: Open in Claude Code (Antigravity IDE)

Now that everything is set up:

1. Open **Claude Code / Antigravity IDE**
2. File → **Open Folder**
3. Navigate to your `sentinel/` directory
4. Click **Open**

You now have:
- ✅ Full codebase in Claude Code
- ✅ All documentation available
- ✅ Database connected
- ✅ Notion integrated
- ✅ Ready to extend

---

## Next: Customizing for Your Projects

Once everything is running, you can:

### 1. Create a Job Search Project Config

Create `config/job-search.json`:

```json
{
  "project": "job-search",
  "description": "Autonomous job search orchestration",
  "sub_agents": [
    {
      "agent_id": "job-research",
      "name": "Research Agent",
      "domain": "job-research",
      "responsibilities": [
        "Identify target companies",
        "Monitor job postings",
        "Validate fit"
      ],
      "autonomy_level": "diagnostic"
    },
    {
      "agent_id": "job-applications",
      "name": "Applications Agent",
      "domain": "job-applications",
      "responsibilities": [
        "Track application status",
        "Schedule follow-ups",
        "Manage interviews"
      ],
      "autonomy_level": "diagnostic"
    },
    {
      "agent_id": "job-preparation",
      "name": "Preparation Agent",
      "domain": "interview-prep",
      "responsibilities": [
        "Identify skill gaps",
        "Recommend preparation",
        "Track progress"
      ],
      "autonomy_level": "diagnostic"
    }
  ],
  "orchestration_rules": {
    "bottleneck_prioritization": "impact-score",
    "autonomy_level": "diagnostic"
  }
}
```

### 2. Initialize the Project

```bash
python -m src.cli.cli init-project --config config/job-search.json
```

### 3. Run Diagnostic

```bash
python -m src.cli.cli run-cycle --mode diagnostic --verbose
```

---

## Troubleshooting

### "DATABASE_URL not set"
- Check `.env` file exists and has `DATABASE_URL`
- Restart your terminal
- Make sure `source venv/bin/activate` was run

### "PostgreSQL connection refused"
- Verify PostgreSQL is running: `psql postgres`
- Check DATABASE_URL format
- Make sure user/password is correct

### "Notion API key invalid"
- Verify API key starts with `ntn_`
- Check it hasn't expired
- Regenerate from https://www.notion.so/my-integrations

### "Module not found"
- Make sure you're in the `sentinel/` directory
- Make sure venv is activated: `source venv/bin/activate`
- Reinstall requirements: `pip install -r requirements.txt`

---

## Quick Commands Reference

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Initialize database
python -m src.cli.cli init-db

# Run diagnostic cycle
python -m src.cli.cli run-cycle --mode diagnostic --verbose

# List agents
python -m src.cli.cli list-agents

# Show agent details
python -m src.cli.cli show-agent --agent-id agent-id

# Run tests
pytest tests/ -v

# Start development server
uvicorn src.mcp_server.sentinel_server:app --reload

# View logs
tail -f logs/sentinel.log
```

---

## Architecture Check-In

Once you have everything running, you've built:

```
Your Local Machine
  ├── Sentinel Code (Python)
  │   ├── FastAPI Server (Backend)
  │   ├── Sub-Agents
  │   └── Orchestrator
  │
  ├── PostgreSQL (Local or Docker)
  │   └── Agent State, Decisions, Audit Logs
  │
  └── Command Center (Next.js/React)
      └── Real-time Dashboard GUI

All three components working together = **complete autonomous agent system**.
```

All three components working together = **complete autonomous agent system**.

---

## Next Steps with Me (Claude)

Once you have this running locally:

1. **Open in Claude Code**
2. **Reply here with: "Sentinel running locally"**
3. **I'll help you:**
   - Build your first custom sub-agent
   - Configure job search project
   - Test the orchestration cycle
   - Debug any issues
   - Extend to your other projects

---

**Ready to set this up?** Start with Step 1 and let me know when you hit any blockers!
