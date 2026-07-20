from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

TruthStatus = Literal["asserted", "inferred", "hypothesized", "rejected", "contradicted"]
RuleMode = Literal["certain", "default", "hypothesis"]
WorldType = Literal["open", "closed"]


class Fact(BaseModel):
    predicate: str
    args: tuple[str, ...]
    status: TruthStatus = "asserted"
    confidence: float = 1.0
    rule_id: str | None = None
    source_facts: list[str] = Field(default_factory=list)
    bronze_ids: list[str] = Field(default_factory=list)
    explanation: str | None = None
    world: WorldType = "open"
    created_at: datetime = Field(default_factory=datetime.now)

    @property
    def key(self) -> str:
        return f"{self.predicate}({','.join(self.args)})"

    def __hash__(self):
        return hash(self.key)

    def __eq__(self, other):
        return isinstance(other, Fact) and self.key == other.key


class Condition(BaseModel):
    predicate: str
    vars: list[str] = Field(default_factory=list)
    negated: bool = False


class Conclusion(BaseModel):
    predicate: str
    vars: list[str] = Field(default_factory=list)
    expression: str | None = None


class Rule(BaseModel):
    id: str
    description: str = ""
    mode: RuleMode = "certain"
    category: str = "general"
    when: list[Condition] = Field(default_factory=list)
    then: list[Conclusion] = Field(default_factory=list)
    weight: float = 1.0


class InferenceTrace(BaseModel):
    fact_key: str
    rule_id: str
    source_keys: list[str] = Field(default_factory=list)
    bindings: dict[str, str] = Field(default_factory=dict)
    iteration: int = 0


class ReasoningResult(BaseModel):
    facts: list[Fact] = Field(default_factory=list)
    inferred: list[Fact] = Field(default_factory=list)
    hypotheses: list[Fact] = Field(default_factory=list)
    traces: list[InferenceTrace] = Field(default_factory=list)
    contradictions: list[str] = Field(default_factory=list)
    iteration_count: int = 0
    converged: bool = False
    duration_ms: float = 0.0
