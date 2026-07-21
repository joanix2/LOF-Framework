import datetime
import shutil
import uuid
from pathlib import Path

from lof.compilation.manifest import ManifestManager
from lof.compilation.pipeline import Pipeline
from lof.domain.settings import LofSettings
from lof.graph.builder import GraphBuilder
from lof.graph.instance_graph import InstanceGraph
from lof.graph.validator import GraphValidator
from lof.loading.loader import Loader
from lof.loading.registry import Registry
from lof.models.artifact import ProjectManifest
from lof.models.reports import CompilationReport
from lof.validation.smt.validation_engine import SemanticValidationEngine


class Compiler:
    def __init__(
        self,
        root: Path | None = None,
        dry_run: bool = False,
        instance_filter: str | None = None,
        type_filter: str | None = None,
        force: bool = False,
        registry: Registry | None = None,
        settings: LofSettings | None = None,
    ):
        self.root = root or Path.cwd()
        self.dry_run = dry_run
        self.instance_filter = instance_filter
        self.type_filter = type_filter
        self.force = force
        self.loader = Loader(self.root)
        self.registry = registry or Registry()
        self.settings = settings or LofSettings()

    def load_all(self) -> None:
        if self.registry.type_count > 0:
            return
        for t in self.loader.load_types_from_dir():
            self.registry.register_type(t)
        for inst in self.loader.load_instances_from_dir():
            self.registry.register_instance(inst)
        for p in self.loader.load_patches_from_dir():
            self.registry.register_patch(p)
        for t in self.loader.load_targets_from_dir():
            self.registry.register_target(t)

    def validate_all(self) -> list[str]:
        errors: list[str] = []
        graph_builder = GraphBuilder(self.registry)
        graph = graph_builder.build()
        graph_validator = GraphValidator(self.registry)
        graph_diag = graph_validator.validate(graph)
        errors.extend(graph_diag.errors)


        return errors

    def validate_semantic(self) -> list[str]:
        errors: list[str] = []
        instance_graph = InstanceGraph()
        instance_graph.build(self.registry.instances)
        engine = SemanticValidationEngine(self.registry, instance_graph)
        result = engine.validate_with_json_diagnostics(output_dir=self.root)
        for d in result.diagnostics:
            errors.append(
                f"[{d.code}] {d.message} "
                f"(constraint: {d.constraint_id}, instances: {', '.join(d.instance_ids)})"
            )
        return errors

    def compile(self) -> CompilationReport:
        report = CompilationReport()
        self.load_all()
        report.types_loaded = self.registry.type_count
        report.instances_loaded = self.registry.instance_count
        report.patches_loaded = self.registry.patch_count

        validation_errors = self.validate_all()
        if validation_errors:
            report.errors.extend(validation_errors)
            report.success = False
            return report

        semantic_errors = self.validate_semantic()
        if semantic_errors:
            report.errors.extend(semantic_errors)
            report.success = False
            return report

        instances = list(self.registry.instances.values())
        if self.instance_filter:
            instances = [i for i in instances if i.id == self.instance_filter]
        if self.type_filter:
            instances = [i for i in instances if i.type == self.type_filter]

        staging_id = uuid.uuid4().hex[:12]
        staging_root = self.root / ".lof" / "staging" / staging_id
        manifest_manager = ManifestManager(self.root)

        pipeline = Pipeline(self.registry, self.root, self.dry_run, staging_root=staging_root)
        artifacts = []

        for inst in instances:
            if not inst.enabled:
                continue
            artifact, errors = pipeline.process_instance(inst)
            if errors:
                report.errors.extend(errors)
                break
            if artifact:
                artifacts.append(artifact)
                report.artifacts_generated.append(artifact.output)
                if artifact.patches:
                    report.artifacts_patched.append(artifact.output)

        if report.errors:
            if staging_root.exists():
                shutil.rmtree(staging_root)
            report.success = False
            return report

        new_manifest = ProjectManifest(project_hash="")
        for a in artifacts:
            new_manifest = manifest_manager.add_artifact(new_manifest, a)
        new_manifest.project_hash = manifest_manager.compute_project_hash(new_manifest)
        new_manifest.compiled_at = datetime.datetime.now().isoformat()

        generated_dir = self.root / "generated"
        staging_generated = staging_root / "generated"

        if staging_generated.exists():
            if self.dry_run:
                pass
            else:
                if generated_dir.exists():
                    shutil.rmtree(generated_dir)
                shutil.copytree(staging_generated, generated_dir, dirs_exist_ok=True)
                manifest_manager.save(new_manifest)

        if staging_root.exists():
            shutil.rmtree(staging_root)

        report.success = True
        return report

    def get_compilation_order(self) -> list[str]:
        self.load_all()
        graph_builder = GraphBuilder(self.registry)
        graph_builder.build()
        return graph_builder.get_types_in_order()
