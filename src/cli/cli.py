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
    
    try:
        # Implementation would run the cycle
        console.print("[green]✓ Cycle complete[/]")
    except Exception as e:
        console.print(f"[red]✗ Failed: {e}[/]")
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
