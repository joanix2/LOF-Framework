from collections import deque

import networkx as nx

from lof.models.instance_definition import InstanceDefinition, InstanceRelationDefinition
from lof.validation.diagnostics import Diagnostics


class InstanceGraph:
    def __init__(self):
        self.graph: nx.DiGraph = nx.DiGraph()

    def build(
        self, instances: dict[str, InstanceDefinition], diagnostics: Diagnostics | None = None
    ) -> None:
        self.graph = nx.DiGraph()
        diag = diagnostics or Diagnostics()

        for inst_id, inst in instances.items():
            self.graph.add_node(inst_id, kind="instance", data=inst)

        for inst_id, inst in instances.items():
            for rel in inst.relations:
                if rel.target not in instances:
                    diag.add_error(
                        f"Relation '{rel.id}' in instance '{inst_id}' "
                        f"references unknown instance '{rel.target}'"
                    )
                    continue

                self.graph.add_edge(
                    inst_id,
                    rel.target,
                    key=rel.id,
                    relation=rel,
                )

                if rel.inverse:
                    self.graph.add_edge(
                        rel.target,
                        inst_id,
                        key=f"inverse:{rel.id}",
                        relation=InstanceRelationDefinition(
                            id=f"inverse:{rel.id}",
                            kind=f"inverse:{rel.kind}",
                            target=inst_id,
                            source_field=rel.target_field,
                            target_field=rel.source_field,
                            inverse=rel.id,
                            required=False,
                        ),
                    )

    def outgoing_relations(self, instance_id: str) -> list[InstanceRelationDefinition]:
        if instance_id not in self.graph:
            return []
        edges = self.graph.out_edges(instance_id, data=True)
        return [d.get("relation") for _, _, d in edges if d.get("relation")]

    def incoming_relations(self, instance_id: str) -> list[InstanceRelationDefinition]:
        if instance_id not in self.graph:
            return []
        edges = self.graph.in_edges(instance_id, data=True)
        return [d.get("relation") for _, _, d in edges if d.get("relation")]

    def outgoing_neighbors(self, instance_id: str, *, kind: str | None = None) -> list[str]:
        if instance_id not in self.graph:
            return []
        result = []
        for _, target, data in self.graph.out_edges(instance_id, data=True):
            rel = data.get("relation")
            if rel is None:
                continue
            if kind is not None and rel.kind != kind:
                continue
            result.append(target)
        return sorted(result)

    def incoming_neighbors(self, instance_id: str, *, kind: str | None = None) -> list[str]:
        if instance_id not in self.graph:
            return []
        result = []
        for source, _, data in self.graph.in_edges(instance_id, data=True):
            rel = data.get("relation")
            if rel is None:
                continue
            if kind is not None and rel.kind != kind:
                continue
            result.append(source)
        return sorted(result)

    def reachable(
        self,
        start_id: str,
        *,
        max_depth: int = 3,
        direction: str = "out",
        kinds: set[str] | None = None,
    ) -> list[str]:
        if start_id not in self.graph:
            return []

        visited: set[str] = {start_id}
        queue: deque[tuple[str, int]] = deque([(start_id, 0)])
        result: list[str] = []

        while queue:
            current_id, depth = queue.popleft()

            if depth >= max_depth:
                continue

            if direction in ("out", "both"):
                edges = sorted(
                    [
                        (e[2].get("relation"), e[1])
                        for e in self.graph.out_edges(current_id, data=True)
                        if e[2].get("relation")
                    ],
                    key=lambda x: (x[0].kind if x[0] else "", x[1]),
                )
                for rel, target_id in edges:
                    if kinds is not None and rel.kind not in kinds:
                        continue
                    if target_id in visited:
                        continue
                    visited.add(target_id)
                    result.append(target_id)
                    queue.append((target_id, depth + 1))

            if direction in ("in", "both"):
                edges = sorted(
                    [
                        (e[2].get("relation"), e[0])
                        for e in self.graph.in_edges(current_id, data=True)
                        if e[2].get("relation")
                    ],
                    key=lambda x: (x[0].kind if x[0] else "", x[1]),
                )
                for rel, source_id in edges:
                    if kinds is not None and rel.kind not in kinds:
                        continue
                    if source_id in visited:
                        continue
                    visited.add(source_id)
                    result.append(source_id)
                    queue.append((source_id, depth + 1))

        return result

    def shortest_path(self, source_id: str, target_id: str, max_depth: int = 5) -> list[str]:
        if source_id not in self.graph or target_id not in self.graph:
            return []
        try:
            path = nx.shortest_path(self.graph, source=source_id, target=target_id)
            if len(path) > max_depth + 1:
                return []
            return path
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []

    def validate(self, instances: dict[str, InstanceDefinition]) -> Diagnostics:
        diag = Diagnostics()
        rel_ids: set[str] = set()
        for inst_id, inst in instances.items():
            for rel in inst.relations:
                if rel.id in rel_ids:
                    diag.add_error(f"Duplicate relation id '{rel.id}'")
                rel_ids.add(rel.id)
                if rel.target not in instances:
                    diag.add_error(
                        f"Relation '{rel.id}' in '{inst_id}' targets unknown '{rel.target}'"
                    )
        self.build(instances, diag)

        try:
            cycles = list(nx.simple_cycles(self.graph))
            for cycle in cycles:
                diag.add_error(f"Cyclic instance relation: {' -> '.join(cycle)}")
        except Exception:
            pass

        return diag
