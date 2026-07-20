from typing import Any, Literal

from pydantic import BaseModel, Field


class ConstraintSelector(BaseModel):
    types: list[str] | None = None
    instances: list[str] | None = None
    profiles: list[str] | None = None


class DiagnosticDefinition(BaseModel):
    code: str
    message: str
    hint: str | None = None


class ConstraintDefinition(BaseModel):
    id: str
    type: str
    description: str | None = None
    enabled: bool = True
    severity: Literal["error", "warning"] = "error"
    parameters: dict[str, Any] = Field(default_factory=dict)
    applies_to: ConstraintSelector | None = None
    diagnostic: DiagnosticDefinition


class ConstraintViolation(BaseModel):
    constraint_id: str
    code: str
    message: str
    hint: str | None = None
    instance_ids: list[str] = Field(default_factory=list)
    type_ids: list[str] = Field(default_factory=list)
    json_paths: list[str] = Field(default_factory=list)
    unsat_core: list[str] = Field(default_factory=list)
    values: dict[str, Any] = Field(default_factory=dict)
    suggested_patches: list[dict[str, Any]] = Field(default_factory=list)


class SolverResult(BaseModel):
    status: Literal["sat", "unsat", "unknown"]
    diagnostics: list[ConstraintViolation] = Field(default_factory=list)
    statistics: dict[str, Any] = Field(default_factory=dict)
