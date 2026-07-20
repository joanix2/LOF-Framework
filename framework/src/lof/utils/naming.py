import re


def snake_case(name: str) -> str:
    if not name:
        return ""
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    if not re.search(r"[-_\s]", s) and name[0].isupper():
        s = re.sub(r"([A-Z])", r"_\1", name).lower().strip("_")
    return s.lower().replace("-", "_").replace(" ", "_")


def camel_case(name: str) -> str:
    parts = re.split(r"[-_\s]+", name)
    if not parts:
        return ""
    if len(parts) == 1:
        s = parts[0]
        return s[0].lower() + s[1:] if s and s[0].isupper() else s
    return parts[0].lower() + "".join(p.capitalize() for p in parts[1:])


def pascal_case(name: str) -> str:
    return "".join(p.capitalize() for p in re.split(r"[-_\s]+", name))


def kebab_case(name: str) -> str:
    return snake_case(name).replace("_", "-")


def pluralize(name: str) -> str:
    if name.endswith(("s", "x", "z", "ch", "sh")):
        return name + "es"
    if name.endswith("y") and len(name) > 1 and name[-2] not in "aeiou":
        return name[:-1] + "ies"
    return name + "s"
