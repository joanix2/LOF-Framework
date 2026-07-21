"""Parses the YAML DSL into the intermediate representation."""

from pathlib import Path

import yaml

from lof.admin.schema.models import (
    ApiMeta,
    ApplicationSchema,
    DetailUIMeta,
    FieldUI,
    FormUIMeta,
    ListUIMeta,
    ModelField,
    ModelPermissions,
    ModelRelation,
    ModelSchema,
    ModelUIMeta,
    PersistenceMeta,
)


def parse_dsl(source: str | Path) -> ApplicationSchema:
    if isinstance(source, Path):
        source = source.read_text()
    data = yaml.safe_load(source)

    roles = data.get("roles", ["admin"])
    app_name = data.get("application", {}).get("name", "Admin App")

    models: list[ModelSchema] = []
    for model_name, model_data in data.get("models", {}).items():
        model = _parse_model(model_name, model_data)
        models.append(model)

    return ApplicationSchema(name=app_name, roles=roles, models=models)


def _parse_model(name: str, data: dict) -> ModelSchema:
    permissions_data = data.get("permissions", {})
    ui_data = data.get("ui", {})

    fields: list[ModelField] = []
    for field_name, field_data in data.get("fields", {}).items():
        field = _parse_field(field_name, field_data)
        fields.append(field)

    return ModelSchema(
        name=name,
        label=data.get("label", name),
        label_plural=data.get("label_plural", f"{name}s"),
        display_field=data.get("display_field", "id"),
        permissions=ModelPermissions(
            create=permissions_data.get("create", ["admin"]),
            read=permissions_data.get("read", ["admin"]),
            update=permissions_data.get("update", ["admin"]),
            delete=permissions_data.get("delete", ["admin"]),
        ),
        ui=ModelUIMeta(edition_mode=ui_data.get("edition_mode", "drawer")),
        fields=fields,
    )


def _parse_field(name: str, data: dict) -> ModelField:
    raw_relation = data.get("relation")
    relation = None
    if raw_relation is not None:
        if isinstance(raw_relation, dict):
            target = raw_relation.get("target", "")
            rel_kind = raw_relation.get("relation", "many_to_one")
            display = raw_relation.get("display_field", "id")
            req = raw_relation.get("required", False)
        else:
            target = data.get("target", "")
            rel_kind = raw_relation
            display = data.get("display_field", "id")
            req = data.get("required", False)
        relation = ModelRelation(
            target=target,
            relation=rel_kind,
            display_field=display,
            required=req,
        )

    ui_data = data.get("ui", {})
    list_data = ui_data.get("list", {}) if isinstance(ui_data, dict) else {}
    form_data = ui_data.get("form", {}) if isinstance(ui_data, dict) else {}
    detail_data = ui_data.get("detail", {}) if isinstance(ui_data, dict) else {}

    persistence_data = data.get("persistence", {})
    api_data = data.get("api", {})

    return ModelField(
        name=name,
        type=data.get("type", "string"),
        required=data.get("required", False),
        default=data.get("default"),
        max_length=data.get("max_length"),
        primary_key=data.get("primary_key", False),
        generated=data.get("generated", False),
        enum_values=data.get("values", []),
        persistence=PersistenceMeta(
            indexed=persistence_data.get("indexed", False)
            if isinstance(persistence_data, dict) else False,
            unique=persistence_data.get("unique", False)
            if isinstance(persistence_data, dict) else False,
        ),
        api=ApiMeta(
            readable=api_data.get("readable", True)
            if isinstance(api_data, dict) else True,
            writable=api_data.get("writable", True)
            if isinstance(api_data, dict) else True,
        ),
        ui=FieldUI(
            widget=ui_data.get("widget") if isinstance(ui_data, dict) else None,
            label=ui_data.get("label") if isinstance(ui_data, dict) else None,
            placeholder=ui_data.get("placeholder") if isinstance(ui_data, dict) else None,
            help_text=ui_data.get("help_text") if isinstance(ui_data, dict) else None,
            list=ListUIMeta(
                visible=list_data.get("visible", True),
                order=list_data.get("order", 0),
                sortable=list_data.get("sortable", True),
                filterable=list_data.get("filterable", True),
                searchable=list_data.get("searchable", False),
                width=list_data.get("width"),
                renderer=list_data.get("renderer"),
            ),
            form=FormUIMeta(
                visible=form_data.get("visible", True),
                order=form_data.get("order", 0),
                section=form_data.get("section", "general"),
                readonly=form_data.get("readonly", False),
            ),
            detail=DetailUIMeta(
                visible=detail_data.get("visible", True),
            ),
        ),
        relation=relation,
    )
