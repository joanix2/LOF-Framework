import pytest
from lof.models.patch_definition import PatchDefinition, PatchOperation
from pydantic import ValidationError


def test_patch_definition_minimal():
    patch = PatchDefinition(
        id="test-patch",
        language="python",
        operations=[
            PatchOperation(op="add_method", name="my_method", body=["pass"]),
        ],
    )
    assert patch.id == "test-patch"
    assert len(patch.operations) == 1


def test_patch_definition_add_import():
    patch = PatchDefinition(
        id="add-typing",
        language="python",
        operations=[
            PatchOperation(op="add_import", module="typing", import_name="Optional"),
        ],
    )
    assert patch.operations[0].op == "add_import"
    assert patch.operations[0].module == "typing"


def test_patch_definition_with_deps():
    patch = PatchDefinition(
        id="advanced-patch",
        language="python",
        operations=[PatchOperation(op="add_method", name="func", body=["pass"])],
        depends_on=["base-patch"],
    )
    assert "base-patch" in patch.depends_on


def test_patch_definition_missing_operations():
    with pytest.raises(ValidationError):
        PatchDefinition(id="bad", language="python")
