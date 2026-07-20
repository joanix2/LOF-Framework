"""LOF CLI — main dispatcher."""

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table
from rich.tree import Tree

from lof.bench.runner import BenchmarkRunner
from lof.bench.scenario_loader import ScenarioLoader
from lof.compilation.compiler import Compiler
from lof.compilation.manifest import ManifestManager
from lof.graph.builder import GraphBuilder
from lof.graph.validator import GraphValidator
from lof.interfaces.commands_bronze import bronze_app
from lof.interfaces.commands_constraints import constraints_app
from lof.interfaces.commands_gold import gold_app
from lof.interfaces.commands_reason import reason_app
from lof.interfaces.commands_silver import silver_app
from lof.loading.loader import Loader

console = Console()

app = typer.Typer(name="lof", help="Language-Oriented Programming Framework", no_args_is_help=True)
app.add_typer(bronze_app, name="bronze")
app.add_typer(silver_app, name="silver")
app.add_typer(gold_app, name="gold")
app.add_typer(reason_app, name="reason")
app.add_typer(constraints_app, name="constraints")


@app.command()
def init() -> None:
    root = Path.cwd()
    for d in ["definitions/types", "definitions/targets", "templates/python",
              "templates/typescript", "templates/markdown", "templates/mermaid",
              "instances", "patches/python", "patches/typescript",
              "interfaces/python", "interfaces/typescript",
              "generated/python", "generated/typescript",
              "generated/docs", "generated/diagrams"]:
        (root / d).mkdir(parents=True, exist_ok=True)
    console.print("[green]LOF project initialized[/green]")


@app.command()
def validate() -> None:
    compiler = Compiler(Path.cwd())
    compiler.load_all()
    errors = compiler.validate_all()
    if errors:
        for e in errors:
            console.print(f"[red]ERROR:[/red] {e}")
        raise typer.Exit(1)
    console.print("[green]Structural validation passed[/green]")
    console.print(f"  Types: {compiler.registry.type_count}, "
                  f"Instances: {compiler.registry.instance_count}, "
                  f"Patches: {compiler.registry.patch_count}")


@app.command()
def graph(format: str = typer.Option("text", "--format", "-f", help="text or mermaid")) -> None:
    compiler = Compiler(Path.cwd())
    compiler.load_all()
    builder = GraphBuilder(compiler.registry)
    builder.build()

    if format == "mermaid":
        console.print(builder.to_mermaid())
        return

    order = builder.get_types_in_order()
    tree = Tree("Dependency Graph")
    for type_id in order:
        node = builder.graph.nodes.get(type_id)
        if node and node.get("type") == "type":
            t = compiler.registry.get_type(type_id)
            if t:
                branch = tree.add(f"[bold]{type_id}[/bold]")
                if t.depends_on:
                    deps = branch.add("depends on")
                    for dep in t.depends_on:
                        deps.add(dep)
                for inst in compiler.registry.instances_for_type(type_id):
                    branch.add(f"[instance] {inst.id}")
    console.print(tree)

    cycles = GraphValidator(compiler.registry).validate(builder.graph)
    if cycles.has_errors:
        console.print("\n[red]Cycle detected![/red]")
        for e in cycles.errors:
            console.print(f"  [red]{e}[/red]")
    else:
        console.print("\n[green]No cycles[/green]")
        console.print(f"Compilation order: {' -> '.join(order)}")


