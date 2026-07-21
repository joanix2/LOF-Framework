from lof.reasoning.profiles.fastapi_react import FASTAPI_REACT_RULES
from lof.reasoning.profiles.registry import ProfileRegistry

_PROFILE_REGISTRY: ProfileRegistry | None = None


def _get_registry() -> ProfileRegistry:
    global _PROFILE_REGISTRY
    if _PROFILE_REGISTRY is None:
        _PROFILE_REGISTRY = ProfileRegistry()
        _PROFILE_REGISTRY.register(
            "fastapi-react", "0.3", "FastAPI backend + React frontend", FASTAPI_REACT_RULES
        )
    return _PROFILE_REGISTRY


def get_profile(profile_id: str = "fastapi-react") -> list:
    reg = _get_registry()
    rules = reg.get_rules(profile_id)
    if rules:
        return rules
    return []


def list_profiles() -> list:
    return _get_registry().list_profiles()


__all__ = ["FASTAPI_REACT_RULES", "get_profile", "list_profiles", "ProfileRegistry"]
