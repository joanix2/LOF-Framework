import json
import tempfile
from pathlib import Path

from lof.loading.loader import Loader
from lof.loading.registry import Registry


def test_loader_load_type():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        types_dir = root / "definitions" / "types"
        types_dir.mkdir(parents=True)
        type_file = types_dir / "test.json"
        type_file.write_text(
            json.dumps(
                {
                    "id": "test-type",
                    "description": "A test type",
                }
            )
        )
        loader = Loader(root)
        t = loader.load_type(type_file)
        assert t.id == "test-type"
        assert t.description == "A test type"


def test_loader_load_instance():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        inst_file = root / "instances" / "test.json"
        inst_file.parent.mkdir(parents=True)
        inst_file.write_text(
            json.dumps(
                {
                    "id": "test-instance",
                    "type": "test-type",
                    "values": {"key": "value"},
                }
            )
        )
        loader = Loader(root)
        inst = loader.load_instance(inst_file)
        assert inst.id == "test-instance"
        assert inst.values["key"] == "value"


def test_loader_load_patch():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        patch_file = root / "patches" / "python" / "test.json"
        patch_file.parent.mkdir(parents=True)
        patch_file.write_text(
            json.dumps(
                {
                    "id": "test-patch",
                    "language": "python",
                    "operations": [{"op": "add_method", "name": "func", "body": ["pass"]}],
                }
            )
        )
        loader = Loader(root)
        patch = loader.load_patch(patch_file)
        assert patch.id == "test-patch"
        assert len(patch.operations) == 1


def test_registry():
    registry = Registry()
    from lof.models.instance_definition import InstanceDefinition
    from lof.models.type_definition import TypeDefinition

    registry.register_type(TypeDefinition(id="entity"))
    registry.register_instance(InstanceDefinition(id="cust", type="entity"))
    assert registry.has_type("entity")
    assert registry.get_instance("cust") is not None
    assert registry.get_type("missing") is None
