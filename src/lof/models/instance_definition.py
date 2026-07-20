from typing import Any

from pydantic import BaseModel, Field


class InstanceRelationDefinition(BaseModel):
    id: str
    kind: str
    target: str
    source_field: str | None = None
    target_field: str | None = None
    inverse: str | None = None
    required: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class InstanceDefinition(BaseModel):
    id: str
    type: str
    values: dict[str, Any] = Field(default_factory=dict)
    patches: list[str] = Field(default_factory=list)
    enabled: bool = True
    relations: list[InstanceRelationDefinition] = Field(default_factory=list)
