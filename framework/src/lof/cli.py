import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table
from rich.tree import Tree

from lof.compilation.compiler import Compiler
from lof.compilation.manifest import ManifestManager
from lof.graph.builder import GraphBuilder
from lof.graph.validator import GraphValidator
from lof.loading.loader import Loader

app = typer.Typer(
    name="lof",
    help="Language-Oriented Programming Framework",
    no_args_is_help=True,
)
console = Console()


@app.command()
def init() -> None:
    """Initialize a new LOF project in the current directory."""
    root = Path.cwd()
    dirs = [
        "definitions/types",
        "definitions/targets",
        "templates/python",
        "templates/typescript",
        "templates/markdown",
        "templates/mermaid",
        "instances",
        "patches/python",
        "patches/typescript",
        "interfaces/python",
        "interfaces/typescript",
        "generated/python",
        "generated/typescript",
        "generated/docs",
        "generated/diagrams",
    ]
    for d in dirs:
        (root / d).mkdir(parents=True, exist_ok=True)
    console.print("[green]LOF project initialized[/green]")


@app.command()
def validate() -> None:
    """Validate all JSON definitions and semantic constraints."""
    root = Path.cwd()
    compiler = Compiler(root)
    compiler.load_all()
    errors = compiler.validate_all()
    if errors:
        for e in errors:
            console.print(f"[red]ERROR:[/red] {e}")
        raise typer.Exit(1)
    else:
        types = compiler.registry.type_count
        instances = compiler.registry.instance_count
        patches = compiler.registry.patch_count
        console.print("[green]Validation passed[/green]")
        console.print(f"  Types: {types}")
        console.print(f"  Instances: {instances}")
        console.print(f"  Patches: {patches}")


@app.command()
def graph(
    format: str = typer.Option("text", "--format", "-f", help="Output format: text or mermaid"),
) -> None:
    """Display the dependency graph."""
    root = Path.cwd()
    compiler = Compiler(root)
    compiler.load_all()
    builder = GraphBuilder(compiler.registry)
    builder.build()

    if format == "mermaid":
        console.print(builder.to_mermaid())
        return

    order = builder.get_types_in_order()
    tree = Tree("Dependency Graph")
    for type_id in order:
        node_data = builder.graph.nodes.get(type_id)
        if node_data and node_data.get("type") == "type":
            t = compiler.registry.get_type(type_id)
            if t:
                branch = tree.add(f"[bold]{type_id}[/bold]")
                if t.depends_on:
                    deps = branch.add("depends on")
                    for dep in t.depends_on:
                        deps.add(dep)
                instances = compiler.registry.instances_for_type(type_id)
                if instances:
                    insts = branch.add("instances")
                    for inst in instances:
                        insts.add(inst.id)

    console.print(tree)

    cycles_diag = GraphValidator(compiler.registry).validate(builder.graph)
    if cycles_diag.has_errors:
        console.print("\n[red]Cycle detected![/red]")
        for e in cycles_diag.errors:
            console.print(f"  [red]{e}[/red]")
    else:
        console.print("\n[green]No cycles[/green]")
        console.print(f"Compilation order: {' -> '.join(order)}")


