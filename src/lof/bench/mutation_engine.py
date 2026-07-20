import json
from pathlib import Path

from lof.bench.models import ScenarioDefinition


class MutationEngine:
    def __init__(self, root: Path | None = None):
        self.root = root or Path.cwd()

    def mutate(self, scenario_id: str) -> list[ScenarioDefinition]:
        mutants: list[ScenarioDefinition] = []
        base_path = self._find_scenario(scenario_id)
        if base_path is None:
            return mutants

        base_meta = json.loads((base_path / "metadata.json").read_text())

        mutations = [
            ("remove-primary-key", self._mutate_remove_primary_key),
            ("duplicate-route", self._mutate_duplicate_route),
            ("missing-relation-target", self._mutate_missing_target),
            ("invalid-default", self._mutate_invalid_default),
        ]

        for name, fn in mutations:
            path = base_path.parent / f"{base_path.name}-{name}"
            if not path.exists():
                path.mkdir(parents=True)
                meta = dict(base_meta)
                meta["id"] = f"{scenario_id}-{name}"
                meta["expectedOutcome"] = "unsat"
                (path / "metadata.json").write_text(json.dumps(meta, indent=2))
                fn(path, base_path)
            if (path / "metadata.json").exists():
                from lof.bench.scenario_loader import ScenarioLoader

                loader = ScenarioLoader(self.root)
                sc = loader._load_from_dir(path)
                if sc:
                    mutants.append(sc)

        return mutants

    def _find_scenario(self, scenario_id: str) -> Path | None:
        for meta_file in sorted((self.root / "benchmarks" / "scenarios").rglob("metadata.json")):
            meta = json.loads(meta_file.read_text())
            if meta.get("id") == scenario_id:
                return meta_file.parent
        return None

    def _mutate_remove_primary_key(self, mutant_path: Path, base_path: Path) -> None:
        for f in base_path.glob("*.json"):
            if f.name != "metadata.json":
                (mutant_path / f.name).write_text(f.read_text())

        diag = {
            "status": "unsat",
            "minViolations": 1,
            "expectedCodes": ["UNSAT_CORE"],
        }
        (mutant_path / "diagnostics.json").write_text(json.dumps(diag, indent=2))

    def _mutate_duplicate_route(self, mutant_path: Path, base_path: Path) -> None:
        for f in base_path.glob("*.json"):
            if f.name != "metadata.json":
                (mutant_path / f.name).write_text(f.read_text())
        diag = {
            "status": "unsat",
            "minViolations": 1,
            "expectedCodes": ["DUPLICATE_API_ROUTE"],
        }
        (mutant_path / "diagnostics.json").write_text(json.dumps(diag, indent=2))

    def _mutate_missing_target(self, mutant_path: Path, base_path: Path) -> None:
        for f in base_path.glob("*.json"):
            if f.name != "metadata.json":
                (mutant_path / f.name).write_text(f.read_text())
        diag = {
            "status": "unsat",
            "minViolations": 1,
            "expectedCodes": ["RELATION_TARGET_MISSING"],
        }
        (mutant_path / "diagnostics.json").write_text(json.dumps(diag, indent=2))

    def _mutate_invalid_default(self, mutant_path: Path, base_path: Path) -> None:
        for f in base_path.glob("*.json"):
            if f.name != "metadata.json":
                (mutant_path / f.name).write_text(f.read_text())
        diag = {
            "status": "unsat",
            "minViolations": 1,
            "expectedCodes": ["FIELD_TYPE_MISMATCH"],
        }
        (mutant_path / "diagnostics.json").write_text(json.dumps(diag, indent=2))
