"""Tests for Phase 7: mobile-field profile, types, instances, templates."""

from pathlib import Path

from lof.reasoning.profiles import get_profile, list_profiles


class TestMobileFieldProfile:
    def test_profile_registered(self):
        profiles = list_profiles()
        ids = [p.id for p in profiles]
        assert "mobile-field" in ids

    def test_profile_has_rules(self):
        rules = get_profile("mobile-field")
        assert len(rules) > 0
        assert any(r.id == "entity_to_screen" for r in rules)

    def test_profile_rules_are_valid(self):
        from lof.reasoning.engine import DatalogEngine
        rules = get_profile("mobile-field")
        engine = DatalogEngine(rules)
        for rule in rules:
            errors = engine._validate_rule(rule)
            assert len(errors) == 0, f"Rule '{rule.id}' has errors: {errors}"


class TestMobileTypes:
    def test_mission_type_exists(self):
        from lof.loading.loader import Loader
        loader = Loader(Path.cwd())
        types = loader.load_types_from_dir("definitions/types/mobile")
        type_ids = [t.id for t in types]
        assert "mission" in type_ids
        assert "employee" in type_ids


class TestMobileInstances:
    def test_demo_instances_exist(self):
        from lof.loading.loader import Loader
        loader = Loader(Path.cwd())
        instances = loader.load_instances_from_dir("instances/mobile")
        ids = [i.id for i in instances]
        assert "employee-julien" in ids
        assert "employee-karim" in ids
        assert "employee-lucas" in ids
        assert "mission-MIS-042" in ids

    def test_missions_have_team_members(self):
        from lof.loading.loader import Loader
        loader = Loader(Path.cwd())
        missions = [i for i in loader.load_instances_from_dir("instances/mobile")
                    if i.type == "mission"]
        for m in missions:
            members = m.values.get("teamMembers", [])
            assert len(members) > 0, f"Mission {m.id} has no team members"

    def test_three_employees(self):
        from lof.loading.loader import Loader
        loader = Loader(Path.cwd())
        employees = [i for i in loader.load_instances_from_dir("instances/mobile")
                     if i.type == "employee"]
        assert len(employees) >= 3


class TestMobileTargets:
    def test_expo_targets_exist(self):
        from lof.loading.loader import Loader
        loader = Loader(Path.cwd())
        targets = loader.load_targets_from_dir("definitions/targets")
        target_ids = [t.id for t in targets]
        for tid in ["expo-screen", "expo-component", "expo-service"]:
            assert tid in target_ids, f"Target '{tid}' not found"


class TestMobileTemplates:
    def test_template_files_exist(self):
        base = Path("templates/mobile")
        assert (base / "layout" / "_layout.tsx.j2").exists()
        assert (base / "screens" / "today.tsx.j2").exists()
        assert (base / "data" / "demo.ts.j2").exists()
        assert (base / "config" / "package.json.j2").exists()

    def test_demo_data_has_missions(self):
        content = Path("templates/mobile/data/demo.ts.j2").read_text()
        assert "MIS-2026-042" in content
        assert "MIS-2026-043" in content
        assert "MIS-2026-044" in content
        assert "MIS-2026-045" in content
