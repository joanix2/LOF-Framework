from lof.reasoning.engine import DatalogEngine
from lof.reasoning.models import ReasoningResult


class ExplanationGenerator:
    def __init__(self, engine: DatalogEngine, rules: list):
        self.engine = engine
        self._rule_map = {r.id: r for r in rules}

    def explain(self, fact_key: str, result: ReasoningResult) -> str:
        fact = next((f for f in result.facts if f.key == fact_key), None)
        if fact is None:
            return f"Fact '{fact_key}' not found in the knowledge base."

        trace = next((t for t in result.traces if t.fact_key == fact_key), None)

        parts: list[str] = []
        parts.append(f"Fact: {fact_key}")
        parts.append(f"  Status: {fact.status}")
        parts.append(f"  Confidence: {fact.confidence}")

        if fact.rule_id:
            rule = self._rule_map.get(fact.rule_id)
            if rule:
                parts.append(f"  Rule: {rule.id} ({rule.mode})")
                parts.append(f"  Rule description: {rule.description}")
                if rule.category:
                    parts.append(f"  Category: {rule.category}")

        if trace:
            parts.append(f"  Derived in iteration {trace.iteration}")
            parts.append(f"  Binding: {trace.bindings}")
            if trace.source_keys:
                parts.append("  Source facts:")
                for sk in trace.source_keys:
                    sf = next((f for f in result.facts if f.key == sk), None)
                    if sf:
                        parts.append(f"    - {sk} ({sf.status})")
                        if sf.rule_id:
                            parts.append(f"      via rule '{sf.rule_id}'")

        if fact.source_facts:
            parts.append("  Direct sources:")
            for sk in fact.source_facts:
                sf = next((f for f in result.facts if f.key == sk), None)
                if sf:
                    parts.append(f"    - {sk}")

        if fact.bronze_ids:
            parts.append(f"  Bronze sources: {', '.join(fact.bronze_ids)}")

        if fact.explanation:
            parts.append(f"  Explanation: {fact.explanation}")

        return "\n".join(parts)

    def trace_path(self, fact_key: str, result: ReasoningResult, depth: int = 0) -> str:
        indent = "  " * depth
        parts: list[str] = []

        fact = next((f for f in result.facts if f.key == fact_key), None)
        if fact is None:
            return f"{indent}{fact_key} (not found)"

        parts.append(f"{indent}{fact_key} [{fact.status}]")
        if fact.rule_id:
            parts.append(f"{indent}  ← rule '{fact.rule_id}'")

        trace = next((t for t in result.traces if t.fact_key == fact_key), None)
        if trace and trace.source_keys:
            for sk in trace.source_keys:
                sub = self.trace_path(sk, result, depth + 2)
                parts.append(sub)

        return "\n".join(parts)
