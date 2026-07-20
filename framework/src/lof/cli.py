import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import typer
from rich.console import Console
from rich.table import Table
from rich.tree import Tree

from lof.bronze.models import BronzeEntry
from lof.bronze.store import BronzeStore
from lof.compilation.compiler import Compiler
from lof.compilation.manifest import ManifestManager
from lof.graph.builder import GraphBuilder
from lof.graph.instance_graph import InstanceGraph
from lof.graph.validator import GraphValidator
from lof.loading.loader import Loader
from lof.silver.extractor import IntentExtractor
from lof.silver.gold_builder import GoldCandidateBuilder
from lof.silver.graph import SilverGraph
from lof.validation.smt.validation_engine import SemanticValidationEngine

app = typer.Typer(
    name="lof",
    help="Language-Oriented Programming Framework",
    no_args_is_help=True,
)
console = Console()


@app.command()
def init() -> None:
    root = Path.cwd()
    dirs = [
        "definitions/types", "definitions/targets",
        "templates/python", "templates/typescript",
        "templates/markdown", "templates/mermaid",
        "instances", "patches/python", "patches/typescript",
        "interfaces/python", "interfaces/typescript",
        "generated/python", "generated/typescript",
        "generated/docs", "generated/diagrams",
    ]
    for d in dirs:
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
    console.print(f"  Types: {compiler.registry.type_count}")
    console.print(f"  Instances: {compiler.registry.instance_count}")
    console.print(f"  Patches: {compiler.registry.patch_count}")


@app.command()
def graph(
    format: str = typer.Option("text", "--format", "-f", help="Output format: text or mermaid"),
) -> None:
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
    diagnostics_json: bool = typer.Option(False, "--diagnostics-json"),
) -> None:
    root = Path.cwd()
    compiler = Compiler(root, dry_run=dry_run)
    report = compiler.compile()

    if json_output or diagnostics_json:
        console.print(json.dumps(report.model_dump(), indent=2))
        if report.errors:
            ec = 3 if any('UNSAT' in e or 'DUPLICATE' in e for e in report.errors) else 5
            raise typer.Exit(ec)
        return

    if report.errors:
        for e in report.errors:
            tag = 'SMT ERROR' if 'UNSAT' in e or 'DUPLICATE' in e else 'ERROR'
            console.print(f'[red]{tag}:[/red] {e}')
        raise typer.Exit(3)

    console.print("[green]Compilation successful[/green]")
    console.print(f"  Types: {report.types_loaded}, Instances: {report.instances_loaded}")
    console.print(f"  Generated: {len(report.artifacts_generated)} files")
    for a in report.artifacts_generated:
        console.print(f"    - {a}")
    if report.artifacts_patched:
        console.print(f"  Patched: {len(report.artifacts_patched)} files")
        for a in report.artifacts_patched:
            console.print(f"    - {a}")


@app.command()
def inspect(
    what: str = typer.Argument(..., help="type or instance"),
    id: str = typer.Option(..., "--id"),
) -> None:
    root = Path.cwd()
    loader = Loader(root)
    if what == "type":
        for t in loader.load_types_from_dir():
            if t.id == id:
                console.print(json.dumps(t.model_dump(exclude_none=True), indent=2, default=str))
                return
        console.print(f"[red]Type '{id}' not found[/red]")
        raise typer.Exit(1)
    elif what == "instance":
        for inst in loader.load_instances_from_dir():
            if inst.id == id:
                console.print(json.dumps(inst.model_dump(exclude_none=True), indent=2, default=str))
                return
        console.print(f"[red]Instance '{id}' not found[/red]")
        raise typer.Exit(1)
    console.print("[red]Must specify 'type' or 'instance'[/red]")
    raise typer.Exit(1)


@app.command()
def diff() -> None:
    root = Path.cwd()
    manifest_manager = ManifestManager(root)
    old_manifest = manifest_manager.load()
    if not old_manifest.artifacts:
        console.print("[yellow]No prior manifest found.[/yellow]")
        return
    compiler = Compiler(root, dry_run=True)
    report = compiler.compile()
    from lof.models.artifact import Artifact, ProjectManifest
    from lof.utils.hashing import compute_hash
    new_artifacts = [
        Artifact(instance="", type="", output=a, hash=compute_hash(""))
        for a in report.artifacts_generated
    ]
    new_manifest = ProjectManifest(project_hash="", artifacts=new_artifacts)
    changes = manifest_manager.diff(old_manifest, new_manifest)
    if changes:
        for c in changes:
            console.print(c)
    else:
        console.print("[green]No changes[/green]")


@app.command()
def check() -> None:
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
    import shutil
    root = Path.cwd()
    for d in [root / "generated", root / "generated-project"]:
        if d.exists():
            shutil.rmtree(d)
            d.mkdir(exist_ok=True)
    console.print("[green]Cleaned generated directories[/green]")


@app.command()
def manifest() -> None:
    root = Path.cwd()
    m = ManifestManager(root).load()
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


constraints_app = typer.Typer(help="SMT semantic constraint management")
app.add_typer(constraints_app, name="constraints")


