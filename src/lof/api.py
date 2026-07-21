"""Public API for the LOF framework."""

from pathlib import Path

from lof.compilation.session import ProjectSession
from lof.domain.settings import LofSettings
from lof.models.reports import (
    CheckReport,
    CompilationReport,
    SemanticValidationReport,
    StepResult,
    ValidationReport,
)


class Project:
    """Represents a LOF project at a given root directory. Main entry point."""

    def __init__(self, root: Path | None = None, settings: LofSettings | None = None):
        self.root = (root or Path.cwd()).resolve()
        self.settings = settings or LofSettings()
        self._session: ProjectSession | None = None

    @property
    def session(self) -> ProjectSession:
        if self._session is None:
            self._session = ProjectSession(self.root, self.settings)
        return self._session

    @classmethod
    def load(cls, root: Path | None = None) -> "Project":
        return cls(root)

    def validate(self) -> ValidationReport:
        compiler = self.session.new_compiler()
        errors = compiler.validate_all()
        return ValidationReport(
            valid=len(errors) == 0,
            errors=errors,
            types_loaded=compiler.registry.type_count,
            instances_loaded=compiler.registry.instance_count,
            patches_loaded=compiler.registry.patch_count,
        )

    def validate_smt(self) -> SemanticValidationReport:
        from lof.graph.instance_graph import InstanceGraph
        from lof.validation.smt.validation_engine import SemanticValidationEngine

        compiler = self.session.new_compiler()
        ig = InstanceGraph()
        ig.build(compiler.registry.instances)
        engine = SemanticValidationEngine(compiler.registry, ig)
        result = engine.validate_with_json_diagnostics(output_dir=self.root)
        return SemanticValidationReport(
            status=result.status,
            diagnostics=[d.model_dump() for d in result.diagnostics],
        )

    def compile(
        self,
        dry_run: bool = False,
        instance_filter: str | None = None,
        type_filter: str | None = None,
        force: bool = False,
    ) -> CompilationReport:
        compiler = self.session.new_compiler(
            dry_run=dry_run,
            instance_filter=instance_filter,
            type_filter=type_filter,
            force=force,
        )
        return compiler.compile()

    def check(self) -> CheckReport:
        report = CheckReport()

        v = self.validate()
        report.steps.append(StepResult(step="validate", passed=v.valid, details=v.errors))
        if not v.valid:
            return report

        smt = self.validate_smt()
        smt_passed = smt.status == "sat"
        report.steps.append(StepResult(step="smt", passed=smt_passed, details=smt.diagnostics))
        if not smt_passed:
            return report

        c = self.compile()
        report.steps.append(
            StepResult(
                step="compile",
                passed=c.success,
                details=c.errors,
            )
        )
        report.compilation = c
        if not c.success:
            return report

        from lof.compilation.artifact_validator import ArtifactValidator
        from lof.compilation.manifest import ManifestManager

        validator = ArtifactValidator(self.root)
        val_errors = validator.validate_all()
        report.steps.append(
            StepResult(step="backend_lint", passed=len(val_errors) == 0, details=val_errors)
        )
        if val_errors:
            return report

        manifest_mgr = ManifestManager(self.root)
        manifest = manifest_mgr.load()
        if manifest.artifacts:
            hashes_ok = all(len(a.hash) == 16 for a in manifest.artifacts)
            report.steps.append(StepResult(step="manifest_integrity", passed=hashes_ok))

        report.all_passed = all(s.passed for s in report.steps)
        return report

    def explain(self, target: str) -> str:
        lines = [f"Explanation for: {target}"]
        from lof.loading.loader import Loader

        loader = Loader(self.root)
        for inst in loader.load_instances_from_dir():
            if inst.id == target or inst.type == target:
                td = inst.type
                lines.append(f"  Instance: {inst.id} (type: {td})")
                lines.append(f"  Values: {dict(list(inst.values.items())[:5])}")
                if inst.relations:
                    lines.append(f"  Relations: {len(inst.relations)}")
                if inst.patches:
                    lines.append(f"  Patches: {inst.patches}")
                return "\n".join(lines)
        for t in loader.load_types_from_dir():
            if t.id == target:
                lines.append(f"  Type: {t.id}")
                if t.template:
                    lines.append(f"  Template: {t.template}")
                if t.depends_on:
                    lines.append(f"  Depends on: {t.depends_on}")
                return "\n".join(lines)
        return f"Nothing found for '{target}'"
