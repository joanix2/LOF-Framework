from lof.ast.adapter import AstAdapter
from lof.models.patch_definition import PatchOperation


class TypeScriptTsMorphAdapter(AstAdapter):
    def parse(self, source: str) -> object:
        raise NotImplementedError("TypeScript adapter not yet implemented")

    def unparse(self, tree: object) -> str:
        raise NotImplementedError("TypeScript adapter not yet implemented")

    def apply_operation(self, tree: object, operation: PatchOperation) -> object:
        raise NotImplementedError("TypeScript adapter not yet implemented")