@constraints_app.command("list")
def constraints_list() -> None:
    engine = _engine()
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
def constraints_validate(
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    root = Path.cwd()
    compiler = Compiler(root)
    compiler.load_all()
    instance_graph = InstanceGraph()
    instance_graph.build(compiler.registry.instances)
    engine = SemanticValidationEngine(compiler.registry, instance_graph)
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
        console.print("[yellow]UNKNOWN[/yellow] — Solver returned unknown.")
        raise typer.Exit(4)


@constraints_app.command("inspect")
def constraints_inspect(
    id: str = typer.Argument(..., help="Constraint ID"),
) -> None:
    engine = _engine()
    for c in engine.build_builtin_constraints():
        if c.id == id:
            console.print(json.dumps(c.model_dump(), indent=2))
            return
    console.print(f"[red]Constraint '{id}' not found[/red]")
    raise typer.Exit(1)


@constraints_app.command("explain")
def constraints_explain(
    code: str = typer.Argument(..., help="Diagnostic error code"),
) -> None:
    engine = _engine()
    diag_path = Path.cwd() / ".lof" / "diagnostics" / "latest.json"
    if diag_path.exists():
        data = json.loads(diag_path.read_text())
        for v in data.get("violations", []):
            if v.get("code") == code:
                console.print(f"[bold]Code:[/bold] {v['code']}")
                console.print(f"[bold]Message:[/bold] {v['message']}")
                if v.get("hint"):
                    console.print(f"[bold]Hint:[/bold] {v['hint']}")
                if v.get("constraint_id"):
                    for c in engine.build_builtin_constraints():
                        if c.id == v["constraint_id"]:
                            console.print(f"[bold]Constraint:[/bold] {c.id} ({c.type})")
                if v.get("instance_ids"):
                    console.print(f"[bold]Instances:[/bold] {', '.join(v['instance_ids'])}")
                if v.get("json_paths"):
                    console.print(f"[bold]JSON paths:[/bold] {', '.join(v['json_paths'])}")
                return
    console.print(f"[yellow]No diagnostics found for code '{code}'.[/yellow]")


def _engine() -> SemanticValidationEngine:
    root = Path.cwd()
    compiler = Compiler(root)
    compiler.load_all()
    instance_graph = InstanceGraph()
    instance_graph.build(compiler.registry.instances)
    return SemanticValidationEngine(compiler.registry, instance_graph)


bronze_app = typer.Typer(help="Bronze layer: raw expression storage (append-only)")
app.add_typer(bronze_app, name="bronze")


@bronze_app.command("add")
def bronze_add(
    content: str = typer.Argument(..., help="Raw expression content"),
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
    path = store.append_entry(entry)
    console.print(f"[green]Bronze entry saved:[/green] {path.name}")

    silver = SilverGraph()
    extractor = IntentExtractor(silver)
    claims = extractor.extract_from_entry(entry)
    for c in claims:
        silver.add_claim(c)
        console.print(f"  [cyan]Claim:[/cyan] {c.subject} {c.predicate} {c.object} ({c.status})")
    silver.save(root)

    if silver.contradictions:
        console.print(f"[yellow]Contradictions detected: {len(silver.contradictions)}[/yellow]")
        for c in silver.contradictions.values():
            console.print(f"  {c.description}")


@bronze_app.command("list")
def bronze_list() -> None:
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


silver_app = typer.Typer(help="Silver layer: semantic graph (open world)")
app.add_typer(silver_app, name="silver")


@silver_app.command("status")
def silver_status() -> None:
    silver = SilverGraph.load(Path.cwd())
    console.print("[bold]Silver Graph:[/bold]")
    console.print(f"  Entities: {len(silver.entities)}")
    console.print(f"  Claims: {len(silver.claims)}")
    console.print(f"  Relations: {len(silver.relations)}")
    console.print(f"  Contradictions: {len(silver.contradictions)}")
    resolved = sum(1 for c in silver.contradictions.values() if c.resolved)
    if silver.contradictions:
        console.print(f"  Resolved: {resolved}/{len(silver.contradictions)}")
        for c in silver.contradictions.values():
            status = "[green]resolved[/green]" if c.resolved else "[red]unresolved[/red]"
            console.print(f"    [{status}] {c.description}")


@silver_app.command("claims")
def silver_claims(
    subject: str | None = typer.Option(None, "--subject", "-s"),
) -> None:
    silver = SilverGraph.load(Path.cwd())
    claims = silver.get_claims_for_subject(subject) if subject else list(silver.claims.values())
    if not claims:
        console.print("[yellow]No claims.[/yellow]")
        return
    table = Table(title=f"Silver Claims{' for ' + subject if subject else ''}")
    table.add_column("ID", style="cyan")
    table.add_column("Subject", style="blue")
    table.add_column("Predicate", style="green")
    table.add_column("Object", style="yellow")
    table.add_column("Status")
    table.add_column("Confidence")
    for c in claims:
        sobj = str(c.object)[:28]
        table.add_row(c.id, c.subject, c.predicate, sobj, c.status, f"{c.confidence:.2f}")
    console.print(table)


gold_app = typer.Typer(help="Gold layer: canonical DSL generation")
app.add_typer(gold_app, name="gold")


@gold_app.command("build")
def gold_build(
    output: str = typer.Option("instances", "--output", "-o", help="Output subdir"),
) -> None:
    root = Path.cwd()
    silver = SilverGraph.load(root)
    builder = GoldCandidateBuilder(silver)
    paths = builder.write_gold_candidate(root)
    console.print(f"[green]Gold candidates generated:[/green] {len(paths)} files")
    for p in paths:
        console.print(f"  - {p.relative_to(root)}")

    if silver.contradictions:
        unresolved = [c for c in silver.contradictions.values() if not c.resolved]
        if unresolved:
            console.print(f"[yellow]{len(unresolved)} unresolved contradiction(s).[/yellow]")


@gold_app.command("provenance")
def gold_provenance(
    instance_id: str = typer.Argument(..., help="Instance ID to trace"),
) -> None:
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
    console.print(f"[bold]Provenance for '{instance_id}':[/bold]")
    subject_prefix = instance_id.split("-")[0].capitalize()
    ref_count = sum(1 for c in silver.claims.values() if c.subject == subject_prefix)
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
            console.print(f"    - \"{s}\"")


def main() -> None:
    app()


if __name__ == "__main__":
    app()
