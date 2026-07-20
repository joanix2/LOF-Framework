"""Silver layer CLI commands."""

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from lof.silver.graph import SilverGraph

console = Console()
silver_app = typer.Typer(help="Silver layer: semantic graph")


@silver_app.command("status")
def status() -> None:
    silver = SilverGraph.load(Path.cwd())
    console.print("[bold]Silver Graph[/bold]")
    console.print(f"  Entities: {len(silver.entities)}")
    console.print(f"  Claims: {len(silver.claims)}")
    console.print(f"  Relations: {len(silver.relations)}")
    console.print(f"  Contradictions: {len(silver.contradictions)}")
    resolved = sum(1 for c in silver.contradictions.values() if c.resolved)
    if silver.contradictions:
        console.print(f"  Resolved: {resolved}/{len(silver.contradictions)}")
        for c in silver.contradictions.values():
            s = "[green]resolved[/green]" if c.resolved else "[red]unresolved[/red]"
            console.print(f"    [{s}] {c.description}")


@silver_app.command("claims")
def claims(subject: str | None = typer.Option(None, "--subject", "-s")) -> None:
    silver = SilverGraph.load(Path.cwd())
    items = silver.get_claims_for_subject(subject) if subject else list(silver.claims.values())
    if not items:
        console.print("[yellow]No claims.[/yellow]")
        return
    table = Table(title="Silver Claims")
    table.add_column("ID", style="cyan")
    table.add_column("Subject", style="blue")
    table.add_column("Predicate", style="green")
    table.add_column("Object", style="yellow")
    table.add_column("Status")
    table.add_column("Confidence")
    for c in items:
        sobj = str(c.object)[:28]
        table.add_row(c.id, c.subject, c.predicate, sobj, c.status, f"{c.confidence:.2f}")
    console.print(table)
