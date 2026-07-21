from pydantic import BaseModel, Field


class Artifact(BaseModel):
    instance: str
    type: str
    template: str | None = None
    patches: list[str] = Field(default_factory=list)
    output: str
    hash: str
    interface_source: str | None = None


class ProjectManifest(BaseModel):
    project_hash: str
    dsl_version: str = "0.3.0"
    compiled_at: str | None = None
    artifacts: list[Artifact] = Field(default_factory=list)
