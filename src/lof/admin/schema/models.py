"""Intermediate representation: normalized schema between DSL and generators."""

from typing import Any, Literal

from pydantic import BaseModel, Field

FieldType = Literal[
    "string", "text", "integer", "float", "boolean",
    "enum", "date", "datetime", "uuid", "relation",
]


RelationKind = Literal[
    "one_to_one", "one_to_many", "many_to_one", "many_to_many",
]


class PersistenceMeta(BaseModel):
    indexed: bool = False
    unique: bool = False


class ApiMeta(BaseModel):
    readable: bool = True
    writable: bool = True


class ListUIMeta(BaseModel):
    visible: bool = True
    order: int = 0
    sortable: bool = True
    filterable: bool = True
    searchable: bool = False
    width: int | None = None
    renderer: str | None = None


class FormUIMeta(BaseModel):
    visible: bool = True
    order: int = 0
    section: str = "general"
    readonly: bool = False


class DetailUIMeta(BaseModel):
    visible: bool = True


class FieldUI(BaseModel):
    widget: str | None = None
    label: str | None = None
    placeholder: str | None = None
    help_text: str | None = None
    list: ListUIMeta = Field(default_factory=ListUIMeta)
    form: FormUIMeta = Field(default_factory=FormUIMeta)
    detail: DetailUIMeta = Field(default_factory=DetailUIMeta)


class ModelRelation(BaseModel):
    target: str
    relation: RelationKind
    display_field: str = "id"
    required: bool = False


class ModelField(BaseModel):
    name: str
    type: FieldType = "string"
    required: bool = False
    default: Any = None
    max_length: int | None = None
    primary_key: bool = False
    generated: bool = False
    enum_values: list[str] = Field(default_factory=list, alias="values")
    persistence: PersistenceMeta = Field(default_factory=PersistenceMeta)
    api: ApiMeta = Field(default_factory=ApiMeta)
    ui: FieldUI = Field(default_factory=FieldUI)
    relation: ModelRelation | None = None

    def resolved_widget(self) -> str:
        if self.ui.widget:
            return self.ui.widget
        defaults = {
            "boolean": "switch",
            "enum": "select",
            "text": "textarea",
            "string": "text-input",
            "integer": "number-input",
            "float": "number-input",
            "date": "date-picker",
            "datetime": "datetime-picker",
            "uuid": "text-input",
        }
        if self.relation:
            if self.relation.relation in ("many_to_many",):
                return "multiselect"
            return "autocomplete"
        return defaults.get(self.type, "text-input")


class ModelPermissions(BaseModel):
    create: list[str] = Field(default_factory=lambda: ["admin"])
    read: list[str] = Field(default_factory=lambda: ["admin"])
    update: list[str] = Field(default_factory=lambda: ["admin"])
    delete: list[str] = Field(default_factory=lambda: ["admin"])


class ModelUIMeta(BaseModel):
    edition_mode: str = "drawer"


class ModelSchema(BaseModel):
    name: str
    label: str = ""
    label_plural: str = ""
    display_field: str = "id"
    permissions: ModelPermissions = Field(default_factory=ModelPermissions)
    ui: ModelUIMeta = Field(default_factory=ModelUIMeta)
    fields: list[ModelField] = Field(default_factory=list)

    @property
    def table_name(self) -> str:
        if self.label_plural:
            return self.label_plural.lower().replace(" ", "_")
        return f"{self.name.lower()}s"

    @property
    def route_path(self) -> str:
        return self.table_name.replace("_", "-")

    @property
    def primary_key_field(self) -> ModelField | None:
        for f in self.fields:
            if f.primary_key:
                return f
        if self.fields:
            return self.fields[0]
        return None

    def fields_in_order(self, section: str = "general") -> list[ModelField]:
        return sorted(
            [f for f in self.fields if f.ui.form.section == section],
            key=lambda f: f.ui.form.order,
        )


class ApplicationSchema(BaseModel):
    name: str = "Admin App"
    roles: list[str] = Field(default_factory=lambda: ["admin"])
    models: list[ModelSchema] = Field(default_factory=list)
    version: str = "0.1.0"

    def model_by_name(self, name: str) -> ModelSchema | None:
        for m in self.models:
            if m.name == name:
                return m
        return None
