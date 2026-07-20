"""Public API for the LOF framework."""

from pathlib import Path
from typing import Any

from lof.compilation.compiler import Compiler
from lof.domain.settings import LofSettings


class Project:
    """Represents a LOF project at a given root directory. Main entry point."""

    def __init__(self, root: Path | None = None):
        self.root = (root or Path.cwd()).resolve()
        self.settings = LofSettings()

    @classmethod
    def load(cls, root: Path | None = None) -> "Project":
        return cls(root)

    def validate(self) -> dict[str, Any]:
        compiler = Compiler(self.root)
        compiler.load_all()
        errors = compiler.validate_all()
        return {"valid": len(errors) == 0, "errors": errors}

    def validate_smt(self) -> dict[str, Any]:
        from lof.graph.instance_graph import InstanceGraph
        from lof.validation.smt.validation_engine import SemanticValidationEngine

        compiler = Compiler(self.root)
        compiler.load_all()
        ig = InstanceGraph()
        ig.build(compiler.registry.instances)
        engine = SemanticValidationEngine(compiler.registry, ig)
        result = engine.validate_with_json_diagnostics(output_dir=self.root)
        return {
            "status": result.status,
            "diagnostics": [d.model_dump() for d in result.diagnostics],
        }  # noqa: E501

    def compile(self, dry_run: bool = False) -> dict[str, Any]:
        compiler = Compiler(self.root, dry_run=dry_run)
        report = compiler.compile()
        return {
            "success": report.success,
            "types_loaded": report.types_loaded,
            "instances_loaded": report.instances_loaded,
            "generated": report.artifacts_generated,
            "patched": report.artifacts_patched,
            "errors": report.errors,
        }

    def check(self) -> dict[str, Any]:
        result = {"steps": []}
        v = self.validate()
        result["steps"].append({"step": "validate", "passed": v["valid"]})
        if v["valid"]:
            smt = self.validate_smt()
            smt_passed = smt["status"] == "sat"
            result["steps"].append({"step": "smt", "passed": smt_passed})
            if smt_passed:
                c = self.compile()
                result["steps"].append({"step": "compile", "passed": c["success"]})
                result["compilation"] = c
        return result

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
