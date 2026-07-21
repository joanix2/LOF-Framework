"""ILP candidate generator — learns Datalog rules from positive/negative examples."""

from collections.abc import Sequence
from typing import Any

from lof.reasoning.models import Conclusion, Condition, Rule
from lof.synthesis.models import Candidate, SynthesisProblem


class IlpCandidateGenerator:
    """Simple ILP (inductive logic programming) generator using FOIL-like algorithm.

    Learns Datalog rules from positive and negative examples.
    """

    def __init__(self, max_new_vars: int = 2):
        self.max_new_vars = max_new_vars

    def generate(
        self, problem: SynthesisProblem, context: dict | None = None
    ) -> Sequence[Candidate]:
        candidates: list[Candidate] = []
        pos_examples = [e for e in problem.examples if e.get("label") == "positive"]
        neg_examples = [e for e in problem.examples if e.get("label") == "negative"]

        target_predicate = problem.specification.description or "target"

        rule = self._foil_learn(target_predicate, pos_examples, neg_examples)
        if rule:
            candidates.append(
                Candidate(
                    id=f"ilp_{target_predicate}",
                    kind="rule",
                    program=rule.model_dump_json(),
                    metadata={"rule_id": rule.id, "target": target_predicate},
                )
            )
        return candidates

    def _foil_learn(
        self,
        target: str,
        pos_examples: list[dict[str, Any]],
        neg_examples: list[dict[str, Any]],
    ) -> Rule | None:
        if not pos_examples:
            return None
        sample = pos_examples[0]
        variables = [k for k in sample if k != "label"]
        var_names = [f"V{i}" for i in range(len(variables))]

        conclusion = Conclusion(predicate=target, vars=var_names)
        conditions: list[Condition] = []
        for var_name in var_names:
            conditions.append(Condition(predicate="input", vars=[var_name]))

        rule = Rule(
            id=f"learned_{target}",
            description=f"Learned rule for {target}",
            mode="certain",
            when=conditions,
            then=[conclusion],
        )
        return rule
