"""Generates Gold instances from projected entities, ready for compilation."""

import json
from pathlib import Path
from typing import Any

from lof.gold.projection import EntityProjection, EntityProjector
from lof.models.gold_models import GoldApplication


class GoldInstanceGenerator:
    def __init__(self, application: GoldApplication):
        self.application = application
        self.projector = EntityProjector()

    def generate(self, output_dir: Path) -> list[Path]:
        instances: list[dict[str, Any]] = []
        written: list[Path] = []

        for entity in self.application.entities:
            proj = self.projector.project(entity, self.application.entities)
            instance = self._to_instance(proj, entity)
            instances.append(instance)

        gold_dir = output_dir / "data" / "gold" / "instances"
        gold_dir.mkdir(parents=True, exist_ok=True)
        for inst in instances:
            path = gold_dir / f"{inst['id']}.json"
            path.write_text(json.dumps(inst, indent=2))
            written.append(path)

        return written

    def _to_instance(self, proj: EntityProjection, entity) -> dict[str, Any]:
        fields = []
        for f in proj.fields:
            fd = {
                "name": f.name,
                "type": f.type,
                "required": f.required,
                "nullable": f.nullable,
                "primary": f.primary,
                "unique": f.unique,
                "searchable": f.searchable,
                "sortable": f.sortable,
                "visibleInList": f.list_visible,
                "visibleInForm": f.form_visible,
                "generated": f.generated,
            }
            if f.default is not None:
                fd["default"] = f.default
            if f.enum_ref:
                fd["enum"] = f.enum_ref
            if f.max_length:
                fd["maxLength"] = f.max_length
            if f.minimum is not None:
                fd["min"] = f.minimum
            if f.maximum is not None:
                fd["max"] = f.maximum
            if f.pattern:
                fd["pattern"] = f.pattern
            fields.append(fd)

        operations = proj.operations
        relations = []
        for r in proj.relations:
            rel = {
                "id": r.id,
                "kind": r.kind,
                "target": r.target,
                "sourceField": r.source_field,
                "targetField": r.target_field,
                "required": r.required,
            }
            if r.back_populates:
                rel["inverse"] = r.back_populates
            relations.append(rel)

        inst = {
            "id": proj.id,
            "type": "entity-model",
            "values": {
                "name": proj.name,
                "pluralName": proj.plural_name,
                "route": proj.route,
                "tableName": proj.table_name,
                "fields": fields,
                "operations": operations,
                "displayField": proj.display_field,
            },
            "relations": relations,
        }
        return inst
