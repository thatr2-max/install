"""Command-line interface for AI Mod Generator."""

import click
import logging
import json
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel

from src.config import Config
from src.openrouter_client import OpenRouterClient
from src.learner.schema_learner import SchemaLearner
from src.agent.modding_agent import ModdingAgent

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Rich console for pretty output
console = Console()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """AI Mod Generator - Create game mods using AI agents."""
    pass


@cli.command()
@click.argument('game')
def learn(game: str):
    """Learn modding patterns from example mods.

    GAME: Game identifier (e.g., cdda, rimworld, factorio)

    Before running this command:
    1. Place example mods in game_schemas/[game]/examples/
    2. Place documentation in game_schemas/[game]/docs/
    """
    console.print(f"\n[bold blue]Learning modding patterns for {game.upper()}[/bold blue]\n")

    try:
        # Get project root
        project_root = Path(__file__).parent

        # Check if examples exist
        schema_dir = project_root / "game_schemas" / game
        examples_dir = schema_dir / "examples"

        if not examples_dir.exists() or not any(examples_dir.iterdir()):
            console.print(f"[red]Error:[/red] No examples found in {examples_dir}")
            console.print("\nPlease add example mods to this directory first.")
            console.print("Each example should be in its own subdirectory.")
            return

        # Run learning with progress indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Analyzing example mods...", total=None)

            learner = SchemaLearner(schema_dir)
            schema = learner.learn()

            progress.update(task, description="✓ Learning complete!")

        # Display summary
        console.print("\n[green]✓ Schema learned successfully![/green]\n")
        console.print(f"Game: [cyan]{schema['game']}[/cyan]")
        console.print(f"Example mods analyzed: [cyan]{schema['example_count']}[/cyan]")
        console.print(f"Templates found: [cyan]{len(schema['templates'])}[/cyan]")

        # Show templates
        if schema['templates']:
            table = Table(title="Discovered Templates")
            table.add_column("Template Type", style="cyan")
            table.add_column("Required Fields", style="green")
            table.add_column("Optional Fields", style="yellow")

            for template_name, template_data in schema['templates'].items():
                table.add_row(
                    template_name,
                    str(len(template_data.get('required_fields', []))),
                    str(len(template_data.get('optional_fields', [])))
                )

            console.print(table)

        console.print(f"\n[dim]Schema saved to: {schema_dir / 'schema.json'}[/dim]")

    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        logger.exception("Learning failed")


