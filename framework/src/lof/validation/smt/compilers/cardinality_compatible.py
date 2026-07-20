from collections.abc import Sequence
from typing import Any

import z3

from lof.validation.smt.constraint_definition import ConstraintDefinition
from lof.validation.smt.context import ConstraintContext
from lof.validation.smt.solver import NamedAssertion


class CardinalityCompatibleCompiler:
    constraint_type = "relation-cardinality-compatible"

    def compile(
        self,
        definition: ConstraintDefinition,
        context: ConstraintContext,
    ) -> Sequence[NamedAssertion]:
        assertions: list[NamedAssertion] = []
        inverse_map: dict[str, list[dict[str, Any]]] = {}

        for rel in context.relations_index:
            inv = rel.get("inverse")
            if inv:
                inverse_map.setdefault(inv, []).append(rel)

        for rel in context.relations_index:
            inv_name = rel.get("inverse")
            if inv_name and inv_name in inverse_map:
                inverses = inverse_map[inv_name]
                for inv_rel in inverses:
                    if inv_rel["source"] != rel["target"] or inv_rel["target"] != rel["source"]:
                        assertions.append(NamedAssertion(
                            name=f"cardinality_{rel['id']}",
                            expression=z3.BoolVal(False),
                            constraint_id=definition.id,
                            instance_ids=(rel["source"], inv_rel["source"]),
                            json_paths=(
                                f"$.instances.{rel['source']}.relations.{rel['id']}",
                                f"$.instances.{inv_rel['source']}.relations.{inv_rel['id']}",
                            ),
                            metadata={
                                "relation": rel["id"],
                                "inverse_relation": inv_rel["id"],
                                "expected_source": rel["target"],
                                "actual_source": inv_rel["source"],
                            },
                        ))

        return assertions or [
            NamedAssertion(
                name="cardinality_all_ok",
                expression=z3.BoolVal(True),
                constraint_id=definition.id,
            )
        ]