@app.command(name="compile")
def compile_cmd(
    instance: str | None = typer.Option(None, "--instance", "-i"),
    type: str | None = typer.Option(None, "--type", "-t"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    force: bool = typer.Option(False, "--force"),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    compiler = Compiler(Path.cwd(), dry_run=dry_run)
    report = compiler.compile()

    if json_output:
        console.print(json.dumps(report.model_dump(), indent=2))
        if report.errors:
            raise typer.Exit(3)
        return

    if report.errors:
        for e in report.errors:
            tag = "SMT ERROR" if "UNSAT" in e else "ERROR"
            console.print(f"[red]{tag}:[/red] {e}")
        raise typer.Exit(3)

    console.print("[green]Compilation successful[/green]")
    console.print(f"  Types: {report.types_loaded}, Instances: {report.instances_loaded}")
    console.print(f"  Generated: {len(report.artifacts_generated)} files")
    for a in report.artifacts_generated:
        console.print(f"    - {a}")
    if report.artifacts_patched:
        console.print(f"  Patched: {len(report.artifacts_patched)}")


@app.command()
def inspect(
    what: str = typer.Argument(..., help="type or instance"),
    id: str = typer.Option(..., "--id"),
) -> None:
    loader = Loader(Path.cwd())
    if what == "type":
        for t in loader.load_types_from_dir():
            if t.id == id:
                console.print(json.dumps(t.model_dump(exclude_none=True), indent=2, default=str))
                return
    elif what == "instance":
        for inst in loader.load_instances_from_dir():
            if inst.id == id:
                console.print(json.dumps(inst.model_dump(exclude_none=True), indent=2, default=str))
                return
    console.print(f"[red]{what.capitalize()} '{id}' not found[/red]")
    raise typer.Exit(1)


@app.command()
def diff() -> None:
    root = Path.cwd()
    mm = ManifestManager(root)
    old = mm.load()
    if not old.artifacts:
        console.print("[yellow]No prior manifest.[/yellow]")
        return
    compiler = Compiler(root, dry_run=True)
    report = compiler.compile()
    from lof.models.artifact import Artifact, ProjectManifest
    from lof.utils.hashing import compute_hash
    new = ProjectManifest(project_hash="", artifacts=[
        Artifact(instance="", type="", output=a, hash=compute_hash("")) for a in report.artifacts_generated  # noqa: E501
    ])
    changes = mm.diff(old, new)
    if changes:
        for c in changes:
            console.print(c)
    else:
        console.print("[green]No changes[/green]")


@app.command()
def check() -> None:
    compiler = Compiler(Path.cwd())
    compiler.load_all()
    errors = compiler.validate_all()
    if errors:
        for e in errors:
            console.print(f"[red]ERROR:[/red] {e}")
        raise typer.Exit(1)
    console.print("[green]All checks passed[/green]")


@app.command()
def clean() -> None:
    import shutil
    root = Path.cwd()
    for d in [root / "generated", root / "generated-project"]:
        if d.exists():
            shutil.rmtree(d)
            d.mkdir(exist_ok=True)
    console.print("[green]Cleaned[/green]")


@app.command()
def manifest() -> None:
    m = ManifestManager(Path.cwd()).load()
    if not m.artifacts:
        console.print("[yellow]No artifacts (run compile first)[/yellow]")
        return
    table = Table(title="Build Manifest")
    table.add_column("Instance", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Output", style="blue")
    table.add_column("Hash", style="yellow")
    for a in m.artifacts:
        table.add_row(a.instance, a.type, a.output, a.hash)
    console.print(table)
    console.print(f"Project hash: {m.project_hash}")


bench_app = typer.Typer(help="LOP-Bench benchmark framework")
app.add_typer(bench_app, name="bench")


@bench_app.command("list")
def bench_list() -> None:
    scenarios = ScenarioLoader(Path.cwd()).list_scenarios()
    if not scenarios:
        console.print("[yellow]No benchmarks found.[/yellow]")
        return
    table = Table(title="LOP-Bench Scenarios")
    table.add_column("ID", style="cyan")
    table.add_column("Level", style="blue")
    table.add_column("Category", style="green")
    table.add_column("Expected", style="yellow")
    table.add_column("Title")
    for s in scenarios:
        exp = s.metadata.expected_outcome[:8]
        table.add_row(s.metadata.id, str(s.metadata.level), s.metadata.category, exp, s.metadata.title)  # noqa: E501
    console.print(table)


@bench_app.command("run")
def bench_run(
    level: int = typer.Option(-1, "--level", "-l"),
    category: str | None = typer.Option(None, "--category", "-c"),
    scenario_id: str | None = typer.Option(None, "--scenario", "-s"),
) -> None:
    from lof.bench.models import BenchmarkReport
    runner = BenchmarkRunner(Path.cwd())
    if scenario_id:
        sc = ScenarioLoader(Path.cwd()).get_scenario(scenario_id)
        if sc is None:
            console.print(f"[red]Scenario '{scenario_id}' not found.[/red]")
            raise typer.Exit(1)
        report = BenchmarkReport()
        report.results = [runner._run_scenario(sc)]
        report.total_scenarios = 1
        report.passed = sum(1 for r in report.results if r.passed)
        report.failed = report.total_scenarios - report.passed
    else:
        report = runner.run_all(level=level, category=category)

    console.print("\n[bold]LOP-Bench Results[/bold]")
    console.print(f"  Scenarios: {report.total_scenarios}, Passed: [green]{report.passed}[/green], "
                  f"Failed: [red]{report.failed}[/red], Rate: {report.pass_rate:.1%}")
    for r in report.results:
        s = "[green]PASS[/green]" if r.passed else "[red]FAIL[/red]"
        console.print(f"  {s} {r.scenario_id} ({r.duration_ms:.0f}ms)")
        for e in r.errors[:3]:
            console.print(f"         {e}")

    report_dir = Path.cwd() / "reports"
    report_dir.mkdir(exist_ok=True)
    (report_dir / "latest.json").write_text(json.dumps(report.model_dump(), indent=2, default=str))
    console.print("\n[blue]Report:[/blue] reports/latest.json")


def main() -> None:
    app()


if __name__ == "__main__":
    app()
