from pathlib import Path
from typing import Any

from lof.ast.patch_engine import PatchEngine
from lof.compilation.manifest import ManifestManager
from lof.compilation.writer import Writer
from lof.loading.registry import Registry
from lof.models.artifact import Artifact
from lof.models.instance_definition import InstanceDefinition
from lof.models.patch_definition import PatchDefinition
from lof.models.type_definition import TypeDefinition
from lof.rendering.context_resolver import ContextResolver
from lof.rendering.jinja_renderer import JinjaRenderer
from lof.utils.hashing import compute_hash


class Pipeline:
    def __init__(self, registry: Registry, root: Path | None = None, dry_run: bool = False):
        self.registry = registry
        self.root = root or Path.cwd()
        self.dry_run = dry_run
        self.renderer = JinjaRenderer(self.root)
        self.context_resolver = ContextResolver(registry)
        self.patch_engine = PatchEngine()
        self.writer = Writer(self.root, dry_run)
        self.manifest_manager = ManifestManager(self.root)

    def process_instance(self, instance: InstanceDefinition) -> tuple[Artifact | None, list[str]]:
        errors: list[str] = []
        td = self.registry.get_type(instance.type)
        if td is None:
            errors.append(f"Type '{instance.type}' not found for instance '{instance.id}'")
            return None, errors

        context, diag = self.context_resolver.resolve(instance)
        if diag.has_errors:
            errors.extend(diag.errors)
            return None, errors

        patches: list[PatchDefinition] = []
        for patch_id in instance.patches:
            patch = self.registry.get_patch(patch_id)
            if patch is None:
                errors.append(f"Patch '{patch_id}' not found for instance '{instance.id}'")
                return None, errors
            patches.append(patch)

        source: str | None = None
        template_path: str | None = None
        interface_source: str | None = None

        if td.interface_source and not td.template:
            interface_source = td.interface_source
            src_path = self.root / td.interface_source
            if src_path.exists():
                source = src_path.read_text()
            else:
                errors.append(f"Interface source not found: {td.interface_source}")
                return None, errors
        elif td.template:
            template_path = td.template
            try:
                source = self.renderer.render(td.template, context)
            except Exception as e:
                errors.append(f"Template rendering failed for '{instance.id}': {e}")
                return None, errors
        else:
            errors.append(f"Type '{td.id}' has no template or interface source")
            return None, errors

        if patches and source:
            try:
                language = self._get_language(td)
                source = self.patch_engine.apply_patches(source, patches, language)
            except Exception as e:
                errors.append(f"Patch application failed for '{instance.id}': {e}")
                return None, errors

        output_path = self._resolve_output_path(td, context, instance)
        if output_path:
            try:
                self.writer.write(output_path, source or "")
            except Exception as e:
                errors.append(f"Write failed for '{instance.id}': {e}")
                return None, errors

        artifact = Artifact(
            instance=instance.id,
            type=td.id,
            template=template_path,
            patches=[p.id for p in patches],
            output=output_path or "",
            hash=compute_hash(source or ""),
            interface_source=interface_source,
        )
        return artifact, errors

    def _get_language(self, td: TypeDefinition) -> str:
        if td.target_type:
            target = self.registry.get_target(td.target_type)
            if target:
                return target.language
        return "python"

    def _resolve_output_path(
        self, td: TypeDefinition, context: dict[str, Any], instance: InstanceDefinition
    ) -> str | None:
        if td.output_pattern:
            try:
                return self.renderer.render_from_string(td.output_pattern, context)
            except Exception:
                pass
        name = context.get("name", instance.id)
        from lof.utils.naming import snake_case

        base = snake_case(str(name))
        if td.target_type:
            target = self.registry.get_target(td.target_type)
            if target:
                return f"generated/{target.language}/{base}{target.extension}"
        return f"generated/{base}.txt"
