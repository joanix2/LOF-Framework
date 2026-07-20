import pytest
from pydantic import ValidationError

from lof.models.type_definition import ParameterDefinition, TypeDefinition


def test_type_definition_minimal():
    t = TypeDefinition(id="test-type")
    assert t.id == "test-type"
    assert t.description is None
    assert t.depends_on == []
    assert t.parameters == {}
    assert t.template is None


def test_type_definition_with_params():
    t = TypeDefinition(
        id="entity",
        description="An entity",
        depends_on=["base"],
        parameters={
            "name": ParameterDefinition(type="string", required=True),
            "count": ParameterDefinition(type="integer", default=0),
        },
        template="templates/entity.py.j2",
        target_type="python-module",
        output_pattern="generated/{{ name }}.py",
    )
    assert t.id == "entity"
    assert len(t.parameters) == 2
    assert t.parameters["name"].required
    assert t.parameters["count"].default == 0


def test_type_definition_missing_id():
    with pytest.raises(ValidationError):
        TypeDefinition()


def test_type_definition_with_enum():
    t = TypeDefinition(
        id="status-type",
        parameters={
            "status": ParameterDefinition(
                type="string",
                required=True,
                enum=["active", "inactive", "pending"],
            ),
        },
    )
    assert t.parameters["status"].enum == ["active", "inactive", "pending"]
