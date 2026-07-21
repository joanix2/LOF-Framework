"""Pipeline: resolves context, renders templates, applies patches, writes artifacts."""

from pathlib import Path
from typing import Any

from lof.ast.patch_engine import PatchEngine
from lof.compilation.manifest import ManifestManager
from lof.compilation.writer import Writer
from lof.graph.context_resolver import GraphContextResolver
from lof.graph.instance_graph import InstanceGraph
from lof.loading.registry import Registry
from lof.models.artifact import Artifact
from lof.models.instance_definition import InstanceDefinition
from lof.models.type_definition import TypeDefinition
from lof.rendering.jinja_renderer import JinjaRenderer
from lof.utils.hashing import compute_hash


class Pipeline:
    def __init__(
        self,
        registry: Registry,
        root: Path | None = None,
        dry_run: bool = False,
        staging_root: Path | None = None,
    ):
        self.registry = registry
        self.root = root or Path.cwd()
        self.dry_run = dry_run
        self.staging_root = staging_root
        self.renderer = JinjaRenderer(self.root)
        self.patch_engine = PatchEngine()
        writer_root = staging_root if staging_root else self.root
        self.writer = Writer(writer_root, dry_run)
        self.manifest_manager = ManifestManager(self.root)
        self.instance_graph = InstanceGraph()
        self.instance_graph.build(registry.instances)
        self.graph_context = GraphContextResolver(registry, self.instance_graph)

    def _build_context(self, instance: InstanceDefinition) -> dict[str, Any]:
        ctx: dict[str, Any] = {}

        td = self.registry.get_type(instance.type)
        if td:
            seen: set[str] = set()

            def resolve_type_params(tid: str) -> None:
                if tid in seen:
                    return
                seen.add(tid)
                t = self.registry.get_type(tid)
                if t is None:
                    return
                for dep in t.depends_on:
                    resolve_type_params(dep)
                for name, param in t.parameters.items():
                    if name not in ctx and param.default is not None:
                        ctx[name] = param.default

            resolve_type_params(instance.type)

        ctx.update(instance.values)
        ctx["instance_id"] = instance.id

        graph_ctx, _ = self.graph_context.context_for_template(instance)
        ctx.update(graph_ctx)
        return ctx

    def process_instance(self, instance: InstanceDefinition) -> tuple[Artifact | None, list[str]]:
        errors: list[str] = []
        td = self.registry.get_type(instance.type)
        if td is None:
            errors.append(f"Type '{instance.type}' not found for instance '{instance.id}'")
            return None, errors

        context = self._build_context(instance)

        patches = [p for pid in instance.patches if (p := self.registry.get_patch(pid)) is not None]
        missing = [pid for pid in instance.patches if self.registry.get_patch(pid) is None]
        if missing:
            errors.append(f"Patches not found: {', '.join(missing)}")
            return None, errors

        source: str | None = None
        template_path: str | None = None
        interface_source: str | None = None

        if td.interface_source and not td.template:
            interface_source = td.interface_source
            src = self.root / td.interface_source
            if not src.exists():
                errors.append(f"Interface source not found: {td.interface_source}")
                return None, errors
            source = src.read_text()
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
                lang = self._get_language(td)
                source = self.patch_engine.apply_patches(source, patches, lang)
            except Exception as e:
                errors.append(f"Patch application failed for '{instance.id}': {e}")
                return None, errors

        out = self._resolve_output_path(td, context, instance)
        if out:
            try:
                self.writer.write(out, source or "")
            except Exception as e:
                errors.append(f"Write failed for '{instance.id}': {e}")
                return None, errors

        artifact = Artifact(
            instance=instance.id,
            type=td.id,
            template=template_path,
            patches=[p.id for p in patches],
            output=out or "",
            hash=compute_hash(source or ""),
            interface_source=interface_source,
        )
        return artifact, errors

    def _get_language(self, td: TypeDefinition) -> str:
        if td.target_type:
            tgt = self.registry.get_target(td.target_type)
            if tgt and tgt.language:
                return tgt.language
        raise ValueError(
            f"Cannot determine language for type '{td.id}': "
            f"no target or target has no language defined"
        )

    def _resolve_output_path(
        self, td: TypeDefinition, ctx: dict[str, Any], instance: InstanceDefinition
    ) -> str | None:
        if td.output_pattern:
            try:
                return self.renderer.render_from_string(td.output_pattern, ctx)
            except Exception as e:
                raise ValueError(
                    f"Output pattern rendering failed for '{instance.id}': "
                    f"pattern='{td.output_pattern}', error={e}"
                )
        name = ctx.get("name", instance.id)
        from lof.utils.naming import snake_case

        base = snake_case(str(name))
        if td.target_type:
            tgt = self.registry.get_target(td.target_type)
            if tgt:
                return f"generated/{tgt.language}/{base}{tgt.extension}"
        return f"generated/{base}.txt"
