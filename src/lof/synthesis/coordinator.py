"""CEGIS coordinator — orchestrates the generate-verify-minimize-store loop."""

import time
from dataclasses import dataclass, field

from lof.synthesis.generator import CandidateGenerator
from lof.synthesis.models import (
    SynthesisProblem,
    SynthesisResult,
)
from lof.synthesis.store import CounterExample, CounterExampleStore
from lof.synthesis.verifier import CandidateVerifier


@dataclass
class SynthesisContext:
    store: CounterExampleStore | None = None
    metadata: dict = field(default_factory=dict)


class CegisCoordinator:
    """Counterexample-Guided Inductive Synthesis coordinator."""

    def __init__(
        self,
        generator: CandidateGenerator,
        verifier: CandidateVerifier,
        store: CounterExampleStore | None = None,
    ):
        self.generator = generator
        self.verifier = verifier
        self.store = store

    def solve(self, problem: SynthesisProblem) -> SynthesisResult:
        start = time.time()
        context = SynthesisContext(store=self.store)

        for iteration in range(problem.budget.max_iterations):
            elapsed = (time.time() - start) * 1000
            if elapsed > problem.budget.timeout_seconds * 1000:
                return SynthesisResult.timeout(duration_ms=elapsed)

            candidates = self.generator.generate(problem, context)
            for candidate in candidates:
                result = self.verifier.verify(candidate, problem)
                if result.valid:
                    return SynthesisResult.success(
                        candidate=candidate,
                        iterations=iteration + 1,
                        duration_ms=(time.time() - start) * 1000,
                    )
                for failure in result.failures:
                    ce = CounterExample(
                        inputs={"candidate_id": candidate.id, "kind": candidate.kind},
                        expected_output="valid",
                        actual_output=failure.message,
                        diagnostic=f"{failure.kind}: {failure.message}",
                    )
                    if self.store is not None:
                        self.store.append(ce)
                    problem = problem.with_counterexample(ce)

        return SynthesisResult.exhausted(
            iterations=problem.budget.max_iterations,
            duration_ms=(time.time() - start) * 1000,
        )
