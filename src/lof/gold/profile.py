"""Profile configuration — loads JSON profile and provides defaults.

This is the single source of truth for all M2-level configuration.
No hardcoded mappings in Python code.
"""

import json
from pathlib import Path
from typing import Any


class Profile:
    def __init__(self, data: dict[str, Any]):
        self._data = data

    @classmethod
    def load(cls, path: str | Path) -> "Profile":
        data = json.loads(Path(path).read_text())
        return cls(data)

    @property
    def inverse_relation_kinds(self) -> dict[str, str]:
        return self._data.get("inverse_relation_kinds", {})

    @property
    def naming(self) -> dict[str, str]:
        return self._data.get("naming", {})

    @property
    def defaults(self) -> dict[str, Any]:
        return self._data.get("defaults", {})

    @property
    def projections(self) -> list[dict[str, Any]]:
        return self._data.get("projections", [])

    @property
    def closed_world_predicates(self) -> set[str]:
        return set(self._data.get("closed_world_predicates", []))

    @property
    def verb_normalization(self) -> dict[str, str]:
        return self._data.get("verb_normalization", {})

    @property
    def widget_mapping(self) -> dict[str, str]:
        return self._data.get("widget_mapping", {})

    @property
    def builtin_constraints(self) -> list[dict[str, Any]]:
        return self._data.get("builtin_constraints", [])

    def inverse_kind(self, kind: str) -> str:
        return self.inverse_relation_kinds.get(kind, kind)

    def naming_convention(self, key: str, entity_id: str) -> str:
        """Apply naming convention from profile."""
        convention = self.naming.get(key, "identity")
        if convention == "kebab":
            return entity_id.lower().replace("_", "-")
        elif convention == "snake":
            return entity_id.lower().replace("-", "_")
        return entity_id

    def default_operations(self) -> list[str]:
        return self.defaults.get("operations", [])

    def default_audit_fields(self) -> list[str]:
        return self.defaults.get("audit_fields", [])

    def condition_matches(self, condition: str, capabilities: Any) -> bool:
        if condition == "always":
            return True
        if condition == "has_operations":
            ops = getattr(capabilities, "create", True) or getattr(capabilities, "list", True)
            return ops
        if condition.startswith("capability."):
            cap_name = condition.split(".")[1]
            return getattr(capabilities, cap_name, False)
        return False
