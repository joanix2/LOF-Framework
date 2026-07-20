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


class SemanticValidationEngine:
    def __init__(self, registry: Registry, instance_graph: InstanceGraph):
        self.registry = registry
        self.instance_graph = instance_graph
        self.solver = Z3SemanticSolver()

    def build_builtin_constraints(self) -> list[ConstraintDefinition]:
        constraints: list[ConstraintDefinition] = []

        constraints.append(
            ConstraintDefinition(
                id="unique-api-route",
                type="unique-property",
                description="Les routes API doivent être uniques.",
                severity="error",
                parameters={"property": "route", "scope": "type"},
                diagnostic=DiagnosticDefinition(
                    code="DUPLICATE_API_ROUTE",
                    message="Deux instances utilisent la même route API.",
                    hint="Renommer une route ou fusionner les ressources.",
                ),
            )
        )

        constraints.append(
            ConstraintDefinition(
                id="unique-table-name",
                type="unique-property",
                description="Les noms de tables doivent être uniques.",
                severity="error",
                parameters={"property": "tableName", "scope": "type"},
                diagnostic=DiagnosticDefinition(
                    code="DUPLICATE_TABLE_NAME",
                    message="Deux instances utilisent le même nom de table.",
                    hint="Vérifier les noms de tables dans les définitions d'entités.",
                ),
            )
        )

        constraints.append(
            ConstraintDefinition(
                id="relation-target-exists",
                type="relation-target-exists",
                description="Chaque relation doit cibler une instance existante.",
                severity="error",
                parameters={},
                diagnostic=DiagnosticDefinition(
                    code="RELATION_TARGET_MISSING",
                    message="Une relation cible une instance inexistante.",
                    hint="Vérifier l'identifiant de la cible dans la relation.",
                ),
            )
        )

        constraints.append(
            ConstraintDefinition(
                id="required-primary-key",
                type="required-property",
                description="Chaque entité persistante doit avoir une clé primaire.",
                severity="error",
                parameters={
                    "property": "primary",
                    "type": "entity-model",
                    "condition": {"key": "enabled", "value": True},
                    "nested_in": "fields",
                },
                diagnostic=DiagnosticDefinition(
                    code="MISSING_PRIMARY_KEY",
                    message="L'entité n'a pas de clé primaire déclarée.",
                    hint="Ajouter un champ avec primary: true dans les champs.",
                ),
            )
        )

        constraints.append(
            ConstraintDefinition(
                id="acyclic-relations",
                type="acyclic-relation",
                description="Les relations ne doivent pas former de cycle.",  # noqa: E501
                severity="error",
                parameters={"kinds": ["many-to-one", "one-to-one"]},
                diagnostic=DiagnosticDefinition(
                    code="CYCLIC_RELATION",
                    message="Un cycle a été détecté dans les relations.",
                    hint="Vérifier les relations inverses et les dépendances.",
                ),
            )
        )

        constraints.append(
            ConstraintDefinition(
                id="field-type-compatible",
                type="field-type-compatible",
                description="Compatibilité des valeurs par défaut avec le type du champ.",
                severity="warning",
                parameters={},
                diagnostic=DiagnosticDefinition(
                    code="FIELD_TYPE_MISMATCH",
                    message="La valeur par défaut n'est pas compatible avec le type du champ.",
                    hint="Vérifier le type de la valeur par défaut.",
                ),
            )
        )

        constraints.append(
            ConstraintDefinition(
                id="dependency-satisfied",
                type="dependency-satisfied",
                description="Les dépendances entre types doivent exister.",  # noqa: E501
                severity="error",
                parameters={"dependency_kind": "type"},
                diagnostic=DiagnosticDefinition(
                    code="MISSING_DEPENDENCY",
                    message="Une dépendance déclarée n'existe pas dans les types.",
                    hint="Vérifier les identifiants dans dependsOn.",
                ),
            )
        )

        return constraints

    def validate(
        self,
        additional_constraints: list[ConstraintDefinition] | None = None,
    ) -> SolverResult:
        context = ConstraintContext.build(self.registry, self.instance_graph)
        constraints = self.build_builtin_constraints()
        if additional_constraints:
            constraints.extend(additional_constraints)
        return self.solver.validate(context, constraints)

    def validate_with_json_diagnostics(
        self,
        output_dir: Path | None = None,
    ) -> SolverResult:
        result = self.validate()

        if output_dir:
            import datetime
            import json

            diag_dir = output_dir / ".lof" / "diagnostics"
            diag_dir.mkdir(parents=True, exist_ok=True)
            diag_file = diag_dir / "latest.json"
            diag_file.write_text(
                json.dumps(
                    {
                        "status": result.status,
                        "timestamp": datetime.datetime.now().isoformat(),
                        "summary": f"{len(result.diagnostics)} violation(s) trouvée(s).",
                        "violations": [d.model_dump() for d in result.diagnostics],
                        "statistics": result.statistics,
                    },
                    indent=2,
                    ensure_ascii=False,
                )
            )

        return result
