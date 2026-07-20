from typing import Any

from pydantic import BaseModel, Field


class ParameterDefinition(BaseModel):
    type: str = "string"
    description: str | None = None
    required: bool = False
    default: Any = None
    enum: list[Any] | None = None


class ContextQuery(BaseModel):
    outgoing_relations: dict[str, Any] = Field(default_factory=lambda: {"max_depth": 0})
    incoming_relations: dict[str, Any] = Field(default_factory=lambda: {"max_depth": 0})
    dependencies: dict[str, Any] = Field(default_factory=lambda: {"max_depth": 0})
    dependents: dict[str, Any] = Field(default_factory=lambda: {"max_depth": 0})


class TypeDefinition(BaseModel):
    id: str
    description: str | None = None
    depends_on: list[str] = Field(default_factory=list)
    parameters: dict[str, ParameterDefinition] = Field(default_factory=dict)
    template: str | None = None
    target_type: str | None = None
    interface_source: str | None = None
    output_pattern: str | None = None
    context_query: ContextQuery | None = None
