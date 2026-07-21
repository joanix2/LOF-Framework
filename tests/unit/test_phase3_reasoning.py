"""Tests for Phase 3: negation, indexing, semi-naive, validation, stats, provenance."""

from lof.reasoning.engine import DatalogEngine
from lof.reasoning.models import (
    Conclusion,
    Condition,
    Fact,
    Rule,
)


class TestNegation:
    def test_negated_condition_matches_negative_fact(self):
        engine = DatalogEngine([])
        fact = Fact(predicate="broken", args=("x",), status="asserted", polarity="negative")
        cond = Condition(predicate="broken", vars=["x"], negated=True)
        result = engine._match_condition(cond, fact, {})
        assert result is not None

    def test_negated_condition_rejects_positive_fact(self):
        engine = DatalogEngine([])
        fact = Fact(predicate="broken", args=("x",), status="asserted", polarity="positive")
        cond = Condition(predicate="broken", vars=["x"], negated=True)
        result = engine._match_condition(cond, fact, {})
        assert result is None

    def test_negated_rule_infers_from_negative(self):
        rule = Rule(
            id="safe_if_not_broken",
            when=[
                Condition(predicate="tool", vars=["x"]),
                Condition(predicate="broken", vars=["x"], negated=True),
            ],
            then=[Conclusion(predicate="safe", vars=["x"])],
        )
        engine = DatalogEngine([rule])
        facts = [
            Fact(predicate="tool", args=("tool1",)),
            Fact(predicate="broken", args=("tool1",), polarity="negative"),
            Fact(predicate="tool", args=("tool2",)),
            Fact(predicate="broken", args=("tool2",), polarity="positive"),
        ]
        result = engine.evaluate(facts)
        safe_tools = [f.args[0] for f in result.inferred if f.predicate == "safe"]
        assert "tool1" in safe_tools
        assert "tool2" not in safe_tools

    def test_negated_rule_no_match_for_positive(self):
        rule = Rule(
            id="safe_if_not_broken",
            when=[
                Condition(predicate="tool", vars=["x"]),
                Condition(predicate="broken", vars=["x"], negated=True),
            ],
            then=[Conclusion(predicate="safe", vars=["x"])],
        )
        engine = DatalogEngine([rule])
        facts = [
            Fact(predicate="tool", args=("tool1",)),
            Fact(predicate="broken", args=("tool1",), polarity="positive"),
        ]
        result = engine.evaluate(facts)
        assert not any(f.predicate == "safe" for f in result.inferred)


class TestRuleValidation:
    def test_unbound_variable_in_conclusion(self):
        engine = DatalogEngine([])
        rule = Rule(
            id="bad",
            when=[Condition(predicate="p", vars=["x"])],
            then=[Conclusion(predicate="q", vars=["y"])],
        )
        errors = engine._validate_rule(rule)
        assert any("unbound" in e for e in errors)

    def test_bound_variable_ok(self):
        engine = DatalogEngine([])
        rule = Rule(
            id="good",
            when=[Condition(predicate="p", vars=["x"])],
            then=[Conclusion(predicate="q", vars=["x"])],
        )
        errors = engine._validate_rule(rule)
        assert len(errors) == 0

    def test_unbound_in_negated_condition(self):
        engine = DatalogEngine([])
        rule = Rule(
            id="bad_neg",
            when=[Condition(predicate="p", vars=["x"], negated=True)],
            then=[Conclusion(predicate="q", vars=["x"])],
        )
        errors = engine._validate_rule(rule)
        assert any("unbound" in e and "negated" in e for e in errors)

    def test_validation_appears_in_result(self):
        rule = Rule(
            id="bad",
            when=[Condition(predicate="p", vars=["x"])],
            then=[Conclusion(predicate="q", vars=["y"])],
        )
        engine = DatalogEngine([rule])
        result = engine.evaluate([])
        assert len(result.errors) >= 1
        assert any("unbound" in e for e in result.errors)


class TestStats:
    def test_stats_after_evaluation(self):
        rule = Rule(
            id="r1",
            when=[Condition(predicate="input", vars=["x"])],
            then=[Conclusion(predicate="output", vars=["x"])],
        )
        engine = DatalogEngine([rule])
        facts = [Fact(predicate="input", args=("a",))]
        result = engine.evaluate(facts)
        assert len(result.stats) == 1
        s = result.stats[0]
        assert s.rule_id == "r1"
        assert s.match_count >= 1
        assert s.produce_count >= 1

    def test_no_rules_no_stats(self):
        engine = DatalogEngine([])
        result = engine.evaluate([])
        assert result.stats == []


class TestSemiNaive:
    def test_same_result_as_naive(self):
        rule = Rule(
            id="r1",
            when=[Condition(predicate="a", vars=["x"])],
            then=[Conclusion(predicate="b", vars=["x"])],
        )
        engine = DatalogEngine([rule])
        facts = [Fact(predicate="a", args=("x",)), Fact(predicate="a", args=("y",))]
        result = engine.evaluate(facts)
        assert len(result.inferred) == 2
        predicates = [f.predicate for f in result.inferred]
        assert predicates.count("b") == 2

    def test_converges_with_semi_naive(self):
        rule = Rule(
            id="r1",
            when=[Condition(predicate="a", vars=["x"])],
            then=[Conclusion(predicate="a", vars=["x"])],
        )
        engine = DatalogEngine([rule])
        facts = [Fact(predicate="a", args=("x",))]
        result = engine.evaluate(facts, max_iterations=10)
        assert result.converged
        assert result.iteration_count >= 1


class TestProvenance:
    def test_bronze_ids_propagated(self):
        rule = Rule(
            id="r1",
            when=[Condition(predicate="input", vars=["x"])],
            then=[Conclusion(predicate="output", vars=["x"])],
        )
        engine = DatalogEngine([rule])
        source = Fact(
            predicate="input",
            args=("x",),
            bronze_ids=["bronze_001"],
        )
        result = engine.evaluate([source])
        assert len(result.inferred) == 1
        inferred = result.inferred[0]
        assert "bronze_001" in inferred.bronze_ids

    def test_inference_trace_has_sources(self):
        rule = Rule(
            id="r1",
            when=[Condition(predicate="input", vars=["x"])],
            then=[Conclusion(predicate="output", vars=["x"])],
        )
        engine = DatalogEngine([rule])
        source = Fact(predicate="input", args=("x",))
        result = engine.evaluate([source])
        assert len(result.traces) >= 1
        t = result.traces[0]
        assert t.rule_id == "r1"
        assert len(t.source_keys) >= 1
        assert t.iteration >= 1

    def test_multi_hop_provenance(self):
        rule1 = Rule(
            id="r1",
            when=[Condition(predicate="a", vars=["x"])],
            then=[Conclusion(predicate="b", vars=["x"])],
        )
        rule2 = Rule(
            id="r2",
            when=[Condition(predicate="b", vars=["x"])],
            then=[Conclusion(predicate="c", vars=["x"])],
        )
        engine = DatalogEngine([rule1, rule2])
        source = Fact(predicate="a", args=("x",), bronze_ids=["ticket_1"])
        result = engine.evaluate([source])
        c_facts = [f for f in result.inferred if f.predicate == "c"]
        assert len(c_facts) == 1
        assert "ticket_1" in c_facts[0].bronze_ids
