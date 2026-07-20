from typing import Any

from lof.graph.instance_graph import InstanceGraph
from lof.graph.projection_context import (
    ProjectionContext,
    ResolvedInstance,
    ResolvedProjectionInput,
    TemplateGraphView,
)
from lof.loading.registry import Registry
from lof.models.instance_definition import InstanceDefinition
from lof.models.type_definition import ContextQuery
from lof.validation.diagnostics import Diagnostics


def _context_query_depth(cq: ContextQuery | None, field: str) -> int:
    if cq is None:
        return 0
    data = getattr(cq, field, {})
    if isinstance(data, dict):
        return data.get("max_depth", 0)
    return 0


class GraphContextResolver:
    def __init__(self, registry: Registry, instance_graph: InstanceGraph):
        self.registry = registry
        self.instance_graph = instance_graph
        self._resolved_cache: dict[str, ResolvedInstance] = {}

    def _resolve_instance(self, inst: InstanceDefinition) -> ResolvedInstance:
        if inst.id in self._resolved_cache:
            return self._resolved_cache[inst.id]
        resolved = ResolvedInstance(
            id=inst.id,
            type_id=inst.type,
            values=dict(inst.values),
        )
        self._resolved_cache[inst.id] = resolved
        return resolved

    def _build_view(self) -> TemplateGraphView:
        instances: dict[str, ResolvedInstance] = {}
        for inst in self.registry.instances.values():
            instances[inst.id] = self._resolve_instance(inst)
        return TemplateGraphView(instances, self.instance_graph)

    def resolve(self, instance: InstanceDefinition) -> tuple[ProjectionContext, Diagnostics]:
        diag = Diagnostics()
        td = self.registry.get_type(instance.type)
        cq = td.context_query if td else None

        inst = self._resolve_instance(instance)
        view = self._build_view()

        out_depth = _context_query_depth(cq, "outgoing_relations")
        in_depth = _context_query_depth(cq, "incoming_relations")
        dep_depth = _context_query_depth(cq, "dependencies")
        dent_depth = _context_query_depth(cq, "dependents")

        if out_depth > 0:
            outgoing = view.relations(instance.id, direction="out")
        else:
            outgoing = ()

        if in_depth > 0:
            incoming = view.relations(instance.id, direction="in")
        else:
            incoming = ()

        if out_depth > 0 or in_depth > 0:
            neighbors = view.neighbors(
                instance.id, direction="both", depth=max(out_depth, in_depth, 1)
            )
        else:
            neighbors = ()

        if dep_depth > 0:
            dependencies = view.reachable(instance.id, direction="out", max_depth=dep_depth)
        else:
            dependencies = ()

        if dent_depth > 0:
            dependents = view.reachable(instance.id, direction="in", max_depth=dent_depth)
        else:
            dependents = ()

        ctx = ProjectionContext(
            instance=inst,
            outgoing_relations=outgoing,
            incoming_relations=incoming,
            neighbors=neighbors,
            dependencies=dependencies,
            dependents=dependents,
            graph=view,
        )
        return ctx, diag

    def resolve_projection(
        self, instance: InstanceDefinition
    ) -> tuple[ResolvedProjectionInput, Diagnostics]:
        ctx, diag = self.resolve(instance)

        deps = [ctx.instance.id]
        for r in ctx.outgoing_relations:
            deps.append(r.target.id)
        for r in ctx.incoming_relations:
            deps.append(r.source.id)

        return ResolvedProjectionInput(
            context=ctx,
            dependency_instance_ids=tuple(sorted(set(deps))),
        ), diag

    def context_for_template(
        self, instance: InstanceDefinition
    ) -> tuple[dict[str, Any], Diagnostics]:
        ctx, diag = self.resolve(instance)
        tctx: dict[str, Any] = {
            "instance": ctx.instance,
            "relations": ctx.outgoing_relations,
            "incoming_relations": ctx.incoming_relations,
            "neighbors": ctx.neighbors,
            "dependencies": ctx.dependencies,
            "dependents": ctx.dependents,
            "graph": ctx.graph,
        }
        if ctx.instance:
            for k, v in ctx.instance.values.items():
                if k not in tctx:
                    tctx[k] = v
        return tctx, diag
