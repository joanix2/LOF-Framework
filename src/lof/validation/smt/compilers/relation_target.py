from collections.abc import Sequence

import z3

from lof.validation.smt.constraint_definition import ConstraintDefinition
from lof.validation.smt.context import ConstraintContext
from lof.validation.smt.solver import NamedAssertion


class RelationTargetExistsCompiler:
    constraint_type = "relation-target-exists"

    def compile(
        self,
        definition: ConstraintDefinition,
        context: ConstraintContext,
    ) -> Sequence[NamedAssertion]:
        assertions: list[NamedAssertion] = []

        for rel in context.relations_index:
            target = rel["target"]
            exists = target in context.instances_index
            if not exists:
                assertions.append(
                    NamedAssertion(
                        name=f"rel_target_{rel['id']}",
                        expression=z3.BoolVal(False),
                        constraint_id=definition.id,
                        instance_ids=(rel["source"],),
                        json_paths=(f"$.instances.{rel['source']}.relations",),
                        metadata={
                            "message": f"Relation '{rel['id']}' targets unknown '{target}'",
                            "hint": "Create the target instance or fix the relation target.",
                            "relation_id": rel["id"],
                            "missing_target": target,
                        },
                    )
                )

        return assertions or [
            NamedAssertion(
                name="rel_targets_ok", expression=z3.BoolVal(True), constraint_id=definition.id
            )  # noqa: E501
        ]
