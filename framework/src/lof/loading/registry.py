from lof.models.instance_definition import InstanceDefinition
from lof.models.patch_definition import PatchDefinition
from lof.models.target_definition import TargetDefinition
from lof.models.type_definition import TypeDefinition


class Registry:
    def __init__(self):
        self.types: dict[str, TypeDefinition] = {}
        self.instances: dict[str, InstanceDefinition] = {}
        self.patches: dict[str, PatchDefinition] = {}
        self.targets: dict[str, TargetDefinition] = {}

    def register_type(self, t: TypeDefinition) -> None:
        self.types[t.id] = t

    def register_instance(self, inst: InstanceDefinition) -> None:
        self.instances[inst.id] = inst

    def register_patch(self, p: PatchDefinition) -> None:
        self.patches[p.id] = p

    def register_target(self, t: TargetDefinition) -> None:
        self.targets[t.id] = t

    def get_type(self, type_id: str) -> TypeDefinition | None:
        return self.types.get(type_id)

    def get_instance(self, instance_id: str) -> InstanceDefinition | None:
        return self.instances.get(instance_id)

    def get_patch(self, patch_id: str) -> PatchDefinition | None:
        return self.patches.get(patch_id)

    def get_target(self, target_id: str) -> TargetDefinition | None:
        return self.targets.get(target_id)

    def has_type(self, type_id: str) -> bool:
        return type_id in self.types

    def instances_for_type(self, type_id: str) -> list[InstanceDefinition]:
        return [i for i in self.instances.values() if i.type == type_id]

    @property
    def type_count(self) -> int:
        return len(self.types)

    @property
    def instance_count(self) -> int:
        return len(self.instances)

    @property
    def patch_count(self) -> int:
        return len(self.patches)

    @property
    def target_count(self) -> int:
        return len(self.targets)
