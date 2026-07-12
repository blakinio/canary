"""Audit manifest for a single deployment attempt.

The manifest is the durable, human- and machine-readable record of what a
deploy actually did: which release id, which files (with checksums) went
into it, whether real Canary preflight validation passed, what the previous
release was, and how the switch/health-check/rollback sequence resolved.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@dataclass
class ManifestFileEntry:
    relative_path: str
    sha256: str
    size_bytes: int

    def to_json(self) -> dict:
        return {"path": self.relative_path, "sha256": self.sha256, "sizeBytes": self.size_bytes}


def build_file_entries(release_dir: Path) -> list[ManifestFileEntry]:
    entries = []
    for path in sorted(p for p in release_dir.rglob("*") if p.is_file()):
        relative = path.relative_to(release_dir).as_posix()
        entries.append(ManifestFileEntry(relative_path=relative, sha256=sha256_file(path), size_bytes=path.stat().st_size))
    return entries


@dataclass
class DeploymentManifest:
    schema_version: str
    release_id: str
    created_at: str
    source_description: str
    dry_run: bool
    files: list[ManifestFileEntry] = field(default_factory=list)
    preflight_status: str = "not-attempted"
    preflight_detail: str = ""
    previous_release_id: str | None = None
    switch_status: str = "not-attempted"
    health_check_status: str = "not-attempted"
    health_check_detail: str = ""
    rollback_status: str = "not-attempted"
    outcome: str = "pending"

    def to_json(self) -> dict:
        return {
            "schemaVersion": self.schema_version,
            "releaseId": self.release_id,
            "createdAt": self.created_at,
            "sourceDescription": self.source_description,
            "dryRun": self.dry_run,
            "files": [entry.to_json() for entry in self.files],
            "fileCount": len(self.files),
            "preflightStatus": self.preflight_status,
            "preflightDetail": self.preflight_detail,
            "previousReleaseId": self.previous_release_id,
            "switchStatus": self.switch_status,
            "healthCheckStatus": self.health_check_status,
            "healthCheckDetail": self.health_check_detail,
            "rollbackStatus": self.rollback_status,
            "outcome": self.outcome,
        }

    def write(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = path.with_name(path.name + ".tmp")
        tmp_path.write_text(json.dumps(self.to_json(), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        tmp_path.replace(path)


def read_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
