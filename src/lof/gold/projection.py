"""Projection layer: transforms GoldEntity → normalized projections for templates."""

from dataclasses import dataclass, field
from typing import Any

from lof.models.gold_models import GoldEntity, GoldField, GoldRelation


def _py_type(field: GoldField) -> str:
    mapping = {
        "string": "str",
        "text": "str",
        "email": "EmailStr",
        "phone": "str",
        "url": "str",
        "uuid": "str",
        "enum": "str",
        "integer": "int",
        "float": "float",
        "decimal": "float",
        "boolean": "bool",
        "date": "datetime",
        "datetime": "datetime",
        "percentage": "float",
        "money": "float",
        "file": "str",
        "image": "str",
        "json": "Any",
    }
    return mapping.get(field.type, "str")


def _ts_type(field: GoldField) -> str:
    mapping = {
        "string": "string",
        "text": "string",
        "email": "string",
        "phone": "string",
        "url": "string",
        "uuid": "string",
        "enum": "string",
        "integer": "number",
        "float": "number",
        "decimal": "number",
        "boolean": "boolean",
        "date": "string",
        "datetime": "string",
        "percentage": "number",
        "money": "number",
        "file": "string",
        "image": "string",
        "json": "unknown",
    }
    return mapping.get(field.type, "string")


def _zod_type(field: GoldField) -> str:
    mapping = {
        "string": "z.string()",
        "text": "z.string()",
        "email": "z.string().email()",
        "phone": "z.string()",
        "url": "z.string().url()",
        "uuid": "z.string().uuid()",
        "enum": "z.string()",
        "integer": "z.number().int()",
        "float": "z.number()",
        "decimal": "z.number()",
        "boolean": "z.boolean()",
        "date": "z.string()",
        "datetime": "z.string().datetime()",
        "percentage": "z.number()",
        "money": "z.number()",
        "file": "z.any()",
        "image": "z.any()",
        "json": "z.any()",
    }
    return mapping.get(field.type, "z.string()")


def _sa_type(field: GoldField) -> str:
    mapping = {
        "string": "String(255)",
        "text": "Text",
        "email": "String(255)",
        "phone": "String(50)",
        "url": "String(500)",
        "uuid": "String(36)",
        "enum": "String(50)",
        "integer": "Integer",
        "float": "Float",
        "decimal": "Numeric(12,2)",
        "boolean": "Boolean",
        "date": "Date",
        "datetime": "DateTime",
        "percentage": "Numeric(5,2)",
        "money": "Numeric(12,2)",
        "file": "String(500)",
        "image": "String(500)",
        "json": "JSON",
    }
    return mapping.get(field.type, "String(255)")


@dataclass
class FieldProjection:
    name: str
    type: str
    py_type: str
    ts_type: str
    zod_type: str
    sa_type: str
    required: bool
    nullable: bool
    primary: bool
    unique: bool
    searchable: bool
    sortable: bool
    filterable: bool
    list_visible: bool
    detail_visible: bool
    form_visible: bool
    default: Any = None
    generated: bool = False
    enum_ref: str | None = None
    relation_ref: str | None = None
    minimum: float | None = None
    maximum: float | None = None
    min_length: int | None = None
    max_length: int | None = None
    pattern: str | None = None
    placeholder: str | None = None


@dataclass
class RelationProjection:
    id: str
    source: str
    target: str
    kind: str
    source_field: str | None
    target_field: str
    target_display_field: str | None
    required: bool
    nullable: bool
    on_delete: str
    back_populates: str | None
    form_widget: str
    list_visible: bool
    detail_visible: bool


@dataclass
class EntityProjection:
    id: str
    name: str
    plural_name: str
    description: str
    route: str
    table_name: str
    display_field: str
    fields: list[FieldProjection] = field(default_factory=list)
    relations: list[RelationProjection] = field(default_factory=list)
    incoming_relations: list[RelationProjection] = field(default_factory=list)
    operations: list[str] = field(default_factory=list)
    searchable_fields: list[str] = field(default_factory=list)
    grid_columns: list[str] = field(default_factory=list)
    form_sections: list[dict[str, Any]] = field(default_factory=list)
    audit_fields: list[str] = field(default_factory=list)
    navigation_visible: bool = True

    def to_context(self) -> dict[str, Any]:
        return {
            "entity": self,
            "name": self.name,
            "pluralName": self.plural_name,
            "route": self.route,
            "tableName": self.table_name,
            "fields": [f.__dict__ for f in self.fields],
            "relations": [r.__dict__ for r in self.relations],
            "incoming_relations": [r.__dict__ for r in self.incoming_relations],
            "operations": self.operations,
            "searchable_fields": self.searchable_fields,
            "grid_columns": self.grid_columns,
            "form_sections": self.form_sections,
            "audit_fields": self.audit_fields,
            "navigation_visible": self.navigation_visible,
            "display_field": self.display_field,
        }


