from lof.ast.adapter import AstAdapter
from lof.models.patch_definition import PatchDefinition


class _AdapterRegistry:
    def __init__(self):
        self._adapters: dict[str, AstAdapter] = {}

    def register(self, language: str, adapter: AstAdapter) -> None:
        self._adapters[language] = adapter

    def get(self, language: str) -> AstAdapter | None:
        return self._adapters.get(language)

    def unregister(self, language: str) -> None:
        self._adapters.pop(language, None)


_adapter_registry = _AdapterRegistry()


def get_adapter_registry() -> _AdapterRegistry:
    return _adapter_registry


class PatchEngine:
    def __init__(self, adapter_registry: _AdapterRegistry | None = None):
        self._registry = adapter_registry or _adapter_registry

    def register_adapter(self, language: str, adapter: AstAdapter) -> None:
        self._registry.register(language, adapter)

    def apply_patches(
        self, source: str, patches: list[PatchDefinition], language: str = "python"
    ) -> str:
        adapter = self._registry.get(language)
        if adapter is None:
            raise ValueError(f"No AST adapter registered for language '{language}'")

        tree = adapter.parse(source)
        for patch in patches:
            for operation in patch.operations:
                tree = adapter.apply_operation(tree, operation, patch.target_selector)
        return adapter.unparse(tree)
