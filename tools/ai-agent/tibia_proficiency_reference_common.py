from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Iterable, Mapping

PROFICIENCY_INDEX_FORMAT = "canary-tibia-proficiency-index-v1"
APPEARANCES_INDEX_FORMAT = "canary-appearances-index-v1"
CANARY_EVIDENCE_FORMAT = "canary-tcr007-canary-evidence-v1"
RESOLVER_FORMAT = "canary-tibia-proficiency-reference-resolver-v1"
CORRELATION_FORMAT = "canary-tibia-proficiency-reference-correlation-v1"
SCHEMA_VERSION = 1
DEFAULT_MAX_JSON_BYTES = 256 * 1024 * 1024
DEFAULT_MAX_RECORDS = 2_000_000
_SHA256_LEN = 64
ALLOWED_STATES = frozenset(
    {
        "confirmed-reference",
        "reference-only",
        "target-only",
        "partial",
        "unresolved-id-space",
        "conflicting",
        "stale-evidence",
    }
)


class ProficiencyReferenceCorrelationError(RuntimeError):
    pass


def object_pairs(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ProficiencyReferenceCorrelationError(f"duplicate JSON object key: {key}")
        result[key] = value
    return result


def read_stable_file(path: Path, *, max_bytes: int, label: str) -> tuple[bytes, str, Path]:
    if not isinstance(max_bytes, int) or isinstance(max_bytes, bool) or max_bytes <= 0:
        raise ProficiencyReferenceCorrelationError(f"{label} max bytes must be positive")
    expanded = path.expanduser()
    if expanded.is_symlink():
        raise ProficiencyReferenceCorrelationError(f"{label} must not be a symlink")
    try:
        resolved = expanded.resolve(strict=True)
    except OSError as exc:
        raise ProficiencyReferenceCorrelationError(f"{label} does not exist") from exc
    if not resolved.is_file():
        raise ProficiencyReferenceCorrelationError(f"{label} must be a regular file")
    before = resolved.stat()
    if before.st_size > max_bytes:
        raise ProficiencyReferenceCorrelationError(f"{label} exceeds {max_bytes} bytes")
    data = resolved.read_bytes()
    after = resolved.stat()
    identity_before = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
    identity_after = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
    if identity_before != identity_after or len(data) != after.st_size:
        raise ProficiencyReferenceCorrelationError(f"{label} changed while reading")
    return data, hashlib.sha256(data).hexdigest(), resolved


def load_json(path: Path, *, max_bytes: int, label: str) -> tuple[dict[str, object], str, Path]:
    data, digest, resolved = read_stable_file(path, max_bytes=max_bytes, label=label)
    try:
        payload = json.loads(data.decode("utf-8"), object_pairs_hook=object_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProficiencyReferenceCorrelationError(f"{label} must be valid UTF-8 JSON") from exc
    if not isinstance(payload, dict):
        raise ProficiencyReferenceCorrelationError(f"{label} root must be an object")
    return payload, digest, resolved


def load_json_array(path: Path, *, max_bytes: int, label: str) -> tuple[list[object], str, Path]:
    data, digest, resolved = read_stable_file(path, max_bytes=max_bytes, label=label)
    try:
        payload = json.loads(data.decode("utf-8"), object_pairs_hook=object_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ProficiencyReferenceCorrelationError(f"{label} must be valid UTF-8 JSON") from exc
    if not isinstance(payload, list):
        raise ProficiencyReferenceCorrelationError(f"{label} root must be an array")
    return payload, digest, resolved


def is_sha256(value: object) -> bool:
    if not isinstance(value, str) or len(value) != _SHA256_LEN:
        return False
    try:
        int(value, 16)
    except ValueError:
        return False
    return True


def nonempty(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProficiencyReferenceCorrelationError(f"{label} must be a non-empty string")
    return value


def uint(value: object, label: str, *, positive: bool = False) -> int:
    minimum = 1 if positive else 0
    if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
        raise ProficiencyReferenceCorrelationError(f"{label} must be an integer >= {minimum}")
    return value


def sha256_json(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode(
        "utf-8"
    )
    return hashlib.sha256(encoded).hexdigest()


def strip_ordinals(value: object) -> object:
    if isinstance(value, dict):
        return {key: strip_ordinals(item) for key, item in value.items() if key != "sourceOrdinal"}
    if isinstance(value, list):
        return [strip_ordinals(item) for item in value]
    return value


def semantic_sha(entry: Mapping[str, object]) -> str:
    return sha256_json(strip_ordinals(dict(entry)))


def repo_head(root: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def source_evidence(path: Path, *, required_markers: tuple[str, ...], label: str) -> dict[str, object]:
    data, digest, resolved = read_stable_file(path, max_bytes=16 * 1024 * 1024, label=label)
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ProficiencyReferenceCorrelationError(f"{label} must be UTF-8 source text") from exc
    missing = [marker for marker in required_markers if marker not in text]
    return {
        "path": resolved.as_posix(),
        "sha256": digest,
        "requiredMarkerCount": len(required_markers),
        "missingMarkers": missing,
        "supported": not missing,
    }


def index_by_id(records: list[dict[str, object]], key: str) -> dict[int, list[dict[str, object]]]:
    result: dict[int, list[dict[str, object]]] = defaultdict(list)
    for record in records:
        value = record.get(key)
        if isinstance(value, int) and not isinstance(value, bool):
            result[value].append(dict(record))
    return result


def deterministic_json(payload: Mapping[str, object]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n"


def write_json(
    output: Path,
    payload: Mapping[str, object],
    *,
    protected_inputs: Iterable[Path] = (),
    overwrite: bool = False,
) -> None:
    target_path = output.expanduser()
    if target_path.is_symlink():
        raise ProficiencyReferenceCorrelationError(f"output must not be a symlink: {output}")
    target = target_path.resolve()
    protected = tuple(path.resolve() for path in protected_inputs)
    if any(target == source or (target.exists() and os.path.samefile(target, source)) for source in protected):
        raise ProficiencyReferenceCorrelationError("output collides with a protected input")
    if target.exists() and not target.is_file():
        raise ProficiencyReferenceCorrelationError(f"output exists but is not a regular file: {target}")
    if target.exists() and not overwrite:
        raise ProficiencyReferenceCorrelationError(f"output already exists: {target}; pass --overwrite")
    target.parent.mkdir(parents=True, exist_ok=True)
    text = deterministic_json(payload)
    if not overwrite:
        fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text)
        return
    fd, temp_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=target.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, target)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
