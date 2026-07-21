"""Tests for Phase 1 fixes: contradictions, writer validation, atomicity."""

from pathlib import Path

import pytest

from lof.compilation.writer import ArtifactPath, ArtifactPathError, Writer
from lof.reasoning.engine import DatalogEngine
from lof.reasoning.models import Conclusion, Condition, Fact, Rule


class TestContradictionFix:
    def test_polarity_field_exists(self):
        f = Fact(predicate="p", args=("x",), polarity="positive")
        assert f.polarity == "positive"

    def test_polarity_negative(self):
        f = Fact(predicate="p", args=("x",), polarity="negative")
        assert f.polarity == "negative"

    def test_rejected_is_not_active(self):
        f = Fact(predicate="test", args=("a",), status="rejected")
        assert not f.is_active

    def test_asserted_is_active(self):
        f = Fact(predicate="test", args=("a",), status="asserted")
        assert f.is_active

    def test_engine_detects_polarity_contradiction(self):
        rule = Rule(
            id="test_rule",
            when=[Condition(predicate="input", vars=["x"])],
            then=[Conclusion(predicate="p", vars=["x"])],
        )
        engine = DatalogEngine([rule])
        facts = [
            Fact(predicate="p", args=("x",), status="asserted", polarity="negative"),
            Fact(predicate="input", args=("x",), status="asserted"),
        ]
        result = engine.evaluate(facts)
        assert len(result.contradictions) >= 1
        assert "Contradiction" in result.contradictions[0]

    def test_engine_rejected_no_contradiction(self):
        rule = Rule(
            id="test_rule",
            when=[Condition(predicate="input", vars=["x"])],
            then=[Conclusion(predicate="p", vars=["x"])],
        )
        engine = DatalogEngine([rule])
        facts = [
            Fact(predicate="p", args=("x",), status="rejected", polarity="negative"),
            Fact(predicate="input", args=("x",), status="asserted"),
        ]
        result = engine.evaluate(facts)
        assert len(result.contradictions) == 0

    def test_engine_same_polarity_no_contradiction(self):
        rule = Rule(
            id="test_rule",
            when=[Condition(predicate="input", vars=["x"])],
            then=[Conclusion(predicate="p", vars=["x"])],
        )
        engine = DatalogEngine([rule])
        facts = [
            Fact(predicate="p", args=("x",), status="asserted", polarity="positive"),
            Fact(predicate="input", args=("x",), status="asserted"),
        ]
        result = engine.evaluate(facts)
        assert len(result.contradictions) == 0


class TestArtifactPathValidation:
    def test_simple_path_ok(self, tmp_path: Path):
        ArtifactPath._validate("apps/api/main.py", tmp_path)
        resolved = ArtifactPath.resolve_inside("apps/api/main.py", tmp_path)
        assert str(resolved).startswith(str(tmp_path.resolve()))

    def test_path_traversal_raises(self, tmp_path: Path):
        with pytest.raises(ArtifactPathError, match=r"\.\."):
            ArtifactPath._validate("../../outside.py", tmp_path)

    def test_absolute_path_raises(self, tmp_path: Path):
        with pytest.raises(ArtifactPathError, match="Absolute path"):
            ArtifactPath._validate("/etc/passwd", tmp_path)

    def test_tilde_path_raises(self, tmp_path: Path):
        with pytest.raises(ArtifactPathError):
            ArtifactPath._validate("~/evil.py", tmp_path)

    def test_whitespace_raises(self, tmp_path: Path):
        with pytest.raises(ArtifactPathError, match="whitespace"):
            ArtifactPath._validate("  leading.py", tmp_path)

    def test_writer_write_validates(self, tmp_path: Path):
        w = Writer(tmp_path)
        with pytest.raises(ArtifactPathError, match=r"\.\."):
            w.write("../../escape.py", "x")

    def test_writer_copy_file_validates(self, tmp_path: Path):
        w = Writer(tmp_path)
        with pytest.raises(ArtifactPathError, match=r"\.\."):
            w.copy_file("source.txt", "../../escape.txt")

    def test_writer_write_creates_file(self, tmp_path: Path):
        w = Writer(tmp_path)
        result = w.write("subdir/test.txt", "content")
        assert result.exists()
        assert result.read_text() == "content"


class TestCompilerDefaults:
    def test_compiler_default_filter_none(self):
        from lof.compilation.compiler import Compiler

        c = Compiler(Path.cwd())
        assert c.instance_filter is None
        assert c.type_filter is None
        assert not c.force
