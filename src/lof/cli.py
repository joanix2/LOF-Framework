"""LOF CLI — main dispatcher."""

import json
from pathlib import Path

import typer
from rich import box
from rich.console import Console
from rich.table import Table
from rich.tree import Tree

from lof import __version__
from lof.api import Project
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

app = typer.Typer(
    name="lof",
    help="Language-Oriented Programming Framework",
    no_args_is_help=True,
    rich_markup_mode="rich",
)
app.add_typer(bronze_app, name="bronze")
app.add_typer(silver_app, name="silver")
app.add_typer(gold_app, name="gold")
app.add_typer(reason_app, name="reason")
app.add_typer(constraints_app, name="constraints")


def version_callback(value: bool):
    if value:
        console.print(f"LOF Framework v{__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(False, "--version", callback=version_callback, is_eager=True),
):
    pass


@app.command()
def new(
    name: str = typer.Argument(..., help="Project name"),
    profile: str = typer.Option("fastapi-react", "--profile", "-p", help="Project profile"),
    mode: str = typer.Option("minimal", "--mode", "-m", help="Mode (minimal/standard/intelligent)"),
    directory: Path = typer.Option(None, "--directory", "-d", help="Output directory"),
):
    """Create a new LOF project."""
    from lof.commands.new_project import new_project as create

    result = create(name, profile=profile, mode=mode, directory=directory)
    if not result["success"]:
        console.print(f"[red]Error:[/red] {result['error']}")
        raise typer.Exit(1)
    console.print(f"[green]Project '{result['name']}' created[/green]")
    console.print(f"  Path: [bold]{result['path']}[/bold]")
    console.print(f"  Profile: {result['profile']}, Mode: {result['mode']}")
    console.print("\n[yellow]Next steps:[/yellow]")
    for step in result["next"]:
        console.print(f"  $ [bold]{step}[/bold]")


@app.command()
def doctor():
    """Check LOF environment and project health."""
    root = Path.cwd()
    checks = [
        ("LOF version", __version__),
        ("Python", __import__("sys").version),
    ]
    project = Project(root)
    v = project.validate()
    checks.append(("Validation", "PASS" if v["valid"] else "FAIL"))

    table = Table(title="LOF Doctor", box=box.ROUNDED)
    table.add_column("Check", style="cyan")
    table.add_column("Status")
    for name, status in checks:
        s = (
            f"[green]{status}[/green]"
            if "PASS" in str(status) or "." in str(status)
            else f"[red]{status}[/red]"
        )  # noqa: E501
        table.add_row(name, s)
    console.print(table)

    lof_file = root / "lof.toml"
    if lof_file.exists():
        console.print("[green]✓[/green] lof.toml found")
    else:
        console.print("[yellow]ℹ[/yellow] Not a LOF project (no lof.toml)")


def _start_processes(
    commands: list[tuple[str, str, list[str]]],
    print_commands: bool = False,
) -> None:
    import subprocess

    if print_commands:
        for name, cwd, cmd in commands:
            console.print(f"[green]{name}:[/green] cd {cwd} && {' '.join(cmd)}")
        return

    processes = []
    try:
        for name, cwd, cmd in commands:
            console.print(f"[green]Starting {name}...[/green]  cd {cwd} && {' '.join(cmd)}")
            p = subprocess.Popen(cmd, cwd=cwd)
            processes.append(p)
        for p in processes:
            p.wait()
    except KeyboardInterrupt:
        console.print("\n[yellow]Shutting down...[/yellow]")
        for p in processes:
            p.terminate()
        for p in processes:
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        for p in processes:
            p.terminate()
        raise typer.Exit(1)


@app.command()
def dev(
    print_commands: bool = typer.Option(
        False, "--print-commands", "-p",
        help="Print commands instead of running",
    ),
):
    """Start development servers for the generated project."""
    root = Path.cwd()
    gen = root / "generated"
    if not gen.exists():
        console.print("[red]No generated/ directory. Run 'lof compile' first.[/red]")
        raise typer.Exit(1)

    manifest_path = gen / "manifest.json"
    commands: list[tuple[str, str, list[str]]] = []

    if manifest_path.exists():
        import json
        manifest = json.loads(manifest_path.read_text())
        for a in manifest.get("artifacts", []):
            dev_cmd = a.get("dev_command")
            if dev_cmd:
                name = a.get("instance", "service")
                out = a.get("output", "")
                cwd = str(gen / Path(out).parent)
                commands.append((name, cwd, dev_cmd.split()))
        if commands:
            _start_processes(commands, print_commands)
            return

    api_dir = gen / "apps" / "api"
    web_dir = gen / "apps" / "web"
    if api_dir.exists():
        commands.append(("API", str(api_dir), ["uvicorn", "app.main:app", "--reload", "--port", "8000"]))  # noqa: E501
    if web_dir.exists():
        commands.append(("Web", str(web_dir), ["npm", "run", "dev"]))

    if not commands:
        console.print("[yellow]No known services found in generated/[/yellow]")
        raise typer.Exit(1)

    _start_processes(commands, print_commands)


