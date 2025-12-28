"""
Command-line interface for Sentinel.
"""

import os
import json
import asyncio
import logging
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

console = Console()


@click.group()
def cli():
    """Sentinel CLI - Multi-agent orchestration"""
    pass


@cli.command()
def init_db():
    """Initialize database schema"""
    console.print("[bold blue]Initializing database...[/]")
    try:
        from src.storage.postgres_client import PostgresClient

        db = PostgresClient()
        db.connect()
        db.init_db()

        console.print("[green]✓ Database initialized[/]")
        console.print("[dim]Tables created: agents, bottlenecks, actions, orchestrator_plans, decision_log, notion_sync[/]")
    except Exception as e:
        console.print(f"[red]✗ Failed: {e}[/]")
        raise


@cli.command()
@click.option("--mode", default="diagnostic", help="diagnostic|conditional|full")
@click.option("--verbose", is_flag=True, help="Verbose output")
def run_cycle(mode, verbose):
    """Run a complete Sentinel cycle"""
    console.print(f"[bold blue]Running cycle in {mode} mode...[/]")

    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    async def _run_cycle_async():
        from src.storage.postgres_client import PostgresClient
        from src.agents.research_agent import ResearchAnalystAgent
        from src.agents.github_agent import GitHubTriageAgent
        from src.observability.telemetry import setup_telemetry
        from datetime import datetime

        # Initialize OpenTelemetry
        setup_telemetry(service_name="sentinel")
        console.print("[dim]OpenTelemetry initialized[/]\n")

        db = PostgresClient()
        db.connect()

        # Get all registered agents
        agents = db.get_all_agents()

        if not agents:
            console.print("[yellow]⚠ No agents registered. Run 'init-project' first.[/]")
            return

        console.print(f"[dim]Found {len(agents)} agent(s)[/]\n")

        # Run diagnostic for each agent
        bottlenecks_found = 0
        for agent_info in agents:
            agent_id = agent_info['agent_id']
            domain = agent_info['domain']
            name = agent_info.get('name', agent_id)

            console.print(f"[cyan]→ {name}[/] ({domain})")

            try:
                # Instantiate the appropriate agent class based on agent_id or domain
                agent = None
                if 'research' in agent_id.lower() or 'research' in domain.lower():
                    agent = ResearchAnalystAgent(agent_id, domain)
                elif 'github' in agent_id.lower() or 'github' in domain.lower():
                    agent = GitHubTriageAgent(agent_id, domain)
                else:
                    # Default to ResearchAnalystAgent for unknown types
                    console.print(f"  [yellow]⚠[/] Unknown agent type, using ResearchAnalystAgent as default")
                    agent = ResearchAnalystAgent(agent_id, domain)

                # Run diagnostic
                bottleneck = await agent.diagnose()

                # Check if bottleneck is significant (confidence > 0)
                if bottleneck and bottleneck.get('confidence', 0) > 0:
                    # Save bottleneck to database
                    db.save_bottleneck(agent_id, bottleneck)

                    # Log the decision
                    db.log_decision(
                        agent_id=agent_id,
                        decision_type="bottleneck_identified",
                        reasoning=bottleneck.get('reasoning', 'Diagnostic analysis'),
                        context={"mode": mode, "domain": domain},
                        outcome={"bottleneck": bottleneck}
                    )

                    console.print(f"  [yellow]⚠[/] Bottleneck: {bottleneck['description']}")
                    console.print(f"  [dim]Impact: {bottleneck['impact_score']}/10 | Confidence: {bottleneck['confidence']:.0%}[/]\n")
                    bottlenecks_found += 1
                else:
                    console.print(f"  [green]✓[/] No significant bottlenecks identified\n")

                # Update last_run timestamp
                db.update_agent_last_run(agent_id)

            except Exception as agent_error:
                console.print(f"  [red]✗[/] Agent failed: {agent_error}\n")
                logger.error(f"Agent {agent_id} failed: {agent_error}", exc_info=True)
                continue

        # Summary
        console.print(f"[green]✓ Cycle complete[/]")
        console.print(f"[dim]Mode: {mode} | Agents: {len(agents)} | Bottlenecks: {bottlenecks_found}[/]")

        if bottlenecks_found > 0:
            console.print(f"\n[yellow]💡 Tip: Review bottlenecks in Notion dashboard[/]")

    try:
        # Run the async function
        asyncio.run(_run_cycle_async())
    except Exception as e:
        console.print(f"[red]✗ Failed: {e}[/]")
        logger.error(f"Cycle failed: {e}", exc_info=True)
        raise




