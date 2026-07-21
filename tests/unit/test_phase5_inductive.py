"""Tests for Phase 5: enumerative generator, ILP, repair memory."""

from pathlib import Path

from lof.synthesis.coordinator import CegisCoordinator
from lof.synthesis.generators import (
    EnumerativeCandidateGenerator,
    IlpCandidateGenerator,
    RepairMemory,
)
from lof.synthesis.models import (
    Candidate,
    SearchBudget,
    SearchSpace,
    Specification,
    SynthesisProblem,
    VerificationFailure,
    VerificationResult,
)


class TestEnumerativeGenerator:
    def test_generates_candidates(self):
        gen = EnumerativeCandidateGenerator(primitives=["add", "sub"])
        problem = SynthesisProblem(
            id="test",
            search_space=SearchSpace(max_depth=2, max_terms=10),
        )
        candidates = gen.generate(problem)
        assert len(candidates) > 0
        assert all(isinstance(c, Candidate) for c in candidates)

    def test_respects_max_terms(self):
        gen = EnumerativeCandidateGenerator(primitives=["a", "b", "c"])
        problem = SynthesisProblem(
            id="test",
            search_space=SearchSpace(max_depth=3, max_terms=5),
        )
        candidates = gen.generate(problem)
        assert len(candidates) <= 5

    def test_all_have_programs(self):
        gen = EnumerativeCandidateGenerator(primitives=["add"])
        problem = SynthesisProblem(
            id="test",
            search_space=SearchSpace(max_depth=2, max_terms=20),
        )
        candidates = gen.generate(problem)
        assert all(c.program for c in candidates)


class TestIlpGenerator:
    def test_generates_rule_from_examples(self):
        gen = IlpCandidateGenerator()
        problem = SynthesisProblem(
            id="learn_parent",
            target_kind="rule",
            specification=Specification(description="parent"),
            examples=[
                {"name": "alice", "parent": "bob", "label": "positive"},
                {"name": "bob", "parent": "charlie", "label": "positive"},
                {"name": "alice", "parent": "charlie", "label": "negative"},
            ],
        )
        candidates = gen.generate(problem)
        assert len(candidates) >= 1
        assert candidates[0].kind == "rule"

    def test_no_examples_no_candidates(self):
        gen = IlpCandidateGenerator()
        problem = SynthesisProblem(id="empty", target_kind="rule")
        candidates = gen.generate(problem)
        assert len(candidates) == 0


class TestRepairMemory:
    def test_record_and_count(self, tmp_path: Path):
        mem = RepairMemory(tmp_path / "repairs.jsonl")
        assert mem.count == 0
        mem.record("p1", "broken code", "fixed code", "patch")
        assert mem.count == 1

    def test_find_similar_by_kind(self, tmp_path: Path):
        mem = RepairMemory(tmp_path / "repairs.jsonl")
        mem.record("p1", "bad", "good", "patch")
        mem.record("p2", "wrong", "right", "template")
        problem = SynthesisProblem(id="p3", target_kind="patch")
        results = mem.find_similar(problem)
        assert len(results) == 1
        assert results[0].program == "good"

    def test_find_similar_no_match(self, tmp_path: Path):
        mem = RepairMemory(tmp_path / "repairs.jsonl")
        mem.record("p1", "bad", "good", "rule")
        problem = SynthesisProblem(id="p2", target_kind="patch")
        results = mem.find_similar(problem)
        assert len(results) == 0

    def test_persistent_storage(self, tmp_path: Path):
        p = tmp_path / "repairs.jsonl"
        mem1 = RepairMemory(p)
        mem1.record("p1", "broken", "fixed", "patch")
        mem2 = RepairMemory(p)
        assert mem2.count == 1
        assert mem2._entries[0].fixed == "fixed"


class TestCegisWithEnumerativeGenerator:
    class AcceptEverythingVerifier:
        def verify(self, candidate, problem):
            return VerificationResult(valid=True)

    def test_enumerative_within_cegis(self):
        gen = EnumerativeCandidateGenerator(primitives=["ok"])
        verifier = self.AcceptEverythingVerifier()
        coord = CegisCoordinator(gen, verifier)
        problem = SynthesisProblem(
            id="test",
            budget=SearchBudget(max_iterations=5),
        )
        result = coord.solve(problem)
        assert result.status == "success"

    class RejectAllVerifier:
        def verify(self, candidate, problem):
            return VerificationResult(
                valid=False,
                failures=[VerificationFailure(kind="test", message="no")],
            )

    def test_enumerative_exhausted(self):
        gen = EnumerativeCandidateGenerator(primitives=["bad"])
        verifier = self.RejectAllVerifier()
        coord = CegisCoordinator(gen, verifier)
        problem = SynthesisProblem(
            id="test",
            budget=SearchBudget(max_iterations=2, max_candidates_per_iteration=3),
            search_space=SearchSpace(max_depth=1, max_terms=3),
        )
        result = coord.solve(problem)
        assert result.status == "exhausted"
