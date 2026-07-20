from typing import Any

from pydantic import BaseModel, Field


class ParameterDefinition(BaseModel):
    type: str = "string"
    description: str | None = None
    required: bool = False
    default: Any = None
    enum: list[Any] | None = None


class TypeDefinition(BaseModel):
    id: str
    description: str | None = None
    depends_on: list[str] = Field(default_factory=list)
    parameters: dict[str, ParameterDefinition] = Field(default_factory=dict)
    template: str | None = None
    target_type: str | None = None
    interface_source: str | None = None
    output_pattern: str | None = None
