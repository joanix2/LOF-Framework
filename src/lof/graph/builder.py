import networkx as nx

from lof.loading.registry import Registry


class GraphBuilder:
    def __init__(self, registry: Registry):
        self.registry = registry
        self.graph: nx.DiGraph = nx.DiGraph()

    def build(self) -> nx.DiGraph:
        self.graph = nx.DiGraph()
        for t in self.registry.types.values():
            self.graph.add_node(t.id, type="type", data=t)
        for t in self.registry.types.values():
            for dep in t.depends_on:
                self.graph.add_edge(dep, t.id, relation="prerequisite_of")
        for inst in self.registry.instances.values():
            if inst.type in self.registry.types:
                self.graph.add_node(inst.id, type="instance", data=inst)
                self.graph.add_edge(inst.type, inst.id, relation="type_of")
            for patch_id in inst.patches:
                if patch_id in self.registry.patches:
                    patch = self.registry.patches[patch_id]
                    patch_node = f"patch:{patch_id}"
                    self.graph.add_node(patch_node, type="patch", data=patch)
                    self.graph.add_edge(patch_node, inst.id, relation="applied_to")
        return self.graph

    def get_types_in_order(self) -> list[str]:
        try:
            order = list(nx.topological_sort(self.graph))
            return [n for n in order if self.graph.nodes[n].get("type") == "type"]
        except nx.NetworkXUnfeasible:
            return []

    def get_dependents(self, type_id: str) -> list[str]:
        if type_id not in self.graph:
            return []
        return list(self.graph.successors(type_id))

    def get_dependencies(self, node_id: str) -> list[str]:
        if node_id not in self.graph:
            return []
        return list(self.graph.predecessors(node_id))

    def to_mermaid(self) -> str:
        lines = ["graph TD"]
        for u, v, data in self.graph.edges(data=True):
            rel = data.get("relation", "unknown")
            lines.append(f"    {u} -->|{rel}| {v}")
        for node, data in self.graph.nodes(data=True):
            ntype = data.get("type", "unknown")
            if ntype == "type":
                lines.append(f"    {node}[{node}]:::type")
            elif ntype == "instance":
                lines.append(f"    {node}({node}):::instance")
            elif ntype == "patch":
                lines.append(f"    {node}{{{node}}}:::patch")
        lines.append("    classDef type fill:#e1f5fe,stroke:#01579b")
        lines.append("    classDef instance fill:#f3e5f5,stroke:#7b1fa2")
        lines.append("    classDef patch fill:#fff3e0,stroke:#e65100")
        return "\n".join(lines)
