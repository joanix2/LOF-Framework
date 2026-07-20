from collections.abc import Sequence

import z3

from lof.validation.smt.constraint_definition import ConstraintDefinition
from lof.validation.smt.context import ConstraintContext
from lof.validation.smt.solver import NamedAssertion


class RequiredPropertyCompiler:
    constraint_type = "required-property"

    def compile(
        self,
        definition: ConstraintDefinition,
        context: ConstraintContext,
    ) -> Sequence[NamedAssertion]:
        prop = definition.parameters.get("property", "primary")
        target_type = definition.parameters.get("type", None)
        condition = definition.parameters.get("condition", None)
        nested_in = definition.parameters.get("nested_in", None)
        assertions: list[NamedAssertion] = []

        for inst in context.registry.instances.values():
            if target_type and inst.type != target_type:
                continue

            if condition:
                cond_key = condition.get("key", "")
                cond_val = condition.get("value", None)
                if cond_key == "enabled":
                    if not inst.enabled:
                        continue
                elif inst.values.get(cond_key) != cond_val:
                    continue

            if nested_in:
                items = inst.values.get(nested_in, [])
                found = any(item.get(prop, False) for item in items)
            else:
                found = prop in inst.values

            if not found:
                assertions.append(
                    NamedAssertion(
                        name=f"required_{prop}_{inst.id}",
                        expression=z3.BoolVal(False),
                        constraint_id=definition.id,
                        instance_ids=(inst.id,),
                        json_paths=(f"$.instances.{inst.id}.values.{nested_in or prop}",),
                        metadata={
                            "message": f"'{inst.id}' missing {prop}=True in {nested_in or 'values'}",  # noqa: E501
                            "hint": f"Add '{prop}: true' to the appropriate location.",
                        },
                    )
                )

        return assertions or [
            NamedAssertion(
                name=f"required_{prop}_ok", expression=z3.BoolVal(True), constraint_id=definition.id
            )  # noqa: E501
        ]
