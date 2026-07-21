import json
from pathlib import Path
from typing import Any

from lof.domain.settings import CompilationSettings
from lof.models.instance_definition import InstanceDefinition
from lof.models.patch_definition import PatchDefinition
from lof.models.target_definition import TargetDefinition
from lof.models.type_definition import TypeDefinition


class Loader:
    def __init__(self, root: Path | None = None, settings: CompilationSettings | None = None):
        self.root = root or Path.cwd()
        self.settings = settings or CompilationSettings()

    def load_json(self, path: str | Path) -> dict[str, Any]:
        full_path = Path(path) if Path(path).is_absolute() else self.root / path
        with open(full_path) as f:
            return dict(json.load(f))

    def load_type(self, path: str | Path) -> TypeDefinition:
        data = self.load_json(path)
        _map = {
            "dependsOn": "depends_on", "targetType": "target_type",
            "interfaceSource": "interface_source", "outputPattern": "output_pattern",
            "contextQuery": "context_query",
        }
        for old, new in _map.items():
            if old in data:
                data[new] = data.pop(old)
        return TypeDefinition(**data)

    def load_instance(self, path: str | Path) -> InstanceDefinition:
        data = self.load_json(path)
        return InstanceDefinition(**data)

    def load_patch(self, path: str | Path) -> PatchDefinition:
        data = self.load_json(path)
        _map = {"targetSelector": "target_selector", "dependsOn": "depends_on"}
        for old, new in _map.items():
            if old in data:
                data[new] = data.pop(old)
        for op in data.get("operations", []):
            if "returnType" in op:
                op["return_type"] = op.pop("returnType")
            if "importName" in op:
                op["import_name"] = op.pop("importName")
        return PatchDefinition(**data)

    def load_target(self, path: str | Path) -> TargetDefinition:
        data = self.load_json(path)
        _map = {"astAdapter": "ast_adapter"}
        for old, new in _map.items():
            if old in data:
                data[new] = data.pop(old)
        return TargetDefinition(**data)

    def load_types_from_dir(self, directory: str | None = None) -> list[TypeDefinition]:
        d = directory or self.settings.types_dir
        dir_path = Path(d) if Path(d).is_absolute() else (self.root / d).resolve()
        types = []
        if dir_path.exists():
            for f in sorted(dir_path.rglob("*.json")):
                types.append(self.load_type(f))
        return types

    def load_instances_from_dir(self, directory: str | None = None) -> list[InstanceDefinition]:
        d = directory or self.settings.instances_dir
        dir_path = Path(d) if Path(d).is_absolute() else (self.root / d).resolve()
        if dir_path.exists():
            return [self.load_instance(f) for f in sorted(dir_path.rglob("*.json"))]
        return []

    def load_patches_from_dir(self, directory: str | None = None) -> list[PatchDefinition]:
        d = directory or self.settings.patches_dir
        dir_path = Path(d) if Path(d).is_absolute() else (self.root / d).resolve()
        patches = []
        if dir_path.exists():
            for f in sorted(dir_path.rglob("*.json")):
                patches.append(self.load_patch(f))
        return patches

    def load_targets_from_dir(self, directory: str | None = None) -> list[TargetDefinition]:
        d = directory or self.settings.targets_dir
        dir_path = Path(d) if Path(d).is_absolute() else (self.root / d).resolve()
        if dir_path.exists():
            return [self.load_target(f) for f in sorted(dir_path.glob("*.json"))]
        return []
