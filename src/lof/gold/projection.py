"""Entity projection — pure data transformation, no hardcoded mappings.

All naming conventions, inverse relation kinds, and defaults
come from the active Profile configuration.
"""

from typing import Any

from lof.gold.profile import Profile
from lof.models.gold_models import GoldCapabilities, ModelDef


def _has_operation(caps: GoldCapabilities, op: str) -> bool:
    return getattr(caps, op, False)


class EntityProjector:
    def __init__(self, profile: Profile | None = None):
        self.profile = profile

    def project(self, entity: ModelDef, all_entities=None) -> dict[str, Any]:
        all_ents = all_entities or [entity]
        caps = entity.capabilities

        route = self._name("route", entity.id)
        table = self._name("table", entity.id)

        fields = []
        for f in entity.fields:
            fd = {
                "name": f.id,
                "type": f.type,
                "label": f.label or f.id,
                "required": f.required,
                "primary": f.primary,
                "nullable": f.nullable,
                "unique": f.unique,
                "searchable": f.searchable,
                "sortable": f.sortable,
                "filterable": f.filterable,
                "list_visible": f.list_visible,
                "detail_visible": f.detail_visible,
                "form_visible": f.form_visible,
                "create_visible": f.create_visible,
                "edit_visible": f.edit_visible,
                "read_only": f.read_only,
                "generated": f.generated,
                "enum_ref": f.enum_ref,
            }
            if f.default is not None:
                fd["default"] = f.default
            if f.min is not None:
                fd["min"] = f.min
            if f.max is not None:
                fd["max"] = f.max
            if f.min_length is not None:
                fd["min_length"] = f.min_length
            if f.max_length is not None:
                fd["max_length"] = f.max_length
            if f.pattern is not None:
                fd["pattern"] = f.pattern
            if f.placeholder is not None:
                fd["placeholder"] = f.placeholder
            if f.description:
                fd["description"] = f.description
            fields.append(fd)

        rels = []
        for r in entity.relations:
            rd = {
                "id": r.id,
                "source": r.source,
                "target": r.target,
                "kind": r.kind,
                "source_field": r.source_field or self._fk_name(r.target),
                "target_field": r.target_field or self._display_field(),
                "target_display_field": r.target_display_field or self._display_field(),
                "required": r.required,
                "nullable": r.nullable,
                "on_delete": r.on_delete,
                "list_visible": r.list_visible,
                "detail_visible": r.detail_visible,
            }
            if r.back_populates:
                rd["back_populates"] = r.back_populates
            rels.append(rd)

        operations = []
        for op in ["create", "read", "update", "delete", "list", "search"]:
            if _has_operation(caps, op):
                operations.append(op)

        profile = self.profile
        inv = (
            profile.inverse_relation_kinds
            if profile
            else {
                "many-to-one": "one-to-many",
                "one-to-one": "one-to-one",
                "one-to-many": "many-to-one",
                "many-to-many": "many-to-many",
            }
        )

        incoming = []
        for other in all_ents:
            if other.id == entity.id:
                continue
            for r in other.relations:
                if r.target == entity.id:
                    inv_kind = inv.get(r.kind, r.kind)
                    incoming.append(
                        {
                            "id": f"inverse_{r.id}",
                            "source": other.id,
                            "target": entity.id,
                            "kind": inv_kind,
                            "source_field": r.target_field,
                            "target_field": r.source_field or self._fk_name(r.target),
                            "target_display_field": r.target_display_field or self._display_field(),
                            "required": r.required,
                            "nullable": r.nullable,
                            "on_delete": r.on_delete,
                            "list_visible": r.list_visible,
                            "detail_visible": r.detail_visible,
                        }
                    )

        audit_f = []
        if profile:
            for af in profile.default_audit_fields():
                audit_f.append(af)

        grid_cols = entity.grid.columns or [
            f.id for f in entity.fields[:5] if getattr(f, "list_visible", True)
        ]  # noqa: E501
        searchable = [f.id for f in entity.fields if f.searchable]
        plural = entity.plural_name
        if not plural:
            plural = entity.name + "s" if entity.name else entity.id + "s"

        return {
            "id": entity.id,
            "name": entity.name or entity.id.capitalize(),
            "pluralName": plural,
            "description": entity.description,
            "route": route,
            "tableName": table,
            "displayField": entity.display_field,
            "fields": fields,
            "relations": rels,
            "incoming_relations": incoming,
            "operations": operations,
            "searchable_fields": searchable,
            "grid_columns": grid_cols,
            "audit_fields": audit_f,
            "navigation_visible": entity.navigation.visible,
        }

    def _name(self, key: str, entity_id: str) -> str:
        p = self.profile
        if p:
            return p.naming_convention(key, entity_id)
        return entity_id.lower()

    def _fk_name(self, target: str) -> str:
        return f"{target}_id"

    def _display_field(self) -> str:
        return "id"
