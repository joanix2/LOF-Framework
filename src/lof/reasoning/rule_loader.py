"""Loads inference rules from .lof/rules/ JSON files."""

import json
from pathlib import Path
from typing import Any

from lof.reasoning.models import Condition, Conclusion, Rule


class RuleLoader:
    def __init__(self, root: Path | None = None):
        self.root = root or Path.cwd()
        self._rules_dir = self.root / ".lof" / "rules"

    def load_all(self) -> list[Rule]:
        rules: list[Rule] = []
        if not self._rules_dir.exists():
            return rules
        for f in sorted(self._rules_dir.glob("*.json")):
            rules.extend(self._load_file(f))
        return rules

    def _load_file(self, path: Path) -> list[Rule]:
        data = json.loads(path.read_text())
        if isinstance(data, dict):
            data = data.get("rules", [data])
        return [
            Rule(
                id=r.get("id", "unknown"),
                description=r.get("description", ""),
                mode=r.get("mode", "certain"),
                category=r.get("category", "general"),
                when=[Condition(**c) for c in r.get("when", [])],
                then=[Conclusion(**c) for c in r.get("then", [])],
                weight=r.get("weight", 1.0),
            )
            for r in data
        ]
