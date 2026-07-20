from lof.loading.registry import Registry
from lof.validation.diagnostics import Diagnostics


class SemanticValidator:
    def __init__(self, registry: Registry):
        self.registry = registry

    def validate(self) -> Diagnostics:
        diag = Diagnostics()
        self._validate_type_dependencies(diag)
        self._validate_target_references(diag)
        self._validate_interface_sources(diag)
        self._validate_template_paths(diag)
        return diag

    def _validate_type_dependencies(self, diag: Diagnostics) -> None:
        for t in self.registry.types.values():
            for dep in t.depends_on:
                if dep not in self.registry.types:
                    diag.add_error(f"Type '{t.id}' depends on unknown type '{dep}'")

    def _validate_target_references(self, diag: Diagnostics) -> None:
        for t in self.registry.types.values():
            if t.target_type and t.target_type not in self.registry.targets:
                diag.add_error(f"Type '{t.id}' references unknown target '{t.target_type}'")

    def _validate_interface_sources(self, diag: Diagnostics) -> None:
        for t in self.registry.types.values():
            if t.interface_source:
                path = t.interface_source
                if not path.startswith("interfaces/"):
                    diag.add_warning(
                        f"Type '{t.id}' interface source '{path}' should be under 'interfaces/'"
                    )

    def _validate_template_paths(self, diag: Diagnostics) -> None:
        for t in self.registry.types.values():
            if t.template and not t.template.startswith("templates/"):
                diag.add_warning(
                    f"Type '{t.id}' template '{t.template}' should be under 'templates/'"
                )
