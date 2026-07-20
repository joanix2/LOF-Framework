from lof.loading.registry import Registry
from lof.models.instance_definition import InstanceDefinition
from lof.models.type_definition import ParameterDefinition, TypeDefinition
from lof.rendering.context_resolver import ContextResolver


def test_context_resolution():
    registry = Registry()
    registry.register_type(
        TypeDefinition(
            id="entity",
            parameters={
                "name": ParameterDefinition(type="string", required=True),
                "count": ParameterDefinition(type="integer", default=1),
            },
        )
    )
    inst = InstanceDefinition(id="test", type="entity", values={"name": "TestEntity"})
    resolver = ContextResolver(registry)
    context, diag = resolver.resolve(inst)
    assert context["name"] == "TestEntity"
    assert context["count"] == 1
    assert not diag.has_errors


def test_context_missing_required():
    registry = Registry()
    registry.register_type(
        TypeDefinition(
            id="entity",
            parameters={
                "name": ParameterDefinition(type="string", required=True),
            },
        )
    )
    inst = InstanceDefinition(id="test", type="entity", values={})
    resolver = ContextResolver(registry)
    context, diag = resolver.resolve(inst)
    assert diag.has_errors


def test_context_inherited():
    registry = Registry()
    registry.register_type(
        TypeDefinition(
            id="base",
            parameters={
                "base_param": ParameterDefinition(type="string", default="base_val"),
            },
        )
    )
    registry.register_type(
        TypeDefinition(
            id="derived",
            depends_on=["base"],
            parameters={
                "derived_param": ParameterDefinition(type="string", required=True),
            },
        )
    )
    inst = InstanceDefinition(id="test", type="derived", values={"derived_param": "derived_val"})
    resolver = ContextResolver(registry)
    context, diag = resolver.resolve(inst)
    assert context["base_param"] == "base_val"
    assert context["derived_param"] == "derived_val"
    assert not diag.has_errors
