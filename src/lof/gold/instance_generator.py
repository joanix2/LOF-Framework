"""Generates Gold instances from projected entity context."""

import json
from pathlib import Path

from lof.gold.projection import EntityProjector
from lof.models.gold_models import GoldApplication


class GoldInstanceGenerator:
    def __init__(self, application: GoldApplication):
        self.application = application
        self.projector = EntityProjector()

    def generate(self, output_dir: Path) -> list[Path]:
        written = []
        for entity in self.application.entities:
            ctx = self.projector.project(entity, self.application.entities)
            instance = {
                "id": ctx["id"],
                "type": "entity-model",
                "values": {
                    "name": ctx["name"],
                    "pluralName": ctx["pluralName"],
                    "route": ctx["route"],
                    "tableName": ctx["tableName"],
                    "fields": ctx["fields"],
                    "operations": ctx["operations"],
                    "displayField": ctx["displayField"],
                },
                "relations": ctx["relations"],
            }
            gold_dir = output_dir / "data" / "gold" / "instances"
            gold_dir.mkdir(parents=True, exist_ok=True)
            path = gold_dir / f"{entity.id}.json"
            path.write_text(json.dumps(instance, indent=2))
            written.append(path)
        return written
