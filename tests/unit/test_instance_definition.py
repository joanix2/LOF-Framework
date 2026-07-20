import pytest
from pydantic import ValidationError

from lof.models.instance_definition import InstanceDefinition


def test_instance_definition_minimal():
    inst = InstanceDefinition(id="test", type="entity")
    assert inst.id == "test"
    assert inst.type == "entity"
    assert inst.values == {}
    assert inst.patches == []
    assert inst.enabled is True


def test_instance_definition_with_values():
    inst = InstanceDefinition(
        id="customer",
        type="python-entity",
        values={"name": "Customer", "fields": [{"name": "id", "type": "UUID"}]},
        patches=["add-timestamp"],
    )
    assert inst.values["name"] == "Customer"
    assert len(inst.patches) == 1


def test_instance_definition_disabled():
    inst = InstanceDefinition(id="test", type="entity", enabled=False)
    assert inst.enabled is False


def test_instance_definition_missing_type():
    with pytest.raises(ValidationError):
        InstanceDefinition(id="test")


def test_instance_definition_missing_id():
    with pytest.raises(ValidationError):
        InstanceDefinition(type="entity")
