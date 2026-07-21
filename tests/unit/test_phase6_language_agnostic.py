"""Tests for Phase 6: language-agnostic framework."""

from pathlib import Path

import pytest

from lof.ast.adapter import AstAdapter
from lof.ast.patch_engine import PatchEngine, get_adapter_registry
from lof.compilation.pipeline import Pipeline
from lof.loading.registry import Registry
from lof.models.target_definition import TargetDefinition
from lof.models.type_definition import TypeDefinition


class TestLanguageAgnosticPipeline:
    def test_get_language_from_target(self):
        registry = Registry()
        registry.register_target(TargetDefinition(id="go-module", language="go", extension=".go"))
        td = TypeDefinition(id="test", target_type="go-module")
        pipeline = Pipeline(registry, Path.cwd())
        lang = pipeline._get_language(td)
        assert lang == "go"

    def test_get_language_raises_without_target(self):
        registry = Registry()
        td = TypeDefinition(id="test", target_type="missing-target")
        pipeline = Pipeline(registry, Path.cwd())
        with pytest.raises(ValueError, match="Cannot determine language"):
            pipeline._get_language(td)

    def test_get_language_raises_without_language_field(self):
        registry = Registry()
        registry.register_target(TargetDefinition(id="custom", language="", extension=""))
        td = TypeDefinition(id="test", target_type="custom")
        pipeline = Pipeline(registry, Path.cwd())
        with pytest.raises(ValueError, match="Cannot determine language"):
            pipeline._get_language(td)


class TestAstAdapterRegistry:
    def test_register_custom_adapter(self):
        registry = get_adapter_registry()

        class FakeAdapter(AstAdapter):
            def parse(self, source):
                return source

            def unparse(self, tree):
                return str(tree)

            def apply_operation(self, tree, operation, target_selector=None):
                return tree

        registry.register("fake_lang", FakeAdapter())
        engine = PatchEngine(registry)
        result = engine.apply_patches("code", [], language="fake_lang")
        assert result == "code"

    def test_missing_adapter_raises(self):
        engine = PatchEngine()
        with pytest.raises(ValueError, match="No AST adapter registered"):
            engine.apply_patches("code", [], language="nonexistent")

    def test_unregister_adapter(self):
        registry = get_adapter_registry()

        class DummyAdapter(AstAdapter):
            def parse(self, source):
                return source

            def unparse(self, tree):
                return str(tree)

            def apply_operation(self, tree, op, ts=None):
                return tree

        registry.register("dummy", DummyAdapter())
        assert registry.get("dummy") is not None
        registry.unregister("dummy")
        assert registry.get("dummy") is None


class TestTargetDefinitionFields:
    def test_default_validators(self):
        t = TargetDefinition(id="test", language="go")
        assert t.validators == []

    def test_custom_validators(self):
        t = TargetDefinition(id="test", language="go", validators=["gofmt", "govet"])
        assert len(t.validators) == 2

    def test_dev_command(self):
        t = TargetDefinition(id="test", language="rust", dev_command="cargo watch -x run")
        assert t.dev_command == "cargo watch -x run"

    def test_build_command(self):
        t = TargetDefinition(id="test", language="rust", build_command="cargo build")
        assert t.build_command == "cargo build"


class TestOptionalLibcst:
    def test_libcst_is_optional_extra(self):
        text = Path("pyproject.toml").read_text()
        in_deps = False
        in_opt = False
        libcst_in_core = False
        found_python_ast = False
        libcst_in_opt = False
        for line in text.splitlines():
            if line.strip().startswith("dependencies"):
                in_deps = True
                in_opt = False
            elif line.strip().startswith("[project.optional-dependencies]"):
                in_deps = False
                in_opt = False
            elif "python-ast" in line and "[" in line:
                in_opt = True
                found_python_ast = True
            elif line.strip().startswith("[") and in_opt:
                in_opt = False
            if in_deps and "libcst" in line:
                libcst_in_core = True
            if in_opt and "libcst" in line:
                libcst_in_opt = True
        assert not libcst_in_core, "libcst found in core dependencies"
        assert found_python_ast, "python-ast extra not found"
        assert libcst_in_opt, "libcst not found in python-ast extra"
