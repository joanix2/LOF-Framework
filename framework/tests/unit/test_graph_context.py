from lof.graph.context_resolver import GraphContextResolver
from lof.graph.instance_graph import InstanceGraph
from lof.loading.registry import Registry
from lof.models.instance_definition import InstanceDefinition, InstanceRelationDefinition
from lof.models.type_definition import ContextQuery, TypeDefinition


def _make_registry():
    reg = Registry()
    reg.register_type(
        TypeDefinition(
            id="entity",
            context_query=ContextQuery(
                outgoing_relations={"max_depth": 3},
                incoming_relations={"max_depth": 1},
                dependencies={"max_depth": 3},
            ),
        )
    )
    return reg


def test_context_contains_instance():
    reg = _make_registry()
    inst = InstanceDefinition(id="customer", type="entity", values={"name": "Customer"})
    reg.register_instance(inst)

    ig = InstanceGraph()
    ig.build(reg.instances)
    resolver = GraphContextResolver(reg, ig)
    ctx, diag = resolver.resolve(inst)
    assert ctx.instance.id == "customer"
    assert ctx.instance.values["name"] == "Customer"


def test_context_relations():
    reg = _make_registry()
    reg.register_instance(InstanceDefinition(id="customer", type="entity"))
    reg.register_instance(
        InstanceDefinition(
            id="project",
            type="entity",
            relations=[
                InstanceRelationDefinition(id="r1", kind="many-to-one", target="customer"),
            ],
        )
    )

    ig = InstanceGraph()
    ig.build(reg.instances)
    resolver = GraphContextResolver(reg, ig)
    ctx, diag = resolver.resolve(reg.get_instance("project"))
    assert len(ctx.outgoing_relations) > 0
    assert ctx.outgoing_relations[0].target.id == "customer"
    assert not diag.has_errors


def test_context_neighbors():
    reg = _make_registry()
    reg.register_instance(InstanceDefinition(id="customer", type="entity"))
    reg.register_instance(
        InstanceDefinition(
            id="project",
            type="entity",
            relations=[
                InstanceRelationDefinition(id="r1", kind="many-to-one", target="customer"),
            ],
        )
    )

    ig = InstanceGraph()
    ig.build(reg.instances)
    resolver = GraphContextResolver(reg, ig)
    ctx, diag = resolver.resolve(reg.get_instance("project"))
    nids = [n.id for n in ctx.neighbors]
    assert "customer" in nids
    assert "project" not in nids
    assert not diag.has_errors


def test_context_graph_view():
    reg = _make_registry()
    reg.register_instance(InstanceDefinition(id="a", type="entity"))
    reg.register_instance(
        InstanceDefinition(
            id="b",
            type="entity",
            relations=[InstanceRelationDefinition(id="r1", kind="depends", target="a")],
        )
    )
    reg.register_instance(
        InstanceDefinition(
            id="c",
            type="entity",
            relations=[InstanceRelationDefinition(id="r2", kind="depends", target="b")],
        )
    )

    ig = InstanceGraph()
    ig.build(reg.instances)
    resolver = GraphContextResolver(reg, ig)
    ctx, _ = resolver.resolve(reg.get_instance("c"))
    view = ctx.graph
    assert view is not None

    reached = view.reachable("c", direction="out", max_depth=3)
    ids = [r.id for r in reached]
    assert "b" in ids
    assert "a" in ids

    nei = view.neighbors("c", direction="out", depth=1)
    assert len(nei) == 1
    assert nei[0].id == "b"


def test_context_no_query_no_relations():
    reg = Registry()
    reg.register_type(TypeDefinition(id="simple"))
    inst = InstanceDefinition(id="x", type="simple", values={"val": 42})
    reg.register_instance(inst)

    ig = InstanceGraph()
    ig.build(reg.instances)
    resolver = GraphContextResolver(reg, ig)
    ctx, diag = resolver.resolve(inst)
    assert ctx.instance.id == "x"
    assert ctx.outgoing_relations == ()
    assert ctx.neighbors == ()
    assert not diag.has_errors


def test_context_for_template():
    reg = _make_registry()
    reg.register_instance(InstanceDefinition(id="customer", type="entity"))
    reg.register_instance(
        InstanceDefinition(
            id="project",
            type="entity",
            values={"name": "Project"},
            relations=[InstanceRelationDefinition(id="r1", kind="many-to-one", target="customer")],
        )
    )

    ig = InstanceGraph()
    ig.build(reg.instances)
    resolver = GraphContextResolver(reg, ig)
    tctx, diag = resolver.context_for_template(reg.get_instance("project"))
    assert "instance" in tctx
    assert "relations" in tctx
    assert "graph" in tctx
    assert tctx["instance"].id == "project"
    assert tctx["name"] == "Project"
    assert not diag.has_errors


def test_deterministic_order():
    reg = _make_registry()
    ids = ["z", "y", "x", "w"]
    for iid in ids:
        reg.register_instance(InstanceDefinition(id=iid, type="entity"))
    for iid in ids[1:]:
        inst = reg.get_instance(iid)
        inst.relations.append(
            InstanceRelationDefinition(id=f"r-{iid}", kind="depends", target=ids[0])
        )

    ig = InstanceGraph()
    ig.build(reg.instances)
    base = ig.reachable(ids[0], direction="in", max_depth=5)
    base2 = ig.reachable(ids[0], direction="in", max_depth=5)
    assert base == base2
