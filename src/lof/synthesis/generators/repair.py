"""Repair memory — stores and retrieves repair pairs for similar problems."""

import json
from collections.abc import Sequence
from pathlib import Path

from lof.synthesis.models import Candidate, SynthesisProblem


class RepairEntry:
    def __init__(self, problem_id: str, broken: str, fixed: str, kind: str):
        self.problem_id = problem_id
        self.broken = broken
        self.fixed = fixed
        self.kind = kind


class RepairMemory:
    """Stores (broken_program, fixed_program, context) triples for reuse."""

    def __init__(self, path: Path | None = None):
        self.path = path
        self._entries: list[RepairEntry] = []
        if path and path.exists():
            self._load()

    def _load(self) -> None:
        with open(self.path) as f:
            for line in f:
                data = json.loads(line)
                self._entries.append(RepairEntry(**data))

    def _save(self, entry: RepairEntry) -> None:
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.path, "a") as f:
                f.write(json.dumps(entry.__dict__) + "\n")

    def record(self, problem_id: str, broken: str, fixed: str, kind: str = "patch") -> None:
        entry = RepairEntry(problem_id, broken, fixed, kind)
        self._entries.append(entry)
        self._save(entry)

    def find_similar(self, problem: SynthesisProblem) -> Sequence[Candidate]:
        candidates: list[Candidate] = []
        for entry in self._entries:
            if entry.kind == problem.target_kind:
                candidates.append(
                    Candidate(
                        id=f"repair_{entry.problem_id}",
                        kind=entry.kind,
                        program=entry.fixed,
                        metadata={
                            "source": "repair_memory",
                            "original_problem": entry.problem_id,
                            "broken": entry.broken,
                        },
                    )
                )
        return candidates

    @property
    def count(self) -> int:
        return len(self._entries)
