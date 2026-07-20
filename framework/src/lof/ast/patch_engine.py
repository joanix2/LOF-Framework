from lof.ast.adapter import AstAdapter
from lof.ast.python_libcst import PythonLibCstAdapter
from lof.models.patch_definition import PatchDefinition


class PatchEngine:
    def __init__(self):
        self._adapters: dict[str, AstAdapter] = {
            "python": PythonLibCstAdapter(),
        }

    def register_adapter(self, language: str, adapter: AstAdapter) -> None:
        self._adapters[language] = adapter

    def apply_patches(
        self, source: str, patches: list[PatchDefinition], language: str = "python"
    ) -> str:
        adapter = self._adapters.get(language)
        if adapter is None:
            raise ValueError(f"No AST adapter registered for language '{language}'")

        tree = adapter.parse(source)
        for patch in patches:
            for operation in patch.operations:
                tree = adapter.apply_operation(tree, operation, patch.target_selector)
        return adapter.unparse(tree)
