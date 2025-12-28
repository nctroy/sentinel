# Sentinel Setup Guide

## Local Development Setup

### 1. Prerequisites

- Python 3.10+
- PostgreSQL 12+ (local or via Docker)
- Notion workspace access
- Claude API key
- GitHub account

### 2. Environment Setup

```bash
# Clone repository
git clone https://github.com/nctroy/sentinel.git
cd sentinel

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. PostgreSQL Setup

#### Option A: Local PostgreSQL (macOS)

```bash
# Install (if not already installed)
brew install postgresql

# Start service
brew services start postgresql

# Create database and user
psql postgres
CREATE USER sentinel WITH PASSWORD 'your-secure-password';
CREATE DATABASE sentinel OWNER sentinel;
GRANT ALL PRIVILEGES ON DATABASE sentinel TO sentinel;
\q
```

#### Option B: PostgreSQL via Docker

```bash
docker run --name sentinel-postgres \
  -e POSTGRES_USER=sentinel \
  -e POSTGRES_PASSWORD=your-secure-password \
  -e POSTGRES_DB=sentinel \
  -p 5432:5432 \
  -d postgres:15
```

#### Option C: AWS RDS (Later)

Set `DATABASE_URL` to your RDS endpoint in `.env`

### 4. Environment Configuration

```bash
# Copy example to actual
cp .env.example .env

# Edit .env with your values
# Required:
# - DATABASE_URL
# - NOTION_API_KEY
# - ANTHROPIC_API_KEY
```

**For local development:**

```bash
DATABASE_URL=postgresql://sentinel:your-password@localhost:5432/sentinel
NOTION_API_KEY=secret_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
NOTION_WORKSPACE_ID=your-workspace-id
NOTION_WORKSPACE_NAME=your-workspace-name
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 5. Initialize Database

```bash
# Run migrations
python -m src.cli.cli init-db

# Verify
psql -U sentinel -d sentinel -c "\dt"
```

### 6. Notion Integration

See `docs/NOTION_SETUP.md` for complete instructions.

TL;DR:
1. Go to `https://www.notion.so/my-integrations`
2. Create new integration: "Sentinel"
3. Copy API key to `.env` as `NOTION_API_KEY`
4. Share your Notion workspace with the integration
5. Copy workspace ID to `.env`

### 7. Verify Setup

```bash
# Test database connection
python -c "from src.storage.postgres_client import PostgresClient; print('✓ DB connected')"

# Test Notion connection
python -c "from src.storage.notion_client import NotionClient; print('✓ Notion connected')"

# Run first diagnostic
python -m src.cli.cli run-cycle --mode diagnostic
```

## Running Sentinel

### Command Line

```bash
# Show help
python -m src.cli.cli --help

# Run diagnostic cycle (read-only)
python -m src.cli.cli run-cycle --mode diagnostic

# Run with verbose logging
python -m src.cli.cli run-cycle --mode diagnostic --verbose

# Initialize a new project
python -m src.cli.cli init-project --config config/podcast-example.json

# List agents
python -m src.cli.cli list-agents

# View agent state
python -m src.cli.cli show-agent --agent-id job-search-001
```

### MCP Server

```bash
# Start MCP server
python -m src.mcp_server.sentinel_server

# Now Claude can call agents via MCP
```

### Development Server

```bash
# Start FastAPI server
uvicorn src.mcp_server.sentinel_server:app --reload --port 8000

# API docs available at http://localhost:8000/docs
```

## Configuration

### Project Configuration

Create `config/my-project.json`:

```json
{
  "project": "my-project",
  "description": "Your project description",
  "sub_agents": [
    {
      "name": "research",
      "domain": "domain-1",
      "responsibilities": ["Task 1", "Task 2"]
    },
    {
      "name": "execution",
      "domain": "domain-2",
      "responsibilities": ["Task 3", "Task 4"]
    }
  ],
  "orchestration_rules": {
    "bottleneck_prioritization": "impact-score",
    "autonomy_level": "diagnostic"
  }
}
```

### Agent Configuration

Edit `src/schemas/agent_config.json` to customize agent behavior.

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_agents.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## Troubleshooting

### Database Connection Error

```bash
# Check PostgreSQL is running
psql -U sentinel -d sentinel -c "SELECT 1"

# Check DATABASE_URL in .env
echo $DATABASE_URL
```

### Notion Connection Error

```bash
# Verify API key
echo $NOTION_API_KEY

# Test Notion connection
python -c "from notion_client import Client; c = Client(auth=input('Key: ')); print(c.users.me())"
```

### Port Already in Use

```bash
# Use different port
uvicorn src.mcp_server.sentinel_server:app --port 8001
```

## Next Steps

1. ✅ Read `docs/ARCHITECTURE.md` to understand the system
2. ✅ Set up your first project in `config/`
3. ✅ Run diagnostic cycle
4. ✅ Review results in Notion dashboard
5. ✅ Move to `docs/AGENT_DESIGN.md` to create custom agents

## Getting Help

- Check logs: `tail -f logs/sentinel.log`
- Review test cases: `tests/`
- Examine example config: `config/podcast-example.json`
