from dataclasses import dataclass, field
from typing import Any

from lof.graph.instance_graph import InstanceGraph
from lof.loading.registry import Registry


@dataclass(frozen=True)
class ConstraintContext:
    registry: Registry
    instance_graph: InstanceGraph
    types_index: dict[str, dict[str, Any]] = field(default_factory=dict)
    instances_index: dict[str, dict[str, Any]] = field(default_factory=dict)
    relations_index: list[dict[str, Any]] = field(default_factory=list)
    projections_index: dict[str, list[str]] = field(default_factory=dict)
    targets: dict[str, Any] = field(default_factory=dict)
    profiles: list[str] = field(default_factory=list)

    @classmethod
    def build(cls, registry: Registry, instance_graph: InstanceGraph) -> "ConstraintContext":
        types_index: dict[str, dict[str, Any]] = {}
        for t in registry.types.values():
            types_index[t.id] = t.model_dump(exclude_none=True)

        instances_index: dict[str, dict[str, Any]] = {}
        for inst in registry.instances.values():
            instances_index[inst.id] = inst.model_dump(exclude_none=True)

        relations_index: list[dict[str, Any]] = []
        for inst in registry.instances.values():
            for rel in inst.relations:
                relations_index.append(
                    {
                        "id": rel.id,
                        "kind": rel.kind,
                        "source": inst.id,
                        "target": rel.target,
                        "source_field": rel.source_field,
                        "target_field": rel.target_field,
                        "inverse": rel.inverse,
                        "required": rel.required,
                    }
                )

        projections_index: dict[str, list[str]] = {}
        for inst_id, inst in registry.instances.items():
            td = registry.get_type(inst.type)
            if td and td.template:
                projections_index.setdefault(td.id, []).append(inst_id)

        targets: dict[str, Any] = {}
        for t in registry.targets.values():
            targets[t.id] = t.model_dump(exclude_none=True)

        return cls(
            registry=registry,
            instance_graph=instance_graph,
            types_index=types_index,
            instances_index=instances_index,
            relations_index=relations_index,
            projections_index=projections_index,
            targets=targets,
        )
