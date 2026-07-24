#!/usr/bin/env python3
"""Fail-closed Real Tibia evidence contracts and deterministic indexes.

Evidence files use the YAML 1.2 JSON-compatible subset.  The runtime uses only
Python 3.12's standard library; published JSON Schemas are documentation and
interchange contracts while this module enforces cross-file semantic rules.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
import tempfile
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Sequence
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_FORMAT = "canary-real-tibia-evidence-record-v1"
REQUEST_FORMAT = "canary-real-tibia-owner-request-v1"
MODULE_INDEX_FORMAT = "canary-real-tibia-module-evidence-index-v1"
VERSION_HISTORY_FORMAT = "canary-real-tibia-version-history-v1"
GENERATED_INDEX_FORMAT = "canary-real-tibia-generated-indexes-v1"
SCHEMA_VERSION = 1
MAX_RECORD_BYTES = 2 * 1024 * 1024

MODULE_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CLAIM_KEY_RE = MODULE_ID_RE
SOURCE_ID_RE = MODULE_ID_RE
EVIDENCE_ID_RE = re.compile(r"^RT-[A-Z0-9]+(?:-[A-Z0-9]+)*-[0-9]{4}$")
REQUEST_ID_RE = re.compile(
    r"^RTREQ-(E2E|OTBM|TCR|PROTOCOL|FEATURE)-[A-Z0-9]+(?:-[A-Z0-9]+)*-[0-9]{4}$"
)
HISTORY_ID_RE = re.compile(r"^RTVH-[A-Z0-9]+(?:-[A-Z0-9]+)*-[0-9]{4}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
VERSION_VALUE_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+:/ -]{0,127}$")
PROGRAM_ID_RE = re.compile(r"^CAN-(?:PROGRAM|OWNER)-[A-Z0-9]+(?:-[A-Z0-9]+)*$")

EVIDENCE_STATES = frozenset(
    {"PROVEN", "DERIVED", "UNKNOWN", "CONFLICT", "STALE", "SUPERSEDED", "REJECTED"}
)
RECORD_STATUSES = frozenset(
    {
        "discovered",
        "normalized",
        "review-needed",
        "accepted",
        "conflicting",
        "blocked-by-owner-request",
        "superseded",
        "rejected",
        "stale",
    }
)
PROOF_LEVELS = (
    "definition-found",
    "registration-proven",
    "runtime-path-proven",
    "persistence-proven",
    "protocol-proven",
    "behavior-proven",
    "gameplay-proven",
    "physical-client-proven",
)
PROOF_RANK = {value: index for index, value in enumerate(PROOF_LEVELS)}
AUTHORITY_DIMENSIONS = frozenset(
    {
        "official-feature-identity",
        "visible-gameplay-behavior",
        "current-canary-behavior",
        "protocol-client-interpretation",
        "persistence-rollback",
        "map-geometry",
        "map-mechanics",
        "implementation-candidate",
        "historical-version",
    }
)
SOURCE_TYPES = frozenset(
    {
        "official-news",
        "official-guide",
        "official-forum",
        "official-client-observation",
        "maintained-wiki",
        "current-canary",
        "maintained-client",
        "upstream-canary",
        "crystalserver",
        "map-reference",
        "packet-capture",
        "canary-test-result",
        "database-test-result",
        "runtime-result",
        "physical-e2e-result",
        "otbm-owner-result",
        "tcr-owner-result",
        "feature-owner-result",
        "other",
    }
)
SOURCE_PROOF_CAP = {
    "official-news": "definition-found",
    "official-guide": "definition-found",
    "official-forum": "definition-found",
    "official-client-observation": "gameplay-proven",
    "maintained-wiki": "definition-found",
    "current-canary": "runtime-path-proven",
    "maintained-client": "protocol-proven",
    "upstream-canary": "runtime-path-proven",
    "crystalserver": "runtime-path-proven",
    "map-reference": "definition-found",
    "packet-capture": "protocol-proven",
    "canary-test-result": "behavior-proven",
    "database-test-result": "persistence-proven",
    "runtime-result": "behavior-proven",
    "physical-e2e-result": "physical-client-proven",
    "otbm-owner-result": "behavior-proven",
    "tcr-owner-result": "protocol-proven",
    "feature-owner-result": "behavior-proven",
    "other": "definition-found",
}
VERSION_AXES = (
    "official_tibia_release",
    "official_client_build",
    "protocol_profile",
    "canary_commit",
    "maintained_otclient_commit",
    "map_sha256",
    "datapack_revision",
    "appearances_items_revision",
    "spawn_npc_sidecar_revision",
    "database_schema_revision",
)
VERSION_MODES = frozenset(
    {"EXACT", "DERIVED_RANGE", "LOWER_BOUND", "UPPER_BOUND", "UNKNOWN", "NOT_APPLICABLE"}
)
VERSION_EVENT_TYPES = frozenset(
    {
        "announced",
        "introduced",
        "enabled",
        "changed",
        "rebalanced",
        "fixed",
        "deprecated",
        "compatibility-only",
        "disabled",
        "removed",
        "observed",
        "unknown-first-version",
    }
)
VERSION_CONFIDENCE = frozenset(
    {
        "proven-official",
        "proven-observation",
        "supported-secondary",
        "derived-range",
        "conflicting",
        "unknown",
    }
)
REQUEST_OWNER_KINDS = frozenset({"e2e", "otbm", "tcr", "protocol", "feature"})
REQUEST_TYPES = frozenset(
    {
        "physical-gameplay-proof",
        "runtime-behavior-proof",
        "persistence-proof",
        "protocol-proof",
        "static-map-evidence",
        "client-reference-evidence",
        "implementation-audit",
        "source-clarification",
    }
)
REQUEST_STATUSES = frozenset(
    {
        "draft",
        "ready-for-owner-triage",
        "accepted-by-owner",
        "planned",
        "active",
        "blocked",
        "result-available",
        "consumed",
        "rejected",
        "superseded",
    }
)
ACTIVE_REQUEST_STATUSES = frozenset(
    {"ready-for-owner-triage", "accepted-by-owner", "planned", "active", "blocked", "result-available"}
)
OWNER_CONTROLLED_STATUSES = frozenset({"accepted-by-owner", "active", "result-available"})
REQUEST_TRANSITIONS = {
    "draft": frozenset({"ready-for-owner-triage", "rejected", "superseded"}),
    "ready-for-owner-triage": frozenset({"accepted-by-owner", "rejected", "superseded"}),
    "accepted-by-owner": frozenset({"planned", "blocked", "rejected", "superseded"}),
    "planned": frozenset({"active", "blocked", "superseded"}),
    "active": frozenset({"blocked", "result-available", "superseded"}),
    "blocked": frozenset({"planned", "active", "rejected", "superseded"}),
    "result-available": frozenset({"consumed", "superseded"}),
    "consumed": frozenset(),
    "rejected": frozenset(),
    "superseded": frozenset(),
}
OWNER_PREFIX = {"e2e": "E2E", "otbm": "OTBM", "tcr": "TCR", "protocol": "PROTOCOL", "feature": "FEATURE"}
OWNER_PROGRAMS = {
    "e2e": "CAN-PROGRAM-E2E-PLATFORM",
    "otbm": "CAN-PROGRAM-OTBM-WORLD-ASSURANCE-OPERATIONS",
    "tcr": "CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE",
}


class EvidenceError(RuntimeError):
    """Raised when the corpus cannot be loaded safely."""


@dataclass(frozen=True, order=True)
class Diagnostic:
    code: str
    path: str
    message: str

    def render(self) -> str:
        return f"{self.code}: {self.path}: {self.message}"


@dataclass(frozen=True)
class ValidationResult:
    errors: tuple[Diagnostic, ...]
    warnings: tuple[Diagnostic, ...] = ()

    @property
    def ok(self) -> bool:
        return not self.errors


@dataclass(frozen=True)
class LoadedDocument:
    path: Path
    relative_path: str
    value: dict[str, Any]
    sha256: str


def module_token(module_id: str) -> str:
    return module_id.upper()


def _pairs_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise EvidenceError(f"duplicate JSON object key {key!r}")
        result[key] = value
    return result


def _relative(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _inside(root: Path, path: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def safe_repo_path(value: object) -> bool:
    if not isinstance(value, str) or not value or value != value.strip():
        return False
    if "\\" in value or value.startswith(("/", "//")) or re.match(r"^[A-Za-z]:", value):
        return False
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        return False
    raw_parts = value.split("/")
    if any(part in {"", ".", ".."} for part in raw_parts):
        return False
    pure = PurePosixPath(value)
    return not pure.is_absolute() and ".." not in pure.parts and "." not in pure.parts


def safe_basename(value: object) -> bool:
    return isinstance(value, str) and bool(value) and value == PurePosixPath(value).name and "/" not in value and "\\" not in value


def _read_json(root: Path, path: Path, label: str) -> LoadedDocument:
    root_resolved = root.resolve(strict=True)
    if not path.exists() and not path.is_symlink():
        raise EvidenceError(f"{label} is missing: {_relative(root_resolved, path.absolute())}")
    absolute = path.absolute()
    for parent in (absolute, *absolute.parents):
        if parent == root_resolved:
            break
        if parent.is_symlink():
            raise EvidenceError(f"{label} must not use a symlink path")
    resolved = path.resolve(strict=True)
    if not _inside(root_resolved, resolved):
        raise EvidenceError(f"{label} escapes repository root")
    before = resolved.stat()
    if not resolved.is_file():
        raise EvidenceError(f"{label} must be a regular file")
    if before.st_size > MAX_RECORD_BYTES:
        raise EvidenceError(f"{label} exceeds {MAX_RECORD_BYTES} bytes")
    data = resolved.read_bytes()
    after = resolved.stat()
    identity_before = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
    identity_after = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
    if identity_before != identity_after or len(data) != after.st_size:
        raise EvidenceError(f"{label} changed while reading")
    try:
        value = json.loads(data.decode("utf-8"), object_pairs_hook=_pairs_no_duplicates)
    except UnicodeDecodeError as exc:
        raise EvidenceError(f"{label} must be UTF-8") from exc
    except json.JSONDecodeError as exc:
        raise EvidenceError(
            f"{label} must use the YAML 1.2 JSON-compatible subset: {exc.msg} at line {exc.lineno}, column {exc.colno}"
        ) from exc
    if not isinstance(value, dict):
        raise EvidenceError(f"{label} root must be an object")
    return LoadedDocument(resolved, _relative(root_resolved, resolved), value, hashlib.sha256(data).hexdigest())


def _is_date(value: object) -> bool:
    if not isinstance(value, str):
        return False
    try:
        return dt.date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def _parse_datetime(value: object) -> dt.datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed


def _nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip()) and value == value.strip()


def _string_list(value: object, *, nonempty: bool = False, unique: bool = True) -> bool:
    if not isinstance(value, list) or (nonempty and not value):
        return False
    if not all(_nonempty_string(item) for item in value):
        return False
    return not unique or len(value) == len(set(value))


def _object_keys(value: object, required: set[str], optional: set[str] = frozenset()) -> tuple[bool, str]:
    if not isinstance(value, dict):
        return False, "must be an object"
    missing = sorted(required - set(value))
    extra = sorted(set(value) - required - optional)
    if missing:
        return False, "missing fields: " + ", ".join(missing)
    if extra:
        return False, "unknown fields: " + ", ".join(extra)
    return True, ""


def _strongest(levels: Iterable[str]) -> str | None:
    available = [value for value in levels if value in PROOF_RANK]
    return max(available, key=PROOF_RANK.__getitem__) if available else None


def _version_axes_values(value: object, label: str, errors: list[Diagnostic], path: str) -> dict[str, str | None] | None:
    ok, detail = _object_keys(value, set(VERSION_AXES))
    if not ok:
        errors.append(Diagnostic("RTEC-VERSION-AXES", path, f"{label} {detail}"))
        return None
    assert isinstance(value, dict)
    result: dict[str, str | None] = {}
    for axis in VERSION_AXES:
        item = value[axis]
        if item is None:
            result[axis] = None
            continue
        if not _nonempty_string(item):
            errors.append(Diagnostic("RTEC-VERSION-VALUE", path, f"{label}.{axis} must be null or a non-empty string"))
            result[axis] = None
            continue
        if axis in {"canary_commit", "maintained_otclient_commit"} and not COMMIT_RE.fullmatch(item):
            errors.append(Diagnostic("RTEC-COMMIT-SHA", path, f"{label}.{axis} must be an exact lowercase 40-character commit SHA"))
        elif axis == "map_sha256" and not SHA256_RE.fullmatch(item):
            errors.append(Diagnostic("RTEC-SHA256", path, f"{label}.map_sha256 must be an exact lowercase SHA-256"))
        elif axis not in {"canary_commit", "maintained_otclient_commit", "map_sha256"} and not VERSION_VALUE_RE.fullmatch(item):
            errors.append(Diagnostic("RTEC-VERSION-VALUE", path, f"{label}.{axis} contains unsupported characters or is too long"))
        result[axis] = item
    return result


def _validate_version_marker(value: object, label: str, errors: list[Diagnostic], path: str) -> dict[str, Any] | None:
    required = {"mode", "exact", "lower_bound", "upper_bound", "evidence_refs", "notes"}
    ok, detail = _object_keys(value, required)
    if not ok:
        errors.append(Diagnostic("RTEC-VERSION-MARKER", path, f"{label} {detail}"))
        return None
    assert isinstance(value, dict)
    mode = value["mode"]
    if mode not in VERSION_MODES:
        errors.append(Diagnostic("RTEC-ENUM", path, f"{label}.mode has unknown value {mode!r}"))
        return None
    refs = value["evidence_refs"]
    notes = value["notes"]
    if not _string_list(refs):
        errors.append(Diagnostic("RTEC-VERSION-REFS", path, f"{label}.evidence_refs must be a unique string array"))
    if not _string_list(notes):
        errors.append(Diagnostic("RTEC-VERSION-NOTES", path, f"{label}.notes must be a unique string array"))
    exact = _version_axes_values(value["exact"], f"{label}.exact", errors, path) if value["exact"] is not None else None
    lower = _version_axes_values(value["lower_bound"], f"{label}.lower_bound", errors, path) if value["lower_bound"] is not None else None
    upper = _version_axes_values(value["upper_bound"], f"{label}.upper_bound", errors, path) if value["upper_bound"] is not None else None
    combinations = {
        "EXACT": (exact is not None, lower is None, upper is None),
        "DERIVED_RANGE": (exact is None, lower is not None, upper is not None),
        "LOWER_BOUND": (exact is None, lower is not None, upper is None),
        "UPPER_BOUND": (exact is None, lower is None, upper is not None),
        "UNKNOWN": (exact is None, lower is None, upper is None),
        "NOT_APPLICABLE": (exact is None, lower is None, upper is None),
    }
    if not all(combinations[mode]):
        errors.append(Diagnostic("RTEC-VERSION-MODE", path, f"{label} fields do not match mode {mode}"))
    for name, axes in (("exact", exact), ("lower_bound", lower), ("upper_bound", upper)):
        if axes is not None and not any(item is not None for item in axes.values()):
            errors.append(Diagnostic("RTEC-VERSION-EMPTY", path, f"{label}.{name} must identify at least one explicit version axis"))
    if mode == "UNKNOWN" and isinstance(notes, list) and not notes:
        errors.append(Diagnostic("RTEC-VERSION-UNKNOWN", path, f"{label}.notes must explain why the version is unknown"))
    if mode in {"EXACT", "DERIVED_RANGE", "LOWER_BOUND", "UPPER_BOUND"} and isinstance(refs, list) and not refs:
        errors.append(Diagnostic("RTEC-VERSION-EVIDENCE", path, f"{label}.evidence_refs must identify evidence for a bounded version claim"))
    return dict(value)


def empty_axes() -> dict[str, None]:
    return {axis: None for axis in VERSION_AXES}


def unknown_marker(note: str) -> dict[str, Any]:
    return {
        "mode": "UNKNOWN",
        "exact": None,
        "lower_bound": None,
        "upper_bound": None,
        "evidence_refs": [],
        "notes": [note],
    }


class Corpus:
    def __init__(
        self,
        root: Path,
        modules: frozenset[str],
        evidence: Sequence[LoadedDocument],
        requests: Sequence[LoadedDocument],
        histories: Sequence[LoadedDocument],
        module_indexes: Sequence[LoadedDocument],
        generated: LoadedDocument | None,
    ) -> None:
        self.root = root
        self.modules = modules
        self.evidence_documents = tuple(evidence)
        self.request_documents = tuple(requests)
        self.history_documents = tuple(histories)
        self.module_index_documents = tuple(module_indexes)
        self.generated_document = generated

    @property
    def evidence_root(self) -> Path:
        return self.root / "docs/agents/real-tibia/evidence"

    @staticmethod
    def _audit_evidence_tree(root: Path, evidence_root: Path) -> None:
        allowed_schema_names = {
            "evidence-record.schema.json",
            "owner-request.schema.json",
            "module-evidence-index.schema.json",
            "version-history.schema.json",
            "generated-indexes.schema.json",
        }
        for current, dirnames, filenames in os.walk(evidence_root, topdown=True, followlinks=False):
            current_path = Path(current)
            for name in sorted(dirnames):
                candidate = current_path / name
                if candidate.is_symlink():
                    raise EvidenceError(f"evidence tree must not contain symlink directory: {_relative(root, candidate)}")
            for name in sorted(filenames):
                candidate = current_path / name
                if candidate.is_symlink():
                    raise EvidenceError(f"evidence tree must not contain symlink file: {_relative(root, candidate)}")
                relative = candidate.relative_to(evidence_root).as_posix()
                pure = PurePosixPath(relative)
                allowed = False
                if relative == "README.md":
                    allowed = True
                elif pure.parts[:1] == ("schemas",) and len(pure.parts) == 2 and pure.name in allowed_schema_names:
                    allowed = True
                elif relative == "generated/EVIDENCE_INDEXES.json":
                    allowed = True
                elif len(pure.parts) == 4 and pure.parts[0] == "modules" and pure.parts[2] == "records" and pure.suffix == ".yaml":
                    allowed = True
                elif len(pure.parts) == 3 and pure.parts[0] == "modules" and pure.name in {"VERSION_HISTORY.yaml", "EVIDENCE_INDEX.yaml", "MODULE.md", "BEHAVIOR_MODEL.md", "DECISIONS.md"}:
                    allowed = True
                elif len(pure.parts) == 4 and pure.parts[0] == "modules" and pure.parts[2] == "reviews" and pure.suffix == ".md":
                    allowed = True
                elif len(pure.parts) == 3 and pure.parts[0] == "requests" and pure.parts[1] in REQUEST_OWNER_KINDS and pure.suffix == ".yaml":
                    allowed = True
                if not candidate.is_file():
                    raise EvidenceError(f"evidence tree entry must be a regular file: {_relative(root, candidate)}")
                if not allowed:
                    raise EvidenceError(f"unregistered or prohibited evidence file: {_relative(root, candidate)}")

    @classmethod
    def load(cls, root: Path = ROOT) -> "Corpus":
        root = root.expanduser().resolve(strict=True)
        registry_dir = root / "docs/agents/real-tibia/registry/modules"
        if registry_dir.is_symlink():
            raise EvidenceError("canonical module registry directory must not be a symlink")
        if not registry_dir.is_dir():
            raise EvidenceError(f"canonical module registry directory is missing: {_relative(root, registry_dir)}")
        modules: set[str] = set()
        for path in sorted(registry_dir.glob("*.yaml"), key=lambda item: item.as_posix()):
            document = _read_json(root, path, "canonical module record")
            module_id = document.value.get("module_id")
            if not isinstance(module_id, str) or not MODULE_ID_RE.fullmatch(module_id):
                raise EvidenceError(f"{document.relative_path}: invalid module_id")
            if path.stem != module_id:
                raise EvidenceError(f"{document.relative_path}: filename must match module_id {module_id!r}")
            if module_id in modules:
                raise EvidenceError(f"duplicate canonical module_id {module_id!r}")
            modules.add(module_id)
        if not modules:
            raise EvidenceError("canonical module registry contains no modules")

        evidence_root = root / "docs/agents/real-tibia/evidence"
        if evidence_root.is_symlink():
            raise EvidenceError("evidence root must not be a symlink")
        if not evidence_root.is_dir():
            raise EvidenceError(f"evidence root is missing: {_relative(root, evidence_root)}")
        cls._audit_evidence_tree(root, evidence_root)
        schema_names = {
            "evidence-record.schema.json",
            "owner-request.schema.json",
            "module-evidence-index.schema.json",
            "version-history.schema.json",
            "generated-indexes.schema.json",
        }
        schema_dir = evidence_root / "schemas"
        for schema_name in sorted(schema_names):
            schema = _read_json(root, schema_dir / schema_name, "published evidence schema")
            if schema.value.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
                raise EvidenceError(f"{schema.relative_path}: schema must declare Draft 2020-12")
            if schema.value.get("$id") != schema_name:
                raise EvidenceError(f"{schema.relative_path}: $id must equal {schema_name!r}")
            if schema.value.get("additionalProperties") is not False:
                raise EvidenceError(f"{schema.relative_path}: top-level additionalProperties must be false")

        def load_pattern(pattern: str, label: str) -> list[LoadedDocument]:
            documents: list[LoadedDocument] = []
            for path in sorted(evidence_root.glob(pattern), key=lambda item: item.as_posix()):
                if path.is_dir():
                    continue
                documents.append(_read_json(root, path, label))
            return documents

        evidence = load_pattern("modules/*/records/*.yaml", "evidence record")
        requests = load_pattern("requests/*/*.yaml", "owner request")
        histories = load_pattern("modules/*/VERSION_HISTORY.yaml", "version history")
        module_indexes = load_pattern("modules/*/EVIDENCE_INDEX.yaml", "module evidence index")
        generated_path = evidence_root / "generated/EVIDENCE_INDEXES.json"
        generated = _read_json(root, generated_path, "generated evidence indexes") if generated_path.exists() else None
        return cls(root, frozenset(modules), evidence, requests, histories, module_indexes, generated)

    def validate(self, as_of: dt.date | None = None) -> ValidationResult:
        errors: list[Diagnostic] = []
        evidence_by_id: dict[str, LoadedDocument] = {}
        requests_by_id: dict[str, LoadedDocument] = {}
        history_by_id: dict[str, tuple[LoadedDocument, dict[str, Any]]] = {}

        for document in self.evidence_documents:
            value = document.value
            path = document.relative_path
            self._validate_evidence_document(document, errors)
            evidence_id = value.get("evidence_id")
            if isinstance(evidence_id, str):
                if evidence_id in evidence_by_id:
                    errors.append(Diagnostic("RTEC-DUPLICATE-EVIDENCE-ID", path, f"duplicate evidence_id {evidence_id!r}; first defined in {evidence_by_id[evidence_id].relative_path}"))
                else:
                    evidence_by_id[evidence_id] = document
        for document in self.request_documents:
            value = document.value
            path = document.relative_path
            self._validate_request_document(document, errors)
            request_id = value.get("request_id")
            if isinstance(request_id, str):
                if request_id in requests_by_id:
                    errors.append(Diagnostic("RTEC-DUPLICATE-REQUEST-ID", path, f"duplicate request_id {request_id!r}; first defined in {requests_by_id[request_id].relative_path}"))
                else:
                    requests_by_id[request_id] = document

        for document in self.history_documents:
            self._validate_history_document(document, errors)
            entries = document.value.get("entries")
            if isinstance(entries, list):
                for entry in entries:
                    if not isinstance(entry, dict):
                        continue
                    history_id = entry.get("history_id")
                    if isinstance(history_id, str):
                        if history_id in history_by_id:
                            errors.append(Diagnostic("RTEC-DUPLICATE-HISTORY-ID", document.relative_path, f"duplicate history_id {history_id!r}; first defined in {history_by_id[history_id][0].relative_path}"))
                        else:
                            history_by_id[history_id] = (document, entry)

        evidence_ids = set(evidence_by_id)
        request_ids = set(requests_by_id)
        history_ids = set(history_by_id)
        for evidence_id, document in sorted(evidence_by_id.items()):
            value = document.value
            path = document.relative_path
            self._validate_references(value.get("related_modules"), self.modules, "module", "RTEC-MISSING-MODULE-REF", path, errors)
            self._validate_references(value.get("conflict_refs"), evidence_ids, "evidence", "RTEC-MISSING-EVIDENCE-REF", path, errors, disallow=evidence_id)
            self._validate_references(value.get("supersedes"), evidence_ids, "evidence", "RTEC-MISSING-EVIDENCE-REF", path, errors, disallow=evidence_id)
            self._validate_references(value.get("superseded_by"), evidence_ids, "evidence", "RTEC-MISSING-EVIDENCE-REF", path, errors, disallow=evidence_id)
            self._validate_references(value.get("owner_request_refs"), request_ids, "request", "RTEC-MISSING-REQUEST-REF", path, errors)
            applicability = value.get("applicability")
            if isinstance(applicability, dict):
                for marker in self._markers_from_applicability(applicability):
                    self._validate_references(marker.get("evidence_refs"), evidence_ids, "evidence", "RTEC-MISSING-EVIDENCE-REF", path, errors)
            if value.get("evidence_state") == "CONFLICT" and not value.get("conflict_refs"):
                errors.append(Diagnostic("RTEC-CONFLICT-REFS", path, "CONFLICT evidence must reference at least one conflicting evidence record"))
            if value.get("evidence_state") == "SUPERSEDED" and not value.get("superseded_by"):
                errors.append(Diagnostic("RTEC-SUPERSESSION-REFS", path, "SUPERSEDED evidence must identify superseded_by"))

        for request_id, document in sorted(requests_by_id.items()):
            value = document.value
            path = document.relative_path
            self._validate_references(value.get("related_modules"), self.modules, "module", "RTEC-MISSING-MODULE-REF", path, errors)
            self._validate_references(value.get("claim_refs"), evidence_ids, "evidence", "RTEC-MISSING-EVIDENCE-REF", path, errors)
            coordination = value.get("coordination")
            if isinstance(coordination, dict):
                self._validate_references(coordination.get("depends_on"), request_ids, "request", "RTEC-MISSING-REQUEST-REF", path, errors, disallow=request_id)
                self._validate_references(coordination.get("blocks"), request_ids, "request", "RTEC-MISSING-REQUEST-REF", path, errors, disallow=request_id)
            self._validate_references(value.get("supersedes"), request_ids, "request", "RTEC-MISSING-REQUEST-REF", path, errors, disallow=request_id)
            self._validate_references(value.get("superseded_by"), request_ids, "request", "RTEC-MISSING-REQUEST-REF", path, errors, disallow=request_id)
            available = value.get("available_inputs")
            if isinstance(available, dict):
                self._validate_references(available.get("source_claims"), evidence_ids, "evidence", "RTEC-MISSING-EVIDENCE-REF", path, errors)
            result = value.get("result")
            if isinstance(result, dict):
                self._validate_references(result.get("consumed_by_evidence_records"), evidence_ids, "evidence", "RTEC-MISSING-EVIDENCE-REF", path, errors)

        for history_id, (document, entry) in sorted(history_by_id.items()):
            path = document.relative_path
            self._validate_references(entry.get("claim_refs"), evidence_ids, "evidence", "RTEC-MISSING-EVIDENCE-REF", path, errors)
            self._validate_references(entry.get("evidence_refs"), evidence_ids, "evidence", "RTEC-MISSING-EVIDENCE-REF", path, errors)
            self._validate_references(entry.get("supersedes"), history_ids, "history", "RTEC-MISSING-HISTORY-REF", path, errors, disallow=history_id)
            self._validate_references(entry.get("superseded_by"), history_ids, "history", "RTEC-MISSING-HISTORY-REF", path, errors, disallow=history_id)
            lifecycle = entry.get("lifecycle")
            if isinstance(lifecycle, dict):
                for marker in self._markers_from_applicability(lifecycle):
                    self._validate_references(marker.get("evidence_refs"), evidence_ids, "evidence", "RTEC-MISSING-EVIDENCE-REF", path, errors)

        errors.extend(self._supersession_consistency(evidence_by_id))
        errors.extend(self._request_supersession_consistency(requests_by_id))
        errors.extend(self._history_supersession_consistency(history_by_id))
        errors.extend(self._cycle_errors({key: doc.value.get("supersedes", []) for key, doc in evidence_by_id.items()}, "evidence supersession", "RTEC-SUPERSESSION-CYCLE"))
        errors.extend(self._cycle_errors({key: doc.value.get("supersedes", []) for key, doc in requests_by_id.items()}, "request supersession", "RTEC-REQUEST-SUPERSESSION-CYCLE"))
        errors.extend(self._cycle_errors({key: entry.get("supersedes", []) for key, (_, entry) in history_by_id.items()}, "history supersession", "RTEC-HISTORY-CYCLE"))
        errors.extend(self._cycle_errors({key: doc.value.get("coordination", {}).get("depends_on", []) if isinstance(doc.value.get("coordination"), dict) else [] for key, doc in requests_by_id.items()}, "request dependency", "RTEC-REQUEST-CYCLE"))

        computed_as_of = as_of or self._generated_as_of()
        for document in self.evidence_documents:
            freshness = document.value.get("freshness")
            observed = freshness.get("observed_or_verified_at") if isinstance(freshness, dict) else None
            if _is_date(observed) and dt.date.fromisoformat(observed) > computed_as_of:
                errors.append(Diagnostic("RTEC-FUTURE-EVIDENCE", document.relative_path, f"freshness date {observed} is after validation as_of {computed_as_of.isoformat()}"))
        expected_module_indexes = self.module_indexes(computed_as_of)
        for document in self.module_index_documents:
            self._validate_module_index_document(document, errors)
            module_id = document.value.get("module_id")
            if isinstance(module_id, str) and module_id in expected_module_indexes:
                expected = expected_module_indexes[module_id]
                if document.value != expected:
                    errors.append(Diagnostic("RTEC-MODULE-INDEX-DRIFT", document.relative_path, "module evidence index does not match deterministic source records"))
        existing_index_modules = {doc.value.get("module_id") for doc in self.module_index_documents}
        for module_id in sorted(expected_module_indexes):
            if module_id not in existing_index_modules:
                errors.append(Diagnostic("RTEC-MODULE-INDEX-MISSING", f"docs/agents/real-tibia/evidence/modules/{module_id}/EVIDENCE_INDEX.yaml", "module dossier directory has records/history/requests but no generated module evidence index"))

        requests_modules = {doc.value.get("module_id") for doc in self.request_documents}
        modules_root = self.evidence_root / "modules"
        if modules_root.is_dir():
            for module_dir in sorted((item for item in modules_root.iterdir() if item.is_dir()), key=lambda item: item.name):
                if module_dir.name not in self.modules:
                    errors.append(Diagnostic("RTEC-MODULE-ID", _relative(self.root, module_dir), f"unknown canonical module directory {module_dir.name!r}"))
                substantive = any((module_dir / name).exists() for name in ("MODULE.md", "BEHAVIOR_MODEL.md", "DECISIONS.md", "VERSION_HISTORY.yaml"))
                records_dir = module_dir / "records"
                substantive = substantive or (records_dir.is_dir() and any(records_dir.glob("*.yaml"))) or module_dir.name in requests_modules
                if not substantive:
                    errors.append(Diagnostic("RTEC-EMPTY-MODULE-DIRECTORY", _relative(self.root, module_dir), "empty placeholder module directories and index-only dossier trees are forbidden"))

        if self.generated_document is None:
            errors.append(Diagnostic("RTEC-GENERATED-INDEX-MISSING", "docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json", "generated factual index is missing"))
        else:
            self._validate_generated_document(self.generated_document, errors)
            expected_global = self.generated_indexes(computed_as_of)
            if self.generated_document.value != expected_global:
                errors.append(Diagnostic("RTEC-GENERATED-INDEX-DRIFT", self.generated_document.relative_path, "generated factual index does not match deterministic source records"))

        return ValidationResult(tuple(sorted(set(errors))))

    def _validate_references(
        self,
        value: object,
        valid: set[str] | frozenset[str],
        label: str,
        code: str,
        path: str,
        errors: list[Diagnostic],
        disallow: str | None = None,
    ) -> None:
        if not isinstance(value, list):
            return
        for item in value:
            if item == disallow:
                errors.append(Diagnostic(code, path, f"{label} reference must not reference itself: {item!r}"))
            elif isinstance(item, str) and item not in valid:
                errors.append(Diagnostic(code, path, f"missing {label} reference {item!r}"))

    @staticmethod
    def _markers_from_applicability(applicability: Mapping[str, Any]) -> list[dict[str, Any]]:
        markers: list[dict[str, Any]] = []
        for key in ("announced_in", "introduced_in", "deprecated_in", "removed_in", "effective_from", "effective_until"):
            marker = applicability.get(key)
            if isinstance(marker, dict):
                markers.append(marker)
        for key in ("observed_in", "changed_in"):
            values = applicability.get(key)
            if isinstance(values, list):
                markers.extend(item for item in values if isinstance(item, dict))
        return markers

    def _validate_evidence_document(self, document: LoadedDocument, errors: list[Diagnostic]) -> None:
        value = document.value
        path = document.relative_path
        required = {
            "format", "schema_version", "evidence_id", "module_id", "related_modules", "claim_key", "claim_statement",
            "record_status", "authority_dimension", "evidence_state", "proof_level", "sources", "applicability",
            "current_canary_comparison", "proves", "does_not_prove", "confidence", "uncertainty", "conflict_refs",
            "supersedes", "superseded_by", "owner_request_refs", "freshness", "review",
        }
        ok, detail = _object_keys(value, required)
        if not ok:
            errors.append(Diagnostic("RTEC-EVIDENCE-SHAPE", path, detail))
            return
        if value["format"] != EVIDENCE_FORMAT or value["schema_version"] != SCHEMA_VERSION:
            errors.append(Diagnostic("RTEC-SCHEMA-VERSION", path, f"format/schema_version must be {EVIDENCE_FORMAT}/{SCHEMA_VERSION}"))
        evidence_id = value["evidence_id"]
        module_id = value["module_id"]
        if not isinstance(evidence_id, str) or not EVIDENCE_ID_RE.fullmatch(evidence_id):
            errors.append(Diagnostic("RTEC-EVIDENCE-ID", path, "evidence_id is malformed"))
        if module_id not in self.modules:
            errors.append(Diagnostic("RTEC-MODULE-ID", path, f"unknown canonical module_id {module_id!r}"))
        if isinstance(module_id, str) and isinstance(evidence_id, str):
            expected_prefix = f"RT-{module_token(module_id)}-"
            if not evidence_id.startswith(expected_prefix):
                errors.append(Diagnostic("RTEC-EVIDENCE-ID", path, f"evidence_id must start with {expected_prefix}"))
            expected_parent = f"docs/agents/real-tibia/evidence/modules/{module_id}/records"
            if PurePosixPath(path).parent.as_posix() != expected_parent or PurePosixPath(path).name != f"{evidence_id}.yaml":
                errors.append(Diagnostic("RTEC-EVIDENCE-PATH", path, f"record path must be {expected_parent}/{evidence_id}.yaml"))
        if not _string_list(value["related_modules"]):
            errors.append(Diagnostic("RTEC-RELATED-MODULES", path, "related_modules must be a unique string array"))
        if not isinstance(value["claim_key"], str) or not CLAIM_KEY_RE.fullmatch(value["claim_key"]):
            errors.append(Diagnostic("RTEC-CLAIM-KEY", path, "claim_key must be stable kebab-case"))
        if not _nonempty_string(value["claim_statement"]):
            errors.append(Diagnostic("RTEC-CLAIM", path, "claim_statement must be non-empty"))
        if value["record_status"] not in RECORD_STATUSES:
            errors.append(Diagnostic("RTEC-ENUM", path, f"unknown record_status {value['record_status']!r}"))
        if value["authority_dimension"] not in AUTHORITY_DIMENSIONS:
            errors.append(Diagnostic("RTEC-ENUM", path, f"unknown authority_dimension {value['authority_dimension']!r}"))
        if value["evidence_state"] not in EVIDENCE_STATES:
            errors.append(Diagnostic("RTEC-ENUM", path, f"unknown evidence_state {value['evidence_state']!r}"))
        if value["proof_level"] not in PROOF_RANK:
            errors.append(Diagnostic("RTEC-ENUM", path, f"unknown proof_level {value['proof_level']!r}"))
        for key in ("proves", "does_not_prove"):
            if not _string_list(value[key], nonempty=True):
                errors.append(Diagnostic("RTEC-PROOF-BOUNDARY", path, f"{key} must be a non-empty unique string array"))
        if value["confidence"] not in {"HIGH", "MEDIUM", "LOW", "UNKNOWN"}:
            errors.append(Diagnostic("RTEC-ENUM", path, f"unknown confidence {value['confidence']!r}"))
        if not _string_list(value["uncertainty"]):
            errors.append(Diagnostic("RTEC-UNCERTAINTY", path, "uncertainty must be a unique string array"))
        if value["evidence_state"] in {"DERIVED", "UNKNOWN", "CONFLICT", "STALE"} and not value["uncertainty"]:
            errors.append(Diagnostic("RTEC-UNCERTAINTY", path, f"{value['evidence_state']} evidence must state uncertainty explicitly"))
        for key in ("conflict_refs", "supersedes", "superseded_by", "owner_request_refs"):
            if not _string_list(value[key]):
                errors.append(Diagnostic("RTEC-REFS", path, f"{key} must be a unique string array"))
        self._validate_sources(value["sources"], value.get("proof_level"), value.get("authority_dimension"), path, errors)
        self._validate_applicability(value["applicability"], value, path, errors)
        self._validate_canary_comparison(value["current_canary_comparison"], path, errors)
        self._validate_freshness(value["freshness"], value.get("evidence_state"), path, errors)
        self._validate_review(value["review"], path, errors)
        if value["record_status"] == "accepted" and value["review"].get("status") != "accepted":
            errors.append(Diagnostic("RTEC-REVIEW-STATE", path, "accepted record_status requires review.status accepted"))
        if value["record_status"] == "superseded" and value["evidence_state"] != "SUPERSEDED":
            errors.append(Diagnostic("RTEC-STATE-MISMATCH", path, "superseded record_status requires SUPERSEDED evidence_state"))
        if value["record_status"] == "rejected" and value["evidence_state"] != "REJECTED":
            errors.append(Diagnostic("RTEC-STATE-MISMATCH", path, "rejected record_status requires REJECTED evidence_state"))

    def _validate_sources(self, value: object, record_level: object, authority: object, path: str, errors: list[Diagnostic]) -> None:
        if not isinstance(value, list) or not value:
            errors.append(Diagnostic("RTEC-SOURCES", path, "sources must be a non-empty array"))
            return
        seen: set[str] = set()
        levels: list[str] = []
        source_types: set[str] = set()
        required = {
            "source_id", "role", "source_type", "locator", "author", "publication_date", "observation_date",
            "selected", "proves", "does_not_prove", "limitations", "proof_level_reached", "external_artifact",
        }
        for index, source in enumerate(value):
            label = f"sources[{index}]"
            ok, detail = _object_keys(source, required)
            if not ok:
                errors.append(Diagnostic("RTEC-SOURCE-SHAPE", path, f"{label} {detail}"))
                continue
            assert isinstance(source, dict)
            source_id = source["source_id"]
            if not isinstance(source_id, str) or not SOURCE_ID_RE.fullmatch(source_id):
                errors.append(Diagnostic("RTEC-SOURCE-ID", path, f"{label}.source_id must be stable kebab-case"))
            elif source_id in seen:
                errors.append(Diagnostic("RTEC-DUPLICATE-SOURCE-ID", path, f"duplicate source_id {source_id!r}"))
            else:
                seen.add(source_id)
            if source["role"] not in {"primary", "corroborating", "conflicting", "comparison", "implementation-candidate"}:
                errors.append(Diagnostic("RTEC-ENUM", path, f"{label}.role has unknown value {source['role']!r}"))
            source_type = source["source_type"]
            if source_type not in SOURCE_TYPES:
                errors.append(Diagnostic("RTEC-ENUM", path, f"{label}.source_type has unknown value {source_type!r}"))
                continue
            source_types.add(source_type)
            level = source["proof_level_reached"]
            if level not in PROOF_RANK:
                errors.append(Diagnostic("RTEC-ENUM", path, f"{label}.proof_level_reached has unknown value {level!r}"))
            else:
                levels.append(level)
                if PROOF_RANK[level] > PROOF_RANK[SOURCE_PROOF_CAP[source_type]]:
                    errors.append(Diagnostic("RTEC-PROOF-PROMOTION", path, f"{label} source_type {source_type} cannot reach {level}; maximum is {SOURCE_PROOF_CAP[source_type]}"))
            self._validate_locator(source["locator"], label, path, errors)
            for date_key in ("publication_date", "observation_date"):
                item = source[date_key]
                if item is not None and not _is_date(item):
                    errors.append(Diagnostic("RTEC-DATE", path, f"{label}.{date_key} must be null or YYYY-MM-DD"))
            if source_type in {"official-news", "official-guide", "official-forum", "maintained-wiki", "official-client-observation"} and not _nonempty_string(source["author"]):
                errors.append(Diagnostic("RTEC-SOURCE-AUTHOR", path, f"{label}.author is required for {source_type}"))
            if source_type in {"official-news", "official-guide", "official-forum", "maintained-wiki"} and not _is_date(source["publication_date"]):
                errors.append(Diagnostic("RTEC-SOURCE-DATE", path, f"{label}.publication_date is required for {source_type}"))
            if source_type in {"official-client-observation", "packet-capture", "runtime-result", "physical-e2e-result", "otbm-owner-result", "tcr-owner-result", "feature-owner-result", "canary-test-result", "database-test-result"} and not _is_date(source["observation_date"]):
                errors.append(Diagnostic("RTEC-SOURCE-DATE", path, f"{label}.observation_date is required for {source_type}"))
            selected = source["selected"]
            ok, detail = _object_keys(selected, {"sections", "symbols", "files", "observations"})
            if not ok:
                errors.append(Diagnostic("RTEC-SOURCE-SELECTION", path, f"{label}.selected {detail}"))
            else:
                assert isinstance(selected, dict)
                for key in ("sections", "symbols", "observations"):
                    if not _string_list(selected[key]):
                        errors.append(Diagnostic("RTEC-SOURCE-SELECTION", path, f"{label}.selected.{key} must be a unique string array"))
                if not _string_list(selected["files"]):
                    errors.append(Diagnostic("RTEC-SOURCE-SELECTION", path, f"{label}.selected.files must be a unique string array"))
                elif any(not safe_repo_path(item) for item in selected["files"]):
                    errors.append(Diagnostic("RTEC-UNSAFE-PATH", path, f"{label}.selected.files contains an unsafe path"))
                if not any(selected[key] for key in ("sections", "symbols", "files", "observations")):
                    errors.append(Diagnostic("RTEC-SOURCE-SELECTION", path, f"{label}.selected must identify at least one exact section, symbol, file or observation"))
            for key in ("proves", "does_not_prove"):
                if not _string_list(source[key], nonempty=True):
                    errors.append(Diagnostic("RTEC-PROOF-BOUNDARY", path, f"{label}.{key} must be non-empty"))
            if not _string_list(source["limitations"]):
                errors.append(Diagnostic("RTEC-SOURCE-LIMITATIONS", path, f"{label}.limitations must be a unique string array"))
            self._validate_external_artifact(source["external_artifact"], label, path, errors)
            artifact = source["external_artifact"]
            locator = source["locator"]
            if isinstance(artifact, dict) and isinstance(locator, dict) and locator.get("artifact_sha256") != artifact.get("sha256"):
                errors.append(Diagnostic("RTEC-ARTIFACT-HASH-MISMATCH", path, f"{label} locator artifact_sha256 must equal external_artifact.sha256"))
        strongest = _strongest(levels)
        if record_level in PROOF_RANK and (strongest is None or PROOF_RANK[record_level] > PROOF_RANK[strongest]):
            errors.append(Diagnostic("RTEC-PROOF-PROMOTION", path, f"record proof_level {record_level} exceeds strongest source proof {strongest or 'none'}"))
        if record_level == "gameplay-proven" and not source_types.intersection({"official-client-observation", "physical-e2e-result"}):
            errors.append(Diagnostic("RTEC-PROOF-PROMOTION", path, "gameplay-proven requires official-client-observation or physical-e2e-result evidence"))
        if record_level == "physical-client-proven" and "physical-e2e-result" not in source_types:
            errors.append(Diagnostic("RTEC-PROOF-PROMOTION", path, "physical-client-proven requires a physical-e2e-result source"))
        if record_level in {"gameplay-proven", "physical-client-proven"} and source_types.issubset({"official-news", "official-guide", "official-forum", "maintained-wiki", "current-canary", "maintained-client", "upstream-canary", "crystalserver", "map-reference", "packet-capture", "otbm-owner-result", "tcr-owner-result"}):
            errors.append(Diagnostic("RTEC-STATIC-PROMOTION", path, "static, source-only, map or protocol evidence cannot be promoted to gameplay/physical-client proof"))
        if authority == "current-canary-behavior" and record_level == "physical-client-proven" and "physical-e2e-result" not in source_types:
            errors.append(Diagnostic("RTEC-STATIC-PROMOTION", path, "current Canary physical-client proof requires retained owner E2E evidence"))

    def _validate_locator(self, value: object, label: str, path: str, errors: list[Diagnostic]) -> None:
        required = {"url", "repository", "repository_path", "commit_sha", "build", "report_id", "artifact_sha256"}
        ok, detail = _object_keys(value, required)
        if not ok:
            errors.append(Diagnostic("RTEC-SOURCE-LOCATOR", path, f"{label}.locator {detail}"))
            return
        assert isinstance(value, dict)
        nonnull = [key for key in required if value[key] is not None]
        if not nonnull:
            errors.append(Diagnostic("RTEC-SOURCE-LOCATOR", path, f"{label}.locator must provide an exact URL, repository path/SHA, build, report ID or artifact hash"))
        for key in ("repository", "build", "report_id"):
            if value[key] is not None and not _nonempty_string(value[key]):
                errors.append(Diagnostic("RTEC-SOURCE-LOCATOR", path, f"{label}.locator.{key} must be null or non-empty"))
        if value["url"] is not None:
            parsed = urlparse(value["url"]) if isinstance(value["url"], str) else None
            if parsed is None or parsed.scheme not in {"https", "http"} or not parsed.netloc or parsed.username or parsed.password:
                errors.append(Diagnostic("RTEC-URL", path, f"{label}.locator.url must be an absolute HTTP(S) URL without credentials"))
        if value["repository_path"] is not None and not safe_repo_path(value["repository_path"]):
            errors.append(Diagnostic("RTEC-UNSAFE-PATH", path, f"{label}.locator.repository_path is unsafe"))
        if value["repository_path"] is not None and not _nonempty_string(value["repository"]):
            errors.append(Diagnostic("RTEC-SOURCE-LOCATOR", path, f"{label}.locator.repository is required with repository_path"))
        if value["commit_sha"] is not None and not _nonempty_string(value["repository"]):
            errors.append(Diagnostic("RTEC-SOURCE-LOCATOR", path, f"{label}.locator.repository is required with commit_sha"))
        if value["repository_path"] is not None and not isinstance(value["commit_sha"], str):
            errors.append(Diagnostic("RTEC-COMMIT-SHA", path, f"{label}.locator.commit_sha is required with repository_path"))
        if value["commit_sha"] is not None and (not isinstance(value["commit_sha"], str) or not COMMIT_RE.fullmatch(value["commit_sha"])):
            errors.append(Diagnostic("RTEC-COMMIT-SHA", path, f"{label}.locator.commit_sha must be an exact lowercase 40-character SHA"))
        if value["artifact_sha256"] is not None and (not isinstance(value["artifact_sha256"], str) or not SHA256_RE.fullmatch(value["artifact_sha256"])):
            errors.append(Diagnostic("RTEC-SHA256", path, f"{label}.locator.artifact_sha256 must be an exact lowercase SHA-256"))

    def _validate_external_artifact(self, value: object, label: str, path: str, errors: list[Diagnostic]) -> None:
        if value is None:
            return
        required = {"retained_outside_git", "filename", "byte_size", "sha256"}
        ok, detail = _object_keys(value, required)
        if not ok:
            errors.append(Diagnostic("RTEC-EXTERNAL-ARTIFACT", path, f"{label}.external_artifact {detail}"))
            return
        assert isinstance(value, dict)
        if value["retained_outside_git"] is not True:
            errors.append(Diagnostic("RTEC-PROPRIETARY-ARTIFACT", path, f"{label}.external_artifact must remain outside Git"))
        if not safe_basename(value["filename"]):
            errors.append(Diagnostic("RTEC-EXTERNAL-ARTIFACT", path, f"{label}.external_artifact.filename must be a safe basename"))
        if not isinstance(value["byte_size"], int) or isinstance(value["byte_size"], bool) or value["byte_size"] <= 0:
            errors.append(Diagnostic("RTEC-EXTERNAL-ARTIFACT", path, f"{label}.external_artifact.byte_size must be positive"))
        if not isinstance(value["sha256"], str) or not SHA256_RE.fullmatch(value["sha256"]):
            errors.append(Diagnostic("RTEC-SHA256", path, f"{label}.external_artifact.sha256 must be an exact lowercase SHA-256"))

    def _validate_applicability(self, value: object, record: Mapping[str, Any], path: str, errors: list[Diagnostic]) -> None:
        required = {"announced_in", "introduced_in", "observed_in", "changed_in", "deprecated_in", "removed_in", "effective_from", "effective_until"}
        ok, detail = _object_keys(value, required)
        if not ok:
            errors.append(Diagnostic("RTEC-APPLICABILITY", path, detail))
            return
        assert isinstance(value, dict)
        markers: dict[str, dict[str, Any] | None] = {}
        for key in ("announced_in", "introduced_in", "deprecated_in", "removed_in", "effective_from", "effective_until"):
            marker = _validate_version_marker(value[key], f"applicability.{key}", errors, path)
            markers[key] = marker
        for key in ("observed_in", "changed_in"):
            items = value[key]
            if not isinstance(items, list):
                errors.append(Diagnostic("RTEC-APPLICABILITY", path, f"applicability.{key} must be an array"))
                continue
            for index, item in enumerate(items):
                _validate_version_marker(item, f"applicability.{key}[{index}]", errors, path)
        introduced = markers.get("introduced_in")
        if introduced and introduced.get("mode") == "EXACT":
            source_types = {source.get("source_type") for source in record.get("sources", []) if isinstance(source, dict)}
            if record.get("evidence_state") != "PROVEN":
                errors.append(Diagnostic("RTEC-INTRODUCTION-VERSION", path, "exact introduced_in requires PROVEN evidence_state"))
            if not source_types.intersection({"official-news", "official-guide", "official-forum", "official-client-observation"}):
                errors.append(Diagnostic("RTEC-INTRODUCTION-VERSION", path, "exact introduced_in requires official or exact official-client observation evidence"))
        effective_from = markers.get("effective_from")
        effective_until = markers.get("effective_until")
        if effective_from and effective_until and effective_from.get("mode") == "EXACT" and effective_until.get("mode") == "EXACT":
            lower = effective_from.get("exact")
            upper = effective_until.get("exact")
            if isinstance(lower, dict) and isinstance(upper, dict):
                for axis in VERSION_AXES:
                    if lower.get(axis) is not None and upper.get(axis) is not None and lower[axis] == upper[axis]:
                        continue
                    # Exact cross-axis ordering is intentionally not inferred from arbitrary release/build strings.

    def _validate_canary_comparison(self, value: object, path: str, errors: list[Diagnostic]) -> None:
        required = {"state", "baseline", "exact_paths", "exact_symbols", "current_behavior", "differences", "missing_proof"}
        ok, detail = _object_keys(value, required)
        if not ok:
            errors.append(Diagnostic("RTEC-CANARY-COMPARISON", path, detail))
            return
        assert isinstance(value, dict)
        if value["state"] not in {"not-assessed", "conforming", "differing", "partial", "conflicting", "blocked-by-reference", "intentionally-unsupported"}:
            errors.append(Diagnostic("RTEC-ENUM", path, f"unknown Canary comparison state {value['state']!r}"))
        _version_axes_values(value["baseline"], "current_canary_comparison.baseline", errors, path)
        if not _string_list(value["exact_paths"]):
            errors.append(Diagnostic("RTEC-CANARY-COMPARISON", path, "exact_paths must be a unique string array"))
        elif any(not safe_repo_path(item) for item in value["exact_paths"]):
            errors.append(Diagnostic("RTEC-UNSAFE-PATH", path, "current_canary_comparison.exact_paths contains an unsafe path"))
        for key in ("exact_symbols", "differences", "missing_proof"):
            if not _string_list(value[key]):
                errors.append(Diagnostic("RTEC-CANARY-COMPARISON", path, f"{key} must be a unique string array"))
        if value["current_behavior"] is not None and not _nonempty_string(value["current_behavior"]):
            errors.append(Diagnostic("RTEC-CANARY-COMPARISON", path, "current_behavior must be null or non-empty"))
        baseline = value["baseline"]
        if isinstance(baseline, dict) and baseline.get("canary_commit") is not None and not COMMIT_RE.fullmatch(str(baseline["canary_commit"])):
            errors.append(Diagnostic("RTEC-COMMIT-SHA", path, "Canary comparison baseline canary_commit is malformed"))
        state = value["state"]
        assessed = {"conforming", "differing", "partial", "conflicting"}
        if state == "not-assessed" and not value["missing_proof"]:
            errors.append(Diagnostic("RTEC-CANARY-COMPARISON", path, "not-assessed comparison must state missing_proof"))
        if state in assessed:
            baseline_commit = baseline.get("canary_commit") if isinstance(baseline, dict) else None
            if not isinstance(baseline_commit, str) or not COMMIT_RE.fullmatch(baseline_commit):
                errors.append(Diagnostic("RTEC-CANARY-COMPARISON", path, f"comparison state {state} requires an exact Canary commit baseline"))
            if not value["exact_paths"] and not value["exact_symbols"]:
                errors.append(Diagnostic("RTEC-CANARY-COMPARISON", path, f"comparison state {state} requires exact_paths or exact_symbols"))
            if not _nonempty_string(value["current_behavior"]):
                errors.append(Diagnostic("RTEC-CANARY-COMPARISON", path, f"comparison state {state} requires current_behavior"))
        if state in {"differing", "partial", "conflicting"} and not value["differences"]:
            errors.append(Diagnostic("RTEC-CANARY-COMPARISON", path, f"comparison state {state} requires explicit differences"))
        if state in {"partial", "conflicting", "blocked-by-reference"} and not value["missing_proof"]:
            errors.append(Diagnostic("RTEC-CANARY-COMPARISON", path, f"comparison state {state} requires missing_proof"))
        if state == "conforming" and value["differences"]:
            errors.append(Diagnostic("RTEC-CANARY-COMPARISON", path, "conforming comparison must not list differences"))

    def _validate_freshness(self, value: object, evidence_state: object, path: str, errors: list[Diagnostic]) -> None:
        required = {"observed_or_verified_at", "warning_after_days", "invalid_after_days", "policy", "invalidation_triggers"}
        ok, detail = _object_keys(value, required)
        if not ok:
            errors.append(Diagnostic("RTEC-FRESHNESS", path, detail))
            return
        assert isinstance(value, dict)
        if not _is_date(value["observed_or_verified_at"]):
            errors.append(Diagnostic("RTEC-DATE", path, "freshness.observed_or_verified_at must be YYYY-MM-DD"))
        warning = value["warning_after_days"]
        invalid = value["invalid_after_days"]
        if not isinstance(warning, int) or isinstance(warning, bool) or warning <= 0:
            errors.append(Diagnostic("RTEC-FRESHNESS", path, "warning_after_days must be a positive integer"))
        if not isinstance(invalid, int) or isinstance(invalid, bool) or invalid <= 0:
            errors.append(Diagnostic("RTEC-FRESHNESS", path, "invalid_after_days must be a positive integer"))
        if isinstance(warning, int) and isinstance(invalid, int) and not isinstance(warning, bool) and not isinstance(invalid, bool) and warning >= invalid:
            errors.append(Diagnostic("RTEC-FRESHNESS", path, "warning_after_days must be lower than invalid_after_days"))
        if value["policy"] not in {"fixed-window", "refresh-before-task", "immutable-source", "owner-result-lifecycle"}:
            errors.append(Diagnostic("RTEC-ENUM", path, f"unknown freshness policy {value['policy']!r}"))
        if not _string_list(value["invalidation_triggers"], nonempty=True):
            errors.append(Diagnostic("RTEC-FRESHNESS", path, "invalidation_triggers must be a non-empty unique string array"))

    def _validate_review(self, value: object, path: str, errors: list[Diagnostic]) -> None:
        required = {"status", "task_id", "pr", "reviewer", "reviewed_at", "notes"}
        ok, detail = _object_keys(value, required)
        if not ok:
            errors.append(Diagnostic("RTEC-REVIEW", path, detail))
            return
        assert isinstance(value, dict)
        if value["status"] not in {"pending", "accepted", "changes-requested", "rejected"}:
            errors.append(Diagnostic("RTEC-ENUM", path, f"unknown review status {value['status']!r}"))
        if value["task_id"] is not None and not _nonempty_string(value["task_id"]):
            errors.append(Diagnostic("RTEC-REVIEW", path, "review.task_id must be null or non-empty"))
        if value["pr"] is not None and (not isinstance(value["pr"], int) or isinstance(value["pr"], bool) or value["pr"] <= 0):
            errors.append(Diagnostic("RTEC-REVIEW", path, "review.pr must be null or a positive integer"))
        if value["reviewed_at"] is not None and _parse_datetime(value["reviewed_at"]) is None:
            errors.append(Diagnostic("RTEC-DATETIME", path, "review.reviewed_at must be null or timezone-aware ISO-8601"))
        if not _string_list(value["notes"]):
            errors.append(Diagnostic("RTEC-REVIEW", path, "review.notes must be a unique string array"))
        if value["status"] in {"accepted", "rejected"} and (not _nonempty_string(value["reviewer"]) or _parse_datetime(value["reviewed_at"]) is None):
            errors.append(Diagnostic("RTEC-REVIEW", path, f"review.status {value['status']} requires reviewer and reviewed_at"))

    def _validate_request_document(self, document: LoadedDocument, errors: list[Diagnostic]) -> None:
        value = document.value
        path = document.relative_path
        required = {
            "format", "schema_version", "request_id", "module_id", "related_modules", "claim_refs", "owner_kind",
            "requested_owner_program", "request_type", "status", "priority", "blocking", "version_impact", "question",
            "why_existing_evidence_is_insufficient", "required_evidence", "available_inputs", "requested_output_contract",
            "collector_must_not_edit", "owner_paths_read_only_for_collector", "suggested_owner_capability_gap", "coordination",
            "result", "history", "supersedes", "superseded_by",
        }
        ok, detail = _object_keys(value, required)
        if not ok:
            errors.append(Diagnostic("RTEC-REQUEST-SHAPE", path, detail))
            return
        if value["format"] != REQUEST_FORMAT or value["schema_version"] != SCHEMA_VERSION:
            errors.append(Diagnostic("RTEC-SCHEMA-VERSION", path, f"format/schema_version must be {REQUEST_FORMAT}/{SCHEMA_VERSION}"))
        request_id = value["request_id"]
        module_id = value["module_id"]
        owner_kind = value["owner_kind"]
        if not isinstance(request_id, str) or not REQUEST_ID_RE.fullmatch(request_id):
            errors.append(Diagnostic("RTEC-REQUEST-ID", path, "request_id is malformed"))
        if module_id not in self.modules:
            errors.append(Diagnostic("RTEC-MODULE-ID", path, f"unknown canonical module_id {module_id!r}"))
        if owner_kind not in REQUEST_OWNER_KINDS:
            errors.append(Diagnostic("RTEC-ENUM", path, f"unknown owner_kind {owner_kind!r}"))
        if isinstance(request_id, str) and isinstance(module_id, str) and owner_kind in OWNER_PREFIX:
            expected_prefix = f"RTREQ-{OWNER_PREFIX[owner_kind]}-{module_token(module_id)}-"
            if not request_id.startswith(expected_prefix):
                errors.append(Diagnostic("RTEC-REQUEST-ID", path, f"request_id must start with {expected_prefix}"))
            expected_parent = f"docs/agents/real-tibia/evidence/requests/{owner_kind}"
            if PurePosixPath(path).parent.as_posix() != expected_parent or PurePosixPath(path).name != f"{request_id}.yaml":
                errors.append(Diagnostic("RTEC-REQUEST-PATH", path, f"request path must be {expected_parent}/{request_id}.yaml"))
        if not _string_list(value["related_modules"]):
            errors.append(Diagnostic("RTEC-RELATED-MODULES", path, "related_modules must be a unique string array"))
        if not _string_list(value["claim_refs"], nonempty=True):
            errors.append(Diagnostic("RTEC-REQUEST-CLAIMS", path, "claim_refs must be a non-empty unique string array"))
        program = value["requested_owner_program"]
        if not isinstance(program, str) or not PROGRAM_ID_RE.fullmatch(program):
            errors.append(Diagnostic("RTEC-OWNER-PROGRAM", path, "requested_owner_program must be a canonical CAN-PROGRAM/CAN-OWNER identifier"))
        elif owner_kind in OWNER_PROGRAMS and program != OWNER_PROGRAMS[owner_kind]:
            errors.append(Diagnostic("RTEC-OWNER-PROGRAM", path, f"owner_kind {owner_kind} must target {OWNER_PROGRAMS[owner_kind]}"))
        if value["request_type"] not in REQUEST_TYPES:
            errors.append(Diagnostic("RTEC-ENUM", path, f"unknown request_type {value['request_type']!r}"))
        if value["status"] not in REQUEST_STATUSES:
            errors.append(Diagnostic("RTEC-ENUM", path, f"unknown request status {value['status']!r}"))
        if value["priority"] not in {"low", "medium", "high", "critical"}:
            errors.append(Diagnostic("RTEC-ENUM", path, f"unknown priority {value['priority']!r}"))
        if not isinstance(value["blocking"], bool):
            errors.append(Diagnostic("RTEC-REQUEST-BLOCKING", path, "blocking must be boolean"))
        if not _nonempty_string(value["question"]):
            errors.append(Diagnostic("RTEC-REQUEST-QUESTION", path, "question must be non-empty"))
        if not _string_list(value["why_existing_evidence_is_insufficient"], nonempty=True):
            errors.append(Diagnostic("RTEC-REQUEST-GAP", path, "why_existing_evidence_is_insufficient must be non-empty"))
        for key in ("supersedes", "superseded_by"):
            if not _string_list(value[key]):
                errors.append(Diagnostic("RTEC-REFS", path, f"{key} must be a unique request-ID array"))
        if value["status"] == "superseded" and not value["superseded_by"]:
            errors.append(Diagnostic("RTEC-REQUEST-SUPERSESSION", path, "superseded request status requires superseded_by"))
        self._validate_request_version_impact(value["version_impact"], path, errors)
        self._validate_required_evidence(value["required_evidence"], path, errors)
        self._validate_available_inputs(value["available_inputs"], path, errors)
        self._validate_requested_output(value["requested_output_contract"], path, errors)
        for key in ("collector_must_not_edit", "owner_paths_read_only_for_collector"):
            if not _string_list(value[key], nonempty=True):
                errors.append(Diagnostic("RTEC-OWNER-BOUNDARY", path, f"{key} must be a non-empty unique path array"))
            elif any(not safe_repo_path(item) for item in value[key]):
                errors.append(Diagnostic("RTEC-UNSAFE-PATH", path, f"{key} contains an unsafe path"))
        self._validate_capability_gap(value["suggested_owner_capability_gap"], path, errors)
        self._validate_coordination(value["coordination"], path, errors)
        self._validate_request_result(value["result"], value["status"], path, errors)
        self._validate_request_history(value["history"], value["status"], path, errors)

    def _validate_request_version_impact(self, value: object, path: str, errors: list[Diagnostic]) -> None:
        required = set(VERSION_AXES)
        ok, detail = _object_keys(value, required)
        if not ok:
            errors.append(Diagnostic("RTEC-REQUEST-VERSION", path, detail))
            return
        assert isinstance(value, dict)
        for key, item in value.items():
            if item is None:
                continue
            if not _nonempty_string(item):
                errors.append(Diagnostic("RTEC-REQUEST-VERSION", path, f"version_impact.{key} must be null or non-empty"))
            elif key in {"canary_commit", "maintained_otclient_commit"} and not COMMIT_RE.fullmatch(item):
                errors.append(Diagnostic("RTEC-COMMIT-SHA", path, f"version_impact.{key} is malformed"))
            elif key == "map_sha256" and not SHA256_RE.fullmatch(item):
                errors.append(Diagnostic("RTEC-SHA256", path, "version_impact.map_sha256 is malformed"))

    def _validate_required_evidence(self, value: object, path: str, errors: list[Diagnostic]) -> None:
        required = {"authority_dimension", "minimum_proof_level", "minimum_e2e_maturity", "required_quality_dimensions", "required_static_dimensions", "required_version_cells"}
        ok, detail = _object_keys(value, required)
        if not ok:
            errors.append(Diagnostic("RTEC-REQUEST-EVIDENCE", path, detail))
            return
        assert isinstance(value, dict)
        if value["authority_dimension"] not in AUTHORITY_DIMENSIONS:
            errors.append(Diagnostic("RTEC-ENUM", path, f"unknown required authority_dimension {value['authority_dimension']!r}"))
        if value["minimum_proof_level"] not in PROOF_RANK:
            errors.append(Diagnostic("RTEC-ENUM", path, f"unknown minimum_proof_level {value['minimum_proof_level']!r}"))
        if value["minimum_e2e_maturity"] is not None and value["minimum_e2e_maturity"] not in {"M0", "M1", "M2", "M3", "M4", "M5"}:
            errors.append(Diagnostic("RTEC-ENUM", path, f"unknown minimum_e2e_maturity {value['minimum_e2e_maturity']!r}"))
        for key in ("required_quality_dimensions", "required_static_dimensions", "required_version_cells"):
            if not _string_list(value[key]):
                errors.append(Diagnostic("RTEC-REQUEST-EVIDENCE", path, f"required_evidence.{key} must be a unique string array"))

    def _validate_available_inputs(self, value: object, path: str, errors: list[Diagnostic]) -> None:
        required = {"source_claims", "source_urls", "canary_paths", "canary_symbols", "exact_map_or_index_hashes", "existing_result_ids", "external_artifact_hashes"}
        ok, detail = _object_keys(value, required)
        if not ok:
            errors.append(Diagnostic("RTEC-REQUEST-INPUTS", path, detail))
            return
        assert isinstance(value, dict)
        for key in required:
            if not _string_list(value[key]):
                errors.append(Diagnostic("RTEC-REQUEST-INPUTS", path, f"available_inputs.{key} must be a unique string array"))
        if isinstance(value["canary_paths"], list) and any(not safe_repo_path(item) for item in value["canary_paths"]):
            errors.append(Diagnostic("RTEC-UNSAFE-PATH", path, "available_inputs.canary_paths contains an unsafe path"))
        for key in ("exact_map_or_index_hashes", "external_artifact_hashes"):
            if isinstance(value[key], list):
                for item in value[key]:
                    digest = item.removeprefix("sha256:") if isinstance(item, str) else ""
                    if not SHA256_RE.fullmatch(digest):
                        errors.append(Diagnostic("RTEC-SHA256", path, f"available_inputs.{key} contains malformed SHA-256 {item!r}"))
        if isinstance(value["source_urls"], list):
            for item in value["source_urls"]:
                parsed = urlparse(item)
                if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.username or parsed.password:
                    errors.append(Diagnostic("RTEC-URL", path, f"available_inputs.source_urls contains invalid URL {item!r}"))

    def _validate_requested_output(self, value: object, path: str, errors: list[Diagnostic]) -> None:
        required = {"result_format_or_schema", "required_fields", "requires_explicit_proves", "requires_explicit_does_not_prove", "retention_boundary"}
        ok, detail = _object_keys(value, required)
        if not ok:
            errors.append(Diagnostic("RTEC-REQUEST-OUTPUT", path, detail))
            return
        assert isinstance(value, dict)
        if value["result_format_or_schema"] is not None and not _nonempty_string(value["result_format_or_schema"]):
            errors.append(Diagnostic("RTEC-REQUEST-OUTPUT", path, "result_format_or_schema must be null or non-empty"))
        if not _string_list(value["required_fields"], nonempty=True):
            errors.append(Diagnostic("RTEC-REQUEST-OUTPUT", path, "required_fields must be non-empty"))
        if value["requires_explicit_proves"] is not True or value["requires_explicit_does_not_prove"] is not True:
            errors.append(Diagnostic("RTEC-PROOF-BOUNDARY", path, "requested owner result must require explicit proves and does_not_prove"))
        if value["retention_boundary"] not in {"metadata-only-in-git", "owner-retained-artifact", "owner-retained-report"}:
            errors.append(Diagnostic("RTEC-ENUM", path, f"unknown retention_boundary {value['retention_boundary']!r}"))

    def _validate_capability_gap(self, value: object, path: str, errors: list[Diagnostic]) -> None:
        required = {"present", "summary", "reuse_value", "note"}
        ok, detail = _object_keys(value, required)
        if not ok:
            errors.append(Diagnostic("RTEC-CAPABILITY-GAP", path, detail))
            return
        assert isinstance(value, dict)
        if not isinstance(value["present"], bool):
            errors.append(Diagnostic("RTEC-CAPABILITY-GAP", path, "present must be boolean"))
        if value["present"] is True and (not _nonempty_string(value["summary"]) or not _nonempty_string(value["reuse_value"])):
            errors.append(Diagnostic("RTEC-CAPABILITY-GAP", path, "present capability gap requires summary and reuse_value"))
        if value["present"] is False and (value["summary"] is not None or value["reuse_value"] is not None):
            errors.append(Diagnostic("RTEC-CAPABILITY-GAP", path, "absent capability gap must leave summary and reuse_value null"))
        if not _nonempty_string(value["note"]):
            errors.append(Diagnostic("RTEC-CAPABILITY-GAP", path, "note must be non-empty"))

    def _validate_coordination(self, value: object, path: str, errors: list[Diagnostic]) -> None:
        required = {"collector_task", "collector_pr", "owner_task", "owner_pr", "coordination_id", "depends_on", "blocks"}
        ok, detail = _object_keys(value, required)
        if not ok:
            errors.append(Diagnostic("RTEC-COORDINATION", path, detail))
            return
        assert isinstance(value, dict)
        for key in ("collector_task", "coordination_id"):
            if not _nonempty_string(value[key]):
                errors.append(Diagnostic("RTEC-COORDINATION", path, f"coordination.{key} must be non-empty"))
        for key in ("owner_task",):
            if value[key] is not None and not _nonempty_string(value[key]):
                errors.append(Diagnostic("RTEC-COORDINATION", path, f"coordination.{key} must be null or non-empty"))
        for key in ("collector_pr", "owner_pr"):
            if value[key] is not None and (not isinstance(value[key], int) or isinstance(value[key], bool) or value[key] <= 0):
                errors.append(Diagnostic("RTEC-COORDINATION", path, f"coordination.{key} must be null or positive"))
        for key in ("depends_on", "blocks"):
            if not _string_list(value[key]):
                errors.append(Diagnostic("RTEC-COORDINATION", path, f"coordination.{key} must be a unique request-ID array"))

    def _validate_request_result(self, value: object, status: object, path: str, errors: list[Diagnostic]) -> None:
        required = {"available", "result_refs", "consumed_by_evidence_records", "proof_level_reached", "proves", "does_not_prove", "blockers"}
        ok, detail = _object_keys(value, required)
        if not ok:
            errors.append(Diagnostic("RTEC-REQUEST-RESULT", path, detail))
            return
        assert isinstance(value, dict)
        if not isinstance(value["available"], bool):
            errors.append(Diagnostic("RTEC-REQUEST-RESULT", path, "result.available must be boolean"))
        for key in ("result_refs", "consumed_by_evidence_records", "proves", "does_not_prove", "blockers"):
            if not _string_list(value[key]):
                errors.append(Diagnostic("RTEC-REQUEST-RESULT", path, f"result.{key} must be a unique string array"))
        if value["proof_level_reached"] is not None and value["proof_level_reached"] not in PROOF_RANK:
            errors.append(Diagnostic("RTEC-ENUM", path, f"unknown result proof level {value['proof_level_reached']!r}"))
        complete = status in {"result-available", "consumed"}
        if complete:
            if value["available"] is not True or not value["result_refs"] or not value["proves"] or not value["does_not_prove"] or value["proof_level_reached"] not in PROOF_RANK:
                errors.append(Diagnostic("RTEC-REQUEST-RESULT", path, f"status {status} requires available result refs, proof level and explicit proof boundaries"))
        elif value["available"] is True:
            errors.append(Diagnostic("RTEC-REQUEST-RESULT", path, f"status {status} cannot set result.available true"))

    def _validate_request_history(self, value: object, status: object, path: str, errors: list[Diagnostic]) -> None:
        if not isinstance(value, list) or not value:
            errors.append(Diagnostic("RTEC-REQUEST-HISTORY", path, "history must be a non-empty array"))
            return
        previous_status: str | None = None
        previous_at: dt.datetime | None = None
        required = {"at", "actor", "actor_role", "actor_task", "actor_pr", "from_status", "to_status", "reason", "owner_evidence_ref"}
        for index, event in enumerate(value):
            label = f"history[{index}]"
            ok, detail = _object_keys(event, required)
            if not ok:
                errors.append(Diagnostic("RTEC-REQUEST-HISTORY", path, f"{label} {detail}"))
                continue
            assert isinstance(event, dict)
            at = _parse_datetime(event["at"])
            if at is None:
                errors.append(Diagnostic("RTEC-DATETIME", path, f"{label}.at must be timezone-aware ISO-8601"))
            elif previous_at is not None and at < previous_at:
                errors.append(Diagnostic("RTEC-REQUEST-HISTORY", path, f"{label}.at moves backwards"))
            if at is not None:
                previous_at = at
            if not _nonempty_string(event["actor"]):
                errors.append(Diagnostic("RTEC-REQUEST-HISTORY", path, f"{label}.actor must be non-empty"))
            if event["actor_role"] not in {"collector", "owner", "reviewer", "automation"}:
                errors.append(Diagnostic("RTEC-ENUM", path, f"{label}.actor_role has unknown value {event['actor_role']!r}"))
            if not _nonempty_string(event["actor_task"]):
                errors.append(Diagnostic("RTEC-REQUEST-HISTORY", path, f"{label}.actor_task must be non-empty"))
            if event["actor_pr"] is not None and (not isinstance(event["actor_pr"], int) or isinstance(event["actor_pr"], bool) or event["actor_pr"] <= 0):
                errors.append(Diagnostic("RTEC-REQUEST-HISTORY", path, f"{label}.actor_pr must be null or positive"))
            if event["to_status"] not in REQUEST_STATUSES:
                errors.append(Diagnostic("RTEC-ENUM", path, f"{label}.to_status has unknown value {event['to_status']!r}"))
                continue
            if not _nonempty_string(event["reason"]):
                errors.append(Diagnostic("RTEC-REQUEST-HISTORY", path, f"{label}.reason must be non-empty"))
            if index == 0:
                if event["from_status"] is not None or event["to_status"] != "draft":
                    errors.append(Diagnostic("RTEC-REQUEST-TRANSITION", path, "first history event must transition null -> draft"))
            else:
                if event["from_status"] != previous_status:
                    errors.append(Diagnostic("RTEC-REQUEST-TRANSITION", path, f"{label}.from_status must equal previous to_status {previous_status!r}"))
                if previous_status in REQUEST_TRANSITIONS and event["to_status"] not in REQUEST_TRANSITIONS[previous_status]:
                    errors.append(Diagnostic("RTEC-REQUEST-TRANSITION", path, f"invalid request transition {previous_status!r} -> {event['to_status']!r}"))
            if event["to_status"] in OWNER_CONTROLLED_STATUSES:
                if event["actor_role"] != "owner" or not _nonempty_string(event["owner_evidence_ref"]):
                    errors.append(Diagnostic("RTEC-OWNER-EVIDENCE", path, f"transition to {event['to_status']} requires owner actor and owner_evidence_ref"))
            elif event["owner_evidence_ref"] is not None and not _nonempty_string(event["owner_evidence_ref"]):
                errors.append(Diagnostic("RTEC-REQUEST-HISTORY", path, f"{label}.owner_evidence_ref must be null or non-empty"))
            previous_status = event["to_status"]
        if previous_status != status:
            errors.append(Diagnostic("RTEC-REQUEST-TRANSITION", path, f"current status {status!r} must equal final history status {previous_status!r}"))

    def _validate_history_document(self, document: LoadedDocument, errors: list[Diagnostic]) -> None:
        value = document.value
        path = document.relative_path
        required = {"format", "schema_version", "module_id", "entries"}
        ok, detail = _object_keys(value, required)
        if not ok:
            errors.append(Diagnostic("RTEC-HISTORY-SHAPE", path, detail))
            return
        if value["format"] != VERSION_HISTORY_FORMAT or value["schema_version"] != SCHEMA_VERSION:
            errors.append(Diagnostic("RTEC-SCHEMA-VERSION", path, f"format/schema_version must be {VERSION_HISTORY_FORMAT}/{SCHEMA_VERSION}"))
        module_id = value["module_id"]
        if module_id not in self.modules:
            errors.append(Diagnostic("RTEC-MODULE-ID", path, f"unknown canonical module_id {module_id!r}"))
        expected = f"docs/agents/real-tibia/evidence/modules/{module_id}/VERSION_HISTORY.yaml"
        if path != expected:
            errors.append(Diagnostic("RTEC-HISTORY-PATH", path, f"version history path must be {expected}"))
        entries = value["entries"]
        if not isinstance(entries, list) or not entries:
            errors.append(Diagnostic("RTEC-HISTORY-ENTRIES", path, "entries must be a non-empty array"))
            return
        required_entry = {
            "history_id", "claim_refs", "lifecycle", "confidence", "statement", "evidence_refs",
            "proves", "does_not_prove", "supersedes", "superseded_by",
        }
        for index, entry in enumerate(entries):
            label = f"entries[{index}]"
            ok, detail = _object_keys(entry, required_entry)
            if not ok:
                errors.append(Diagnostic("RTEC-HISTORY-ENTRY", path, f"{label} {detail}"))
                continue
            assert isinstance(entry, dict)
            history_id = entry["history_id"]
            if not isinstance(history_id, str) or not HISTORY_ID_RE.fullmatch(history_id):
                errors.append(Diagnostic("RTEC-HISTORY-ID", path, f"{label}.history_id is malformed"))
            elif isinstance(module_id, str) and not history_id.startswith(f"RTVH-{module_token(module_id)}-"):
                errors.append(Diagnostic("RTEC-HISTORY-ID", path, f"{label}.history_id must use module token {module_token(module_id)}"))
            if entry["confidence"] not in VERSION_CONFIDENCE:
                errors.append(Diagnostic("RTEC-ENUM", path, f"{label}.confidence has unknown value {entry['confidence']!r}"))
            if not _nonempty_string(entry["statement"]):
                errors.append(Diagnostic("RTEC-HISTORY-ENTRY", path, f"{label}.statement must be non-empty"))
            for key in ("claim_refs", "evidence_refs", "proves", "does_not_prove", "supersedes", "superseded_by"):
                required_values = key in {"claim_refs", "evidence_refs", "proves", "does_not_prove"}
                if not _string_list(entry[key], nonempty=required_values):
                    qualifier = "non-empty " if required_values else ""
                    errors.append(Diagnostic("RTEC-HISTORY-ENTRY", path, f"{label}.{key} must be a {qualifier}unique string array"))
            lifecycle = entry["lifecycle"]
            required_lifecycle = {
                "announced_in", "introduced_in", "observed_in", "changed_in", "deprecated_in",
                "removed_in", "effective_from", "effective_until",
            }
            ok, detail = _object_keys(lifecycle, required_lifecycle)
            if not ok:
                errors.append(Diagnostic("RTEC-HISTORY-LIFECYCLE", path, f"{label}.lifecycle {detail}"))
                continue
            assert isinstance(lifecycle, dict)
            parsed: dict[str, dict[str, Any] | None] = {}
            for key in ("announced_in", "introduced_in", "deprecated_in", "removed_in", "effective_from", "effective_until"):
                parsed[key] = _validate_version_marker(lifecycle[key], f"{label}.lifecycle.{key}", errors, path)
            for key in ("observed_in", "changed_in"):
                items = lifecycle[key]
                if not isinstance(items, list):
                    errors.append(Diagnostic("RTEC-HISTORY-LIFECYCLE", path, f"{label}.lifecycle.{key} must be an array"))
                    continue
                for marker_index, marker in enumerate(items):
                    _validate_version_marker(marker, f"{label}.lifecycle.{key}[{marker_index}]", errors, path)
            introduced = parsed.get("introduced_in")
            if introduced and introduced.get("mode") == "EXACT" and entry["confidence"] not in {"proven-official", "proven-observation"}:
                errors.append(Diagnostic("RTEC-INTRODUCTION-VERSION", path, f"{label} exact introduced_in requires proven-official or proven-observation confidence"))
            if entry["confidence"] == "derived-range" and (not introduced or introduced.get("mode") != "DERIVED_RANGE"):
                errors.append(Diagnostic("RTEC-VERSION-MODE", path, f"{label} derived-range confidence requires DERIVED_RANGE introduced_in"))
            if introduced and introduced.get("mode") == "EXACT" and entry["confidence"] in {"supported-secondary", "unknown", "conflicting"}:
                errors.append(Diagnostic("RTEC-INTRODUCTION-VERSION", path, f"{label} must not invent an exact introduction version from secondary, unknown or conflicting evidence"))

    def _validate_module_index_document(self, document: LoadedDocument, errors: list[Diagnostic]) -> None:
        value = document.value
        path = document.relative_path
        required = {"format", "schema_version", "module_id", "as_of", "record_count", "evidence_ids", "by_claim_key", "by_authority_dimension", "by_state", "by_proof_level", "version_history_ids", "owner_request_ids", "unresolved_conflict_ids", "stale_evidence_ids", "superseded_evidence_ids"}
        ok, detail = _object_keys(value, required)
        if not ok:
            errors.append(Diagnostic("RTEC-MODULE-INDEX-SHAPE", path, detail))
            return
        if value["format"] != MODULE_INDEX_FORMAT or value["schema_version"] != SCHEMA_VERSION:
            errors.append(Diagnostic("RTEC-SCHEMA-VERSION", path, f"format/schema_version must be {MODULE_INDEX_FORMAT}/{SCHEMA_VERSION}"))
        module_id = value["module_id"]
        if module_id not in self.modules:
            errors.append(Diagnostic("RTEC-MODULE-ID", path, f"unknown canonical module_id {module_id!r}"))
        if not _is_date(value["as_of"]):
            errors.append(Diagnostic("RTEC-DATE", path, "module index as_of must be YYYY-MM-DD"))
        if not isinstance(value["record_count"], int) or isinstance(value["record_count"], bool) or value["record_count"] < 0:
            errors.append(Diagnostic("RTEC-MODULE-INDEX-SHAPE", path, "record_count must be a non-negative integer"))
        for key in ("evidence_ids", "version_history_ids", "owner_request_ids", "unresolved_conflict_ids", "stale_evidence_ids", "superseded_evidence_ids"):
            if not _string_list(value[key]):
                errors.append(Diagnostic("RTEC-MODULE-INDEX-SHAPE", path, f"{key} must be a unique string array"))
        for key in ("by_claim_key", "by_authority_dimension", "by_state", "by_proof_level"):
            mapping = value[key]
            if not isinstance(mapping, dict) or not all(isinstance(name, str) and _string_list(items) for name, items in mapping.items()):
                errors.append(Diagnostic("RTEC-MODULE-INDEX-SHAPE", path, f"{key} must map strings to unique string arrays"))

    def _request_supersession_consistency(self, requests_by_id: Mapping[str, LoadedDocument]) -> list[Diagnostic]:
        errors: list[Diagnostic] = []
        for request_id, document in sorted(requests_by_id.items()):
            value = document.value
            for older in value.get("supersedes", []) if isinstance(value.get("supersedes"), list) else []:
                target = requests_by_id.get(older)
                if target is None:
                    continue
                if request_id not in target.value.get("superseded_by", []):
                    errors.append(Diagnostic("RTEC-REQUEST-SUPERSESSION-RECIPROCAL", document.relative_path, f"{request_id} supersedes {older}, but the older request does not list it in superseded_by"))
                if target.value.get("status") != "superseded":
                    errors.append(Diagnostic("RTEC-REQUEST-SUPERSESSION-STATE", target.relative_path, f"request superseded by {request_id} must use superseded status"))
            for newer in value.get("superseded_by", []) if isinstance(value.get("superseded_by"), list) else []:
                target = requests_by_id.get(newer)
                if target is not None and request_id not in target.value.get("supersedes", []):
                    errors.append(Diagnostic("RTEC-REQUEST-SUPERSESSION-RECIPROCAL", document.relative_path, f"{request_id} lists superseded_by {newer}, but the newer request does not list it in supersedes"))
        return errors

    def _history_supersession_consistency(self, history_by_id: Mapping[str, tuple[LoadedDocument, dict[str, Any]]]) -> list[Diagnostic]:
        errors: list[Diagnostic] = []
        for history_id, (document, event) in sorted(history_by_id.items()):
            for older in event.get("supersedes", []) if isinstance(event.get("supersedes"), list) else []:
                target = history_by_id.get(older)
                if target is not None and history_id not in target[1].get("superseded_by", []):
                    errors.append(Diagnostic("RTEC-HISTORY-SUPERSESSION-RECIPROCAL", document.relative_path, f"{history_id} supersedes {older}, but the older history event does not list it in superseded_by"))
            for newer in event.get("superseded_by", []) if isinstance(event.get("superseded_by"), list) else []:
                target = history_by_id.get(newer)
                if target is not None and history_id not in target[1].get("supersedes", []):
                    errors.append(Diagnostic("RTEC-HISTORY-SUPERSESSION-RECIPROCAL", document.relative_path, f"{history_id} lists superseded_by {newer}, but the newer history event does not list it in supersedes"))
        return errors

    def _validate_generated_document(self, document: LoadedDocument, errors: list[Diagnostic]) -> None:
        value = document.value
        path = document.relative_path
        required = {
            "format", "schema_version", "as_of", "input_sha256", "source_counts",
            "evidence_by_module", "evidence_by_authority_dimension", "evidence_by_version_axis",
            "unresolved_conflicts", "stale_evidence", "active_owner_requests",
            "superseded_records", "proof_maturity_by_dimension", "nonclaims",
        }
        ok, detail = _object_keys(value, required)
        if not ok:
            errors.append(Diagnostic("RTEC-GENERATED-INDEX-SHAPE", path, detail))
            return
        if value["format"] != GENERATED_INDEX_FORMAT or value["schema_version"] != SCHEMA_VERSION:
            errors.append(Diagnostic("RTEC-SCHEMA-VERSION", path, f"format/schema_version must be {GENERATED_INDEX_FORMAT}/{SCHEMA_VERSION}"))
        if not _is_date(value["as_of"]):
            errors.append(Diagnostic("RTEC-DATE", path, "generated index as_of must be YYYY-MM-DD"))
        if not isinstance(value["input_sha256"], str) or not SHA256_RE.fullmatch(value["input_sha256"]):
            errors.append(Diagnostic("RTEC-SHA256", path, "generated index input_sha256 must be an exact lowercase SHA-256"))
        counts = value["source_counts"]
        ok, detail = _object_keys(counts, {"evidence_records", "owner_requests", "version_history_records"})
        if not ok:
            errors.append(Diagnostic("RTEC-GENERATED-INDEX-SHAPE", path, f"source_counts {detail}"))
        elif any(not isinstance(item, int) or isinstance(item, bool) or item < 0 for item in counts.values()):
            errors.append(Diagnostic("RTEC-GENERATED-INDEX-SHAPE", path, "source_counts values must be non-negative integers"))
        for key in ("evidence_by_module", "evidence_by_authority_dimension"):
            mapping = value[key]
            if not isinstance(mapping, dict) or not all(isinstance(name, str) and _string_list(items) for name, items in mapping.items()):
                errors.append(Diagnostic("RTEC-GENERATED-INDEX-SHAPE", path, f"{key} must map strings to unique string arrays"))
        version_map = value["evidence_by_version_axis"]
        if not isinstance(version_map, dict) or any(axis not in VERSION_AXES for axis in version_map):
            errors.append(Diagnostic("RTEC-GENERATED-INDEX-SHAPE", path, "evidence_by_version_axis contains an unknown version axis"))
        elif not all(isinstance(rows, dict) and all(_nonempty_string(version) and _string_list(refs) for version, refs in rows.items()) for rows in version_map.values()):
            errors.append(Diagnostic("RTEC-GENERATED-INDEX-SHAPE", path, "evidence_by_version_axis must map version values to unique reference arrays"))
        for key in ("unresolved_conflicts", "active_owner_requests", "nonclaims"):
            if not _string_list(value[key]):
                errors.append(Diagnostic("RTEC-GENERATED-INDEX-SHAPE", path, f"{key} must be a unique string array"))
        if not isinstance(value["stale_evidence"], list) or not all(
            isinstance(row, dict) and set(row) == {"evidence_id", "module_id", "age_days", "reason"}
            and _nonempty_string(row["evidence_id"]) and _nonempty_string(row["module_id"])
            and isinstance(row["age_days"], int) and not isinstance(row["age_days"], bool)
            and _nonempty_string(row["reason"]) for row in value["stale_evidence"]
        ):
            errors.append(Diagnostic("RTEC-GENERATED-INDEX-SHAPE", path, "stale_evidence rows are malformed"))
        if not isinstance(value["superseded_records"], list) or not all(
            isinstance(row, dict) and set(row) == {"record_type", "record_id"}
            and row["record_type"] in {"evidence", "request"} and _nonempty_string(row["record_id"])
            for row in value["superseded_records"]
        ):
            errors.append(Diagnostic("RTEC-GENERATED-INDEX-SHAPE", path, "superseded_records rows are malformed"))
        maturity = value["proof_maturity_by_dimension"]
        maturity_ok = isinstance(maturity, dict)
        if maturity_ok:
            for module_id, dimensions in maturity.items():
                if module_id not in self.modules or not isinstance(dimensions, dict):
                    maturity_ok = False
                    break
                for dimension, row in dimensions.items():
                    if dimension not in AUTHORITY_DIMENSIONS or not isinstance(row, dict) or set(row) != {"proof_level", "evidence_ids", "evidence_states"}:
                        maturity_ok = False
                        break
                    if row["proof_level"] not in PROOF_RANK or not _string_list(row["evidence_ids"], nonempty=True) or not _string_list(row["evidence_states"], nonempty=True):
                        maturity_ok = False
                        break
                    if any(state not in EVIDENCE_STATES for state in row["evidence_states"]):
                        maturity_ok = False
                        break
                if not maturity_ok:
                    break
        if not maturity_ok:
            errors.append(Diagnostic("RTEC-GENERATED-INDEX-SHAPE", path, "proof_maturity_by_dimension must map canonical modules and authority dimensions to validated proof rows"))
        forbidden = {"overall_parity_percentage", "release_approval", "whole_game_parity"}
        if forbidden.intersection(value):
            errors.append(Diagnostic("RTEC-FORBIDDEN-AGGREGATE", path, "generated index contains a forbidden score or approval field"))

    def _supersession_consistency(self, evidence_by_id: Mapping[str, LoadedDocument]) -> list[Diagnostic]:
        errors: list[Diagnostic] = []
        for evidence_id, document in sorted(evidence_by_id.items()):
            value = document.value
            path = document.relative_path
            for older in value.get("supersedes", []) if isinstance(value.get("supersedes"), list) else []:
                target = evidence_by_id.get(older)
                if target is None:
                    continue
                if evidence_id not in target.value.get("superseded_by", []):
                    errors.append(Diagnostic("RTEC-SUPERSESSION-RECIPROCAL", path, f"{evidence_id} supersedes {older}, but the older record does not list it in superseded_by"))
                if target.value.get("evidence_state") != "SUPERSEDED":
                    errors.append(Diagnostic("RTEC-SUPERSESSION-STATE", target.relative_path, f"record superseded by {evidence_id} must use SUPERSEDED evidence_state"))
            for newer in value.get("superseded_by", []) if isinstance(value.get("superseded_by"), list) else []:
                target = evidence_by_id.get(newer)
                if target is not None and evidence_id not in target.value.get("supersedes", []):
                    errors.append(Diagnostic("RTEC-SUPERSESSION-RECIPROCAL", path, f"{evidence_id} lists superseded_by {newer}, but the newer record does not list it in supersedes"))
        return errors

    @staticmethod
    def _cycle_errors(graph: Mapping[str, object], label: str, code: str) -> list[Diagnostic]:
        state: dict[str, int] = {}
        stack: list[str] = []
        errors: list[Diagnostic] = []

        def visit(node: str) -> None:
            if state.get(node) == 2:
                return
            if state.get(node) == 1:
                start = stack.index(node)
                cycle = stack[start:] + [node]
                errors.append(Diagnostic(code, node, f"{label} cycle: {' -> '.join(cycle)}"))
                return
            state[node] = 1
            stack.append(node)
            targets = graph.get(node, [])
            if isinstance(targets, list):
                for target in sorted(item for item in targets if isinstance(item, str) and item in graph):
                    visit(target)
            stack.pop()
            state[node] = 2

        for node in sorted(graph):
            visit(node)
        return errors

    def _generated_as_of(self) -> dt.date:
        dates: list[dt.date] = []
        for document in self.evidence_documents:
            freshness = document.value.get("freshness")
            if isinstance(freshness, dict) and _is_date(freshness.get("observed_or_verified_at")):
                dates.append(dt.date.fromisoformat(freshness["observed_or_verified_at"]))
        for document in self.request_documents:
            history = document.value.get("history")
            if isinstance(history, list):
                for event in history:
                    parsed = _parse_datetime(event.get("at")) if isinstance(event, dict) else None
                    if parsed is not None:
                        dates.append(parsed.date())
        if self.generated_document is not None and _is_date(self.generated_document.value.get("as_of")):
            dates.append(dt.date.fromisoformat(self.generated_document.value["as_of"]))
        return max(dates) if dates else dt.date(1970, 1, 1)

    def stale_rows(self, as_of: dt.date) -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for document in sorted(self.evidence_documents, key=lambda item: str(item.value.get("evidence_id"))):
            value = document.value
            freshness = value.get("freshness")
            if not isinstance(freshness, dict) or not _is_date(freshness.get("observed_or_verified_at")):
                continue
            observed = dt.date.fromisoformat(freshness["observed_or_verified_at"])
            age = (as_of - observed).days
            warning = freshness.get("warning_after_days")
            invalid = freshness.get("invalid_after_days")
            explicit = value.get("evidence_state") == "STALE"
            warned = isinstance(warning, int) and not isinstance(warning, bool) and age >= warning
            expired = isinstance(invalid, int) and not isinstance(invalid, bool) and age >= invalid
            if explicit or warned:
                if explicit:
                    reason = "explicit-state"
                elif expired:
                    reason = "invalidation-window-expired"
                else:
                    reason = "freshness-warning-window-reached"
                rows.append(
                    {
                        "evidence_id": value.get("evidence_id"),
                        "module_id": value.get("module_id"),
                        "age_days": age,
                        "reason": reason,
                    }
                )
        return rows

    def module_indexes(self, as_of: dt.date) -> dict[str, dict[str, Any]]:
        evidence_by_module: dict[str, list[dict[str, Any]]] = defaultdict(list)
        request_by_module: dict[str, list[str]] = defaultdict(list)
        history_by_module: dict[str, list[str]] = defaultdict(list)
        stale = {row["evidence_id"] for row in self.stale_rows(as_of)}
        for document in self.evidence_documents:
            module_id = document.value.get("module_id")
            if isinstance(module_id, str):
                evidence_by_module[module_id].append(document.value)
        for document in self.request_documents:
            module_id = document.value.get("module_id")
            request_id = document.value.get("request_id")
            if isinstance(module_id, str) and isinstance(request_id, str):
                request_by_module[module_id].append(request_id)
        for document in self.history_documents:
            module_id = document.value.get("module_id")
            entries = document.value.get("entries")
            if isinstance(module_id, str) and isinstance(entries, list):
                history_by_module[module_id].extend(entry["history_id"] for entry in entries if isinstance(entry, dict) and isinstance(entry.get("history_id"), str))
        module_dirs = {
            path.name
            for path in (self.evidence_root / "modules").iterdir()
            if path.is_dir() and not path.is_symlink()
        } if (self.evidence_root / "modules").is_dir() else set()
        modules = sorted(set(evidence_by_module) | set(request_by_module) | set(history_by_module) | module_dirs)
        result: dict[str, dict[str, Any]] = {}
        for module_id in modules:
            records = sorted(evidence_by_module[module_id], key=lambda row: row["evidence_id"])
            by_claim: dict[str, list[str]] = defaultdict(list)
            by_authority: dict[str, list[str]] = defaultdict(list)
            by_state: dict[str, list[str]] = defaultdict(list)
            by_proof: dict[str, list[str]] = defaultdict(list)
            for record in records:
                evidence_id = record["evidence_id"]
                by_claim[record["claim_key"]].append(evidence_id)
                by_authority[record["authority_dimension"]].append(evidence_id)
                by_state[record["evidence_state"]].append(evidence_id)
                by_proof[record["proof_level"]].append(evidence_id)
            result[module_id] = {
                "format": MODULE_INDEX_FORMAT,
                "schema_version": SCHEMA_VERSION,
                "module_id": module_id,
                "as_of": as_of.isoformat(),
                "record_count": len(records),
                "evidence_ids": [row["evidence_id"] for row in records],
                "by_claim_key": {key: sorted(values) for key, values in sorted(by_claim.items())},
                "by_authority_dimension": {key: sorted(values) for key, values in sorted(by_authority.items())},
                "by_state": {key: sorted(values) for key, values in sorted(by_state.items())},
                "by_proof_level": {key: sorted(values) for key, values in sorted(by_proof.items(), key=lambda item: PROOF_RANK.get(item[0], 999))},
                "version_history_ids": sorted(set(history_by_module[module_id])),
                "owner_request_ids": sorted(set(request_by_module[module_id])),
                "unresolved_conflict_ids": sorted(row["evidence_id"] for row in records if row["evidence_state"] == "CONFLICT"),
                "stale_evidence_ids": sorted(row["evidence_id"] for row in records if row["evidence_id"] in stale),
                "superseded_evidence_ids": sorted(row["evidence_id"] for row in records if row["evidence_state"] == "SUPERSEDED"),
            }
        return result

    def generated_indexes(self, as_of: dt.date) -> dict[str, Any]:
        by_module: dict[str, list[str]] = defaultdict(list)
        by_authority: dict[str, list[str]] = defaultdict(list)
        by_version: dict[str, dict[str, set[str]]] = {axis: defaultdict(set) for axis in VERSION_AXES}
        conflicts: list[str] = []
        superseded: list[dict[str, str]] = []
        proof: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
        input_fingerprints: list[str] = []

        for document in sorted(self.evidence_documents, key=lambda item: str(item.value.get("evidence_id"))):
            record = document.value
            evidence_id = record["evidence_id"]
            module_id = record["module_id"]
            dimension = record["authority_dimension"]
            by_module[module_id].append(evidence_id)
            by_authority[dimension].append(evidence_id)
            if record["evidence_state"] == "CONFLICT":
                conflicts.append(evidence_id)
            if record["evidence_state"] == "SUPERSEDED":
                superseded.append({"record_type": "evidence", "record_id": evidence_id})
            if record["evidence_state"] not in {"REJECTED", "SUPERSEDED"}:
                proof[module_id][dimension].append(record)
            for marker in self._markers_from_applicability(record["applicability"]):
                for location in ("exact", "lower_bound", "upper_bound"):
                    axes = marker.get(location)
                    if isinstance(axes, dict):
                        for axis in VERSION_AXES:
                            value = axes.get(axis)
                            if isinstance(value, str):
                                by_version[axis][value].add(evidence_id)
            input_fingerprints.append(f"evidence:{document.relative_path}:{document.sha256}")

        active_requests: list[str] = []
        for document in sorted(self.request_documents, key=lambda item: str(item.value.get("request_id"))):
            request = document.value
            request_id = request["request_id"]
            if request["status"] in ACTIVE_REQUEST_STATUSES:
                active_requests.append(request_id)
            if request["status"] == "superseded":
                superseded.append({"record_type": "request", "record_id": request_id})
            input_fingerprints.append(f"request:{document.relative_path}:{document.sha256}")

        version_history_count = 0
        for document in sorted(self.history_documents, key=lambda item: item.relative_path):
            entries = document.value.get("entries", [])
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                version_history_count += 1
                history_id = entry.get("history_id")
                lifecycle = entry.get("lifecycle")
                if isinstance(history_id, str) and isinstance(lifecycle, dict):
                    for marker in self._markers_from_applicability(lifecycle):
                        for location in ("exact", "lower_bound", "upper_bound"):
                            axis_values = marker.get(location)
                            if isinstance(axis_values, dict):
                                for axis in VERSION_AXES:
                                    axis_value = axis_values.get(axis)
                                    if isinstance(axis_value, str):
                                        by_version[axis][axis_value].add(history_id)
            input_fingerprints.append(f"history:{document.relative_path}:{document.sha256}")

        maturity: dict[str, dict[str, dict[str, Any]]] = {}
        for module_id, dimensions in sorted(proof.items()):
            maturity[module_id] = {}
            for dimension, records in sorted(dimensions.items()):
                strongest = _strongest(record["proof_level"] for record in records)
                assert strongest is not None
                strongest_ids = sorted(record["evidence_id"] for record in records if record["proof_level"] == strongest)
                maturity[module_id][dimension] = {
                    "proof_level": strongest,
                    "evidence_ids": strongest_ids,
                    "evidence_states": sorted({record["evidence_state"] for record in records if record["proof_level"] == strongest}),
                }

        stale = self.stale_rows(as_of)
        digest = hashlib.sha256("\n".join(sorted(input_fingerprints)).encode("utf-8")).hexdigest()
        return {
            "format": GENERATED_INDEX_FORMAT,
            "schema_version": SCHEMA_VERSION,
            "as_of": as_of.isoformat(),
            "input_sha256": digest,
            "source_counts": {
                "evidence_records": len(self.evidence_documents),
                "owner_requests": len(self.request_documents),
                "version_history_records": version_history_count,
            },
            "evidence_by_module": {key: sorted(values) for key, values in sorted(by_module.items())},
            "evidence_by_authority_dimension": {key: sorted(values) for key, values in sorted(by_authority.items())},
            "evidence_by_version_axis": {
                axis: {value: sorted(refs) for value, refs in sorted(values.items())}
                for axis, values in sorted(by_version.items())
                if values
            },
            "unresolved_conflicts": sorted(conflicts),
            "stale_evidence": stale,
            "active_owner_requests": sorted(active_requests),
            "superseded_records": sorted(superseded, key=lambda row: (row["record_type"], row["record_id"])),
            "proof_maturity_by_dimension": maturity,
            "nonclaims": [
                "No overall parity percentage is generated.",
                "No release approval or whole-game parity claim is generated.",
                "File presence alone is not evidence.",
            ],
        }

    def generated_files(self, as_of: dt.date) -> dict[Path, str]:
        output: dict[Path, str] = {}
        global_path = self.evidence_root / "generated/EVIDENCE_INDEXES.json"
        output[global_path] = json.dumps(self.generated_indexes(as_of), indent=2, sort_keys=True, ensure_ascii=False) + "\n"
        for module_id, index in self.module_indexes(as_of).items():
            path = self.evidence_root / "modules" / module_id / "EVIDENCE_INDEX.yaml"
            output[path] = json.dumps(index, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
        return output


def _atomic_write(path: Path, content: str, root: Path) -> None:
    root = root.resolve(strict=True)
    parent = path.parent
    existing = parent
    while not existing.exists() and existing != existing.parent:
        existing = existing.parent
    for candidate in (existing, *existing.parents):
        if candidate == root:
            break
        if candidate.is_symlink():
            raise EvidenceError(f"output path must not use a symlink ancestor: {_relative(root, candidate)}")
    parent.mkdir(parents=True, exist_ok=True)
    if parent.is_symlink():
        raise EvidenceError(f"output directory must not be a symlink: {_relative(root, parent)}")
    resolved_parent = parent.resolve(strict=True)
    if not _inside(root, resolved_parent):
        raise EvidenceError(f"output path escapes repository root: {path}")
    if path.exists() and path.is_symlink():
        raise EvidenceError(f"output path must not be a symlink: {_relative(root, path)}")
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=resolved_parent)
    temp_path = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def write_generated(corpus: Corpus, *, check: bool, as_of: dt.date | None) -> int:
    if as_of is None:
        if corpus.generated_document is None or not _is_date(corpus.generated_document.value.get("as_of")):
            raise EvidenceError("--as-of YYYY-MM-DD is required when no valid generated index exists")
        as_of = dt.date.fromisoformat(corpus.generated_document.value["as_of"])
    files = corpus.generated_files(as_of)
    stale: list[str] = []
    for path, expected in sorted(files.items(), key=lambda item: item[0].as_posix()):
        relative = _relative(corpus.root, path)
        if check:
            if path.is_symlink() or not path.exists() or path.read_text(encoding="utf-8") != expected:
                stale.append(relative)
        else:
            _atomic_write(path, expected, corpus.root)
    # Existing module indexes without a corresponding generated module are stale/unsafe.
    expected_paths = {path.resolve(strict=False) for path in files}
    for document in corpus.module_index_documents:
        if document.path.resolve(strict=False) not in expected_paths:
            stale.append(document.relative_path)
    if stale:
        raise EvidenceError("generated files are stale, missing or unexpected: " + ", ".join(sorted(set(stale))))
    return 0
