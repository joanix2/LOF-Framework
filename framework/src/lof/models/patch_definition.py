from typing import Any

from pydantic import BaseModel, Field


class PatchOperation(BaseModel):
    op: str
    name: str | None = None
    parameters: list[dict[str, Any]] | None = None
    return_type: str | None = None
    body: list[str] | None = None
    decorators: list[str] | None = None
    bases: list[str] | None = None
    target_code: str | None = None
    replacement_code: str | None = None
    module: str | None = None
    import_name: str | None = None
    alias: str | None = None
    annotation: str | None = None
    value: str | None = None
    attributes: list[dict[str, Any]] | None = None


class PatchDefinition(BaseModel):
    id: str
    language: str
    target_selector: dict[str, Any] = Field(default_factory=dict)
    operations: list[PatchOperation]
    depends_on: list[str] = Field(default_factory=list)
