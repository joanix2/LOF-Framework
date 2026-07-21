from pathlib import Path

from lof.utils.paths import ensure_dir


class ArtifactPathError(ValueError):
    pass


class ArtifactPath:
    def __init__(self, path: str, output_root: Path):
        self._validate(path, output_root)

    @staticmethod
    def resolve_inside(path: str, output_root: Path) -> Path:
        resolved = (output_root.resolve() / path).resolve()
        if not str(resolved).startswith(str(output_root.resolve())):
            raise ArtifactPathError(
                f"Path traversal detected: '{path}' resolves outside '{output_root}'"
            )
        return resolved

    @staticmethod
    def _validate(path: str, output_root: Path) -> None:
        if not path or path.strip() != path:
            raise ArtifactPathError(f"Path '{path}' has leading/trailing whitespace")
        if ".." in path.split("/"):
            raise ArtifactPathError(f"Path '{path}' contains '..' segments")
        if path.startswith("/"):
            raise ArtifactPathError(f"Absolute path '{path}' is not allowed")
        if "~" in path:
            raise ArtifactPathError(f"Path '{path}' contains '~'")
        resolved = ArtifactPath.resolve_inside(path, output_root)
        if not resolved.parent.exists():
            resolved.parent.mkdir(parents=True, exist_ok=True)


class Writer:
    def __init__(self, root: Path | None = None, dry_run: bool = False):
        self.root = (root or Path.cwd()).resolve()
        self.dry_run = dry_run

    def write(self, relative_path: str, content: str) -> Path:
        ArtifactPath._validate(relative_path, self.root)
        output_path = ArtifactPath.resolve_inside(relative_path, self.root)
        if self.dry_run:
            return output_path
        ensure_dir(output_path.parent)
        output_path.write_text(content)
        return output_path

    def copy_file(self, source: str | Path, dest: str | Path) -> Path:
        src_path = Path(source) if Path(source).is_absolute() else self.root / source
        if isinstance(dest, Path):
            dest_str = str(dest)
        else:
            dest_str = dest
        ArtifactPath._validate(dest_str, self.root)
        dst_path = ArtifactPath.resolve_inside(dest_str, self.root)
        if self.dry_run:
            return dst_path
        ensure_dir(dst_path.parent)
        dst_path.write_bytes(src_path.read_bytes())
        return dst_path
