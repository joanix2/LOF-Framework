"""Generic pipeline stage protocol and execution context."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol


@dataclass
class PipelineContext:
    root: Path = Path.cwd()
    dry_run: bool = False
    data: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class StageResult:
    success: bool = True
    errors: list[str] = field(default_factory=list)
    output: Any = None


class PipelineStage(Protocol):
    name: str

    def execute(self, context: PipelineContext) -> StageResult: ...


class PipelineOrchestrator:
    def __init__(self, stages: list[PipelineStage]):
        self.stages = stages

    def run(self, context: PipelineContext | None = None) -> PipelineContext:
        ctx = context or PipelineContext()
        for stage in self.stages:
            result = stage.execute(ctx)
            ctx.errors.extend(result.errors)
            if not result.success:
                ctx.data["failed_stage"] = stage.name
                break
            if result.output is not None:
                ctx.data[stage.name] = result.output
        return ctx