@app.command(name="compile")
def compile_cmd(
    instance: str | None = typer.Option(
        None, "--instance", "-i", help="Compile a specific instance"
    ),
    type: str | None = typer.Option(None, "--type", "-t", help="Compile all instances of a type"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be generated"),
    force: bool = typer.Option(False, "--force", help="Force regeneration"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Compile the project or specific parts."""
    root = Path.cwd()
    compiler = Compiler(root, dry_run=dry_run)
    report = compiler.compile()

    if json_output:
        console.print(json.dumps(report.model_dump(), indent=2))
        return

    if report.errors:
        for e in report.errors:
            console.print(f"[red]ERROR:[/red] {e}")
        raise typer.Exit(1)

    console.print("[green]Compilation successful[/green]")
    console.print(f"  Types loaded: {report.types_loaded}")
    console.print(f"  Instances loaded: {report.instances_loaded}")
    console.print(f"  Patches loaded: {report.patches_loaded}")
    console.print(f"  Generated: {len(report.artifacts_generated)} files")
    for a in report.artifacts_generated:
        console.print(f"    - {a}")
    if report.artifacts_patched:
        console.print(f"  Patched: {len(report.artifacts_patched)} files")
        for a in report.artifacts_patched:
            console.print(f"    - {a}")


@app.command()
def inspect(
    what: str = typer.Argument(..., help="What to inspect: type or instance"),
    id: str = typer.Option(..., "--id", help="ID of the type or instance"),
) -> None:
    """Inspect a type or instance definition."""
    root = Path.cwd()
    loader = Loader(root)

    if what == "type":
        types = loader.load_types_from_dir()
        for t in types:
            if t.id == id:
                data = t.model_dump(exclude_none=True)
                console.print(json.dumps(data, indent=2, default=str))
                return
        console.print(f"[red]Type '{id}' not found[/red]")
        raise typer.Exit(1)
    elif what == "instance":
        instances = loader.load_instances_from_dir()
        for inst in instances:
            if inst.id == id:
                data = inst.model_dump(exclude_none=True)
                console.print(json.dumps(data, indent=2, default=str))
                return
        console.print(f"[red]Instance '{id}' not found[/red]")
        raise typer.Exit(1)
    else:
        console.print("[red]Must specify 'type' or 'instance'[/red]")
        raise typer.Exit(1)


@app.command()
def diff() -> None:
    """Show differences between last compiled state and current state."""
    root = Path.cwd()
    manifest_manager = ManifestManager(root)
    old_manifest = manifest_manager.load()
    if not old_manifest.artifacts:
        console.print("[yellow]No prior manifest found. Run compile first.[/yellow]")
        return

    compiler = Compiler(root, dry_run=True)
    report = compiler.compile()

    from lof.models.artifact import Artifact, ProjectManifest
    from lof.utils.hashing import compute_hash

    new_artifacts = []
    for a in report.artifacts_generated:
        new_artifacts.append(
            Artifact(
                instance="",
                type="",
                output=a,
                hash=compute_hash(""),
            )
        )
    new_manifest = ProjectManifest(project_hash="", artifacts=new_artifacts)
    changes = manifest_manager.diff(old_manifest, new_manifest)
    if changes:
        for c in changes:
            console.print(c)
    else:
        console.print("[green]No changes detected[/green]")


@app.command()
def check() -> None:
    """Run all validation checks."""
    root = Path.cwd()
    compiler = Compiler(root)
    compiler.load_all()
    errors = compiler.validate_all()
    if errors:
        for e in errors:
            console.print(f"[red]ERROR:[/red] {e}")
        raise typer.Exit(1)
    console.print("[green]All checks passed[/green]")


@app.command()
def clean() -> None:
    """Remove all generated files."""
    root = Path.cwd()
    import shutil

    gen_dir = root / "generated"
    if gen_dir.exists():
        shutil.rmtree(gen_dir)
        gen_dir.mkdir()
        console.print("[green]Cleaned generated/ directory[/green]")
    else:
        console.print("[yellow]No generated/ directory to clean[/yellow]")


@app.command()
def manifest() -> None:
    """Display the current build manifest."""
    root = Path.cwd()
    manifest_manager = ManifestManager(root)
    m = manifest_manager.load()
    if m.artifacts:
        table = Table(title="Build Manifest")
        table.add_column("Instance", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Output", style="blue")
        table.add_column("Hash", style="yellow")
        for a in m.artifacts:
            table.add_row(a.instance, a.type, a.output, a.hash)
        console.print(table)
        console.print(f"Project hash: {m.project_hash}")
    else:
        console.print("[yellow]No artifacts in manifest (run compile first)[/yellow]")


def main() -> None:
    app()


if __name__ == "__main__":
    app()
