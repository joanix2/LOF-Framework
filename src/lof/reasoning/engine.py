"""Datalog engine with semi-naive evaluation, negation, indexing, and statistics.

Closed-world predicates come from the active Profile config.
"""

import time
from collections import defaultdict

from lof.gold.profile import Profile
from lof.reasoning.models import (
    Conclusion,
    Condition,
    Fact,
    InferenceTrace,
    ReasoningResult,
    Rule,
    RuleStats,
    TruthStatus,
)

# Predicates known to be closed-world (absence = negation)
CLOSED_WORLD_PREDICATES = {
    "requires_projection",
    "requires_endpoint",
    "form_widget",
}


class DatalogEngine:
    def __init__(self, rules: list[Rule], profile: Profile | None = None):
        self.rules = rules
        self.profile = profile
        self._rule_index: dict[str, list[Rule]] = defaultdict(list)
        for rule in rules:
            for c in rule.when:
                self._rule_index[c.predicate].append(rule)
        self._closed_world = (profile.closed_world_predicates if profile
                              else {"requires_projection", "requires_endpoint", "form_widget"})
        self._stats: dict[str, RuleStats] = {rule.id: RuleStats(rule_id=rule.id) for rule in rules}

    @property
    def stats(self) -> list[RuleStats]:
        return list(self._stats.values())

    def evaluate(self, facts: list[Fact], max_iterations: int = 100) -> ReasoningResult:
        start = time.time()
        fact_map: dict[str, Fact] = {}
        for f in facts:
            fact_map[f.key] = f

        errors: list[str] = []
        for rule in self.rules:
            rule_errors = self._validate_rule(rule)
            errors.extend(rule_errors)
        if errors:
            return ReasoningResult(
                facts=list(fact_map.values()),
                inferred=[],
                hypotheses=[],
                traces=[],
                contradictions=[],
                errors=errors,
                iteration_count=0,
                converged=False,
                duration_ms=(time.time() - start) * 1000,
                stats=list(self._stats.values()),
            )

        traces: list[InferenceTrace] = []
        contradictions: list[str] = []
        iteration = 0
        converged = False

        new_keys: set[str] = set(fact_map.keys())

        while iteration < max_iterations:
            iteration += 1
            derived: list[Fact] = []
            iteration_traces: list[InferenceTrace] = []

            for rule in self.rules:
                rule_start = time.time()
                matches = self._match_rule(rule, fact_map, semi_naive_keys=new_keys)
                self._stats[rule.id].match_count += len(matches)
                self._stats[rule.id].eval_time_ms += (time.time() - rule_start) * 1000

                for bindings, source_keys in matches:
                    for conclusion in rule.then:
                        cf = self._build_conclusion_fact(
                            conclusion, bindings, rule, source_keys, fact_map
                        )
                        if cf:
                            existing = fact_map.get(cf.key)
                            if existing is None:
                                fact_map[cf.key] = cf
                                derived.append(cf)
                                self._stats[rule.id].produce_count += 1
                                iteration_traces.append(
                                    InferenceTrace(
                                        fact_key=cf.key,
                                        rule_id=rule.id,
                                        source_keys=list(source_keys),
                                        bindings=dict(bindings),
                                        iteration=iteration,
                                    )
                                )
                            elif (
                                existing.is_active
                                and cf.is_active
                                and existing.polarity != cf.polarity
                            ):
                                contradictions.append(
                                    f"Contradiction: {cf.key} inferred as {cf.polarity} "
                                    f"but already exists as {existing.polarity} "
                                    f"(rule: {rule.id})"
                                )

            traces.extend(iteration_traces)
            new_keys = {f.key for f in derived}

            if not derived:
                converged = True
                break

        inferred = [f for f in fact_map.values() if f.status == "inferred"]
        hypotheses = [f for f in fact_map.values() if f.status == "hypothesized"]

        return ReasoningResult(
            facts=list(fact_map.values()),
            inferred=inferred,
            hypotheses=hypotheses,
            traces=traces,
            contradictions=contradictions,
            errors=errors,
            iteration_count=iteration,
            converged=converged,
            duration_ms=(time.time() - start) * 1000,
            stats=list(self._stats.values()),
        )

    def _validate_rule(self, rule: Rule) -> list[str]:
        errors: list[str] = []
        bound: set[str] = set()
        for cond in rule.when:
            if cond.negated:
                for v in cond.vars:
                    if v not in bound and not v.startswith("_"):
                        errors.append(
                            f"Rule '{rule.id}': unbound variable '{v}' "
                            f"in negated condition '{cond.predicate}'"
                        )
            else:
                for v in cond.vars:
                    if not v.startswith("_"):
                        bound.add(v)
        for concl in rule.then:
            for v in concl.vars:
                if v not in bound and not v.startswith("_"):
                    errors.append(
                        f"Rule '{rule.id}': unbound variable '{v}' "
                        f"in conclusion '{concl.predicate}'"
                    )
        return errors

    def _match_condition(
        self, cond: Condition, fact: Fact, var_map: dict[str, str]
    ) -> dict[str, str] | None:
        if cond.negated:
            return self._match_negated(cond, fact, var_map)
        if fact.predicate != cond.predicate:
            return None
        if len(fact.args) != len(cond.vars):
            return None
        bindings: dict[str, str] = {}
        for f_arg, c_var in zip(fact.args, cond.vars):
            if c_var.startswith("_"):
                continue
            if c_var in var_map:
                if var_map[c_var] != f_arg:
                    return None
            elif c_var in bindings:
                if bindings[c_var] != f_arg:
                    return None
            else:
                bindings[c_var] = f_arg
        return bindings

    def _match_negated(
        self, cond: Condition, fact: Fact, var_map: dict[str, str]
    ) -> dict[str, str] | None:
        if fact.status == "rejected":
            return None
        if fact.predicate != cond.predicate:
            return None
        if len(fact.args) != len(cond.vars):
            return None
        for f_arg, c_var in zip(fact.args, cond.vars):
            if c_var.startswith("_"):
                continue
            if c_var in var_map:
                if var_map[c_var] != f_arg:
                    return None
        if fact.polarity == "negative":
            return dict(var_map)
        return None

    def _match_rule(
        self,
        rule: Rule,
        fact_map: dict[str, Fact],
        semi_naive_keys: set[str] | None = None,
    ) -> list[tuple[dict[str, str], set[str]]]:
        if not rule.when:
            return [({}, set())]

        results: list[tuple[dict[str, str], set[str]]] = []
        first = rule.when[0]
        remaining = rule.when[1:]
        var_map: dict[str, str] = {}

        candidates = (
            [f for f in fact_map.values() if f.key in semi_naive_keys]
            if semi_naive_keys
            else list(fact_map.values())
        )

        for fact in candidates:
            if fact.status == "rejected":
                continue
            bindings = self._match_condition(first, fact, var_map)
            if bindings is not None:
                combined = dict(var_map)
                combined.update(bindings)
                source_keys = {fact.key}
                self._match_remaining(remaining, fact_map, combined, source_keys, results, rule)

        return results

    def _match_remaining(
        self,
        conditions: list[Condition],
        fact_map: dict[str, Fact],
        bindings: dict[str, str],
        source_keys: set[str],
        results: list[tuple[dict[str, str], set[str]]],
        rule: Rule,
    ) -> None:
        if not conditions:
            results.append((dict(bindings), set(source_keys)))
            return

        cond = conditions[0]
        rest = conditions[1:]

        for fact in fact_map.values():
            if fact.status == "rejected":
                continue
            matched = self._match_condition(cond, fact, bindings)
            if matched is not None:
                new_bindings = dict(bindings)
                new_bindings.update(matched)
                new_sources = set(source_keys)
                new_sources.add(fact.key)
                self._match_remaining(rest, fact_map, new_bindings, new_sources, results, rule)

    def _build_conclusion_fact(
        self,
        conclusion: Conclusion,
        bindings: dict[str, str],
        rule: Rule,
        source_keys: set[str],
        fact_map: dict[str, Fact],
    ) -> Fact | None:
        args: list[str] = []
        for v in conclusion.vars:
            if v.startswith("_"):
                args.append(v)
            elif v in bindings:
                args.append(bindings[v])
            else:
                return None

        status: TruthStatus = "inferred" if rule.mode == "certain" else "hypothesized"

        bronze_ids: set[str] = set()
        for sk in source_keys:
            if sk in fact_map:
                bronze_ids.update(fact_map[sk].bronze_ids)

        return Fact(
            predicate=conclusion.predicate,
            args=tuple(args),
            status=status,
            rule_id=rule.id,
            source_facts=list(source_keys),
            bronze_ids=list(bronze_ids),
            explanation=(
                f"Inferred by rule '{rule.id}': {rule.description}" if rule.description else None
            ),
            world="closed" if conclusion.predicate in self._closed_world else "open",
        )

    def _detect_contradictions(self, fact_map: dict[str, Fact]) -> list[str]:
        contras: list[str] = []
        groups: dict[str, list[Fact]] = defaultdict(list)
        for f in fact_map.values():
            groups[f.key].append(f)

        for key, facts in groups.items():
            active = [f for f in facts if f.is_active]
            if len(active) < 2:
                continue
            for i in range(len(active)):
                for j in range(i + 1, len(active)):
                    if active[i].polarity != active[j].polarity:
                        contras.append(
                            f"Contradiction: {key} is both "
                            f"{active[i].polarity} ({active[i].status}) and "
                            f"{active[j].polarity} ({active[j].status})"
                        )
        return contras
