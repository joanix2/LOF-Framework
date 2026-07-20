"""Characterization tests for error hierarchy."""

from lof.domain.errors import (
    BronzeError,
    CompilationError,
    ConfigError,
    LofError,
    SMTError,
    TemplateError,
)


def test_lof_error_default_code():
    e = LofError("test error")
    assert e.code == "LOF_ERROR"
    assert "test error" in str(e)


def test_lof_error_custom_code():
    e = LofError("custom", code="CUSTOM_CODE")
    assert e.code == "CUSTOM_CODE"


def test_lof_error_with_suggestion():
    e = LofError("missing", step="validate", suggestion="add a primary key")
    assert e.step == "validate"
    assert e.suggestion == "add a primary key"


def test_bronze_error():
    e = BronzeError("cannot write")
    assert e.code == "BRONZE_ERROR"


def test_smt_error():
    e = SMTError("unsat model", step="smt")
    assert e.code == "SMT_ERROR"
    assert e.step == "smt"


def test_compilation_error():
    e = CompilationError("generation failed")
    assert e.code == "COMPILATION_ERROR"


def test_template_error():
    e = TemplateError("undefined variable")
    assert e.code == "TEMPLATE_ERROR"


def test_config_error():
    e = ConfigError("invalid path")
    assert e.code == "CONFIG_ERROR"
