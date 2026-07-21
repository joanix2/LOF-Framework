"""Generates .lof/types/ from the profile's projections.

No more manual type definitions — everything comes from the profile.
"""

import json
from pathlib import Path

from lof.gold.profile import Profile


class TypeDefGenerator:
    def __init__(self, profile: Profile):
        self.profile = profile

    def generate(self, output_dir: Path) -> list[Path]:
        written = []
        target_map = {
            "python-module": "backend",
            "typescript-module": "frontend",
            "react-component": "frontend",
        }

        for proj in self.profile._data.get("projections", []):
            type_id = proj["type"]
            template = proj["template"]
            output_pattern = proj.get("outputPattern", "")
            target_type = proj.get("targetType", "python-module")
            subdir = target_map.get(target_type, "backend")

            # Determine suffix and parameters from context
            params = {
                "name": {"type": "string", "required": True},
                "fields": {"type": "array"},
            }

            td = {
                "id": type_id,
                "template": template,
                "targetType": target_type,
                "outputPattern": output_pattern,
                "parameters": params,
            }

            types_dir = output_dir / ".lof" / "types" / subdir
            types_dir.mkdir(parents=True, exist_ok=True)
            path = types_dir / f"{type_id}.json"
            path.write_text(json.dumps(td, indent=2))
            written.append(path)

        return written
