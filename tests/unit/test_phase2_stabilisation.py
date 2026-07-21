"""Tests for Phase 2: reports, session, profile registry, path errors."""

from pathlib import Path

import pytest

from lof.models.reports import (
    CheckReport,
    CompilationReport,
    SemanticValidationReport,
    StepResult,
    ValidationReport,
)
from lof.reasoning.profiles.registry import ProfileRegistry


class TestReports:
    def test_validation_report_defaults(self):
        r = ValidationReport()
        assert r.valid is False
        assert r.errors == []

    def test_validation_report_custom(self):
        r = ValidationReport(valid=True, errors=["e1"], types_loaded=5)
        assert r.valid
        assert r.types_loaded == 5
        assert "e1" in r.errors

    def test_step_result(self):
        s = StepResult(step="lint", passed=True, details=["ok"])
        assert s.step == "lint"
        assert s.passed
        assert s.details == ["ok"]

    def test_compilation_report(self):
        r = CompilationReport(success=True, artifacts_generated=["a.py"])
        assert r.success
        assert r.artifacts_generated == ["a.py"]

    def test_semantic_report(self):
        r = SemanticValidationReport(status="sat")
        assert r.status == "sat"

    def test_check_report_all_passed(self):
        r = CheckReport()
        r.steps.append(StepResult(step="a", passed=True))
        r.steps.append(StepResult(step="b", passed=True))
        r.all_passed = all(s.passed for s in r.steps)
        assert r.all_passed

    def test_check_report_some_failed(self):
        r = CheckReport()
        r.steps.append(StepResult(step="a", passed=True))
        r.steps.append(StepResult(step="b", passed=False))
        r.all_passed = all(s.passed for s in r.steps)
        assert not r.all_passed


class TestProfileRegistry:
    def test_empty_registry(self):
        reg = ProfileRegistry()
        assert reg.list_profiles() == []

    def test_register_profile(self):
        reg = ProfileRegistry()
        reg.register("test", "1.0", "Test profile", [])
        assert reg.get("test") is not None
        assert reg.get("test").version == "1.0"

    def test_get_nonexistent(self):
        reg = ProfileRegistry()
        assert reg.get("missing") is None

    def test_list_profiles(self):
        reg = ProfileRegistry()
        reg.register("a", "1.0", "A", [])
        reg.register("b", "2.0", "B", [])
        assert len(reg.list_profiles()) == 2

    def test_get_rules(self):
        reg = ProfileRegistry()
        rules = ["rule1", "rule2"]
        reg.register("test", "1.0", "Test", rules)
        assert reg.get_rules("test") == rules

    def test_get_rules_nonexistent(self):
        reg = ProfileRegistry()
        assert reg.get_rules("missing") == []


class TestProjectSession:
    def test_session_loads_once(self):
        from pathlib import Path

        from lof.compilation.session import ProjectSession

        session = ProjectSession(Path.cwd())
        assert not session._loaded
        session.load()
        assert session._loaded
        # Loading again should not reload
        session.load()
        assert session._loaded

    def test_session_new_compiler_shares_registry(self):
        from pathlib import Path

        from lof.compilation.session import ProjectSession

        session = ProjectSession(Path.cwd())
        c1 = session.new_compiler()
        c2 = session.new_compiler()
        assert c1.registry is c2.registry
        assert c1.settings is c2.settings


class TestPipelinePathError:
    def test_output_pattern_raises_value_error(self):
        from lof.compilation.pipeline import Pipeline
        from lof.loading.registry import Registry
        from lof.models.instance_definition import InstanceDefinition
        from lof.models.type_definition import TypeDefinition

        td = TypeDefinition(
            id="test",
            output_pattern="{{ invalid_var }}",
        )
        inst = InstanceDefinition(id="x", type="test")
        registry = Registry()
        registry.register_type(td)

        pipeline = Pipeline(registry, Path.cwd())
        with pytest.raises(Exception):
            pipeline._resolve_output_path(td, {}, inst)


class TestManifestVersion:
    def test_manifest_has_dsl_version(self):
        from lof.models.artifact import ProjectManifest

        m = ProjectManifest(project_hash="abc")
        assert m.dsl_version == "0.3.0"

    def test_manifest_custom_version(self):
        from lof.models.artifact import ProjectManifest

        m = ProjectManifest(project_hash="abc", dsl_version="1.0.0")
        assert m.dsl_version == "1.0.0"
