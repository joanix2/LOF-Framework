"""Semantic validation engine — loads constraints from profile config."""

from pathlib import Path

from lof.graph.instance_graph import InstanceGraph
from lof.loading.registry import Registry
from lof.validation.smt.constraint_definition import (
    ConstraintDefinition,
    DiagnosticDefinition,
    SolverResult,
)
from lof.validation.smt.context import ConstraintContext
from lof.validation.smt.solver import Z3SemanticSolver

_DEFAULT_CONSTRAINTS: list[ConstraintDefinition] = [
    ConstraintDefinition(
        id="relation-target-exists", type="relation-target-exists",
        description="Chaque relation doit cibler une instance existante.",
        severity="error", parameters={},
        diagnostic=DiagnosticDefinition(
            code="RELATION_TARGET_MISSING",
            message="Une relation cible une instance inexistante.",
            hint="Vérifier l'identifiant de la cible dans la relation.",
        ),
    ),
    ConstraintDefinition(
        id="required-primary-key", type="required-property",
        description="Chaque entité persistante doit avoir une clé primaire.",
        severity="error",
        parameters={"property": "primary", "type": "entity-model",
                     "condition": {"key": "enabled", "value": True},
                     "nested_in": "fields"},
        diagnostic=DiagnosticDefinition(
            code="MISSING_PRIMARY_KEY",
            message="L'entité n'a pas de clé primaire déclarée.",
            hint="Ajouter un champ avec primary: true dans les champs.",
        ),
    ),
    ConstraintDefinition(
        id="dependency-satisfied", type="dependency-satisfied",
        description="Les dépendances entre types doivent exister.",
        severity="error", parameters={"dependency_kind": "type"},
        diagnostic=DiagnosticDefinition(
            code="MISSING_DEPENDENCY",
            message="Une dépendance déclarée n'existe pas.",
            hint="Vérifier les identifiants dans dependsOn.",
        ),
    ),
    ConstraintDefinition(
        id="field-type-compatible", type="field-type-compatible",
        description="Compatibilité des valeurs par défaut avec le type du champ.",
        severity="warning", parameters={},
        diagnostic=DiagnosticDefinition(
            code="FIELD_TYPE_MISMATCH",
            message="La valeur par défaut n'est pas compatible avec le type du champ.",
            hint="Vérifier le type de la valeur par défaut.",
        ),
    ),
]


class SemanticValidationEngine:
    def __init__(self, registry: Registry, instance_graph: InstanceGraph):
        self.registry = registry
        self.instance_graph = instance_graph
        self.solver = Z3SemanticSolver()

    def build_builtin_constraints(self) -> list[ConstraintDefinition]:
        constraints = list(_DEFAULT_CONSTRAINTS)

        # Try to load profile constraints
        profile_path = Path.cwd() / "profiles" / "fastapi-react" / "profile.json"
        if profile_path.exists():
            import json
            data = json.loads(profile_path.read_text())
            for cd in data.get("builtin_constraints", []):
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
            import datetime
            import json
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
