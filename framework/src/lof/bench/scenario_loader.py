import json
from pathlib import Path
from typing import Any

from lof.bench.models import (
    BronzeExpectation,
    DiagnosticExpectation,
    GenerationExpectation,
    GoldExpectation,
    ScenarioDefinition,
    ScenarioMetadata,
    SilverExpectation,
)


class ScenarioLoader:
    def __init__(self, root: Path | None = None):
        self.root = root or Path.cwd()
        self._scenarios_dir = self.root / "benchmarks" / "scenarios"

    def list_scenarios(self) -> list[ScenarioDefinition]:
        scenarios: list[ScenarioDefinition] = []
        for meta_file in sorted(self._scenarios_dir.rglob("metadata.json")):
            scenarios.append(self._load_from_dir(meta_file.parent))
        return scenarios

    def get_scenario(self, scenario_id: str) -> ScenarioDefinition | None:
        for meta_file in self._scenarios_dir.rglob("metadata.json"):
            parent = meta_file.parent
            meta = json.loads(meta_file.read_text())
            if meta.get("id") == scenario_id:
                return self._load_from_dir(parent)
        return None

    def _load_from_dir(self, scenario_dir: Path) -> ScenarioDefinition:
        meta_path = scenario_dir / "metadata.json"
        meta_data = json.loads(meta_path.read_text())

        return ScenarioDefinition(
            metadata=ScenarioMetadata(**meta_data),
            bronze=self._load_optional(scenario_dir / "bronze.json", BronzeExpectation),
            silver=self._load_optional(scenario_dir / "silver.json", SilverExpectation),
            gold=self._load_optional(scenario_dir / "gold.json", GoldExpectation),
            diagnostics=self._load_optional(
                scenario_dir / "diagnostics.json", DiagnosticExpectation
            ),
            generation=self._load_optional(
                scenario_dir / "generation.json", GenerationExpectation
            ),
        )

    def _load_optional(self, path: Path, model_class: type) -> Any:
        if path.exists():
            return model_class(**json.loads(path.read_text()))
        return model_class()
