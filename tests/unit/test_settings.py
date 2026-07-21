"""Characterization tests for centralized settings."""

from lof.domain.settings import (
    BronzeSettings,
    CompilationSettings,
    LofSettings,
    SolverSettings,
)


def test_bronze_settings_defaults():
    s = BronzeSettings()
    assert s.entries_dir == "data/bronze/entries"
    assert s.max_ticket_size_bytes == 1_000_000


def test_compilation_settings_defaults():
    s = CompilationSettings()
    assert s.types_dir == ".lof/types"
    assert s.instances_dir == ".lof/instances"
    assert s.dry_run is False


def test_solver_settings_defaults():
    s = SolverSettings()
    assert s.timeout_ms == 30_000
    assert s.max_constraints == 500


def test_lof_settings_composition():
    s = LofSettings()
    assert s.bronze.entries_dir == "data/bronze/entries"
    assert s.compilation.types_dir == ".lof/types"
    assert s.solver.timeout_ms == 30_000
    assert s.reasoning.default_profile is None
    assert s.graph.max_depth == 5


def test_lof_settings_custom():
    s = LofSettings(compilation=CompilationSettings(dry_run=True))
    assert s.compilation.dry_run is True
