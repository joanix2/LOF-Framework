"""Core models for the synthesis subsystem."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

CandidateKind = Literal["patch", "template", "rule", "smt_constraint"]


class Specification(BaseModel):
    description: str = ""
    constraints: list[str] = Field(default_factory=list)


class SearchSpace(BaseModel):
    max_depth: int = 5
    max_terms: int = 100
    allowed_primitives: list[str] = Field(default_factory=list)


class SearchBudget(BaseModel):
    max_iterations: int = 10
    timeout_seconds: float = 60.0
    max_candidates_per_iteration: int = 5


class SynthesisProblem(BaseModel):
    id: str
    target_kind: CandidateKind = "patch"
    specification: Specification = Field(default_factory=Specification)
    examples: list[dict[str, Any]] = Field(default_factory=list)
    counterexamples: list["CounterExample"] = Field(default_factory=list)
    search_space: SearchSpace = Field(default_factory=SearchSpace)
    budget: SearchBudget = Field(default_factory=SearchBudget)
    constraints: list[str] = Field(default_factory=list)

    def with_counterexample(self, ce: "CounterExample") -> "SynthesisProblem":
        return self.model_copy(update={"counterexamples": [*self.counterexamples, ce]})


class Candidate(BaseModel):
    id: str
    kind: CandidateKind = "patch"
    program: str = ""
    score: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class VerificationFailure(BaseModel):
    kind: str = "unknown"
    location: str = ""
    message: str = ""
    context: dict[str, Any] = Field(default_factory=dict)


class VerificationResult(BaseModel):
    valid: bool = True
    failures: list[VerificationFailure] = Field(default_factory=list)


class CounterExample(BaseModel):
    inputs: dict[str, Any] = Field(default_factory=dict)
    expected_output: str = ""
    actual_output: str = ""
    diagnostic: str = ""
    created_at: datetime = Field(default_factory=datetime.now)


class SynthesisResult(BaseModel):
    status: Literal["success", "exhausted", "timeout", "error"] = "error"
    candidate: Candidate | None = None
    iterations: int = 0
    duration_ms: float = 0.0
    error: str = ""

    @classmethod
    def success(cls, candidate: Candidate, iterations: int = 0, duration_ms: float = 0.0):
        return cls(
            status="success",
            candidate=candidate,
            iterations=iterations,
            duration_ms=duration_ms,
        )

    @classmethod
    def exhausted(cls, iterations: int, duration_ms: float = 0.0):
        return cls(
            status="exhausted",
            iterations=iterations,
            duration_ms=duration_ms,
            error="Budget exhausted",
        )

    @classmethod
    def timeout(cls, duration_ms: float = 0.0):
        return cls(status="timeout", duration_ms=duration_ms, error="Timeout")
