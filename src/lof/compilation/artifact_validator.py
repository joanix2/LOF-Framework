"""Post-generation validation of generated artifacts."""

import subprocess
import sys
from pathlib import Path


class ArtifactValidator:
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.generated = project_dir / "generated"

    def validate_python(self, paths: list[str] | None = None) -> list[str]:
        errors: list[str] = []
        targets = []
        if paths:
            targets = [self.project_dir / p for p in paths]
        else:
            api_dir = self.generated / "apps" / "api"
            if api_dir.exists():
                targets.append(api_dir)
        for target in targets:
            if not target.exists():
                continue
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
                    ],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                if r.returncode != 0:
                    n = len(r.stdout.splitlines())
                    errors.append(f"Python lint ({target.name}): {n} issue(s)")
            except Exception as e:
                errors.append(f"Python lint error ({target.name}): {e}")
        return errors

    def validate_python_tests(self) -> list[str]:
        errors: list[str] = []
        test_dir = self.generated / "apps" / "api" / "tests"
        if not test_dir.exists():
            return errors
        try:
            r = subprocess.run(
                [sys.executable or "python3", "-m", "pytest", str(test_dir), "-q"],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if r.returncode != 0:
                errors.append(f"Python tests: {len(r.stdout.splitlines())} failure(s)")
        except Exception as e:
            errors.append(f"Python test error: {e}")
        return errors

    def validate_typescript(self) -> list[str]:
        errors: list[str] = []
        web_dir = self.generated / "apps" / "web"
        if not web_dir.exists():
            return errors
        try:
            r = subprocess.run(
                ["npx", "tsc", "--noEmit"],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=str(web_dir),
            )
            if r.returncode != 0:
                errors.append(f"TypeScript: {len(r.stdout.splitlines())} issue(s)")
        except Exception as e:
            errors.append(f"TypeScript error: {e}")
        return errors

    def validate_all(self) -> list[str]:
        errors: list[str] = []
        errors.extend(self.validate_python())
        errors.extend(self.validate_typescript())
        errors.extend(self.validate_python_tests())
        return errors
