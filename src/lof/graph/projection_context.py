from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from lof.graph.instance_graph import InstanceGraph
from lof.models.instance_definition import InstanceRelationDefinition


@dataclass(frozen=True)
class ResolvedInstance:
    id: str
    type_id: str
    values: Mapping[str, Any]

    def __getitem__(self, key: str) -> Any:
        return self.values[key]

    def get(self, key: str, default: Any = None) -> Any:
        return self.values.get(key, default)


@dataclass(frozen=True)
class ResolvedRelation:
    id: str
    kind: str
    source: ResolvedInstance
    target: ResolvedInstance
    source_field: str | None = None
    target_field: str | None = None
    inverse: str | None = None
    required: bool = False


class TemplateGraphView:
    def __init__(self, instances: dict[str, ResolvedInstance], graph: InstanceGraph):
        self._instances = instances
        self._graph = graph

    def get(self, instance_id: str) -> ResolvedInstance | None:
        return self._instances.get(instance_id)

    def relations(
        self,
        instance_id: str,
        *,
        direction: str = "out",
        kinds: tuple[str, ...] | None = None,
    ) -> tuple[ResolvedRelation, ...]:
        inst = self._instances.get(instance_id)
        if inst is None:
            return ()

        raw_relations: list[InstanceRelationDefinition] = []
        if direction in ("out", "both"):
            raw_relations.extend(self._graph.outgoing_relations(instance_id))
        if direction in ("in", "both"):
            raw_relations.extend(self._graph.incoming_relations(instance_id))

        result: list[ResolvedRelation] = []
        for r in raw_relations:
            if kinds and r.kind not in kinds:
                continue
            target_inst = self._instances.get(r.target)
            if target_inst is None:
                continue
            resolved = ResolvedRelation(
                id=r.id,
                kind=r.kind,
                source=inst if r.target != instance_id else target_inst,
                target=target_inst if r.target != instance_id else inst,
                source_field=r.source_field,
                target_field=r.target_field,
                inverse=r.inverse,
                required=r.required,
            )
            result.append(resolved)
        return tuple(result)

    def neighbors(
        self,
        instance_id: str,
        *,
        direction: str = "both",
        kinds: tuple[str, ...] | None = None,
        depth: int = 1,
    ) -> tuple[ResolvedInstance, ...]:
        ids = self._graph.reachable(
            instance_id,
            max_depth=depth,
            direction=direction,
            kinds=set(kinds) if kinds else None,
        )
        return tuple(self._instances[i] for i in ids if i in self._instances)

    def reachable(
        self,
        instance_id: str,
        *,
        direction: str = "out",
        kinds: tuple[str, ...] | None = None,
        max_depth: int = 3,
    ) -> tuple[ResolvedInstance, ...]:
        ids = self._graph.reachable(
            instance_id,
            max_depth=max_depth,
            direction=direction,
            kinds=set(kinds) if kinds else None,
        )
        return tuple(self._instances[i] for i in ids if i in self._instances)

    def shortest_path(
        self,
        source_id: str,
        target_id: str,
        *,
        max_depth: int = 5,
    ) -> tuple[ResolvedInstance, ...]:
        ids = self._graph.shortest_path(source_id, target_id, max_depth)
        return tuple(self._instances[i] for i in ids if i in self._instances)


@dataclass(frozen=True)
class ProjectionContext:
    instance: ResolvedInstance
    outgoing_relations: tuple[ResolvedRelation, ...] = field(default_factory=tuple)
    incoming_relations: tuple[ResolvedRelation, ...] = field(default_factory=tuple)
    neighbors: tuple[ResolvedInstance, ...] = field(default_factory=tuple)
    dependencies: tuple[ResolvedInstance, ...] = field(default_factory=tuple)
    dependents: tuple[ResolvedInstance, ...] = field(default_factory=tuple)
    graph: TemplateGraphView | None = None


@dataclass(frozen=True)
class ResolvedProjectionInput:
    context: ProjectionContext
    dependency_instance_ids: tuple[str, ...] = field(default_factory=tuple)
    dependency_files: tuple[Path, ...] = field(default_factory=tuple)
