# Sentinel

**Sentinel** is a multi-agent orchestration system designed to manage domain-specific AI agents and coordinate their priorities across projects. It serves as your Chief of Staff, identifying bottlenecks, automating workflows, and scaling your problem-solving capacity.

## Features

- **Multi-Agent Architecture**: Run specialized sub-agents for different domains (job search, AI business, photography, etc.)
- **Daily Diagnostics**: Each sub-agent identifies daily bottlenecks in its domain
- **Weekly Orchestration**: Central orchestrator agent synthesizes findings and routes priorities
- **Persistent State**: PostgreSQL for system state, Notion for human-readable dashboards
- **MCP Integration**: Agents communicate via Model Context Protocol for deep reasoning
- **Autonomous Execution**: Graduated autonomy model (read-only → conditional → full)
- **Audit Trails**: Complete logging of decisions, reasoning, and outcomes

## Architecture

```
┌─────────────────────────────────────────┐
│         Your Strategic Goals            │
└────────────────┬────────────────────────┘
                 │
         ┌───────▼────────┐
         │  Orchestrator  │
         │  (Chief of     │
         │   Staff)       │
         └───┬──┬──┬──┬───┘
             │  │  │  │
    ┌────────┘  │  │  └──────────┐
    │        ┌──┘  └──┐           │
    ▼        ▼        ▼           ▼
┌──────┐ ┌──────┐ ┌──────┐   ┌────────┐
│ Job  │ │  AI  │ │Photo │   │Personal│
│Search│ │Biz   │ │graphy│   │Dev     │
│Agent │ │Agent │ │Agent │   │Agent   │
└────┬─┘ └──┬───┘ └──┬───┘   └────┬───┘
     │      │        │            │
     └──────┼────┬───┼────────────┘
            │    │   │
     ┌──────▼────▼───▼──┐
     │  Persistent      │
     │  State Store     │
     │ (PostgreSQL)     │
     └──────┬───────────┘
            │
     ┌──────▼──────────┐
     │  Notion         │
     │  Dashboard      │
     └─────────────────┘
```

## Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL (local or AWS RDS)
- Notion API credentials
- Claude API access (via MCP)

### Installation

```bash
# Clone the repository
git clone https://github.com/nctroy/sentinel.git
cd sentinel

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your credentials
```

### Running Locally

```bash
# Start PostgreSQL
# (On macOS with Homebrew: brew services start postgresql)

# Initialize database
python -m src.cli.cli init-db

# Run first cycle
python -m src.cli.cli run-cycle --mode diagnostic

# View results in Notion dashboard
```

## Project Structure

```
sentinel/
├── src/
│   ├── mcp_server/        # MCP server for agent communication
│   ├── agents/            # Agent implementations
│   ├── storage/           # Database and Notion clients
│   ├── schemas/           # Data models and configurations
│   └── cli/               # Command-line interface
├── config/                # Example configurations
├── docs/                  # Architecture and setup docs
├── tests/                 # Unit and integration tests
└── docker/                # Docker configuration
```

## Documentation

- [Architecture Overview](docs/ARCHITECTURE.md) — How Sentinel works
- [Setup Guide](docs/SETUP.md) — Detailed setup instructions
- [Agent Design](docs/AGENT_DESIGN.md) — Building domain-specific agents
- [Notion Integration](docs/NOTION_SETUP.md) — Connecting to your Notion workspace

## Configuration

Sentinel uses JSON configuration files to define agents and their behavior:

```json
{
  "project": "podcast-production",
  "sub_agents": [
    {
      "name": "research",
      "domain": "topic-research",
      "responsibilities": ["Find topics", "Validate audience interest"]
    }
  ],
  "orchestration_rules": {
    "bottleneck_prioritization": "impact-score"
  }
}
```

See `config/podcast-example.json` for a complete example.

## Development

### Running Tests

```bash
pytest tests/ -v
```

### Development Mode

```bash
# Run with verbose logging
python -m src.cli.cli run-cycle --mode diagnostic --verbose
```

## Deployment

### Local Development
PostgreSQL running locally, perfect for testing.

### AWS RDS
Production-ready PostgreSQL deployment (free tier available).

See [Setup Guide](docs/SETUP.md) for cloud deployment instructions.

## Safety & Autonomy

Sentinel implements a graduated autonomy model:

1. **Diagnostic Mode** (default): Agents analyze and report; no actions
2. **Conditional Autonomy**: Agents execute pre-approved action types
3. **Full Autonomy**: Agents make independent decisions (requires explicit trust)

You control the autonomy level per agent and per action type.

## Contributing

This is a personal portfolio project. For questions or collaboration inquiries, contact Troy directly.

## License

MIT License — See LICENSE file for details.

---

**Built by Troy** | Cloud Security Architect | AI Systems Builder
