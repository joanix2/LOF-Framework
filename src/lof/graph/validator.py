import networkx as nx

from lof.loading.registry import Registry
from lof.validation.diagnostics import Diagnostics


class GraphValidator:
    def __init__(self, registry: Registry):
        self.registry = registry
        self.diagnostics = Diagnostics()

    def validate(self, graph: nx.DiGraph) -> Diagnostics:
        self.diagnostics = Diagnostics()
        self._check_missing_types()
        self._check_type_dependencies()
        self._check_cycles(graph)
        self._check_orphan_instances()
        self._check_missing_patches()
        return self.diagnostics

    def _check_missing_types(self) -> None:
        for inst in self.registry.instances.values():
            if inst.type not in self.registry.types:
                self.diagnostics.add_error(
                    f"Instance '{inst.id}' references unknown type '{inst.type}'"
                )

    def _check_type_dependencies(self) -> None:
        for t in self.registry.types.values():
            for dep in t.depends_on:
                if dep not in self.registry.types:
                    self.diagnostics.add_error(f"Type '{t.id}' depends on unknown type '{dep}'")

    def _check_cycles(self, graph: nx.DiGraph) -> None:
        cycles = list(nx.simple_cycles(graph))
        for cycle in cycles:
            self.diagnostics.add_error(f"Circular dependency detected: {' -> '.join(cycle)}")

    def _check_orphan_instances(self) -> None:
        for inst in self.registry.instances.values():
            if inst.type in self.registry.types:
                td = self.registry.types[inst.type]
                for param_name, param_def in td.parameters.items():
                    if param_def.required and param_name not in inst.values:
                        self.diagnostics.add_error(
                            f"Instance '{inst.id}' missing required parameter '{param_name}' "
                            f"for type '{inst.type}'"
                        )

    def _check_missing_patches(self) -> None:
        for inst in self.registry.instances.values():
            for patch_id in inst.patches:
                if patch_id not in self.registry.patches:
                    self.diagnostics.add_error(
                        f"Instance '{inst.id}' references unknown patch '{patch_id}'"
                    )
