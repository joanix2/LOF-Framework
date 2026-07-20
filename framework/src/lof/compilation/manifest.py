import json
from pathlib import Path

from lof.models.artifact import Artifact, ProjectManifest
from lof.utils.hashing import compute_hash


class ManifestManager:
    def __init__(self, root: Path | None = None):
        self.root = root or Path.cwd()
        self.manifest_path = self.root / "generated" / "manifest.json"

    def load(self) -> ProjectManifest:
        if self.manifest_path.exists():
            with open(self.manifest_path) as f:
                data = json.load(f)
                return ProjectManifest(**data)
        return ProjectManifest(project_hash="")

    def save(self, manifest: ProjectManifest) -> None:
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.manifest_path, "w") as f:
            json.dump(manifest.model_dump(), f, indent=2)

    def add_artifact(self, manifest: ProjectManifest, artifact: Artifact) -> ProjectManifest:
        manifest.artifacts.append(artifact)
        return manifest

    def compute_project_hash(self, manifest: ProjectManifest) -> str:
        content = json.dumps([a.model_dump() for a in manifest.artifacts], sort_keys=True)
        return compute_hash(content)

    def diff(self, old: ProjectManifest, new: ProjectManifest) -> list[str]:
        changes: list[str] = []
        old_artifacts = {a.output: a for a in old.artifacts}
        new_artifacts = {a.output: a for a in new.artifacts}
        for output, artifact in new_artifacts.items():
            if output not in old_artifacts:
                changes.append(f"ADDED: {output}")
            elif old_artifacts[output].hash != artifact.hash:
                changes.append(f"MODIFIED: {output}")
        for output in old_artifacts:
            if output not in new_artifacts:
                changes.append(f"REMOVED: {output}")
        return changes
