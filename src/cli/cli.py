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
        # Implementation would create tables
        console.print("[green]✓ Database initialized[/]")
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
    """Initialize a new project"""
    console.print(f"[bold blue]Initializing project from {config}...[/]")
    
    try:
        with open(config, 'r') as f:
            project_config = json.load(f)
        
        console.print(f"[green]✓ Project created: {project_config['project']}[/]")
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
