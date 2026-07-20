from pathlib import Path

from lof.utils.paths import ensure_dir


class Writer:
    def __init__(self, root: Path | None = None, dry_run: bool = False):
        self.root = root or Path.cwd()
        self.dry_run = dry_run

    def write(self, relative_path: str, content: str) -> Path:
        output_path = self.root / relative_path
        if self.dry_run:
            return output_path
        ensure_dir(output_path.parent)
        output_path.write_text(content)
        return output_path

    def copy_file(self, source: str | Path, dest: str | Path) -> Path:
        src_path = Path(source) if Path(source).is_absolute() else self.root / source
        dst_path = Path(dest) if Path(dest).is_absolute() else self.root / dest
        if self.dry_run:
            return dst_path
        ensure_dir(dst_path.parent)
        dst_path.write_bytes(src_path.read_bytes())
        return dst_path
