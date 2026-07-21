from lof.ast.adapter import AstAdapter
from lof.ast.patch_engine import PatchEngine, get_adapter_registry
from lof.ast.python_libcst import PythonLibCstAdapter

get_adapter_registry().register("python", PythonLibCstAdapter())

__all__ = ["AstAdapter", "PatchEngine", "PythonLibCstAdapter", "get_adapter_registry"]
