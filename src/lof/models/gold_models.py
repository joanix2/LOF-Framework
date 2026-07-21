"""Rich DSL models for entity definition (Gold layer)."""

from typing import Any, Literal

from pydantic import BaseModel, Field


class EnumValue(BaseModel):
    id: str
    label: str = ""
    description: str | None = None
    order: int = 0
    color: str | None = None


class GoldEnum(BaseModel):
    id: str
    values: list[EnumValue] = Field(default_factory=list)


class AttributeDef(BaseModel):
    id: str
    label: str = ""
    type: str = "string"
    required: bool = False
    unique: bool = False
    nullable: bool = True
    searchable: bool = False
    sortable: bool = False
    filterable: bool = False
    list_visible: bool = True
    detail_visible: bool = True
    form_visible: bool = True
    create_visible: bool = True
    edit_visible: bool = True
    read_only: bool = False
    generated: bool = False
    indexed: bool = False
    default: Any = None
    min: float | None = None
    max: float | None = None
    min_length: int | None = None
    max_length: int | None = None
    pattern: str | None = None
    placeholder: str | None = None
    description: str | None = None
    enum_ref: str | None = None
    primary: bool = False


class GoldRelation(BaseModel):
    id: str
    source: str
    target: str
    kind: Literal["one-to-one", "many-to-one", "one-to-many", "many-to-many"]
    source_field: str | None = None
    target_field: str = "id"
    target_display_field: str | None = None
    required: bool = False
    nullable: bool = True
    on_delete: str = "restrict"
    back_populates: str | None = None
    form_widget: str | None = None
    list_visible: bool = True
    detail_visible: bool = True
    eager_loading: bool = False


class GoldCapabilities(BaseModel):
    create: bool = True
    read: bool = True
    update: bool = True
    delete: bool = True
    list: bool = True
    search: bool = True
    pagination: bool = True
    export: bool = False


class GridConfig(BaseModel):
    default_sort_field: str = "created_at"
    default_sort_direction: str = "desc"
    columns: list[str] = Field(default_factory=list)
    filters: list[str] = Field(default_factory=list)
    searchable_fields: list[str] = Field(default_factory=list)


class FormSection(BaseModel):
    id: str
    label: str = ""
    fields: list[str] = Field(default_factory=list)


class FormConfig(BaseModel):
    sections: list[FormSection] = Field(default_factory=list)


class AuditConfig(BaseModel):
    created_at: bool = True
    updated_at: bool = True
    created_by: bool = False
    updated_by: bool = False


class NavigationConfig(BaseModel):
    visible: bool = True
    label: str = ""
    icon: str = "folder"
    order: int = 100


class ModelDef(BaseModel):
    id: str
    name: str = ""
    plural_name: str = ""
    description: str = ""
    display_field: str = "id"
    fields: list[AttributeDef] = Field(default_factory=list)
    enums: list[GoldEnum] = Field(default_factory=list)
    relations: list[GoldRelation] = Field(default_factory=list)
    capabilities: GoldCapabilities = Field(default_factory=GoldCapabilities)
    grid: GridConfig = Field(default_factory=GridConfig)
    forms: FormConfig = Field(default_factory=FormConfig)
    audit: AuditConfig = Field(default_factory=AuditConfig)
    navigation: NavigationConfig = Field(default_factory=NavigationConfig)


class GoldApplication(BaseModel):
    id: str = "app"
    name: str = ""
    profile: str = "fastapi-react"
    entities: list[ModelDef] = Field(default_factory=list)
    enums: list[GoldEnum] = Field(default_factory=list)
