from typing import Any

from pydantic import BaseModel, Field


class InstanceDefinition(BaseModel):
    id: str
    type: str
    values: dict[str, Any] = Field(default_factory=dict)
    patches: list[str] = Field(default_factory=list)
    enabled: bool = True
