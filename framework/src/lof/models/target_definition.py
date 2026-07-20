from pydantic import BaseModel


class TargetDefinition(BaseModel):
    id: str
    language: str
    extension: str = ""
    formatter: str | None = None
    ast_adapter: str | None = None
