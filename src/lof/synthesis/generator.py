"""Candidate generator protocol and implementations."""

from collections.abc import Sequence
from typing import Protocol

from lof.synthesis.models import Candidate, SynthesisProblem


class CandidateGenerator(Protocol):
    def generate(
        self, problem: SynthesisProblem, context: dict | None = None
    ) -> Sequence[Candidate]:
        ...
