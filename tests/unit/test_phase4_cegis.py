"""Tests for Phase 4: CEGIS models, coordinator, verifier, store."""

from pathlib import Path

from lof.synthesis.coordinator import CegisCoordinator
from lof.synthesis.models import (
    Candidate,
    CandidateKind,
    CounterExample,
    SearchBudget,
    SynthesisProblem,
    SynthesisResult,
    VerificationFailure,
    VerificationResult,
)
from lof.synthesis.store import CounterExampleQuery, JsonlCounterExampleStore
from lof.synthesis.verifier import SchemaVerifier


class TestSynthesisModels:
    def test_synthesis_problem_defaults(self):
        p = SynthesisProblem(id="test")
        assert p.id == "test"
        assert p.target_kind == "patch"
        assert p.budget.max_iterations == 10

    def test_synthesis_problem_with_counterexample(self):
        p = SynthesisProblem(id="test")
        ce = CounterExample(inputs={"x": 1}, expected_output="2", actual_output="3")
        p2 = p.with_counterexample(ce)
        assert len(p2.counterexamples) == 1
        assert len(p.counterexamples) == 0  # immutability

    def test_candidate_defaults(self):
        c = Candidate(id="c1", program="print('hello')")
        assert c.kind == "patch"
        assert c.score is None

    def test_verification_result_defaults(self):
        r = VerificationResult()
        assert r.valid
        assert r.failures == []

    def test_verification_result_failure(self):
        f = VerificationFailure(kind="lint", location="line 5", message="E201")
        r = VerificationResult(valid=False, failures=[f])
        assert not r.valid
        assert r.failures[0].kind == "lint"

    def test_synthesis_result_success(self):
        c = Candidate(id="c1", program="x")
        r = SynthesisResult.success(candidate=c, iterations=3)
        assert r.status == "success"
        assert r.candidate is not None
        assert r.iterations == 3

    def test_synthesis_result_exhausted(self):
        r = SynthesisResult.exhausted(iterations=10)
        assert r.status == "exhausted"
        assert "Budget" in r.error

    def test_counter_example_defaults(self):
        ce = CounterExample(inputs={"x": 1}, expected_output="2", actual_output="3")
        assert ce.diagnostic == ""
        assert ce.created_at is not None

    def test_candidate_kind_values(self):
        assert Candidate.__annotations__["kind"] == CandidateKind


class TestSchemaVerifier:
    def test_valid_candidate(self):
        v = SchemaVerifier()
        c = Candidate(id="c1", program="def f(): pass")
        result = v.verify(c, SynthesisProblem(id="p1"))
        assert result.valid

    def test_missing_id(self):
        v = SchemaVerifier()
        c = Candidate(id="", program="x")
        result = v.verify(c, SynthesisProblem(id="p1"))
        assert not result.valid

    def test_missing_program(self):
        v = SchemaVerifier()
        c = Candidate(id="c1", program="")
        result = v.verify(c, SynthesisProblem(id="p1"))
        assert not result.valid


class TestJsonlStore:
    def test_append_and_count(self, tmp_path: Path):
        store = JsonlCounterExampleStore(tmp_path / "ce.jsonl")
        assert store.count == 0
        store.append(CounterExample(inputs={"a": 1}, expected_output="b", actual_output="c"))
        assert store.count == 1

    def test_duplicate_not_appended(self, tmp_path: Path):
        store = JsonlCounterExampleStore(tmp_path / "ce.jsonl")
        ce = CounterExample(inputs={"a": 1}, expected_output="b", actual_output="c")
        store.append(ce)
        store.append(ce)
        assert store.count == 1

    def test_find_similar(self, tmp_path: Path):
        store = JsonlCounterExampleStore(tmp_path / "ce.jsonl")
        store.append(
            CounterExample(
                inputs={"x": 1}, expected_output="2", actual_output="3", diagnostic="lint error"
            )
        )
        store.append(
            CounterExample(
                inputs={"y": 2}, expected_output="4", actual_output="5", diagnostic="type error"
            )
        )
        results = store.find_similar(CounterExampleQuery(kind="lint"))
        assert len(results) == 1
        assert "lint" in results[0].diagnostic


class TestCegisCoordinator:
    def test_success_first_candidate(self):
        class AlwaysValidGenerator:
            def generate(self, problem, context=None):
                return [Candidate(id="c1", program="ok")]

        class AlwaysValidVerifier:
            def verify(self, candidate, problem):
                return VerificationResult(valid=True)

        coord = CegisCoordinator(AlwaysValidGenerator(), AlwaysValidVerifier())
        problem = SynthesisProblem(id="test", budget=SearchBudget(max_iterations=5))
        result = coord.solve(problem)
        assert result.status == "success"
        assert result.candidate is not None

    def test_exhausted_budget(self):
        class AlwaysInvalidGenerator:
            def generate(self, problem, context=None):
                return [Candidate(id="c_bad", program="bad")]

        class AlwaysInvalidVerifier:
            def verify(self, candidate, problem):
                return VerificationResult(
                    valid=False,
                    failures=[VerificationFailure(kind="test", message="always fails")],
                )

        coord = CegisCoordinator(AlwaysInvalidGenerator(), AlwaysInvalidVerifier())
        problem = SynthesisProblem(id="test", budget=SearchBudget(max_iterations=3))
        result = coord.solve(problem)
        assert result.status == "exhausted"
        assert result.iterations == 3

    def test_counterexamples_collected(self, tmp_path: Path):
        class FailOnceGenerator:
            def __init__(self):
                self.called = 0

            def generate(self, problem, context=None):
                self.called += 1
                return [Candidate(id=f"c{self.called}", program=f"p{self.called}")]

        class FailOnceVerifier:
            def __init__(self):
                self.called = 0

            def verify(self, candidate, problem):
                self.called += 1
                if self.called == 1:
                    return VerificationResult(
                        valid=False,
                        failures=[VerificationFailure(kind="test", message="fail first")],
                    )
                return VerificationResult(valid=True)

        store = JsonlCounterExampleStore(tmp_path / "ce.jsonl")
        coord = CegisCoordinator(FailOnceGenerator(), FailOnceVerifier(), store=store)
        problem = SynthesisProblem(id="test", budget=SearchBudget(max_iterations=5))
        result = coord.solve(problem)
        assert result.status == "success"
        assert store.count == 1
