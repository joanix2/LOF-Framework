from lof.graph.builder import GraphBuilder
from lof.graph.validator import GraphValidator
from lof.loading.registry import Registry
from lof.models.instance_definition import InstanceDefinition
from lof.models.type_definition import TypeDefinition


def test_graph_basic():
    registry = Registry()
    registry.register_type(TypeDefinition(id="base"))
    registry.register_type(TypeDefinition(id="derived", depends_on=["base"]))
    builder = GraphBuilder(registry)
    graph = builder.build()
    assert graph.has_node("base")
    assert graph.has_node("derived")
    assert graph.has_edge("base", "derived")


def test_topological_order():
    registry = Registry()
    registry.register_type(TypeDefinition(id="a"))
    registry.register_type(TypeDefinition(id="b", depends_on=["a"]))
    registry.register_type(TypeDefinition(id="c", depends_on=["b"]))
    builder = GraphBuilder(registry)
    builder.build()
    order = builder.get_types_in_order()
    assert order.index("a") < order.index("b")
    assert order.index("b") < order.index("c")


def test_cycle_detection():
    registry = Registry()
    registry.register_type(TypeDefinition(id="a", depends_on=["b"]))
    registry.register_type(TypeDefinition(id="b", depends_on=["a"]))
    builder = GraphBuilder(registry)
    graph = builder.build()
    validator = GraphValidator(registry)
    diag = validator.validate(graph)
    assert diag.has_errors
    assert any("circular" in e.lower() for e in diag.errors)


def test_missing_dependency():
    registry = Registry()
    registry.register_type(TypeDefinition(id="a", depends_on=["missing"]))
    builder = GraphBuilder(registry)
    graph = builder.build()
    validator = GraphValidator(registry)
    diag = validator.validate(graph)
    assert diag.has_errors


def test_instance_type_link():
    registry = Registry()
    registry.register_type(TypeDefinition(id="entity"))
    registry.register_instance(InstanceDefinition(id="cust", type="entity"))
    builder = GraphBuilder(registry)
    graph = builder.build()
    assert graph.has_node("cust")
    assert graph.has_edge("entity", "cust")
