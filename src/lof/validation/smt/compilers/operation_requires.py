from collections.abc import Sequence

import z3

from lof.validation.smt.constraint_definition import ConstraintDefinition
from lof.validation.smt.context import ConstraintContext
from lof.validation.smt.solver import NamedAssertion


class OperationRequiresProjectionCompiler:
    constraint_type = "operation-requires-projection"

    def compile(
        self,
        definition: ConstraintDefinition,
        context: ConstraintContext,
    ) -> Sequence[NamedAssertion]:
        op = definition.parameters.get("operation", None)
        required_type = definition.parameters.get("required_type", None)
        assertions: list[NamedAssertion] = []

        for inst in context.registry.instances.values():
            operations = inst.values.get("operations", [])
            td = context.registry.get_type(inst.type)
            if td is None:
                continue

            if op is not None and op not in operations:
                continue

            if required_type:
                has_projection = required_type in context.projections_index
                if has_projection:
                    projectors = context.projections_index.get(required_type, [])
                    if inst.id not in projectors:
                        assertions.append(
                            NamedAssertion(
                                name=f"op_req_{op}_{inst.id}_{required_type}",
                                expression=z3.BoolVal(False),
                                constraint_id=definition.id,
                                instance_ids=(inst.id,),
                                json_paths=(f"$.instances.{inst.id}.values.operations",),
                                metadata={
                                    "operation": op,
                                    "required_type": required_type,
                                    "instance": inst.id,
                                    "existing_projections": projectors,
                                },
                            )
                        )

        return assertions or [
            NamedAssertion(
                name="op_req_all_ok",
                expression=z3.BoolVal(True),
                constraint_id=definition.id,
            )
        ]
