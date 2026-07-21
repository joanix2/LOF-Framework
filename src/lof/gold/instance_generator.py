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
        gold_dir = output_dir / ".lof" / "gold" / "instances"
        gold_dir.mkdir(parents=True, exist_ok=True)
        inst_dir = output_dir / ".lof" / "instances"
        inst_dir.mkdir(parents=True, exist_ok=True)

        for entity in self.application.entities:
            ctx = self.projector.project(entity, self.application.entities)
            n, pl, rt, tb = ctx["name"], ctx["pluralName"], ctx["route"], ctx["tableName"]  # noqa: E501
            fds, ops = ctx["fields"], ctx["operations"]

            model_relations = [
                {**rel, "target": f"{rel['target']}-model"}
                for rel in ctx.get("relations", [])
            ]

            projections = [
                ("model", "entity-model", {
                    "name": n, "tableName": tb, "fields": fds, "operations": ops,
                    "relations": model_relations,
                }),
                ("schemas", "entity-schemas", {
                    "name": n, "fields": fds,
                }),
                ("router", "entity-router", {
                    "name": n, "route": rt, "pluralName": pl, "operations": ops,
                }),
                ("types", "entity-types", {
                    "name": n, "fields": fds,
                }),
                ("hooks", "entity-hooks", {
                    "name": n, "route": rt, "pluralName": pl,
                }),
                ("list-page", "entity-list-page", {
                    "name": n, "pluralName": pl, "route": rt, "fields": fds,
                }),
            ]

            for suffix, type_id, values in projections:
                instance = {
                    "id": f"{entity.id}-{suffix}",
                    "type": type_id,
                    "values": values,
                    "relations": values.pop("relations", []) if suffix == "model" else [],
                }
                path = gold_dir / f"{entity.id}-{suffix}.json"
                path.write_text(json.dumps(instance, indent=2))
                # Also copy to .lof/instances/ for the compiler
                inst_path = inst_dir / f"{entity.id}-{suffix}.json"
                inst_path.write_text(json.dumps(instance, indent=2))
                written.append(path)

        return written
