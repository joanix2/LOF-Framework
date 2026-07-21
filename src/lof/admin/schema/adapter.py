"""Adapter: maps LOF TypeDefinition/InstanceDefinition to admin schema."""

from lof.loading.registry import Registry
from lof.models.type_definition import TypeDefinition


class AdminField:
    def __init__(self, name: str, param_type: str, required: bool, default, enum: list | None):
        self.name = name
        self.type = param_type
        self.required = required
        self.default = default
        self.enum_values = enum or []
        self.is_relation = param_type == "relation"
        self.relation_target: str | None = None
        self.relation_kind: str = "many_to_one"

    @property
    def ts_type(self) -> str:
        mapping = {
            "string": "string",
            "text": "string",
            "integer": "number",
            "float": "number",
            "boolean": "boolean",
            "date": "string",
            "datetime": "string",
            "enum": "string",
            "uuid": "string",
            "relation": "string",
        }
        return mapping.get(self.type, "string")

    @property
    def py_type(self) -> str:
        mapping = {
            "string": "str",
            "text": "str",
            "integer": "int",
            "float": "float",
            "boolean": "bool",
            "date": "date",
            "datetime": "datetime",
            "enum": "str",
            "uuid": "UUID",
            "relation": "str",
        }
        return mapping.get(self.type, "str")

    @property
    def widget(self) -> str:
        if self.is_relation:
            return "autocomplete"
        defaults = {
            "boolean": "switch",
            "enum": "select",
            "text": "textarea",
            "string": "text-input",
            "integer": "number-input",
            "float": "number-input",
            "date": "date-picker",
            "datetime": "datetime-picker",
        }
        return defaults.get(self.type, "text-input")

    @property
    def sql_type(self) -> str:
        mapping = {
            "string": "String",
            "text": "Text",
            "integer": "Integer",
            "float": "Float",
            "boolean": "Boolean",
            "date": "Date",
            "datetime": "DateTime",
            "uuid": "SA_UUID",
        }
        if self.type == "enum":
            vals = ", ".join(f'"{v}"' for v in self.enum_values)
            return f"Enum({vals})"
        return mapping.get(self.type, "String")


class AdminModel:
    def __init__(self, td: TypeDefinition, registry: Registry):
        self.td = td
        self.registry = registry
        self.fields: list[AdminField] = []
        for name, param in td.parameters.items():
            field = AdminField(name, param.type, param.required, param.default, param.enum)
            self.fields.append(field)

    @property
    def name(self) -> str:
        return self.td.id

    @property
    def label(self) -> str:
        return self.td.description or self.name

    @property
    def label_plural(self) -> str:
        return f"{self.label}s"

    @property
    def table_name(self) -> str:
        return f"{self.name.lower()}s"

    @property
    def route_path(self) -> str:
        return self.table_name.replace("_", "-")

    def fields_for_list(self) -> list[AdminField]:
        return [f for f in self.fields if f.type != "relation"]


class AdminApp:
    def __init__(self, registry: Registry):
        self.models: list[AdminModel] = []
        for td in registry.types.values():
            if td.parameters:
                self.models.append(AdminModel(td, registry))
