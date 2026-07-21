"""Loads Gold DSL from JSON files into validated GoldApplication models."""

import json
from pathlib import Path

from lof.models.gold_models import GoldApplication


def load_gold_application(path: str | Path) -> GoldApplication:
    """Load JSON → GoldApplication. Validated by Pydantic. This is the only entry point
    for DSL definitions — no Python constructors.
    """
    p = Path(path) if isinstance(path, str) else path
    data = json.loads(p.read_text())
    return GoldApplication(**data)


def load_gold_application_from_string(content: str) -> GoldApplication:
    """Load a JSON string as a GoldApplication."""
    data = json.loads(content)
    return GoldApplication(**data)
