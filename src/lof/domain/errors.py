"""Error hierarchy for the LOP framework."""


class LofError(Exception):
    """Base error for all LOF errors."""

    code: str = "LOF_ERROR"
    step: str = ""
    suggestion: str = ""

    def __init__(
        self,
        message: str = "",
        *,
        code: str = "",
        step: str = "",
        suggestion: str = "",
        cause: Exception | None = None,
    ):
        self.message = message
        if code:
            self.code = code
        if step:
            self.step = step
        if suggestion:
            self.suggestion = suggestion
        self.cause = cause
        super().__init__(self._format())

    def _format(self) -> str:
        parts = [f"[{self.code}] {self.message}"]
        if self.step:
            parts.append(f" (step: {self.step})")
        if self.suggestion:
            parts.append(f" — {self.suggestion}")
        return "".join(parts)


class ConfigError(LofError):
    code = "CONFIG_ERROR"


class BronzeError(LofError):
    code = "BRONZE_ERROR"


class SilverError(LofError):
    code = "SILVER_ERROR"


class ReasoningError(LofError):
    code = "REASONING_ERROR"


class GoldError(LofError):
    code = "GOLD_ERROR"


class DomainValidationError(LofError):  # trailing underscore to avoid stdlib clash
    code = "VALIDATION_ERROR"


class SMTError(LofError):
    code = "SMT_ERROR"


class TemplateError(LofError):
    code = "TEMPLATE_ERROR"


class AstPatchError(LofError):
    code = "AST_PATCH_ERROR"


class CompilationError(LofError):
    code = "COMPILATION_ERROR"


class ArtifactError(LofError):
    code = "ARTIFACT_ERROR"


class ExternalToolError(LofError):
    code = "EXTERNAL_TOOL_ERROR"
