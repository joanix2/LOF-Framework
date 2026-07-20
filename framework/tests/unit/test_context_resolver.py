"""Tests for context resolution (parameter inheritance + graph context)."""

from lof.compilation.pipeline import Pipeline
from lof.loading.registry import Registry
from lof.models.instance_definition import InstanceDefinition
from lof.models.type_definition import ParameterDefinition, TypeDefinition


def _make_registry() -> Registry:
    r = Registry()
    r.register_type(TypeDefinition(
        id="entity",
        parameters={
            "name": ParameterDefinition(type="string", required=True),
            "count": ParameterDefinition(type="integer", default=1),
        },
    ))
    return r


def test_context_includes_instance_values():
    reg = _make_registry()
    reg.register_instance(InstanceDefinition(id="test", type="entity", values={"name": "Test"}))
    pipeline = Pipeline(reg)
    ctx = pipeline._build_context(reg.get_instance("test"))
    assert ctx["name"] == "Test"
    assert ctx["instance_id"] == "test"


def test_context_includes_defaults():
    reg = _make_registry()
    reg.register_instance(InstanceDefinition(id="test", type="entity", values={"name": "X"}))
    pipeline = Pipeline(reg)
    ctx = pipeline._build_context(reg.get_instance("test"))
    assert ctx["count"] == 1


def test_context_instance_overrides_default():
    reg = _make_registry()
    reg.register_instance(InstanceDefinition(id="test", type="entity", values={"name": "X", "count": 5}))
    pipeline = Pipeline(reg)
    ctx = pipeline._build_context(reg.get_instance("test"))
    assert ctx["count"] == 5


def test_context_inherited_parameters():
    reg = Registry()
    reg.register_type(TypeDefinition(
        id="base", parameters={"base_p": ParameterDefinition(type="string", default="base_val")},
    ))
    reg.register_type(TypeDefinition(
        id="derived", depends_on=["base"],
        parameters={"derived_p": ParameterDefinition(type="string", required=True)},
    ))
    reg.register_instance(InstanceDefinition(id="test", type="derived", values={"derived_p": "v"}))
    pipeline = Pipeline(reg)
    ctx = pipeline._build_context(reg.get_instance("test"))
    assert ctx["base_p"] == "base_val"
    assert ctx["derived_p"] == "v"
