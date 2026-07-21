"""Semantic validation engine — loads constraints from profile config only."""

from pathlib import Path

from lof.graph.instance_graph import InstanceGraph
from lof.loading.registry import Registry
from lof.validation.smt.constraint_definition import (
    ConstraintDefinition, DiagnosticDefinition, SolverResult,
)
from lof.validation.smt.context import ConstraintContext
from lof.validation.smt.solver import Z3SemanticSolver


class SemanticValidationEngine:
    def __init__(self, registry: Registry, instance_graph: InstanceGraph):
        self.registry = registry
        self.instance_graph = instance_graph
        self.solver = Z3SemanticSolver()

    def build_builtin_constraints(self) -> list[ConstraintDefinition]:
        constraints: list[ConstraintDefinition] = []

        constraints_dir = Path.cwd() / ".lof" / "constraints"
        if constraints_dir.exists():
            for f in sorted(constraints_dir.glob("*.json")):
                import json
                cd = json.loads(f.read_text())
                constraints.append(ConstraintDefinition(
                    id=cd["id"], type=cd["type"],
                    severity=cd.get("severity", "error"),
                    parameters=cd.get("parameters", {}),
                    diagnostic=DiagnosticDefinition(
                        code=cd.get("diagnostic", {}).get("code", "UNKNOWN"),
                        message=cd.get("diagnostic", {}).get("message", ""),
                        hint=cd.get("diagnostic", {}).get("hint"),
                    ),
                    description=cd.get("description"),
                ))

        return constraints

    def validate(self, additional: list[ConstraintDefinition] | None = None) -> SolverResult:
        ctx = ConstraintContext.build(self.registry, self.instance_graph)
        constraints = self.build_builtin_constraints()
        if additional:
            constraints.extend(additional)
        return self.solver.validate(ctx, constraints)

    def validate_with_json_diagnostics(self, output_dir: Path | None = None) -> SolverResult:
        result = self.validate()
        if output_dir:
            import json, datetime
            diag_dir = output_dir / ".lof" / "diagnostics"
            diag_dir.mkdir(parents=True, exist_ok=True)
            diag_file = diag_dir / "latest.json"
            diag_file.write_text(json.dumps({
                "status": result.status,
                "timestamp": datetime.datetime.now().isoformat(),
                "summary": f"{len(result.diagnostics)} violation(s).",
                "violations": [d.model_dump() for d in result.diagnostics],
            }, indent=2, ensure_ascii=False))
        return result
