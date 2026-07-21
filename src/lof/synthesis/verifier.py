"""Candidate verifier protocol and implementations."""

from typing import Protocol

from lof.synthesis.models import (
    Candidate,
    SynthesisProblem,
    VerificationFailure,
    VerificationResult,
)


class CandidateVerifier(Protocol):
    def verify(self, candidate: Candidate, problem: SynthesisProblem) -> VerificationResult:
        ...


class SchemaVerifier:
    """Verifies that a candidate has the required fields for its kind."""

    def verify(self, candidate: Candidate, problem: SynthesisProblem) -> VerificationResult:
        failures: list[VerificationFailure] = []
        if not candidate.id:
            failures.append(
                VerificationFailure(kind="schema", location="id", message="Candidate has no id")
            )
        if not candidate.program:
            failures.append(
                VerificationFailure(
                    kind="schema", location="program", message="Candidate has no program"
                )
            )
        return VerificationResult(valid=len(failures) == 0, failures=failures)
