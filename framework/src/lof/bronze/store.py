import json
from pathlib import Path

from lof.bronze.models import BronzeEntry, BronzeEvent


class BronzeStore:
    def __init__(self, root: Path | None = None):
        self.root = root or Path.cwd()
        self._entries_dir = self.root / "data" / "bronze" / "entries"
        self._events_dir = self.root / "data" / "bronze" / "events"

    def ensure_dirs(self) -> None:
        self._entries_dir.mkdir(parents=True, exist_ok=True)
        self._events_dir.mkdir(parents=True, exist_ok=True)

    def append_entry(self, entry: BronzeEntry) -> Path:
        self.ensure_dirs()
        path = self._entries_dir / f"{entry.id}.json"
        if path.exists():
            raise FileExistsError(f"Bronze entry '{entry.id}' already exists (append-only).")
        path.write_text(json.dumps(entry.model_dump(), indent=2, default=str))
        return path

    def append_event(self, event: BronzeEvent) -> Path:
        self.ensure_dirs()
        path = self._events_dir / f"{event.id}.json"
        if path.exists():
            raise FileExistsError(f"Bronze event '{event.id}' already exists.")
        path.write_text(json.dumps(event.model_dump(), indent=2, default=str))
        return path

    def get_entry(self, entry_id: str) -> BronzeEntry | None:
        path = self._entries_dir / f"{entry_id}.json"
        if not path.exists():
            return None
        return BronzeEntry(**json.loads(path.read_text()))

    def list_entries(self) -> list[BronzeEntry]:
        if not self._entries_dir.exists():
            return []
        entries = []
        for f in sorted(self._entries_dir.glob("*.json")):
            entries.append(BronzeEntry(**json.loads(f.read_text())))
        return entries

    def list_events(self) -> list[BronzeEvent]:
        if not self._events_dir.exists():
            return []
        events = []
        for f in sorted(self._events_dir.glob("*.json")):
            events.append(BronzeEvent(**json.loads(f.read_text())))
        return events

    def has_entry(self, entry_id: str) -> bool:
        return (self._entries_dir / f"{entry_id}.json").exists()
