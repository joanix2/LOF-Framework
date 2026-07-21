"""Profile registry — discovers profiles dynamically."""

from pathlib import Path


class ProfileInfo:
    def __init__(self, profile_id: str, version: str, description: str, rules: list):
        self.id = profile_id
        self.version = version
        self.description = description
        self.rules = rules


class ProfileRegistry:
    def __init__(self, profiles_dir: Path | None = None):
        self._profiles: dict[str, ProfileInfo] = {}
        if profiles_dir:
            self._discover(profiles_dir)

    def register(self, profile_id: str, version: str, description: str, rules: list) -> None:
        self._profiles[profile_id] = ProfileInfo(profile_id, version, description, rules)

    def get(self, profile_id: str) -> ProfileInfo | None:
        return self._profiles.get(profile_id)

    def get_rules(self, profile_id: str) -> list:
        info = self.get(profile_id)
        if info:
            return info.rules
        return []

    def list_profiles(self) -> list[ProfileInfo]:
        return list(self._profiles.values())

    def _discover(self, profiles_dir: Path) -> None:
        if not profiles_dir.exists():
            return
        for f in sorted(profiles_dir.glob("*.py")):
            if f.name.startswith("_"):
                continue
            profile_id = f.stem.replace("_", "-")
            self.register(profile_id, "0.1", f"Profile: {profile_id}", [])