@cli.command()
@click.argument("config")
def init_project(config):
    """Initialize a new project and register agents"""
    console.print(f"[bold blue]Initializing project from {config}...[/]")

    try:
        from src.storage.postgres_client import PostgresClient

        # Load config
        with open(config, 'r') as f:
            project_config = json.load(f)

        project_name = project_config['project']
        console.print(f"[cyan]Project: {project_name}[/]")
        console.print(f"[dim]{project_config.get('description', '')}[/]\n")

        # Connect to database
        db = PostgresClient()
        db.connect()

        # Register agents
        agents_registered = 0
        for agent_config in project_config.get('sub_agents', []):
            agent_id = agent_config['agent_id']
            domain = agent_config['domain']

            db.register_agent(
                agent_id=agent_id,
                domain=domain,
                name=agent_config.get('name'),
                responsibilities=agent_config.get('responsibilities'),
                autonomy_level=agent_config.get('autonomy_level', 'diagnostic')
            )
            console.print(f"  [green]✓[/] Registered: {agent_id} ({domain})")
            agents_registered += 1

        console.print(f"\n[green]✓ Project initialized: {project_name}[/]")
        console.print(f"[dim]Registered {agents_registered} agents[/]")

    except Exception as e:
        console.print(f"[red]✗ Failed: {e}[/]")
        raise


@cli.command()
def test_notion():
    """Test Notion API connection"""
    console.print("[bold blue]Testing Notion connection...[/]")

    try:
        from src.storage.notion_client import NotionClient

        notion = NotionClient()
        result = notion.test_connection()

        console.print(f"[green]✓ Connected to Notion[/]")
        console.print(f"[dim]Workspace: {result['workspace']}[/]")
        console.print(f"[dim]Users: {result['users_count']}[/]\n")

        # Search for pages
        console.print("[cyan]Searching for pages...[/]")
        pages = notion.search_pages()

        if pages:
            console.print(f"[dim]Found {len(pages)} page(s):[/]")
            for page in pages[:5]:  # Show first 5
                title = "Untitled"
                if page.get("properties", {}).get("title"):
                    title_prop = page["properties"]["title"]
                    if title_prop.get("title") and len(title_prop["title"]) > 0:
                        title = title_prop["title"][0]["text"]["content"]

                console.print(f"  • {title}")

            if len(pages) > 5:
                console.print(f"  [dim]... and {len(pages) - 5} more[/]")
        else:
            console.print("[yellow]No pages found in workspace[/]")

        console.print(f"\n[green]✓ Notion connection successful[/]")

    except Exception as e:
        console.print(f"[red]✗ Failed: {e}[/]")
        raise


@cli.command()
@click.argument("page_id")
def init_notion(page_id):
    """Initialize Notion dashboard on a parent page"""
    console.print(f"[bold blue]Initializing Notion dashboard on page {page_id}...[/]")

    try:
        from src.storage.notion_client import NotionClient

        notion = NotionClient()
        result = notion.setup_dashboard(page_id)

        console.print("[green]✓ Dashboard databases created successfully[/]")
        console.print(f"[dim]• Agent Daily Reports: {result['reports_db']}[/]")
        console.print(f"[dim]• Weekly Priorities: {result['priorities_db']}[/]")
        console.print(f"[dim]• Decision Log: {result['decisions_db']}[/]")
        console.print("\n[yellow]Note: Update your .env file with these database IDs if you wish to persist them specifically.[/]")

    except Exception as e:
        console.print(f"[red]✗ Failed: {e}[/]")
        raise


@cli.command()
def list_agents():
    """List all agents"""
    table = Table(title="Registered Agents")
    table.add_column("Agent ID", style="cyan")
    table.add_column("Domain", style="magenta")
    table.add_column("Status", style="green")
    
    # Implementation would populate from database
    console.print(table)


@cli.command()
@click.argument("agent_id")
def show_agent(agent_id):
    """Show agent details"""
    console.print(f"[bold blue]Agent: {agent_id}[/]")
    
    # Implementation would fetch and display
    console.print("Not yet implemented")


def main():
    """Main entry point"""
    cli()


if __name__ == "__main__":
    main()
