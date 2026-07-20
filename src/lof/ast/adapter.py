from abc import ABC, abstractmethod
from typing import Any

from lof.models.patch_definition import PatchOperation


class AstAdapter(ABC):
    @abstractmethod
    def parse(self, source: str) -> object: ...

    @abstractmethod
    def unparse(self, tree: object) -> str: ...

    @abstractmethod
    def apply_operation(
        self, tree: object, operation: PatchOperation, target_selector: dict[str, Any] | None = None
    ) -> object: ...
