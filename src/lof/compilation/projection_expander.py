"""Expands one entity instance into multiple projection instances.

The profile defines which projections each entity type produces.
This is the bridge between "one entity instance" and "multiple generated files".
"""

from lof.gold.profile import Profile
from lof.loading.registry import Registry
from lof.models.instance_definition import InstanceDefinition


class ProjectionExpander:
    def __init__(self, registry: Registry, profile: Profile | None = None):
        self.registry = registry
        self.profile = profile

    def expand(self) -> list[InstanceDefinition]:
        if not self.profile:
            return list(self.registry.instances.values())

        expanded: list[InstanceDefinition] = []
        for inst in self.registry.instances.values():
            if inst.type == "entity":
                expanded.extend(self._expand_entity(inst))
            else:
                expanded.append(inst)
        return expanded

    def _expand_entity(self, entity_inst: InstanceDefinition) -> list[InstanceDefinition]:
        results: list[InstanceDefinition] = []
        ops = entity_inst.values.get("operations", [])
        has_ops = len(ops) > 0
        can_list = "list" in ops

        for proj_def in self.profile.projections:
            condition = proj_def.get("condition", "always")
            if not self._match_condition(condition, has_ops, can_list):
                continue

            type_id = proj_def["type"]

            proj_inst = InstanceDefinition(
                id=f"{entity_inst.id}_{type_id}",
                type=type_id,
                values=dict(entity_inst.values),
                enabled=entity_inst.enabled,
            )

            if type_id == "model":
                proj_inst.values["relations"] = [
                    {**r, "target": f"{r['target']}"}
                    for r in entity_inst.values.get("relations", [])
                ]

            results.append(proj_inst)

        return results

    def _match_condition(self, condition: str, has_ops: bool, can_list: bool) -> bool:
        if condition == "always":
            return True
        if condition == "has_operations":
            return has_ops
        if condition == "capability.list":
            return can_list
        return True
