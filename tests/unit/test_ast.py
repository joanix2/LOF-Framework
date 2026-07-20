from lof.ast.python_libcst import PythonLibCstAdapter
from lof.models.patch_definition import PatchOperation


def test_parse_unparse():
    adapter = PythonLibCstAdapter()
    source = "x = 1\n"
    tree = adapter.parse(source)
    result = adapter.unparse(tree)
    assert result == source


def test_add_import():
    adapter = PythonLibCstAdapter()
    source = "class Foo:\n    pass\n"
    tree = adapter.parse(source)
    op = PatchOperation(op="add_import", module="typing", import_name="Optional")
    result = adapter.apply_operation(tree, op)
    code = adapter.unparse(result)
    assert "from typing import Optional" in code


def test_add_method():
    adapter = PythonLibCstAdapter()
    source = "class Foo:\n    pass\n"
    tree = adapter.parse(source)
    op = PatchOperation(
        op="add_method",
        name="find_by_email",
        parameters=[{"name": "email", "annotation": "str"}],
        return_type="Optional[Foo]",
        body=["return None"],
    )
    result = adapter.apply_operation(tree, op)
    code = adapter.unparse(result)
    assert "def find_by_email" in code
    assert "Foo" in code


def test_add_import_module_only():
    adapter = PythonLibCstAdapter()
    source = "class Bar:\n    pass\n"
    tree = adapter.parse(source)
    op = PatchOperation(op="add_import", module="os")
    result = adapter.apply_operation(tree, op)
    code = adapter.unparse(result)
    assert "import os" in code


def test_add_decorator():
    adapter = PythonLibCstAdapter()
    source = "class Foo:\n    pass\n"
    tree = adapter.parse(source)
    op = PatchOperation(
        op="add_decorator",
        decorators=["dataclass"],
    )
    result = adapter.apply_operation(tree, op)
    code = adapter.unparse(result)
    assert "@dataclass" in code


def test_preserve_existing_code():
    adapter = PythonLibCstAdapter()
    source = """import os

class Foo:
    def existing(self):
        pass
"""
    tree = adapter.parse(source)
    op = PatchOperation(op="add_import", module="typing", import_name="List")
    result = adapter.apply_operation(tree, op)
    code = adapter.unparse(result)
    assert "import os" in code
    assert "from typing import List" in code
    assert "def existing" in code
