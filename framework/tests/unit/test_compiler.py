import json
import tempfile
from pathlib import Path

from lof.compilation.compiler import Compiler


def test_compiler_load_and_validate():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _setup_minimal_project(root)
        compiler = Compiler(root)
        compiler.load_all()
        errors = compiler.validate_all()
        assert not errors, f"Validation errors: {errors}"


def test_compiler_compile():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        _setup_minimal_project(root)
        compiler = Compiler(root)
        report = compiler.compile()
        assert report.success, f"Errors: {report.errors}"


def _setup_minimal_project(root: Path) -> None:
    (root / "definitions" / "types").mkdir(parents=True)
    (root / "definitions" / "targets").mkdir(parents=True)
    (root / "instances").mkdir(parents=True)
    (root / "templates" / "python").mkdir(parents=True)
    (root / "patches" / "python").mkdir(parents=True)
    (root / "schemas").mkdir(parents=True)

    (root / "definitions" / "types" / "entity.json").write_text(
        json.dumps(
            {
                "id": "entity",
                "description": "A test entity",
                "parameters": {
                    "name": {"type": "string", "required": True},
                    "fields": {"type": "array", "required": True},
                },
                "template": "templates/python/entity.py.j2",
                "targetType": "python-module",
                "outputPattern": "generated/python/{{ name | snake_case }}.py",
            }
        )
    )

    (root / "definitions" / "targets" / "python.json").write_text(
        json.dumps(
            {
                "id": "python-module",
                "language": "python",
                "extension": ".py",
                "astAdapter": "libcst",
            }
        )
    )

    (root / "templates" / "python" / "entity.py.j2").write_text("class {{ name }}:\n    pass\n")

    (root / "instances" / "test.json").write_text(
        json.dumps(
            {
                "id": "test-entity",
                "type": "entity",
                "values": {"name": "TestEntity", "fields": []},
            }
        )
    )
