from typing import Any

from lof.loading.registry import Registry
from lof.models.instance_definition import InstanceDefinition
from lof.validation.diagnostics import Diagnostics


class ContextResolver:
    def __init__(self, registry: Registry):
        self.registry = registry

    def resolve(self, instance: InstanceDefinition) -> tuple[dict[str, Any], Diagnostics]:
        diag = Diagnostics()
        context: dict[str, Any] = {}
        resolved_types: set[str] = set()

        def resolve_type(type_id: str, path: set[str]) -> None:
            if type_id in resolved_types:
                return
            if type_id in path:
                diag.add_error(
                    f"Circular dependency detected during context resolution for type '{type_id}'"
                )
                return
            td = self.registry.get_type(type_id)
            if td is None:
                diag.add_error(f"Type '{type_id}' not found")
                return
            path.add(type_id)
            for dep in td.depends_on:
                resolve_type(dep, path)
            for param_name, param_def in td.parameters.items():
                if param_name not in context:
                    if param_def.default is not None:
                        context[param_name] = param_def.default
                    elif param_def.required:
                        pass
            path.remove(type_id)
            resolved_types.add(type_id)

        resolve_type(instance.type, set())

        context.update(instance.values)

        td = self.registry.get_type(instance.type)
        if td:
            for param_name, param_def in td.parameters.items():
                if param_def.required and param_name not in context:
                    diag.add_error(
                        f"Required parameter '{param_name}' not provided for "
                        f"instance '{instance.id}' of type '{instance.type}'"
                    )

        context["instance_id"] = instance.id
        return context, diag
