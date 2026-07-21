"""Generates Gold instances from projected entity context.

Passes the FULL entity context to every projection template.
Templates decide what to use — no if/elif chains on type_id.
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
        inst_dir = output_dir / ".lof" / "instances"
        inst_dir.mkdir(parents=True, exist_ok=True)

        for entity in self.application.entities:
            ctx = self.projector.project(entity, self.application.entities)

            projections = self._build_projections(entity, ctx)

            for suffix, type_id, values in projections:
                instance = {
                    "id": f"{entity.id}-{suffix}",
                    "type": type_id,
                    "values": values,
                    "relations": [],
                }
                path = inst_dir / f"{entity.id}-{suffix}.json"
                path.write_text(json.dumps(instance, indent=2))
                written.append(path)

        return written

    def _build_projections(self, entity, ctx: dict) -> list[tuple[str, str, dict]]:
        if self.profile:
            return self._profile_projections(entity, ctx)
        return self._default_projections(ctx)

    def _profile_projections(self, entity, ctx: dict) -> list[tuple[str, str, dict]]:
        result = []
        for proj_def in self.profile.projections:
            condition = proj_def.get("condition", "always")
            if not self.profile.condition_matches(condition, entity.capabilities):
                continue
            type_id = proj_def["type"]
            suffix = type_id.replace("entity-", "")
            values = dict(ctx)
            if type_id == "entity-model":
                values["relations"] = [
                    {**r, "target": f"{r['target']}-model"}
                    for r in ctx.get("relations", [])
                ]
            result.append((suffix, type_id, values))
        return result

    def _default_projections(self, ctx: dict) -> list[tuple[str, str, dict]]:
        ctx = dict(ctx)
        ctx["relations"] = [
            {**r, "target": f"{r['target']}-model"}
            for r in ctx.get("relations", [])
        ]
        return [
            ("model", "entity-model", ctx),
            ("schemas", "entity-schemas", ctx),
            ("router", "entity-router", ctx),
            ("types", "entity-types", ctx),
            ("hooks", "entity-hooks", ctx),
            ("list-page", "entity-list-page", ctx),
        ]
