"""Project session — shared context across compilation operations."""

from pathlib import Path

from lof.compilation.compiler import Compiler
from lof.domain.settings import LofSettings
from lof.loading.loader import Loader
from lof.loading.registry import Registry


class ProjectSession:
    """Holds shared state across Project operations (validate, compile, etc.)."""

    def __init__(self, root: Path, settings: LofSettings | None = None):
        self.root = root
        self.settings = settings or LofSettings()
        self._registry: Registry | None = None
        self._loaded = False

    @property
    def registry(self) -> Registry:
        if self._registry is None:
            self._registry = Registry()
        return self._registry

    def load(self) -> None:
        if self._loaded:
            return
        loader = Loader(self.root)
        for t in loader.load_types_from_dir():
            self.registry.register_type(t)
        for inst in loader.load_instances_from_dir():
            self.registry.register_instance(inst)
        for p in loader.load_patches_from_dir():
            self.registry.register_patch(p)
        for t in loader.load_targets_from_dir():
            self.registry.register_target(t)
        self._loaded = True

    def new_compiler(
        self,
        dry_run: bool = False,
        instance_filter: str | None = None,
        type_filter: str | None = None,
        force: bool = False,
    ) -> Compiler:
        self.load()
        return Compiler(
            root=self.root,
            dry_run=dry_run,
            instance_filter=instance_filter,
            type_filter=type_filter,
            force=force,
            registry=self.registry,
            settings=self.settings,
        )
