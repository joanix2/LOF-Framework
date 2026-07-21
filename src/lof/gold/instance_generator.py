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

        for entity in self.application.entities:
            ctx = self.projector.project(entity, self.application.entities)

            instance = {
                "id": entity.id,
                "type": "entity",
                "values": ctx,
                "relations": [
                    {**r, "target": f"{r['target']}-model"}
                    for r in ctx.get("relations", [])
                ],
            }
            path = inst_dir / f"{entity.id}.json"
            path.write_text(json.dumps(instance, indent=2))
            written.append(path)

        return written
