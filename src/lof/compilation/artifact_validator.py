"""Post-generation validation of generated artifacts."""

import subprocess
import sys
from pathlib import Path


class ArtifactValidator:
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir

    def validate_python(self, paths: list[str] | None = None) -> list[str]:
        errors: list[str] = []
        target = self.project_dir / "apps" / "api"
        if not target.exists():
            return errors
        try:
            r = subprocess.run(
                [
                    sys.executable or "python3",
                    "-m",
                    "ruff",
                    "check",
                    "--ignore",
                    "F821,E402,N815,F401",
                    str(target),
                ],  # noqa: E501
                capture_output=True,
                text=True,
                timeout=60,
            )
            if r.returncode != 0:
                errors.append(f"Python lint: {len(r.stdout.splitlines())} issue(s)")
        except Exception as e:
            errors.append(f"Python lint error: {e}")
        return errors

    def validate_python_tests(self) -> list[str]:
        errors: list[str] = []
        target = self.project_dir / "apps" / "api"
        if not (target / "tests").exists():
            return errors
        try:
            r = subprocess.run(
                [sys.executable or "python3", "-m", "pytest", str(target / "tests"), "-q"],  # noqa: E501
                capture_output=True,
                text=True,
                timeout=120,
            )
            if r.returncode != 0:
                errors.append(f"Python tests: {len(r.stdout.splitlines())} failure(s)")
        except Exception as e:
            errors.append(f"Python test error: {e}")
        return errors

    def validate_all(self) -> list[str]:
        errors: list[str] = []
        if (self.project_dir / "apps" / "api").exists():
            errors.extend(self.validate_python())
        if (self.project_dir / "apps" / "web").exists():
            pass  # TypeScript validation would go here
        return errors
