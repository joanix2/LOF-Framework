"""Tests for Phase 8: admin CRUD generator."""

from pathlib import Path

from lof.admin.generators.backend import generate_all as gen_backend
from lof.admin.generators.frontend import generate_all as gen_frontend
from lof.admin.parsers.dsl_parser import parse_dsl
from lof.admin.schema.models import ApplicationSchema

DEMO_YAML = Path("tests/fixtures/admin_demo.yaml")


class TestDSLParsing:
    def test_parse_full_yaml(self):
        app = parse_dsl(DEMO_YAML)
        assert isinstance(app, ApplicationSchema)
        assert app.name == "LMP Admin"
        assert "admin" in app.roles
        assert len(app.models) == 2

    def test_parse_team_model(self):
        app = parse_dsl(DEMO_YAML)
        team = app.model_by_name("Team")
        assert team is not None
        assert team.label == "Équipe"
        assert team.label_plural == "Équipes"
        assert team.display_field == "name"

    def test_parse_team_fields(self):
        app = parse_dsl(DEMO_YAML)
        team = app.model_by_name("Team")
        names = [f.name for f in team.fields]
        assert "id" in names
        assert "name" in names
        assert "active" in names

    def test_parse_employee_fields(self):
        app = parse_dsl(DEMO_YAML)
        emp = app.model_by_name("Employee")
        names = [f.name for f in emp.fields]
        assert "first_name" in names
        assert "last_name" in names
        assert "team" in names
        assert "active" in names

    def test_parse_employee_relation(self):
        app = parse_dsl(DEMO_YAML)
        emp = app.model_by_name("Employee")
        team_field = [f for f in emp.fields if f.name == "team"]
        assert len(team_field) == 1
        assert team_field[0].relation is not None
        assert team_field[0].relation.target == "Team"
        assert team_field[0].relation.relation == "many_to_one"

    def test_parse_permissions(self):
        app = parse_dsl(DEMO_YAML)
        team = app.model_by_name("Team")
        assert "admin" in team.permissions.create
        assert "manager" in team.permissions.create
        assert "employee" in team.permissions.read

    def test_parse_ui_metadata(self):
        app = parse_dsl(DEMO_YAML)
        team = app.model_by_name("Team")
        name_field = [f for f in team.fields if f.name == "name"][0]
        assert name_field.ui.label == "Nom"
        assert name_field.ui.widget == "text-input"
        assert name_field.ui.list.searchable
        assert name_field.ui.form.section == "general"

    def test_resolved_widget(self):
        app = parse_dsl(DEMO_YAML)
        emp = app.model_by_name("Employee")
        active = [f for f in emp.fields if f.name == "active"][0]
        assert active.resolved_widget() == "switch"
        team = [f for f in emp.fields if f.name == "team"][0]
        assert team.resolved_widget() == "autocomplete"

    def test_table_name(self):
        app = parse_dsl(DEMO_YAML)
        team = app.model_by_name("Team")
        assert team.table_name == "équipes"


class TestBackendGeneration:
    def test_generates_model_py(self):
        app = parse_dsl(DEMO_YAML)
        files = gen_backend(app)
        assert any("model.py" in f for f in files)

    def test_generates_schemas(self):
        app = parse_dsl(DEMO_YAML)
        files = gen_backend(app)
        assert any("schemas.py" in f for f in files)

    def test_generates_service(self):
        app = parse_dsl(DEMO_YAML)
        files = gen_backend(app)
        assert any("service.py" in f for f in files)

    def test_generates_router(self):
        app = parse_dsl(DEMO_YAML)
        files = gen_backend(app)
        assert any("router.py" in f for f in files)

    def test_model_has_sqlalchemy(self):
        app = parse_dsl(DEMO_YAML)
        files = gen_backend(app)
        for path, content in files.items():
            if "model.py" in path:
                assert "Column" in content

    def test_router_has_crud_routes(self):
        app = parse_dsl(DEMO_YAML)
        files = gen_backend(app)
        for path, content in files.items():
            if "router.py" in path:
                assert "@router.get" in content
                assert "@router.post" in content
                assert "@router.put" in content
                assert "@router.delete" in content

    def test_eight_files_total(self):
        app = parse_dsl(DEMO_YAML)
        files = gen_backend(app)
        # 2 models × 4 files (model, schemas, service, router)
        assert len(files) == 8


class TestFrontendGeneration:
    def test_generates_types(self):
        app = parse_dsl(DEMO_YAML)
        files = gen_frontend(app)
        assert any("types.ts" in f for f in files)

    def test_generates_service(self):
        app = parse_dsl(DEMO_YAML)
        files = gen_frontend(app)
        assert any("service.ts" in f for f in files)

    def test_generates_hooks(self):
        app = parse_dsl(DEMO_YAML)
        files = gen_frontend(app)
        assert any("hooks.ts" in f for f in files)

    def test_generates_datagrid(self):
        app = parse_dsl(DEMO_YAML)
        files = gen_frontend(app)
        assert any("datagrid.tsx" in f for f in files)

    def test_generates_form(self):
        app = parse_dsl(DEMO_YAML)
        files = gen_frontend(app)
        assert any("form.tsx" in f for f in files)

    def test_generates_list_page(self):
        app = parse_dsl(DEMO_YAML)
        files = gen_frontend(app)
        assert any("list_page.tsx" in f for f in files)

    def test_twelve_files_total(self):
        app = parse_dsl(DEMO_YAML)
        files = gen_frontend(app)
        # 2 models × 6 files = 12
        assert len(files) == 12

    def test_types_have_interfaces(self):
        app = parse_dsl(DEMO_YAML)
        files = gen_frontend(app)
        for path, content in files.items():
            if "types.ts" in path:
                assert "export interface" in content

    def test_hooks_have_crud(self):
        app = parse_dsl(DEMO_YAML)
        files = gen_frontend(app)
        for path, content in files.items():
            if "hooks.ts" in path:
                assert "useQuery" in content
                assert "useMutation" in content


class TestEndToEnd:
    def test_full_pipeline(self):
        app = parse_dsl(DEMO_YAML)
        backend = gen_backend(app)
        frontend = gen_frontend(app)
        total = len(backend) + len(frontend)
        assert total == 20  # 8 backend + 12 frontend

    def test_all_generated_files_have_content(self):
        app = parse_dsl(DEMO_YAML)
        for name, gen in [("backend", gen_backend), ("frontend", gen_frontend)]:
            files = gen(app)
            for path, content in files.items():
                assert len(content) > 50, f"{name}: {path} is too short"