class EntityProjector:
    def project(
        self, entity: GoldEntity, all_entities: list[GoldEntity] | None = None
    ) -> EntityProjection:
        all_ents = all_entities or [entity]
        fields = [self._project_field(f, entity, all_ents) for f in entity.fields]

        operations = []
        if entity.capabilities.list:
            operations.append("list")
        if entity.capabilities.search:
            operations.append("search")
        if entity.capabilities.create:
            operations.append("create")
        if entity.capabilities.read:
            operations.append("read")
        if entity.capabilities.update:
            operations.append("update")
        if entity.capabilities.delete:
            operations.append("delete")

        rels = [self._project_relation(r, entity, all_ents) for r in entity.relations]
        incoming = self._compute_incoming(entity, all_ents)

        audit_f = []
        if entity.audit.created_at:
            audit_f.append("created_at")
        if entity.audit.updated_at:
            audit_f.append("updated_at")

        route = entity.id.lower().replace("_", "-")
        table = entity.id.lower().replace("-", "_")

        grid_cols = entity.grid.columns or [f.id for f in entity.fields[:5] if f.list_visible]

        return EntityProjection(
            id=entity.id,
            name=entity.name or entity.id.capitalize(),
            plural_name=entity.plural_name or entity.name + "s",
            description=entity.description,
            route=route,
            table_name=table,
            display_field=entity.display_field,
            fields=fields,
            relations=rels,
            incoming_relations=incoming,
            operations=operations,
            searchable_fields=[f.id for f in entity.fields if f.searchable],
            grid_columns=grid_cols,
            audit_fields=audit_f,
            navigation_visible=entity.navigation.visible,
        )

    def _project_field(
        self, f: GoldField, entity: GoldEntity, all_ents: list[GoldEntity]
    ) -> FieldProjection:
        return FieldProjection(
            name=f.id,
            type=f.type,
            py_type=_py_type(f),
            ts_type=_ts_type(f),
            zod_type=_zod_type(f),
            sa_type=_sa_type(f),
            required=f.required,
            nullable=f.nullable,
            primary=f.primary,
            unique=f.unique,
            searchable=f.searchable,
            sortable=f.sortable,
            filterable=f.filterable,
            list_visible=f.list_visible,
            detail_visible=f.detail_visible,
            form_visible=f.form_visible,
            default=f.default,
            generated=f.generated,
            enum_ref=f.enum_ref,
            minimum=f.min,
            maximum=f.max,
            min_length=f.min_length,
            max_length=f.max_length,
            pattern=f.pattern,
            placeholder=f.placeholder,
        )

    def _project_relation(
        self, r: GoldRelation, entity: GoldEntity, all_ents: list[GoldEntity]
    ) -> RelationProjection:
        sf = r.source_field or f"{r.target}_id"
        widget = r.form_widget or (
            "multi_select" if r.kind == "many-to-many" else "relation_select"
        )
        return RelationProjection(
            id=r.id,
            source=r.source,
            target=r.target,
            kind=r.kind,
            source_field=sf,
            target_field=r.target_field,
            target_display_field=r.target_display_field,
            required=r.required,
            nullable=r.nullable,
            on_delete=r.on_delete,
            back_populates=r.back_populates,
            form_widget=widget,
            list_visible=r.list_visible,
            detail_visible=r.detail_visible,
        )

    def _compute_incoming(
        self, entity: GoldEntity, all_ents: list[GoldEntity]
    ) -> list[RelationProjection]:
        incoming = []
        for other in all_ents:
            if other.id == entity.id:
                continue
            for r in other.relations:
                if r.target == entity.id:
                    inv = RelationProjection(
                        id=f"inverse_{r.id}",
                        source=other.id,
                        target=entity.id,
                        kind={
                            "many-to-one": "one-to-many",
                            "one-to-one": "one-to-one",
                            "one-to-many": "many-to-one",
                            "many-to-many": "many-to-many",
                        }.get(r.kind, r.kind),
                        source_field=r.target_field,
                        target_field=r.source_field,
                        target_display_field=r.target_display_field,
                        required=r.required,
                        nullable=r.nullable,
                        on_delete=r.on_delete,
                        back_populates=r.id,
                        form_widget="relation_select",
                        list_visible=r.list_visible,
                        detail_visible=r.detail_visible,
                    )
                    incoming.append(inv)
        return incoming
