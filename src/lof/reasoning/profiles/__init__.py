from lof.reasoning.profiles.fastapi_react import FASTAPI_REACT_RULES


def get_profile(profile_id: str = "fastapi-react") -> list:
    profiles = {"fastapi-react": FASTAPI_REACT_RULES}
    return profiles.get(profile_id, [])


__all__ = ["FASTAPI_REACT_RULES", "get_profile"]
