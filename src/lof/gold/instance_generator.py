"""Generates Gold instances from projected entity context.

All projection types and naming conventions come from the Profile.
No hardcoded list of projections.
"""

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
        gold_dir = output_dir / ".lof" / "gold" / "instances"
        gold_dir.mkdir(parents=True, exist_ok=True)
        inst_dir = output_dir / ".lof" / "instances"
        inst_dir.mkdir(parents=True, exist_ok=True)

        for entity in self.application.entities:
            ctx = self.projector.project(entity, self.application.entities)

            # Build projections from profile definition
            projections = self._build_projections(entity, ctx)

            for suffix, type_id, values in projections:
                instance = {
                    "id": f"{entity.id}-{suffix}",
                    "type": type_id,
                    "values": values,
                    "relations": [],
                }
                path = gold_dir / f"{entity.id}-{suffix}.json"
                path.write_text(json.dumps(instance, indent=2))
                inst_path = inst_dir / f"{entity.id}-{suffix}.json"
                inst_path.write_text(json.dumps(instance, indent=2))
                written.append(path)

        return written

    def _build_projections(self, entity, ctx: dict) -> list[tuple[str, str, dict]]:
        projections = []

        if self.profile:
            for proj_def in self.profile.projections:
                condition = proj_def.get("condition", "always")
                if not self.profile.condition_matches(condition, entity.capabilities):
                    continue

                type_id = proj_def["type"]
                suffix = type_id.replace("entity-", "")

                values = self._values_for_type(type_id, ctx, entity)
                projections.append((suffix, type_id, values))
        else:
            # Fallback sans profile
            projections = self._default_projections(ctx, entity)

        return projections

    def _values_for_type(self, type_id: str, ctx: dict, entity) -> dict:
        base = {
            "name": ctx["name"],
            "pluralName": ctx["pluralName"],
            "route": ctx["route"],
            "tableName": ctx["tableName"],
            "fields": ctx["fields"],
            "operations": ctx["operations"],
        }

        if type_id == "entity-model":
            model_rels = []
            for rel in ctx["relations"]:
                mr = dict(rel)
                mr["target"] = f"{rel['target']}-model"
                model_rels.append(mr)
            return {**base, "tableName": ctx["tableName"], "relations": model_rels}

        if type_id == "entity-router":
            return {"name": ctx["name"], "route": ctx["route"],
                    "pluralName": ctx["pluralName"], "operations": ctx["operations"]}

        if type_id == "entity-hooks":
            return {"name": ctx["name"], "route": ctx["route"],
                    "pluralName": ctx["pluralName"]}

        if type_id in ("entity-types", "entity-schemas", "entity-list-page"):
            return {"name": ctx["name"], "fields": ctx["fields"],
                    "pluralName": ctx.get("pluralName", ctx["name"] + "s"),
                    "route": ctx.get("route", ctx["name"])}

        return base

    def _default_projections(self, ctx: dict, entity) -> list[tuple[str, str, dict]]:
        n, pl, rt, tb = ctx["name"], ctx["pluralName"], ctx["route"], ctx["tableName"]
        fds, ops = ctx["fields"], ctx["operations"]

        model_rels = [dict(r, target=f"{r['target']}-model") for r in ctx.get("relations", [])]
        return [
            ("model", "entity-model", {"name": n, "tableName": tb, "fields": fds,
                                       "operations": ops, "relations": model_rels}),
            ("schemas", "entity-schemas", {"name": n, "fields": fds}),
            ("router", "entity-router", {"name": n, "route": rt, "pluralName": pl, "operations": ops}),
            ("types", "entity-types", {"name": n, "fields": fds}),
            ("hooks", "entity-hooks", {"name": n, "route": rt, "pluralName": pl}),
            ("list-page", "entity-list-page",
             {"name": n, "fields": fds, "pluralName": pl, "route": rt}),
        ]
