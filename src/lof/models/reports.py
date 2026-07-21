"""Public result types for the LOF API."""

from pydantic import BaseModel, Field


class StepResult(BaseModel):
    step: str
    passed: bool
    details: list[str] = Field(default_factory=list)


class ValidationReport(BaseModel):
    valid: bool = False
    errors: list[str] = Field(default_factory=list)
    types_loaded: int = 0
    instances_loaded: int = 0
    patches_loaded: int = 0


class SemanticValidationReport(BaseModel):
    status: str = "unknown"
    diagnostics: list[dict] = Field(default_factory=list)


class CompilationReport(BaseModel):
    types_loaded: int = 0
    instances_loaded: int = 0
    patches_loaded: int = 0
    artifacts_generated: list[str] = Field(default_factory=list)
    artifacts_patched: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    success: bool = False


class CheckReport(BaseModel):
    steps: list[StepResult] = Field(default_factory=list)
    compilation: CompilationReport | None = None
    all_passed: bool = False


class Explanation(BaseModel):
    target: str
    found: bool = False
    kind: str | None = None
    details: dict = Field(default_factory=dict)
