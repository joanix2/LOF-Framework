"""Reasoning engine CLI commands."""

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from lof.reasoning import DatalogEngine, ExplanationGenerator, FactEncoder, get_profile
from lof.silver.graph import SilverGraph

console = Console()
reason_app = typer.Typer(help="Reasoning layer: Datalog inference")


def _run_reasoning(root: Path):
    silver = SilverGraph.load(root)
    encoder = FactEncoder()
    facts = encoder.encode(silver)
    profile = get_profile("fastapi-react")
    engine = DatalogEngine(profile)
    result = engine.evaluate(facts)
    return silver, facts, engine, result


@reason_app.command("status")
def status() -> None:
    _, _, _, result = _run_reasoning(Path.cwd())
    console.print("[bold]Reasoning Engine Status[/bold]")
    total = sum(1 for f in result.facts if f.status in ("asserted", "inferred"))
    console.print(f"  Facts (asserted+inferred): {total}")
    console.print(f"  Facts (inferred): {len(result.inferred)}")
    console.print(f"  Hypotheses: {len(result.hypotheses)}")
    console.print(f"  Iterations: {result.iteration_count}")
    console.print(f"  Converged: {result.converged}")
    console.print(f"  Duration: {result.duration_ms:.1f}ms")
    if result.contradictions:
        console.print(f"  [red]Contradictions: {len(result.contradictions)}[/red]")
        for c in result.contradictions:
            console.print(f"    {c}")
    for inf in result.inferred[:10]:
        console.print(f"  [green]inferred:[/green] {inf.key} (via {inf.rule_id})")


@reason_app.command("facts")
def facts(predicate: str | None = typer.Option(None, "--predicate", "-p")) -> None:
    _, _, _, result = _run_reasoning(Path.cwd())
    filtered = result.facts
    if predicate:
        filtered = [f for f in filtered if f.predicate == predicate]
    table = Table(title="Reasoning Facts")
    table.add_column("Fact", style="cyan")
    table.add_column("Status", style="yellow")
    table.add_column("Confidence")
    table.add_column("Rule")
    for f in filtered:
        table.add_row(f.key, f.status, f"{f.confidence:.2f}", f.rule_id or "")
    console.print(table)


@reason_app.command("explain")
def explain(fact_key: str = typer.Argument(..., help="Fact key")) -> None:
    _, _, engine, result = _run_reasoning(Path.cwd())
    gen = ExplanationGenerator(engine, get_profile("fastapi-react"))
    console.print(gen.explain(fact_key, result))


@reason_app.command("trace")
def trace(fact_key: str = typer.Argument(..., help="Fact key to trace")) -> None:
    _, _, engine, result = _run_reasoning(Path.cwd())
    gen = ExplanationGenerator(engine, get_profile("fastapi-react"))
    console.print(gen.trace_path(fact_key, result))
