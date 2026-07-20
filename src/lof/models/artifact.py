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
    compiled_at: str | None = None
    artifacts: list[Artifact] = Field(default_factory=list)


class CompilationReport(BaseModel):
    types_loaded: int = 0
    instances_loaded: int = 0
    patches_loaded: int = 0
    artifacts_generated: list[str] = Field(default_factory=list)
    artifacts_patched: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    success: bool = False
