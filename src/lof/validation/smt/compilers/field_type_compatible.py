from collections.abc import Sequence

import z3

from lof.validation.smt.constraint_definition import ConstraintDefinition
from lof.validation.smt.context import ConstraintContext
from lof.validation.smt.solver import NamedAssertion

_TYPE_MAP = {
    "string": (str,),
    "email": (str,),
    "url": (str,),
    "text": (str,),
    "enum": (str,),
    "uuid": (str,),
    "integer": (int,),
    "int": (int,),
    "float": (float,),
    "decimal": (float,),
    "boolean": (bool,),
    "bool": (bool,),
    "datetime": (str,),
    "date": (str,),
}


class FieldTypeCompatibleCompiler:
    constraint_type = "field-type-compatible"

    def compile(
        self,
        definition: ConstraintDefinition,
        context: ConstraintContext,
    ) -> Sequence[NamedAssertion]:
        assertions: list[NamedAssertion] = []

        for inst in context.registry.instances.values():
            fields = inst.values.get("fields", [])
            for i, field in enumerate(fields):
                f_type = field.get("type", "string")
                default = field.get("default")
                if default is not None:
                    expected = _TYPE_MAP.get(f_type, (str,))
                    if not isinstance(default, expected):
                        fname = field.get("name", f"index_{i}")
                        assertions.append(
                            NamedAssertion(
                                name=f"field_type_{inst.id}_{fname}",
                                expression=z3.BoolVal(False),
                                constraint_id=definition.id,
                                instance_ids=(inst.id,),
                                json_paths=(f"$.instances.{inst.id}.values.fields[{i}].default",),
                                metadata={
                                    "message": f"Field '{fname}': {f_type} vs {type(default).__name__}",  # noqa: E501
                                    "hint": "Change the default value to match the field type.",
                                    "field": fname,
                                    "expected_type": f_type,
                                    "actual_type": type(default).__name__,
                                },
                            )
                        )

        return assertions or [
            NamedAssertion(
                name="field_types_ok", expression=z3.BoolVal(True), constraint_id=definition.id
            )  # noqa: E501
        ]
