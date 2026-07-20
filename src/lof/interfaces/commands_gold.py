"""Gold layer CLI commands."""

from pathlib import Path

import typer
from rich.console import Console

from lof.bronze.store import BronzeStore
from lof.reasoning import DatalogEngine, FactEncoder, get_profile
from lof.reasoning.integration import silver_to_gold_via_reasoning
from lof.silver.graph import SilverGraph

console = Console()
gold_app = typer.Typer(help="Gold layer: DSL generation")


@gold_app.command("build")
def build() -> None:
    root = Path.cwd()
    silver = SilverGraph.load(root)
    paths = silver_to_gold_via_reasoning(silver, root, "fastapi-react")
    console.print(f"[green]Gold candidates (via reasoning):[/green] {len(paths)} files")
    for p in paths:
        console.print(f"  - {p.relative_to(root)}")

    encoder = FactEncoder()
    facts = encoder.encode(silver)
    engine = DatalogEngine(get_profile("fastapi-react"))
    result = engine.evaluate(facts)
    console.print(
        f"  Inferred: {len(result.inferred)} facts in {result.iteration_count} iterations"
    )  # noqa: E501
    if result.contradictions:
        console.print(f"  [red]Contradictions: {len(result.contradictions)}[/red]")


@gold_app.command("provenance")
def provenance(instance_id: str = typer.Argument(..., help="Instance ID to trace")) -> None:
    root = Path.cwd()
    silver = SilverGraph.load(root)

    spans: list[str] = []
    bronze_ids: set[str] = set()
    for claim in silver.claims.values():
        for ref in claim.provenance:
            if ref.bronze_id:
                bronze_ids.add(ref.bronze_id)
            if ref.span:
                spans.append(ref.span)

    store = BronzeStore(root)
    subject_prefix = instance_id.split("-")[0].capitalize()
    ref_count = sum(1 for c in silver.claims.values() if c.subject == subject_prefix)
    console.print(f"[bold]Provenance for '{instance_id}':[/bold]")
    console.print(f"  Silver claims referencing '{subject_prefix}': {ref_count}")
    if bronze_ids:
        console.print(f"  Bronze sources: {len(bronze_ids)}")
        for bid in sorted(bronze_ids):
            entry = store.get_entry(bid)
            if entry:
                console.print(f"    - {bid}: {entry.content[:80]}")
    if spans:
        console.print(f"  Extraction spans: {len(spans)}")
        for s in spans[:5]:
            console.print(f'    - "{s}"')
