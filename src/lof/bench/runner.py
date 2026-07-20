import json
import time
from pathlib import Path

from lof.bench.models import (
    BenchmarkReport,
    ScenarioDefinition,
    ScenarioResult,
)
from lof.bench.scenario_loader import ScenarioLoader
from lof.compilation.compiler import Compiler
from lof.graph.instance_graph import InstanceGraph
from lof.models.instance_definition import InstanceDefinition
from lof.models.type_definition import TypeDefinition
from lof.validation.smt.validation_engine import SemanticValidationEngine


class BenchmarkRunner:
    def __init__(self, root: Path | None = None):
        self.root = root or Path.cwd()
        self.loader = ScenarioLoader(root)

    def run_all(self, level: int = -1, category: str | None = None) -> BenchmarkReport:
        scenarios = self.loader.list_scenarios()
        if level >= 0:
            scenarios = [s for s in scenarios if s.metadata.level <= level]
        if category:
            scenarios = [s for s in scenarios if s.metadata.category == category]

        results: list[ScenarioResult] = []
        for sc in scenarios:
            results.append(self._run_scenario(sc))

        passed = sum(1 for r in results if r.passed)
        report = BenchmarkReport(
            total_scenarios=len(results),
            passed=passed,
            failed=len(results) - passed,
            pass_rate=passed / len(results) if results else 0.0,
            results=results,
        )
        if results:
            report.composite_score = sum(
                r.bronze_score
                + r.silver_score
                + r.gold_score
                + r.diagnostic_score
                + r.generation_score
                for r in results
            ) / (len(results) * 5.0)
        return report

    def _run_scenario(self, scenario: ScenarioDefinition) -> ScenarioResult:
        start = time.time()
        errors: list[str] = []
        bronze_score = silver_score = gold_score = diagnostic_score = generation_score = 0.0

        with ScenarioState(self.root, scenario) as state:
            bronze_score = self._test_bronze(scenario, errors)
            silver_score = self._test_silver(scenario, errors)
            gold_score = self._test_gold(scenario, errors)
            diagnostic_score = self._test_smt(scenario, errors, state.compiler)
            generation_score = self._test_generation(scenario, errors, state.compiler)

        passed = len(errors) == 0
        duration = (time.time() - start) * 1000

        return ScenarioResult(
            scenario_id=scenario.metadata.id,
            passed=passed,
            bronze_score=bronze_score,
            silver_score=silver_score,
            gold_score=gold_score,
            diagnostic_score=diagnostic_score,
            generation_score=generation_score,
            errors=errors,
            duration_ms=duration,
        )

    def _test_bronze(self, scenario: ScenarioDefinition, errors: list[str]) -> float:
        score = 1.0
        if scenario.bronze.entry_count > 0:
            d = self.root / "data" / "bronze" / "entries"
            if not d.exists():
                errors.append("Bronze: no entries")
                return 0.0
            actual = len(list(d.glob("*.json")))
            if actual < scenario.bronze.entry_count:
                errors.append(f"Bronze: expected >= {scenario.bronze.entry_count}, got {actual}")
                score = min(score, actual / max(scenario.bronze.entry_count, 1))
        return score

    def _test_silver(self, scenario: ScenarioDefinition, errors: list[str]) -> float:
        score = 1.0
        if scenario.silver.entity_count > 0 or scenario.silver.claim_count > 0:
            sd = self.root / "data" / "silver"
            if not sd.exists():
                errors.append("Silver: directory not found")
                return 0.0
            entities = list((sd / "entities").glob("*.json")) if (sd / "entities").exists() else []
            if scenario.silver.entity_count > 0 and len(entities) < scenario.silver.entity_count:
                errors.append(
                    f"Silver: expected>={scenario.silver.entity_count} e, got {len(entities)}"
                )  # noqa: E501
                score = min(score, len(entities) / max(scenario.silver.entity_count, 1))
        return score

    def _test_gold(self, scenario: ScenarioDefinition, errors: list[str]) -> float:
        score = 1.0
        gd = self.root / "data" / "gold" / "instances"
        if scenario.gold.instance_count > 0:
            if not gd.exists():
                errors.append("Gold: directory not found")
                return 0.0
            actual = len(list(gd.glob("*.json")))
            if actual < scenario.gold.instance_count:
                errors.append(f"Gold: expected >= {scenario.gold.instance_count}, got {actual}")
                score = min(score, actual / max(scenario.gold.instance_count, 1))
        return score

    def _test_smt(
        self, scenario: ScenarioDefinition, errors: list[str], compiler: Compiler
    ) -> float:  # noqa: E501
        try:
            ig = InstanceGraph()
            ig.build(compiler.registry.instances)
            engine = SemanticValidationEngine(compiler.registry, ig)
            result = engine.validate()
            expected = scenario.metadata.expected_outcome

            if expected == "sat" and result.status != "sat":
                errors.append(f"SMT: expected {expected}, got {result.status}")
                for d in result.diagnostics:
                    errors.append(f"  {d.code}: {d.message}")
                return 0.0
            if expected == "unsat" and result.status != "unsat":
                errors.append(f"SMT: expected {expected}, got {result.status}")
                return 0.0
            if expected == "sat":
                return 1.0
            if result.status == "unsat":
                codes = [d.code for d in result.diagnostics]
                for ec in scenario.diagnostics.expected_codes:
                    if ec not in codes:
                        errors.append(f"Diagnostic: expected '{ec}' not found (got {codes})")
                        return 0.5
                return 1.0
        except Exception as e:
            errors.append(f"SMT error: {e}")
        return 0.0

    def _test_generation(
        self, scenario: ScenarioDefinition, errors: list[str], compiler: Compiler
    ) -> float:  # noqa: E501
        try:
            report = compiler.compile()
            expected = scenario.metadata.expected_outcome

            if expected == "sat" and not report.success:
                errors.append(f"Generation: {len(report.errors)} error(s)")
                for e in report.errors[:3]:
                    errors.append(f"  {e}")
                return 0.0
            if expected == "unsat" and report.success:
                errors.append("Generation: expected failure but succeeded")
                return 0.0
            if expected == "sat":
                return 1.0
        except Exception as e:
            errors.append(f"Generation error: {e}")
        return 0.0


