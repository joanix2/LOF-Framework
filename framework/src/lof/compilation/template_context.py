"""TemplateContextBuilder — prepares Jinja context before rendering."""

from typing import Any

from lof.graph.context_resolver import GraphContextResolver
from lof.loading.registry import Registry
from lof.models.instance_definition import InstanceDefinition


class TemplateContextBuilder:
    def __init__(self, registry: Registry, graph_resolver: GraphContextResolver):
        self.registry = registry
        self.graph_resolver = graph_resolver

    def build(self, instance: InstanceDefinition) -> dict[str, Any]:
        ctx: dict[str, Any] = {}

        td = self.registry.get_type(instance.type)
        if td:
            seen: set[str] = set()

            def resolve_params(tid: str) -> None:
                if tid in seen:
                    return
                seen.add(tid)
                t = self.registry.get_type(tid)
                if t is None:
                    return
                for dep in t.depends_on:
                    resolve_params(dep)
                for name, param in t.parameters.items():
                    if name not in ctx and param.default is not None:
                        ctx[name] = param.default

            resolve_params(instance.type)

        ctx.update(instance.values)
        ctx["instance_id"] = instance.id

        gctx, _ = self.graph_resolver.context_for_template(instance)
        ctx.update(gctx)

        return ctx
