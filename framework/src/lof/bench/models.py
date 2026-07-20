from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ScenarioMetadata(BaseModel):
    id: str
    title: str
    level: int = 0
    category: str = "general"
    expected_outcome: Literal["sat", "unsat", "unknown", "needs-clarification"] = "sat"
    tags: list[str] = Field(default_factory=list)
    features: list[str] = Field(default_factory=list)


class BronzeExpectation(BaseModel):
    entry_count: int = 0
    fidelity: float = 1.0
    expected_hashes: list[str] = Field(default_factory=list)


class SilverExpectation(BaseModel):
    entity_count: int = 0
    claim_count: int = 0
    relation_count: int = 0
    contradiction_count: int = 0
    expected_entities: list[str] = Field(default_factory=list)
    expected_claims: list[dict[str, str]] = Field(default_factory=list)


class GoldExpectation(BaseModel):
    instance_count: int = 0
    expected_files: list[str] = Field(default_factory=list)
    forbidden_files: list[str] = Field(default_factory=list)


class DiagnosticExpectation(BaseModel):
    status: str = "sat"
    min_violations: int = 0
    max_violations: int = 100
    expected_codes: list[str] = Field(default_factory=list)
    forbidden_codes: list[str] = Field(default_factory=list)


class GenerationExpectation(BaseModel):
    file_count: int = 0
    expected_files: list[str] = Field(default_factory=list)
    forbidden_files: list[str] = Field(default_factory=list)
    deterministic: bool = True


class ScenarioDefinition(BaseModel):
    metadata: ScenarioMetadata
    bronze: BronzeExpectation = Field(default_factory=BronzeExpectation)
    silver: SilverExpectation = Field(default_factory=SilverExpectation)
    gold: GoldExpectation = Field(default_factory=GoldExpectation)
    diagnostics: DiagnosticExpectation = Field(default_factory=DiagnosticExpectation)
    generation: GenerationExpectation = Field(default_factory=GenerationExpectation)


class MetricResult(BaseModel):
    name: str
    value: float
    target: float = 1.0
    weight: float = 1.0


class ScenarioResult(BaseModel):
    scenario_id: str
    passed: bool
    bronze_score: float = 0.0
    silver_score: float = 0.0
    gold_score: float = 0.0
    diagnostic_score: float = 0.0
    generation_score: float = 0.0
    errors: list[str] = Field(default_factory=list)
    metrics: list[MetricResult] = Field(default_factory=list)
    duration_ms: float = 0.0


class BenchmarkReport(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now)
    total_scenarios: int = 0
    passed: int = 0
    failed: int = 0
    pass_rate: float = 0.0
    composite_score: float = 0.0
    results: list[ScenarioResult] = Field(default_factory=list)
    metrics: dict[str, float] = Field(default_factory=dict)