class ScenarioState:
    def __init__(self, root: Path, scenario: ScenarioDefinition):
        self.root = root
        self.scenario = scenario
        self._instance_backups: dict[str, str] = {}
        self.compiler = Compiler(root)

    def __enter__(self):
        self.compiler.load_all()
        self._setup_invalid_scenario()
        return self

    def __exit__(self, *args):
        self._teardown()

    def _setup_invalid_scenario(self):
        if self.scenario.metadata.expected_outcome != "unsat":
            return
        sid = self.scenario.metadata.id

        if sid == "duplicate-route":
            self._duplicate_route()
        elif sid == "missing-target":
            self._missing_target()
        elif sid == "cycle":
            self._cycle_dep()
        elif sid == "crate-no-endpoint":
            self._remove_operation()
        elif sid == "bad-patch":
            pass
        elif sid == "file-collision":
            self._duplicate_output()

    def _duplicate_route(self):
        registry = self.compiler.registry
        for inst in registry.instances.values():
            if "route" in inst.values and inst.values["route"] == "customers":
                old = dict(inst.values)
                self._instance_backups[inst.id] = json.dumps(old)
                inst.values["route"] = "projects"
                self.compiler.registry.instances[inst.id] = inst
                break

    def _missing_target(self):
        fields = [{"name": "id", "type": "uuid", "primary": True}]
        inst = InstanceDefinition(
            id="test-bad-relation",
            type="entity-model",
            values={"name": "BadRelation", "fields": fields},
            relations=[{"id": "bad-rel", "kind": "many-to-one", "target": "non-existent-instance"}],
        )
        self.compiler.registry.register_instance(inst)
        self._instance_backups["test-bad-relation"] = ""

    def _cycle_dep(self):
        t1 = TypeDefinition(id="cycle-a", depends_on=["cycle-b"])
        t2 = TypeDefinition(id="cycle-b", depends_on=["cycle-a"])
        self.compiler.registry.register_type(t1)
        self.compiler.registry.register_type(t2)

    def _remove_operation(self):
        for inst in self.compiler.registry.instances.values():
            if inst.id == "customer-model":
                ops = inst.values.get("operations", [])
                self._instance_backups["customer-model"] = json.dumps(dict(inst.values))
                if "create" in ops:
                    ops.remove("create")
                inst.values["operations"] = ops

    def _duplicate_output(self):
        t1 = TypeDefinition(
            id="dup-output-a",
            template="templates/backend/model.py.j2",
            target_type="python-module",
            output_pattern="generated/DUPLICATE.py",
            parameters={"name": {"type": "string", "required": True}},
        )
        t2 = TypeDefinition(
            id="dup-output-b",
            template="templates/backend/model.py.j2",
            target_type="python-module",
            output_pattern="generated/DUPLICATE.py",
            parameters={"name": {"type": "string", "required": True}},
        )
        self.compiler.registry.register_type(t1)
        self.compiler.registry.register_type(t2)
        self.compiler.registry.register_instance(
            InstanceDefinition(id="dup-a", type="dup-output-a", values={"name": "A"})
        )
        self.compiler.registry.register_instance(
            InstanceDefinition(id="dup-b", type="dup-output-b", values={"name": "B"})
        )

    def _teardown(self):
        for inst_id, backup in self._instance_backups.items():
            if inst_id in self.compiler.registry.instances:
                if backup:
                    self.compiler.registry.instances[inst_id].values = json.loads(backup)
                else:
                    del self.compiler.registry.instances[inst_id]
        for tid in ["cycle-a", "cycle-b", "dup-output-a", "dup-output-b"]:
            if tid in self.compiler.registry.types:
                del self.compiler.registry.types[tid]
