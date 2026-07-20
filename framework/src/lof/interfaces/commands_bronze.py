"""Bronze layer CLI commands."""

from datetime import datetime
from pathlib import Path
from uuid import uuid4

import typer
from rich.console import Console
from rich.table import Table

from lof.bronze.models import BronzeEntry
from lof.bronze.store import BronzeStore
from lof.silver.extractor import SpacyExtractor
from lof.silver.graph import SilverGraph

console = Console()
bronze_app = typer.Typer(help="Bronze layer: raw expression storage")


@bronze_app.command("add")
def add(
    content: str = typer.Argument(..., help="Raw expression"),
    source: str = typer.Option("user", "--source", "-s"),
    entry_type: str = typer.Option("message", "--type", "-t"),
) -> None:
    root = Path.cwd()
    store = BronzeStore(root)
    entry = BronzeEntry(
        id=f"bronze-{uuid4().hex[:12]}",
        created_at=datetime.now(),
        source=source,
        content=content,
        entry_type=entry_type,
    )
    store.append_entry(entry)
    console.print(f"[green]Bronze entry saved:[/green] {entry.id}")

    silver = SilverGraph()
    extractor = SpacyExtractor(silver)
    claims = extractor.extract_from_entry(entry)
    for c in claims:
        silver.add_claim(c)
        console.print(f"  [cyan]Claim:[/cyan] {c.subject} {c.predicate} {c.object} ({c.status})")
    silver.save(root)

    if silver.contradictions:
        console.print(f"[yellow]{len(silver.contradictions)} contradiction(s)[/yellow]")


@bronze_app.command("list")
def list_entries() -> None:
    store = BronzeStore(Path.cwd())
    entries = store.list_entries()
    if not entries:
        console.print("[yellow]No bronze entries.[/yellow]")
        return
    table = Table(title="Bronze Entries")
    table.add_column("ID", style="cyan")
    table.add_column("Source", style="green")
    table.add_column("Content")
    table.add_column("Created")
    for e in entries:
        table.add_row(e.id, e.source, e.content[:60], e.created_at.isoformat()[:10])
    console.print(table)
