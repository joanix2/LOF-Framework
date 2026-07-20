from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent.parent.parent


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path