@app.command()
def explain(
    target: str = typer.Argument(..., help="Instance, type, file, or diagnostic code"),
):
    """Explain a project element."""
    project = Project(Path.cwd())
    result = project.explain(target)
    console.print(result)


@app.command()
def profiles():
    """List available profiles."""
    from lof.reasoning.profiles import list_profiles

    table = Table(title="Available Profiles")
    table.add_column("Name", style="cyan")
    table.add_column("Version", style="green")
    table.add_column("Description")
    for p in list_profiles():
        table.add_row(p.id, p.version, p.description)
    if not list_profiles():
        table.add_row("(none)", "", "No profiles registered")
    console.print(table)


@app.command()
def init(
    profile: str = typer.Option("fastapi-react", "--profile", "-p", help="Profile name"),
) -> None:
    root = Path.cwd()
    for d in [
        "definitions/types",
        "definitions/targets",
        "templates",
        "instances",
        "patches",
        "generated",
        "app/bronze",
        "app/silver",
        "app/gold",
        "app/rules",
    ]:
        (root / d).mkdir(parents=True, exist_ok=True)
    readme = root / "README.md"
    if not readme.exists():
        readme.write_text(f"# LOF Project\n\nProfile: {profile}\n")
    console.print(f"[green]LOF project initialized (profile: {profile})[/green]")
    console.print("  Next: define types in definitions/types/, add instances, then run lof compile")


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
    console.print(
        f"  Types: {compiler.registry.type_count}, "
        f"Instances: {compiler.registry.instance_count}, "
        f"Patches: {compiler.registry.patch_count}"
    )


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
    project = Project(Path.cwd())
    report = project.compile(
        dry_run=dry_run,
        instance_filter=instance,
        type_filter=type,
        force=force,
    )

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
        console.print("[yellow]No prior manifest. Run 'lof compile' first.[/yellow]")
        return
    project = Project(root)
    report = project.compile(dry_run=True)
    if not report.success:
        console.print("[red]Compilation failed — cannot compute diff[/red]")
        return
    old_map = {a.output: a.hash for a in old.artifacts}
    new_map = {}
    from lof.utils.hashing import compute_hash
    for a in report.artifacts_generated:
        new_map[a] = compute_hash(a)

    changes = []
    for out in sorted(set(list(old_map.keys()) + list(new_map.keys()))):
        old_h = old_map.get(out)
        new_h = new_map.get(out)
        if old_h is None:
            changes.append(f"  [green]ADDED[/green]    {out}")
        elif new_h is None:
            changes.append(f"  [red]REMOVED[/red]  {out}")
        elif old_h != new_h:
            changes.append(f"  [yellow]MODIFIED[/yellow] {out}")
    if changes:
        for c in changes:
            console.print(c)
    else:
        console.print("[green]No changes[/green]")


@app.command()
def check():
    project = Project(Path.cwd())
    report = project.check()

    all_passed = True
    for step in report.steps:
        status = "[green]PASS[/green]" if step.passed else "[red]FAIL[/red]"
        console.print(f"  {status} {step.step}")
        if not step.passed:
            all_passed = False
            for d in step.details[:5]:
                console.print(f"         {d}")

    if all_passed:
        console.print("[green]All checks passed[/green]")
    else:
        raise typer.Exit(1)


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
        table.add_row(
            s.metadata.id, str(s.metadata.level), s.metadata.category, exp, s.metadata.title
        )  # noqa: E501
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
    console.print(
        f"  Scenarios: {report.total_scenarios}, Passed: [green]{report.passed}[/green], "
        f"Failed: [red]{report.failed}[/red], Rate: {report.pass_rate:.1%}"
    )
    for r in report.results:
        s = "[green]PASS[/green]" if r.passed else "[red]FAIL[/red]"
        console.print(f"  {s} {r.scenario_id} ({r.duration_ms:.0f}ms)")
        for e in r.errors[:3]:
            console.print(f"         {e}")

    report_dir = Path.cwd() / "reports"
    report_dir.mkdir(exist_ok=True)
    (report_dir / "latest.json").write_text(json.dumps(report.model_dump(), indent=2, default=str))
    console.print("\n[blue]Report:[/blue] reports/latest.json")