@cli.command()
@click.argument('game')
@click.argument('description')
@click.option('--output-dir', default=None, help='Custom output directory')
@click.option('--verbose', is_flag=True, help='Show detailed agent reasoning')
@click.option('--max-iterations', default=10, help='Maximum iterations for agent')
def create(game: str, description: str, output_dir: str, verbose: bool, max_iterations: int):
    """Create a new mod using AI agent.

    GAME: Game identifier (e.g., cdda, rimworld, factorio)
    DESCRIPTION: Natural language description of the mod
    """
    console.print(f"\n[bold blue]Creating mod for {game.upper()}[/bold blue]\n")
    console.print(f"Description: [italic]{description}[/italic]\n")

    try:
        # Load config
        config = Config()

        # Check if schema exists
        project_root = Path(__file__).parent
        schema_path = project_root / "game_schemas" / game / "schema.json"

        if not schema_path.exists():
            console.print(f"[red]Error:[/red] No schema found for {game}")
            console.print(f"\nRun [cyan]modgen learn {game}[/cyan] first to analyze example mods.")
            return

        # Initialize client and agent
        client = OpenRouterClient(
            api_key=config.api_key,
            base_url=config.base_url,
            model=config.model,
            log_dir=str(project_root / "logs"),
            input_cost_per_1m=config.cost_tracking.get("input_cost_per_1m_tokens", 0.15),
            output_cost_per_1m=config.cost_tracking.get("output_cost_per_1m_tokens", 1.50)
        )

        agent = ModdingAgent(
            client=client,
            project_root=project_root,
            log_dir=project_root / "logs"
        )

        # Generate mod with progress
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Generating mod...", total=None)

            result = agent.generate_mod(
                game=game,
                description=description,
                max_iterations=max_iterations,
                verbose=verbose
            )

        # Check if successful
        if not result.get("success"):
            console.print(f"[red]✗ Generation failed:[/red] {result.get('error')}")
            return

        # Display results
        console.print("\n[green]✓ Mod generated successfully![/green]\n")

        # Show files
        files = result.get("files", {})
        console.print(Panel(
            f"[bold]Generated {len(files)} file(s)[/bold]",
            style="green"
        ))

        for file_path in files.keys():
            console.print(f"  📄 {file_path}")

        # Save files
        if output_dir is None:
            output_dir = project_root / "output" / game / f"{result['mod_name']}"
        else:
            output_dir = Path(output_dir)

        output_dir.mkdir(parents=True, exist_ok=True)

        for file_path, content in files.items():
            full_path = output_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)

        console.print(f"\n[cyan]Files saved to:[/cyan] {output_dir}")

        # Show metadata
        metadata = result.get("metadata", {})
        console.print(f"\nIterations: [cyan]{metadata.get('iterations', 0)}[/cyan]")
        console.print(f"Tool calls: [cyan]{metadata.get('tool_calls_count', 0)}[/cyan]")

        # Show cost
        cost = client.get_total_cost()
        console.print(f"Total cost: [cyan]${cost:.4f}[/cyan]")

        # Show warnings
        warnings = result.get("warnings", [])
        if warnings:
            console.print("\n[yellow]Warnings:[/yellow]")
            for warning in warnings:
                console.print(f"  ⚠️  {warning}")

        console.print("\n[green]Done![/green] 🎉\n")

    except ValueError as e:
        console.print(f"[red]Configuration Error:[/red] {str(e)}")
        console.print("\nPlease check your config.json file.")
    except Exception as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        logger.exception("Generation failed")


@cli.command()
def list():
    """List all learned games and their details."""
    project_root = Path(__file__).parent
    schemas_dir = project_root / "game_schemas"

    console.print("\n[bold blue]Learned Games[/bold blue]\n")

    table = Table()
    table.add_column("Game", style="cyan")
    table.add_column("Schema", style="green")
    table.add_column("Examples", style="yellow")
    table.add_column("Templates", style="magenta")

    for game_dir in schemas_dir.iterdir():
        if not game_dir.is_dir():
            continue

        schema_path = game_dir / "schema.json"
        examples_dir = game_dir / "examples"

        has_schema = "✓" if schema_path.exists() else "✗"

        example_count = 0
        if examples_dir.exists():
            example_count = len([d for d in examples_dir.iterdir() if d.is_dir()])

        template_count = 0
        if schema_path.exists():
            with open(schema_path, 'r') as f:
                schema = json.load(f)
                template_count = len(schema.get('templates', {}))

        table.add_row(
            game_dir.name,
            has_schema,
            str(example_count),
            str(template_count) if template_count > 0 else "-"
        )

    console.print(table)
    console.print()


@cli.command()
def cost():
    """Show total API usage and cost."""
    project_root = Path(__file__).parent
    tracker_file = project_root / "logs" / "cost_tracker.json"

    console.print("\n[bold blue]API Usage & Cost[/bold blue]\n")

    if not tracker_file.exists():
        console.print("[yellow]No usage data found yet.[/yellow]\n")
        return

    with open(tracker_file, 'r') as f:
        data = json.load(f)

    console.print(f"Total Input Tokens: [cyan]{data.get('total_input_tokens', 0):,}[/cyan]")
    console.print(f"Total Output Tokens: [cyan]{data.get('total_output_tokens', 0):,}[/cyan]")
    console.print(f"Total Cost: [green]${data.get('total_cost', 0):.4f}[/green]")
    console.print(f"\nLast Updated: [dim]{data.get('last_updated', 'Unknown')}[/dim]\n")


if __name__ == '__main__':
    cli()
