"""Centralized configuration for the LOP framework."""

from pydantic import BaseModel, Field


class BronzeSettings(BaseModel):
    entries_dir: str = "data/bronze/entries"
    events_dir: str = "data/bronze/events"
    max_ticket_size_bytes: int = 1_000_000


class ExtractionSettings(BaseModel):
    spacy_model: str = "fr_core_news_sm"
    max_doc_length_chars: int = 100_000


class GraphSettings(BaseModel):
    max_depth: int = 5
    max_neighbors: int = 100
    default_reach_depth: int = 3


class ReasoningSettings(BaseModel):
    max_iterations: int = 100
    default_profile: str | None = None
    hypothesis_confidence_threshold: float = 0.5
    rules_dir: str = ".lof/rules"


class SolverSettings(BaseModel):
    timeout_ms: int = 30_000
    max_constraints: int = 500


class CompilationSettings(BaseModel):
    output_dir: str = "generated-project"
    types_dir: str = ".lof/types"
    instances_dir: str = ".lof/instances"
    patches_dir: str = ".lof/patches"
    targets_dir: str = ".lof/targets"
    templates_dir: str = ".lof/templates"
    dry_run: bool = False
    max_artifacts: int = 500


class ValidationSettings(BaseModel):
    strict: bool = True
    diagnostics_dir: str = ".lof/diagnostics"
    constraints_dir: str = ".lof/constraints"


class BenchmarkSettings(BaseModel):
    scenarios_dir: str = "benchmarks/scenarios"
    report_dir: str = "reports"
    max_level: int = 6


class LofSettings(BaseModel):
    bronze: BronzeSettings = Field(default_factory=BronzeSettings)
    extraction: ExtractionSettings = Field(default_factory=ExtractionSettings)
    graph: GraphSettings = Field(default_factory=GraphSettings)
    reasoning: ReasoningSettings = Field(default_factory=ReasoningSettings)
    solver: SolverSettings = Field(default_factory=SolverSettings)
    compilation: CompilationSettings = Field(default_factory=CompilationSettings)
    validation: ValidationSettings = Field(default_factory=ValidationSettings)
    benchmark: BenchmarkSettings = Field(default_factory=BenchmarkSettings)
