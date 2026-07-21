"""Counter-example store protocol and implementations."""

import json
from collections.abc import Sequence
from pathlib import Path
from typing import Protocol

from lof.synthesis.models import CounterExample


class CounterExampleQuery:
    def __init__(
        self,
        kind: str | None = None,
        predicate: str | None = None,
        limit: int = 10,
    ):
        self.kind = kind
        self.predicate = predicate
        self.limit = limit


class CounterExampleStore(Protocol):
    def append(self, counterexample: CounterExample) -> None:
        ...

    def find_similar(self, query: CounterExampleQuery) -> Sequence[CounterExample]:
        ...


class JsonlCounterExampleStore:
    """Simple JSONL-backed counterexample store."""

    def __init__(self, path: Path):
        self.path = path
        self._entries: list[CounterExample] = []
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        with open(self.path) as f:
            for line in f:
                line = line.strip()
                if line:
                    data = json.loads(line)
                    if "created_at" in data:
                        from datetime import datetime
                        data["created_at"] = datetime.fromisoformat(data["created_at"])
                    self._entries.append(CounterExample(**data))

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "a") as f:
            f.write(json.dumps(self._entries[-1].model_dump(mode="json")) + "\n")

    def append(self, counterexample: CounterExample) -> None:
        if not self._is_duplicate(counterexample):
            self._entries.append(counterexample)
            self._save()

    def _is_duplicate(self, ce: CounterExample) -> bool:
        for existing in self._entries:
            if (existing.inputs == ce.inputs
                    and existing.expected_output == ce.expected_output):
                return True
        return False

    def find_similar(self, query: CounterExampleQuery) -> Sequence[CounterExample]:
        results = []
        for ce in self._entries:
            if query.kind and query.kind not in str(ce.diagnostic):
                continue
            if query.predicate and query.predicate not in str(ce.inputs):
                continue
            results.append(ce)
            if len(results) >= query.limit:
                break
        return results

    @property
    def count(self) -> int:
        return len(self._entries)
