from pydantic import BaseModel, Field


class TargetDefinition(BaseModel):
    id: str
    language: str
    extension: str = ""
    formatter: str | None = None
    ast_adapter: str | None = None
    validators: list[str] = Field(default_factory=list)
    dev_command: str | None = None
    build_command: str | None = None
    check_command: str | None = None
