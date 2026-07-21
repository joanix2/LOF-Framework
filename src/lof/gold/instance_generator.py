"""Generates one Gold instance per entity — projections are derived by the compiler."""

import json
from pathlib import Path

from lof.gold.profile import Profile
from lof.gold.projection import EntityProjector
from lof.models.gold_models import GoldApplication


class GoldInstanceGenerator:
    def __init__(self, application: GoldApplication, profile: Profile | None = None):
        self.application = application
        self.profile = profile
        self.projector = EntityProjector(profile)

    def generate(self, output_dir: Path) -> list[Path]:
        written = []
        inst_dir = output_dir / ".lof" / "instances"
        inst_dir.mkdir(parents=True, exist_ok=True)

        modules = [e.id for e in self.application.entities]
        app_name = self.application.name or self.application.id.capitalize()

        app_instance = {
            "id": "application",
            "type": "application",
            "values": {
                "id": self.application.id,
                "name": app_name,
                "title": app_name,
                "version": getattr(self.application, "version", "0.1.0"),
                "modules": modules,
                "apiPrefix": "/api/v1",
                "databaseUrl": "sqlite+aiosqlite:///./app.db",
                "echo": False,
            },
        }
        path = inst_dir / "application.json"
        path.write_text(json.dumps(app_instance, indent=2))
        written.append(path)

        for entity in self.application.entities:
            ctx = self.projector.project(entity, self.application.entities)

            instance = {
                "id": entity.id,
                "type": "entity",
                "values": ctx,
                "relations": [
                    {**r, "target": f"{r['target']}-model"} for r in ctx.get("relations", [])
                ],
            }
            path = inst_dir / f"{entity.id}.json"
            path.write_text(json.dumps(instance, indent=2))
            written.append(path)

        return written
