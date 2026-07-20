"""Constraints (SMT) CLI commands."""

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from lof.compilation.compiler import Compiler
from lof.graph.instance_graph import InstanceGraph
from lof.validation.smt.validation_engine import SemanticValidationEngine

console = Console()
constraints_app = typer.Typer(help="SMT semantic constraints")


def _build_engine(root: Path) -> SemanticValidationEngine:
    compiler = Compiler(root)
    compiler.load_all()
    ig = InstanceGraph()
    ig.build(compiler.registry.instances)
    return SemanticValidationEngine(compiler.registry, ig)


@constraints_app.command("list")
def list_constraints() -> None:
    engine = _build_engine(Path.cwd())
    constraints = engine.build_builtin_constraints()
    table = Table(title="Built-in Constraints")
    table.add_column("ID", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Severity", style="yellow")
    table.add_column("Description")
    for c in constraints:
        table.add_row(c.id, c.type, c.severity, c.description or "")
    console.print(table)


@constraints_app.command("validate")
def validate(json_output: bool = typer.Option(False, "--json")) -> None:
    root = Path.cwd()
    compiler = Compiler(root)
    compiler.load_all()
    ig = InstanceGraph()
    ig.build(compiler.registry.instances)
    engine = SemanticValidationEngine(compiler.registry, ig)
    result = engine.validate_with_json_diagnostics(output_dir=root)

    if json_output:
        console.print(json.dumps(result.model_dump(), indent=2))
    elif result.status == "sat":
        console.print("[green]SAT[/green] — All semantic constraints satisfied.")
    elif result.status == "unsat":
        console.print(f"[red]UNSAT[/red] — {len(result.diagnostics)} violation(s):")
        for d in result.diagnostics:
            hint = f" ({d.hint})" if d.hint else ""
            console.print(f"  [{d.code}] {d.message}{hint}")
            if d.instance_ids:
                console.print(f"    instances: {', '.join(d.instance_ids)}")
            if d.json_paths:
                console.print(f"    paths: {', '.join(d.json_paths)}")
        raise typer.Exit(3)
    else:
        console.print("[yellow]UNKNOWN[/yellow]")
        raise typer.Exit(4)


@constraints_app.command("inspect")
def inspect(id: str = typer.Argument(..., help="Constraint ID")) -> None:
    engine = _build_engine(Path.cwd())
    for c in engine.build_builtin_constraints():
        if c.id == id:
            console.print(json.dumps(c.model_dump(), indent=2))
            return
    console.print(f"[red]Constraint '{id}' not found[/red]")
    raise typer.Exit(1)


@constraints_app.command("explain")
def explain(code: str = typer.Argument(..., help="Diagnostic error code")) -> None:
    root = Path.cwd()
    diag_path = root / ".lof" / "diagnostics" / "latest.json"
    if diag_path.exists():
        data = json.loads(diag_path.read_text())
        for v in data.get("violations", []):
            if v.get("code") == code:
                console.print(f"[bold]Code:[/bold] {v['code']}")
                console.print(f"[bold]Message:[/bold] {v['message']}")
                if v.get("hint"):
                    console.print(f"[bold]Hint:[/bold] {v['hint']}")
                if v.get("instance_ids"):
                    console.print(f"[bold]Instances:[/bold] {', '.join(v['instance_ids'])}")
                return
    console.print(f"[yellow]No diagnostics for code '{code}'.[/yellow]")
