from collections.abc import Sequence
from typing import Any

import z3

from lof.validation.smt.constraint_definition import ConstraintDefinition
from lof.validation.smt.context import ConstraintContext
from lof.validation.smt.solver import NamedAssertion


class UniquePropertyCompiler:
    constraint_type = "unique-property"

    def compile(
        self,
        definition: ConstraintDefinition,
        context: ConstraintContext,
    ) -> Sequence[NamedAssertion]:
        prop = definition.parameters.get("property", "id")
        scope = definition.parameters.get("scope", "global")
        assertions: list[NamedAssertion] = []

        groups: dict[str, list[dict[str, Any]]] = {}

        for inst in context.registry.instances.values():
            if prop not in inst.values:
                continue
            val = inst.values.get(prop, "")
            if scope == "type":
                key = f"{inst.type}:{val}"
            else:
                key = str(val)
            groups.setdefault(key, []).append({"id": inst.id, "value": val, "type": inst.type})

        for key, items in groups.items():
            if len(items) > 1:
                ids = [i["id"] for i in items]
                dups = ", ".join(ids)
                display_val = items[0]["value"]
                assertions.append(
                    NamedAssertion(
                        name=f"unique_{prop}_{key}",
                        expression=z3.BoolVal(False),
                        constraint_id=definition.id,
                        instance_ids=tuple(ids),
                        json_paths=tuple(f"$.instances.{i}.values.{prop}" for i in ids),
                        metadata={
                            "property": prop,
                            "value": display_val,
                            "duplicates": dups,
                            "message": f"Duplicate {prop}: '{display_val}' used by {dups}",
                            "hint": "Rename one of the instances to use a different value.",
                        },
                    )
                )

        if not assertions:
            assertions.append(
                NamedAssertion(
                    name=f"unique_{prop}_ok",
                    expression=z3.BoolVal(True),
                    constraint_id=definition.id,
                )
            )

        return assertions
