import json
from pathlib import Path

from lof.validation.diagnostics import Diagnostics


class SchemaValidator:
    def __init__(self, root: Path | None = None):
        self.root = root or Path.cwd()
        self._schemas: dict[str, dict] = {}

    def load_schema(self, path: str | Path) -> dict:
        full_path = Path(path) if Path(path).is_absolute() else self.root / path
        with open(full_path) as f:
            return dict(json.load(f))

    def validate_file(self, file_path: str | Path, schema_path: str | Path) -> Diagnostics:
        diag = Diagnostics()
        try:
            data = self._load_json(file_path)
            schema = self.load_schema(schema_path)
            self._validate_basic(data, schema, diag)
        except json.JSONDecodeError as e:
            diag.add_error(f"Invalid JSON in {file_path}: {e}")
        except FileNotFoundError as e:
            diag.add_error(f"File not found: {e}")
        return diag

    def _load_json(self, path: str | Path) -> dict:
        full_path = Path(path) if Path(path).is_absolute() else self.root / path
        with open(full_path) as f:
            return dict(json.load(f))

    def _validate_basic(self, data: dict, schema: dict, diag: Diagnostics) -> None:
        required = schema.get("required", [])
        for field in required:
            if field not in data:
                diag.add_error(f"Missing required field '{field}'")
        props = schema.get("properties", {})
        for key in data:
            if key not in props:
                diag.add_warning(f"Unknown field '{key}'")
        if "id" in data and not isinstance(data["id"], str):
            diag.add_error("Field 'id' must be a string")
