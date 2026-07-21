"""Projection layer: transforms GoldEntity → template context.

No hardcoded type mappings. Templates handle language specifics via Jinja.
Python only builds the data structure and the computational graph.
"""

from typing import Any

from lof.models.gold_models import GoldEntity


class EntityProjector:
    def project(self, entity: GoldEntity, all_entities: list[GoldEntity] | None = None) -> dict[str, Any]:  # noqa: E501
        all_ents = all_entities or [entity]
        operations = []
        caps = entity.capabilities
        if caps.list:
            operations.append("list")
        if caps.search:
            operations.append("search")
        if caps.create:
            operations.append("create")
        if caps.read:
            operations.append("read")
        if caps.update:
            operations.append("update")
        if caps.delete:
            operations.append("delete")

        route = entity.id.lower().replace("_", "-")
        table = entity.id.lower().replace("-", "_")

        fields = []
        for f in entity.fields:
            fd = {
                "name": f.id, "type": f.type, "label": f.label or f.id,
                "required": f.required, "primary": f.primary,
                "nullable": f.nullable, "unique": f.unique,
                "searchable": f.searchable, "sortable": f.sortable,
                "filterable": f.filterable,
                "list_visible": f.list_visible, "detail_visible": f.detail_visible,
                "form_visible": f.form_visible,
                "create_visible": f.create_visible, "edit_visible": f.edit_visible,
                "read_only": f.read_only, "generated": f.generated,
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

        relations = []
        for r in entity.relations:
            rd = {
                "id": r.id, "source": r.source, "target": r.target,
                "kind": r.kind,
                "source_field": r.source_field or f"{r.target}_id",
                "target_field": r.target_field,
                "target_display_field": r.target_display_field or "id",
                "required": r.required, "nullable": r.nullable,
                "on_delete": r.on_delete,
                "list_visible": r.list_visible, "detail_visible": r.detail_visible,
            }
            if r.back_populates:
                rd["back_populates"] = r.back_populates
            relations.append(rd)

        incoming_relations = self._compute_incoming(entity, all_ents)

        audit_fields = []
        if entity.audit.created_at:
            audit_fields.append("created_at")
        if entity.audit.updated_at:
            audit_fields.append("updated_at")

        grid_columns = entity.grid.columns or [f.id for f in entity.fields[:5] if f.list_visible]
        searchable = [f.id for f in entity.fields if f.searchable]

        return {
            "id": entity.id,
            "name": entity.name or entity.id.capitalize(),
            "pluralName": entity.plural_name or f"{entity.name}s",
            "description": entity.description,
            "route": route,
            "tableName": table,
            "displayField": entity.display_field,
            "fields": fields,
            "relations": relations,
            "incoming_relations": incoming_relations,
            "operations": operations,
            "searchable_fields": searchable,
            "grid_columns": grid_columns,
            "audit_fields": audit_fields,
            "navigation_visible": entity.navigation.visible,
        }

    def _compute_incoming(self, entity: GoldEntity, all_ents: list[GoldEntity]) -> list[dict[str, Any]]:  # noqa: E501
        incoming = []
        inv_kind = {"many-to-one": "one-to-many", "one-to-one": "one-to-one",
                     "one-to-many": "many-to-one", "many-to-many": "many-to-many"}
        for other in all_ents:
            if other.id == entity.id:
                continue
            for r in other.relations:
                if r.target == entity.id:
                    incoming.append({
                        "id": f"inverse_{r.id}",
                        "source": other.id, "target": entity.id,
                        "kind": inv_kind.get(r.kind, r.kind),
                        "source_field": r.target_field,
                        "target_field": r.source_field,
                        "target_display_field": r.target_display_field,
                        "required": r.required, "nullable": r.nullable,
                        "on_delete": r.on_delete,
                        "list_visible": r.list_visible,
                        "detail_visible": r.detail_visible,
                    })
        return incoming
