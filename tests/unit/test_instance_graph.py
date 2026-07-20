from lof.graph.instance_graph import InstanceGraph
from lof.models.instance_definition import InstanceDefinition, InstanceRelationDefinition


def test_empty_graph():
    ig = InstanceGraph()
    ig.build({})
    assert ig.outgoing_relations("nonexistent") == []


def test_simple_relation():
    instances = {
        "a": InstanceDefinition(id="a", type="t"),
        "b": InstanceDefinition(
            id="b",
            type="t",
            relations=[
                InstanceRelationDefinition(id="r1", kind="depends", target="a"),
            ],
        ),
    }
    ig = InstanceGraph()
    ig.build(instances)
    rels = ig.outgoing_relations("b")
    assert len(rels) == 1
    assert rels[0].target == "a"
    assert rels[0].kind == "depends"


def test_inverse_relation():
    instances = {
        "a": InstanceDefinition(id="a", type="t"),
        "b": InstanceDefinition(
            id="b",
            type="t",
            relations=[
                InstanceRelationDefinition(
                    id="r1", kind="many-to-one", target="a", inverse="children"
                ),
            ],
        ),
    }
    ig = InstanceGraph()
    ig.build(instances)
    incoming = ig.incoming_relations("a")
    assert len(incoming) == 1
    assert incoming[0].target == "a"
    assert incoming[0].kind == "many-to-one"


def test_reachable_depth_1():
    instances = {
        "customer": InstanceDefinition(id="customer", type="t"),
        "project": InstanceDefinition(
            id="project",
            type="t",
            relations=[
                InstanceRelationDefinition(id="r1", kind="many-to-one", target="customer"),
            ],
        ),
        "task": InstanceDefinition(
            id="task",
            type="t",
            relations=[
                InstanceRelationDefinition(id="r2", kind="many-to-one", target="project"),
            ],
        ),
    }
    ig = InstanceGraph()
    ig.build(instances)
    reached = ig.reachable("task", max_depth=1, direction="out")
    assert "project" in reached
    assert "customer" not in reached


def test_reachable_depth_2():
    instances = {
        "customer": InstanceDefinition(id="customer", type="t"),
        "project": InstanceDefinition(
            id="project",
            type="t",
            relations=[
                InstanceRelationDefinition(id="r1", kind="many-to-one", target="customer"),
            ],
        ),
        "task": InstanceDefinition(
            id="task",
            type="t",
            relations=[
                InstanceRelationDefinition(id="r2", kind="many-to-one", target="project"),
            ],
        ),
    }
    ig = InstanceGraph()
    ig.build(instances)
    reached = ig.reachable("task", max_depth=2, direction="out")
    assert "project" in reached
    assert "customer" in reached


def test_reachable_kind_filter():
    instances = {
        "a": InstanceDefinition(id="a", type="t"),
        "b": InstanceDefinition(
            id="b",
            type="t",
            relations=[
                InstanceRelationDefinition(id="r1", kind="depends", target="a"),
            ],
        ),
        "c": InstanceDefinition(
            id="c",
            type="t",
            relations=[
                InstanceRelationDefinition(id="r2", kind="references", target="a"),
            ],
        ),
    }
    ig = InstanceGraph()
    ig.build(instances)
    reached = ig.reachable("a", max_depth=2, direction="in", kinds={"depends"})
    assert "b" in reached
    assert "c" not in reached


def test_shortest_path():
    instances = {
        "a": InstanceDefinition(id="a", type="t"),
        "b": InstanceDefinition(
            id="b",
            type="t",
            relations=[InstanceRelationDefinition(id="r1", kind="edge", target="a")],
        ),
        "c": InstanceDefinition(
            id="c",
            type="t",
            relations=[InstanceRelationDefinition(id="r2", kind="edge", target="b")],
        ),
    }
    ig = InstanceGraph()
    ig.build(instances)
    path = ig.shortest_path("c", "a")
    assert path == ["c", "b", "a"]


def test_unknown_instance():
    ig = InstanceGraph()
    ig.build({})
    assert ig.outgoing_relations("unknown") == []
    assert ig.reachable("unknown", max_depth=3) == []


def test_duplicate_relation_id():
    instances = {
        "a": InstanceDefinition(
            id="a",
            type="t",
            relations=[
                InstanceRelationDefinition(id="dup", kind="x", target="b"),
            ],
        ),
        "b": InstanceDefinition(
            id="b",
            type="t",
            relations=[
                InstanceRelationDefinition(id="dup", kind="x", target="a"),
            ],
        ),
    }
    ig = InstanceGraph()
    diag = ig.validate(instances)
    assert diag.has_errors
