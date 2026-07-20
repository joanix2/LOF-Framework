"""lof new — create a new LOF project."""

from pathlib import Path
from typing import Any

TEMPLATE_DIR = (
    Path(__file__).resolve().parent.parent.parent.parent / "project-templates" / "default"
)  # noqa: E501


def new_project(
    name: str,
    profile: str = "fastapi-react",
    mode: str = "minimal",
    directory: Path | None = None,
) -> dict[str, Any]:
    target = (directory or Path.cwd() / name).resolve()
    if target.exists() and any(target.iterdir()):
        return {"success": False, "error": f"Directory {target} is not empty."}

    target.mkdir(parents=True, exist_ok=True)

    # Generate lof.toml
    settings = {
        "project": {
            "name": name,
            "slug": name.lower().replace("-", "_").replace(" ", "_"),
            "version": "0.1.0",
            "description": f"Project generated with LOF ({profile} profile)",
        },
        "lof": {
            "framework_version": "0.2",
            "dsl_version": "1",
            "profile": profile,
            "mode": mode,
        },
        "paths": {
            "bronze": "app/bronze",
            "silver": "app/silver",
            "gold": "app/gold",
            "rules": "app/rules",
            "constraints": "app/constraints",
            "templates": "app/templates",
            "patches": "app/patches",
            "custom": "app/custom",
            "generated": "generated",
        },
        "pipeline": {
            "semantic_extraction": mode == "intelligent",
            "reasoning": mode != "minimal",
            "semantic_validation": True,
        },
    }
    import tomli_w

    with open(target / "lof.toml", "wb") as f:
        tomli_w.dump(settings, f)

    # Create directory structure
    dirs = [
        "app/bronze",
        "app/silver",
        "app/gold",
        "app/rules",
        "app/constraints",
        "app/templates",
        "app/patches",
        "app/custom",
        "generated",
        "tests",
        ".lof/diagnostics",
        ".lof/manifests",
    ]
    for d in dirs:
        (target / d).mkdir(parents=True, exist_ok=True)

    # Create README
    readme = f"""# {name}

Generated with LOF (profile: {profile}, mode: {mode}).

## Quick start

```bash
lof doctor
lof validate
lof compile
lof check
lof dev
```

## Project structure

```
app/
├── bronze/    — raw tickets (append-only)
├── silver/    — semantic graph
├── gold/      — DSL application model
├── rules/     — inference rules
├── constraints/ — SMT constraints
├── templates/ — Jinja templates (profile overrides)
├── patches/   — AST patches
└── custom/    — user custom code

generated/     — autonomous generated project (no LOF dependency)

.lof/          — LOF internal data (diagnostics, cache, manifests)
```

## Modes

- **minimal** : Gold DSL → validation → compilation
- **standard** : tickets → assistance → Gold → compilation
- **intelligent** : Bronze → Silver → Reasoning → Gold → SMT → compilation
"""
    (target / "README.md").write_text(readme)

    # Create .gitignore
    (target / ".gitignore").write_text("""# LOF
.lof/cache/
.lof/diagnostics/
generated/
!generated/.gitkeep

# Python
__pycache__/
*.py[cod]
.venv/
venv/

# Node
node_modules/

# OS
.DS_Store
""")

    # Create Makefile
    help_awk = """@IFS=:; grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk -F ':.*?## ' '{printf "\\033[36m%-20s\\033[0m %s\\n", $$1, $$2}'"""  # noqa: E501
    makefile = f"""# {name} — LOF project

.PHONY: help doctor validate compile check dev clean

help:
\t{help_awk}

doctor: ## Check LOF environment
	lof doctor

validate: ## Validate project
	lof validate

compile: ## Compile project
	lof compile

check: ## Full validation
	lof check

dev: ## Start development servers
	lof dev

clean: ## Remove generated files
	lof clean
"""
    (target / "Makefile").write_text(makefile)

    (target / ".gitkeep").touch()

    return {
        "success": True,
        "path": str(target),
        "name": name,
        "profile": profile,
        "mode": mode,
        "next": ["lof doctor", "lof validate", "lof compile", "lof dev"],
    }
