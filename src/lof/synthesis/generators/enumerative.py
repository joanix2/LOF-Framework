"""Enumerative candidate generator — exhaustive enumeration for small DSLs."""

import itertools
from collections.abc import Sequence

from lof.synthesis.models import Candidate, SynthesisProblem


class EnumerativeCandidateGenerator:
    """Generates candidates by enumerating all programs within a bounded DSL."""

    def __init__(self, primitives: list[str] | None = None):
        self.primitives = primitives or [
            "add",
            "sub",
            "mul",
            "div",
            "eq",
            "lt",
            "gt",
            "if",
            "and",
            "or",
            "not",
        ]

    def generate(
        self, problem: SynthesisProblem, context: dict | None = None
    ) -> Sequence[Candidate]:
        space = problem.search_space
        candidates: list[Candidate] = []
        for size in range(1, space.max_depth + 1):
            for combo in itertools.product(self.primitives, repeat=size):
                program = "(" + " ".join(combo) + ")"
                candidates.append(
                    Candidate(
                        id=f"enum_{len(candidates)}",
                        kind=problem.target_kind,
                        program=program,
                    )
                )
                if len(candidates) >= space.max_terms:
                    return candidates
        return candidates
