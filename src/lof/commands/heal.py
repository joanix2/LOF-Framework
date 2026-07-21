"""Self-healing loop: compile → validate → fix → repeat until stable."""

import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from lof.compilation.pipeline import Pipeline
from lof.compilation.projection_expander import ProjectionExpander
from lof.gold.instance_generator import GoldInstanceGenerator
from lof.gold.json_loader import load_gold_application
from lof.gold.profile import Profile
from lof.gold.type_def_generator import TypeDefGenerator
from lof.loading.loader import Loader
from lof.loading.registry import Registry


class HealingLoop:
    def __init__(self, project_dir: Path, max_iterations: int = 10):
        self.project_dir = project_dir.resolve()
        self.max_iterations = max_iterations
        self.history: list[dict[str, Any]] = []
        self.framework_root = Path(__file__).resolve().parent.parent.parent.parent

    def heal(self) -> dict[str, Any]:
        print(f"\n{'=' * 60}")
        print(f"🔁 LOF Healing Loop — {self.project_dir.name}")
        print(f"{'=' * 60}\n")

        for iteration in range(1, self.max_iterations + 1):
            print(f"\n--- Iteration {iteration}/{self.max_iterations} ---")
            iteration_result = {"iteration": iteration, "steps": []}

            self._step(iteration_result, "compile", self._compile)
            self._step(iteration_result, "lint-fix", self._lint_fix)
            self._step(iteration_result, "test", self._run_tests)

            self.history.append(iteration_result)
            errors = iteration_result.get("errors", [])
            test_failures = iteration_result.get("test_failures", 0)

            if not errors and test_failures == 0:
                print(f"\n✅ Tout est stable à l'itération {iteration}")
                return iteration_result

            if iteration < self.max_iterations:
                wait = min(iteration * 0.5, 3.0)
                print(
                    f"  ⏳ {len(errors)} erreur(s), {test_failures} test(s) échouent"
                    f" — nouvelle tentative dans {wait:.1f}s"
                )
                time.sleep(wait)

        print(f"\n⚠️  Maximum d'itérations atteint ({self.max_iterations})")
        return iteration_result

    def _step(self, result: dict, name: str, func) -> None:
        try:
            func(result)
        except Exception as e:
            result.setdefault("errors", []).append(f"{name}: {e}")

    def _compile(self, result: dict) -> None:
        isoclim_json = self.project_dir / "isoclim.json"
        if not isoclim_json.exists():
            result.setdefault("errors", []).append(f"isoclim.json not found in {self.project_dir}")
            return

        profile = Profile.load(
            str(self.framework_root / "profiles" / "fastapi-react" / "profile.json")
        )
        app = load_gold_application(str(isoclim_json))
        GoldInstanceGenerator(app, profile).generate(self.project_dir)
        TypeDefGenerator(profile).generate(self.project_dir)

        templates_src = self.framework_root / "profiles" / "fastapi-react" / "templates"
        if templates_src.exists():
            import shutil

            shutil.copytree(
                str(templates_src), str(self.project_dir / ".lof" / "templates"), dirs_exist_ok=True
            )

        tgt_dir = self.project_dir / ".lof" / "targets"
        tgt_dir.mkdir(parents=True, exist_ok=True)
        import json

        for n, d in [
            (
                "python_module.json",
                {"id": "python-module", "language": "python", "extension": ".py"},
            ),
            (
                "typescript_module.json",
                {"id": "typescript-module", "language": "typescript", "extension": ".ts"},
            ),
            (
                "react_component.json",
                {"id": "react-component", "language": "typescript", "extension": ".tsx"},
            ),
        ]:
            (tgt_dir / n).write_text(json.dumps(d))

        loader = Loader(self.project_dir)
        reg = Registry()
        for t in loader.load_types_from_dir():
            reg.register_type(t)
        for inst in loader.load_instances_from_dir():
            reg.register_instance(inst)

        expanded = ProjectionExpander(reg, profile).expand()
        reg2 = Registry()
        for t in reg.types.values():
            reg2.register_type(t)
        for inst in expanded:
            reg2.register_instance(inst)

        pipeline = Pipeline(reg2, self.project_dir)
        count = 0
        errors = []
        for inst in reg2.instances.values():
            art, errs = pipeline.process_instance(inst)
            if art and not errs:
                count += 1
            if errs:
                errors.extend(errs)

        result["files_generated"] = count
        if errors:
            result.setdefault("errors", []).extend(errors[:3])
        print(f"  ⚙️  Compilation: {count} fichiers")

    def _lint_fix(self, result: dict) -> None:
        api_dir = self.project_dir / "generated-project" / "apps" / "api"
        if not api_dir.exists():
            return
        r = subprocess.run(
            [
                sys.executable,
                "-m",
                "ruff",
                "check",
                "--fix",
                "--ignore",
                "F821,E402,N815,F401",
                str(api_dir / "src"),
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        remaining = len(r.stdout.splitlines()) if r.stdout else 0
        result["lint_remaining"] = remaining
        status = "✅" if r.returncode == 0 else "⚠️"
        print(f"  {status} Lint: {remaining} issue(s)")

    def _run_tests(self, result: dict) -> None:
        api_dir = self.project_dir / "generated-project" / "apps" / "api"
        if not (api_dir / "tests").exists():
            return
        venv_python = api_dir / ".venv" / "bin" / "python"
        if not venv_python.exists():
            venv_python = sys.executable
        r = subprocess.run(
            [str(venv_python), "-m", "pytest", str(api_dir / "tests"), "-q", "--tb=line"],
            capture_output=True,
            text=True,
            timeout=120,
            cwd=api_dir,
            env={"PYTHONPATH": str(api_dir / "src"), **dict(os.environ)},
        )
        failed = (r.stdout or "").count("FAILED") + (r.stderr or "").count("FAILED")
        passed = 0
        import re
        for line in ((r.stdout or "") + (r.stderr or "")).splitlines():
            m = re.search(r"(\d+)\s+passed", line)
            if m:
                passed = int(m.group(1))
        result["test_passed"] = passed
        result["test_failures"] = failed
        status = "✅" if failed == 0 else f"⚠️  ({failed} failed)"
        print(f"  {status} Tests: {passed} pass, {failed} fail")


def heal_project(project_dir: Path, max_iterations: int = 10) -> dict[str, Any]:
    loop = HealingLoop(project_dir, max_iterations)
    return loop.heal()
