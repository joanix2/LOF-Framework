"""Tests for Phase 8: admin CRUD generator from LOF Registry."""

from pathlib import Path

from lof.admin.generators.backend import generate_all as gen_backend
from lof.admin.generators.frontend import generate_all as gen_frontend
from lof.admin.schema.adapter import AdminApp
from lof.loading.loader import Loader
from lof.loading.registry import Registry
from lof.reasoning.profiles.admin_crud import generate


def _registry_with_types() -> Registry:
    """Create registry with ISOCLIM mobile types."""
    loader = Loader(Path.cwd())
    _registry = Registry()
    for t in loader.load_types_from_dir(Path("definitions/types/mobile")):
        _registry.register_type(t)
    for inst in loader.load_instances_from_dir(Path("instances/mobile")):
        _registry.register_instance(inst)
    return _registry


class TestAdminAdapter:
    def test_admin_app_from_registry(self):
        r = _registry_with_types()
        app = AdminApp(r)
        model_names = [m.name for m in app.models]
        assert "mission" in model_names
        assert "employee" in model_names
        assert "client" in model_names
        assert "worksite" in model_names

    def test_admin_model_has_fields(self):
        r = _registry_with_types()
        app = AdminApp(r)
        mission = [m for m in app.models if m.name == "mission"][0]
        field_names = [f.name for f in mission.fields]
        assert "reference" in field_names
        assert "title" in field_names
        assert "status" in field_names

    def test_admin_model_labels(self):
        r = _registry_with_types()
        app = AdminApp(r)
        emp = [m for m in app.models if m.name == "employee"][0]
        assert emp.label == "Employee profile"
        assert emp.table_name == "employees"

    def test_field_widget_inference(self):
        r = _registry_with_types()
        app = AdminApp(r)
        emp = [m for m in app.models if m.name == "employee"][0]
        for f in emp.fields:
            assert f.widget in ("text-input", "textarea", "number-input",
                                "switch", "select", "date-picker",
                                "datetime-picker", "autocomplete")

    def test_enum_fields_detected(self):
        r = _registry_with_types()
        app = AdminApp(r)
        mission = [m for m in app.models if m.name == "mission"][0]
        status = [f for f in mission.fields if f.name == "status"][0]
        assert status.type == "string"


class TestBackendGeneration:
    def test_generates_four_files_per_model(self):
        r = _registry_with_types()
        app = AdminApp(r)
        files = gen_backend(app)
        assert len(files) == 4 * len(app.models)

    def test_model_has_sqlalchemy(self):
        r = _registry_with_types()
        app = AdminApp(r)
        files = gen_backend(app)
        for path, content in files.items():
            if "model.py" in path:
                assert "Column" in content
                assert "declarative_base" in content

    def test_router_has_crud_routes(self):
        r = _registry_with_types()
        app = AdminApp(r)
        files = gen_backend(app)
        for path, content in files.items():
            if "router.py" in path:
                assert "@router.get" in content
                assert "@router.post" in content
                assert "@router.put" in content
                assert "@router.delete" in content


class TestFrontendGeneration:
    def test_generates_six_files_per_model(self):
        r = _registry_with_types()
        app = AdminApp(r)
        files = gen_frontend(app)
        assert len(files) == 6 * len(app.models)

    def test_types_have_interfaces(self):
        r = _registry_with_types()
        app = AdminApp(r)
        files = gen_frontend(app)
        for path, content in files.items():
            if "types.ts" in path:
                assert "export interface" in content


class TestProfileGenerator:
    def test_generate_returns_files(self):
        r = _registry_with_types()
        files = generate(r)
        assert len(files) > 0
        assert any("model.py" in f for f in files)
        assert any("types.ts" in f for f in files)

    def test_generated_files_have_content(self):
        r = _registry_with_types()
        files = generate(r)
        for path, content in files.items():
            assert len(content) > 50, f"{path} is too short"
