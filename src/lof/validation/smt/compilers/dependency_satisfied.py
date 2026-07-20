from collections.abc import Sequence

import z3

from lof.validation.smt.constraint_definition import ConstraintDefinition
from lof.validation.smt.context import ConstraintContext
from lof.validation.smt.solver import NamedAssertion


class DependencySatisfiedCompiler:
    constraint_type = "dependency-satisfied"

    def compile(
        self,
        definition: ConstraintDefinition,
        context: ConstraintContext,
    ) -> Sequence[NamedAssertion]:
        kind = definition.parameters.get("dependency_kind", "type")
        assertions: list[NamedAssertion] = []

        if kind == "type":
            for t in context.registry.types.values():
                for dep in t.depends_on:
                    if dep not in context.registry.types:
                        assertions.append(
                            NamedAssertion(
                                name=f"dep_{t.id}_{dep}",
                                expression=z3.BoolVal(False),
                                constraint_id=definition.id,
                                type_ids=(t.id,),
                                json_paths=(f"$.types.{t.id}.depends_on",),
                                metadata={
                                    "message": f"Type '{t.id}' depends on unknown type '{dep}'",
                                    "hint": "Create the missing type definition or fix the dependency.",  # noqa: E501
                                    "missing_dep": dep,
                                },
                            )
                        )

        return assertions or [
            NamedAssertion(name="deps_ok", expression=z3.BoolVal(True), constraint_id=definition.id)
        ]
