#!/usr/bin/env python3
"""Deterministic drift over exact retained Tibia client-reference indexes.

The producer consumes existing TCR manifests and indexes. It never reparses client
files and never mutates the supplied evidence. All provenance and compatibility
checks fail closed before semantic comparison.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

FORMAT = "canary-tibia-client-reference-drift-v1"
SCHEMA_VERSION = 1
MANIFEST_FORMAT = "canary-tibia-client-reference-manifest-v1"
MANIFEST_SCHEMA = 1
REPORT_SPECS: dict[str, tuple[str, frozenset[int], str]] = {
    "staticdata": ("canary-tibia-staticdata-index-v1", frozenset({2}), "staticdata"),
    "staticmapdata": ("canary-tibia-staticmapdata-index-v1", frozenset({1}), "staticmapdata"),
    "proficiencies": ("canary-tibia-proficiency-index-v1", frozenset({1, 2}), "proficiencies"),
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
REVISION_RE = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")
DEFAULT_MAX_FILE_BYTES = 64 * 1024 * 1024
DEFAULT_MAX_FINDINGS = 2_000_000
DEFAULT_MAX_FIELD_CHANGES = 10_000_000

COMPONENT_DEPENDENCIES: dict[str, tuple[str, ...]] = {
    "package-metadata": ("tcr.package-identity",),
    "staticdata": (
        "tcr.content-reference-correlation",
        "tcr.house-reference-parity",
        "tcr.reference-adoption-routing",
        "owa.tcr-freshness-integration",
    ),
    "staticmapdata": (
        "tcr.house-reference-parity",
        "tcr.reference-adoption-routing",
        "owa.tcr-freshness-integration",
    ),
    "proficiencies": (
        "tcr.proficiency-reference-correlation",
        "tcr.reference-adoption-routing",
        "owa.tcr-freshness-integration",
    ),
}
STATICDATA_CATEGORY_DEPENDENCIES: dict[str, tuple[str, ...]] = {
    "houses": COMPONENT_DEPENDENCIES["staticdata"],
    "monsters": ("tcr.content-reference-correlation", "tcr.reference-adoption-routing", "owa.tcr-freshness-integration"),
    "monsterClasses": ("tcr.content-reference-correlation", "tcr.reference-adoption-routing", "owa.tcr-freshness-integration"),
    "bosses": ("tcr.content-reference-correlation", "tcr.reference-adoption-routing", "owa.tcr-freshness-integration"),
    "quests": ("tcr.content-reference-correlation", "tcr.reference-adoption-routing", "owa.tcr-freshness-integration"),
    "achievements": ("tcr.content-reference-correlation", "tcr.reference-adoption-routing", "owa.tcr-freshness-integration"),
}


class DriftError(ValueError):
    """Raised when exact retained evidence cannot be compared safely."""


def _pairs_no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DriftError(f"duplicate JSON object key {key!r}")
        result[key] = value
    return result


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while True:
            chunk = stream.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def _inside(root: Path, path: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def load_json(path: Path, *, root: Path | None = None, max_bytes: int = DEFAULT_MAX_FILE_BYTES) -> tuple[dict[str, Any], str, int]:
    if max_bytes <= 0:
        raise DriftError("max file bytes must be positive")
    absolute = path.expanduser().absolute()
    if not absolute.exists() and not absolute.is_symlink():
        raise DriftError(f"input is missing: {path}")
    if root is not None:
        resolved_root = root.expanduser().resolve(strict=True)
        for parent in (absolute, *absolute.parents):
            if parent == resolved_root:
                break
            if parent.is_symlink():
                raise DriftError(f"input must not traverse a symlink: {path}")
        resolved = absolute.resolve(strict=True)
        if not _inside(resolved_root, resolved):
            raise DriftError(f"input escapes root: {path}")
    else:
        for parent in (absolute, *absolute.parents):
            if parent.is_symlink():
                raise DriftError(f"input must not traverse a symlink: {path}")
        resolved = absolute.resolve(strict=True)
    before = resolved.stat()
    if not stat.S_ISREG(before.st_mode):
        raise DriftError(f"input must be a regular file: {path}")
    if before.st_size > max_bytes:
        raise DriftError(f"input exceeds {max_bytes} bytes: {path}")
    data = resolved.read_bytes()
    after = resolved.stat()
    before_identity = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
    after_identity = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
    if before_identity != after_identity or len(data) != after.st_size:
        raise DriftError(f"input changed while reading: {path}")
    try:
        value = json.loads(data.decode("utf-8"), object_pairs_hook=_pairs_no_duplicates)
    except UnicodeDecodeError as exc:
        raise DriftError(f"input must be UTF-8: {path}") from exc
    except json.JSONDecodeError as exc:
        raise DriftError(f"invalid JSON at line {exc.lineno}, column {exc.colno}: {path}") from exc
    if not isinstance(value, dict):
        raise DriftError(f"input root must be an object: {path}")
    return value, hashlib.sha256(data).hexdigest(), len(data)


def _require_keys(value: Mapping[str, Any], required: Iterable[str], label: str) -> None:
    missing = sorted(set(required) - set(value))
    if missing:
        raise DriftError(f"{label} is missing keys: {', '.join(missing)}")


def _require_sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or not SHA256_RE.fullmatch(value):
        raise DriftError(f"{label} must be an exact lowercase SHA-256")
    return value


def _require_revision(value: Any, label: str) -> str:
    if not isinstance(value, str) or not REVISION_RE.fullmatch(value):
        raise DriftError(f"{label} must be a 40- or 64-character lowercase revision")
    return value


def _require_int(value: Any, label: str, *, minimum: int = 0) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < minimum:
        raise DriftError(f"{label} must be an integer >= {minimum}")
    return value


def _pointer_token(value: object) -> str:
    return str(value).replace("~", "~0").replace("/", "~1")


def _field_changes(before: Any, after: Any, *, max_changes: int) -> list[dict[str, Any]]:
    changes: list[dict[str, Any]] = []

    def add(path: str, left: Any, right: Any, left_exists: bool = True, right_exists: bool = True) -> None:
        if len(changes) >= max_changes:
            raise DriftError(f"field-change count exceeds {max_changes}")
        row: dict[str, Any] = {"path": path or "/"}
        if left_exists:
            row["before"] = left
        if right_exists:
            row["after"] = right
        changes.append(row)

    def walk(path: str, left: Any, right: Any) -> None:
        if type(left) is not type(right):
            add(path, left, right)
            return
        if isinstance(left, dict):
            keys = sorted(set(left) | set(right))
            for key in keys:
                child = f"{path}/{_pointer_token(key)}"
                if key not in left:
                    add(child, None, right[key], left_exists=False)
                elif key not in right:
                    add(child, left[key], None, right_exists=False)
                else:
                    walk(child, left[key], right[key])
            return
        if isinstance(left, list):
            common = min(len(left), len(right))
            for index in range(common):
                walk(f"{path}/{index}", left[index], right[index])
            for index in range(common, len(left)):
                add(f"{path}/{index}", left[index], None, right_exists=False)
            for index in range(common, len(right)):
                add(f"{path}/{index}", None, right[index], left_exists=False)
            return
        if left != right:
            add(path, left, right)

    walk("", before, after)
    return changes


@dataclass(frozen=True)
class SnapshotPaths:
    manifest: Path
    bootstrap_manifest: Path
    staticdata: Path
    staticmapdata: Path
    proficiencies: Path


@dataclass(frozen=True)
class LoadedSnapshot:
    label: str
    manifest: dict[str, Any]
    manifest_sha256: str
    manifest_size: int
    bootstrap: dict[str, Any]
    bootstrap_sha256: str
    bootstrap_size: int
    reports: dict[str, dict[str, Any]]
    report_sha256: dict[str, str]
    report_sizes: dict[str, int]
    report_paths: dict[str, Path]
    manifest_path: Path
    bootstrap_path: Path

    @property
    def reference_id(self) -> str:
        return str(self.manifest["referenceId"])

    @property
    def parser_revision(self) -> str:
        return str(self.manifest["parserRevision"])


class FindingCollector:
    def __init__(self, *, max_findings: int, max_field_changes: int) -> None:
        if max_findings <= 0 or max_field_changes <= 0:
            raise DriftError("finding and field-change bounds must be positive")
        self.max_findings = max_findings
        self.max_field_changes = max_field_changes
        self.rows: list[dict[str, Any]] = []
        self.field_change_count = 0

    def add(
        self,
        *,
        family: str,
        component: str,
        record_key: str,
        change_type: str,
        comparison_state: str,
        dependencies: Sequence[str],
        before: Any | None,
        after: Any | None,
        before_pointer: str | None,
        after_pointer: str | None,
        include_field_changes: bool = True,
    ) -> None:
        if len(self.rows) >= self.max_findings:
            raise DriftError(f"finding count exceeds {self.max_findings}")
        seed = {
            "family": family,
            "component": component,
            "recordKey": record_key,
            "changeType": change_type,
            "beforeSha256": canonical_sha256(before) if before is not None else None,
            "afterSha256": canonical_sha256(after) if after is not None else None,
        }
        row: dict[str, Any] = {
            "id": f"tcr-drift.{canonical_sha256(seed)[:16]}",
            "family": family,
            "component": component,
            "recordKey": record_key,
            "changeType": change_type,
            "comparisonState": comparison_state,
            "dependencies": sorted(set(dependencies)),
            "evidence": {"beforePointer": before_pointer, "afterPointer": after_pointer},
        }
        if before is not None:
            row["beforeSha256"] = canonical_sha256(before)
        if after is not None:
            row["afterSha256"] = canonical_sha256(after)
        if include_field_changes and before is not None and after is not None:
            remaining = self.max_field_changes - self.field_change_count
            if remaining <= 0:
                raise DriftError(f"field-change count exceeds {self.max_field_changes}")
            changes = _field_changes(before, after, max_changes=remaining)
            self.field_change_count += len(changes)
            row["fieldChanges"] = changes
        self.rows.append(row)


def _manifest_input_map(manifest: Mapping[str, Any], label: str) -> dict[str, dict[str, Any]]:
    rows = manifest.get("selectedInputs")
    if not isinstance(rows, list) or not rows:
        raise DriftError(f"{label}.selectedInputs must be a non-empty array")
    result: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise DriftError(f"{label}.selectedInputs[{index}] must be an object")
        _require_keys(row, {"id", "path", "sizeBytes", "sha256"}, f"{label}.selectedInputs[{index}]")
        input_id = row.get("id")
        if not isinstance(input_id, str) or not input_id:
            raise DriftError(f"{label}.selectedInputs[{index}].id must be non-empty")
        if input_id in result:
            raise DriftError(f"{label} contains duplicate selected input {input_id!r}")
        if not isinstance(row.get("path"), str) or not row["path"]:
            raise DriftError(f"{label}.selectedInputs[{index}].path must be non-empty")
        _require_int(row.get("sizeBytes"), f"{label}.selectedInputs[{index}].sizeBytes")
        _require_sha(row.get("sha256"), f"{label}.selectedInputs[{index}].sha256")
        result[input_id] = dict(row)
    return result


def _generated_map(manifest: Mapping[str, Any], label: str) -> dict[str, str]:
    rows = manifest.get("generatedIndexes")
    if not isinstance(rows, list):
        raise DriftError(f"{label}.generatedIndexes must be an array")
    result: dict[str, str] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict) or set(row) != {"id", "sha256"}:
            raise DriftError(f"{label}.generatedIndexes[{index}] must contain only id and sha256")
        key = row.get("id")
        if not isinstance(key, str) or not key:
            raise DriftError(f"{label}.generatedIndexes[{index}].id must be non-empty")
        if key in result:
            raise DriftError(f"{label} contains duplicate generated index {key!r}")
        result[key] = _require_sha(row.get("sha256"), f"{label}.generatedIndexes[{index}].sha256")
    return result


def _validate_manifest(value: Mapping[str, Any], label: str) -> None:
    _require_keys(
        value,
        {
            "format", "schemaVersion", "referenceId", "sourceRole", "clientBuild",
            "parserRevision", "selectedInputs", "generatedIndexes", "policy",
        },
        label,
    )
    if value.get("format") != MANIFEST_FORMAT or value.get("schemaVersion") != MANIFEST_SCHEMA:
        raise DriftError(f"{label} must be {MANIFEST_FORMAT} schema {MANIFEST_SCHEMA}")
    if not isinstance(value.get("referenceId"), str) or not value["referenceId"]:
        raise DriftError(f"{label}.referenceId must be non-empty")
    _require_revision(value.get("parserRevision"), f"{label}.parserRevision")
    build = value.get("clientBuild")
    if not isinstance(build, dict):
        raise DriftError(f"{label}.clientBuild must be an object")
    _require_keys(build, {"evidence", "value", "conflictingValues"}, f"{label}.clientBuild")
    if build.get("evidence") not in {"proven", "declared", "unknown", "conflicting"}:
        raise DriftError(f"{label}.clientBuild.evidence is unsupported")
    policy = value.get("policy")
    if not isinstance(policy, dict) or policy.get("executesSelectedContent") is not False:
        raise DriftError(f"{label} must declare executesSelectedContent=false")
    _manifest_input_map(value, label)
    _generated_map(value, label)


def _validate_report(
    component: str,
    value: Mapping[str, Any],
    *,
    report_sha: str,
    snapshot: Mapping[str, Any],
    bootstrap_sha: str,
    label: str,
) -> None:
    expected_format, schemas, input_id = REPORT_SPECS[component]
    _require_keys(value, {"format", "schemaVersion", "source"}, label)
    if value.get("format") != expected_format:
        raise DriftError(f"{label}.format must be {expected_format}")
    schema = value.get("schemaVersion")
    if schema not in schemas:
        raise DriftError(f"{label}.schemaVersion {schema!r} is unsupported")
    generated = _generated_map(snapshot, f"{label} manifest")
    if generated.get(component) != report_sha:
        raise DriftError(f"{label} hash does not match final manifest generatedIndexes[{component!r}]")
    source = value.get("source")
    if not isinstance(source, dict):
        raise DriftError(f"{label}.source must be an object")
    _require_keys(
        source,
        {"manifestFormat", "manifestSha256", "referenceId", "inputId", "manifestPath", "sizeBytes", "sha256"},
        f"{label}.source",
    )
    if source.get("manifestFormat") != MANIFEST_FORMAT:
        raise DriftError(f"{label}.source.manifestFormat is incompatible")
    if source.get("manifestSha256") != bootstrap_sha:
        raise DriftError(f"{label}.source.manifestSha256 does not bind the bootstrap manifest")
    if source.get("referenceId") != snapshot.get("referenceId"):
        raise DriftError(f"{label}.source.referenceId does not bind the final manifest")
    if source.get("inputId") != input_id:
        raise DriftError(f"{label}.source.inputId must be {input_id!r}")
    inputs = _manifest_input_map(snapshot, f"{label} manifest")
    selected = inputs.get(input_id)
    if selected is None:
        raise DriftError(f"{label} manifest lacks selected input {input_id!r}")
    if source.get("manifestPath") != selected.get("path"):
        raise DriftError(f"{label}.source.manifestPath does not match selected input")
    if source.get("sizeBytes") != selected.get("sizeBytes"):
        raise DriftError(f"{label}.source.sizeBytes does not match selected input")
    if source.get("sha256") != selected.get("sha256"):
        raise DriftError(f"{label}.source.sha256 does not match selected input")


def load_snapshot(
    paths: SnapshotPaths,
    *,
    label: str,
    root: Path | None = None,
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
) -> LoadedSnapshot:
    manifest, manifest_sha, manifest_size = load_json(paths.manifest, root=root, max_bytes=max_file_bytes)
    bootstrap, bootstrap_sha, bootstrap_size = load_json(paths.bootstrap_manifest, root=root, max_bytes=max_file_bytes)
    _validate_manifest(manifest, f"{label} manifest")
    _validate_manifest(bootstrap, f"{label} bootstrap manifest")
    if _manifest_input_map(manifest, f"{label} manifest") != _manifest_input_map(bootstrap, f"{label} bootstrap manifest"):
        raise DriftError(f"{label} final and bootstrap manifests select different inputs")
    for key in ("format", "schemaVersion", "referenceId", "sourceRole", "clientBuild", "parserRevision"):
        if manifest.get(key) != bootstrap.get(key):
            raise DriftError(f"{label} final and bootstrap manifests differ at {key}")

    report_paths = {
        "staticdata": paths.staticdata,
        "staticmapdata": paths.staticmapdata,
        "proficiencies": paths.proficiencies,
    }
    reports: dict[str, dict[str, Any]] = {}
    report_sha: dict[str, str] = {}
    report_sizes: dict[str, int] = {}
    for component, path in report_paths.items():
        value, digest, size = load_json(path, root=root, max_bytes=max_file_bytes)
        _validate_report(
            component,
            value,
            report_sha=digest,
            snapshot=manifest,
            bootstrap_sha=bootstrap_sha,
            label=f"{label} {component} report",
        )
        reports[component] = value
        report_sha[component] = digest
        report_sizes[component] = size
    return LoadedSnapshot(
        label=label,
        manifest=manifest,
        manifest_sha256=manifest_sha,
        manifest_size=manifest_size,
        bootstrap=bootstrap,
        bootstrap_sha256=bootstrap_sha,
        bootstrap_size=bootstrap_size,
        reports=reports,
        report_sha256=report_sha,
        report_sizes=report_sizes,
        report_paths=report_paths,
        manifest_path=paths.manifest,
        bootstrap_path=paths.bootstrap_manifest,
    )


def _report_revision(report: Mapping[str, Any], manifest_revision: str) -> str:
    revision = report.get("parserRevision", manifest_revision)
    return _require_revision(revision, "report parserRevision")


def validate_compatibility(baseline: LoadedSnapshot, current: LoadedSnapshot) -> dict[str, Any]:
    if baseline.reference_id == current.reference_id:
        raise DriftError("baseline and current referenceId must be distinct")
    if baseline.parser_revision != current.parser_revision:
        raise DriftError("manifest parser revisions differ")
    result: dict[str, Any] = {
        "manifestFormat": MANIFEST_FORMAT,
        "manifestSchemaVersion": MANIFEST_SCHEMA,
        "manifestParserRevision": baseline.parser_revision,
        "failClosed": True,
    }
    for component in ("staticdata", "staticmapdata", "proficiencies"):
        before = baseline.reports[component]
        after = current.reports[component]
        if before.get("format") != after.get("format"):
            raise DriftError(f"{component} report formats differ")
        if before.get("schemaVersion") != after.get("schemaVersion"):
            raise DriftError(f"{component} report schema versions differ")
        before_revision = _report_revision(before, baseline.parser_revision)
        after_revision = _report_revision(after, current.parser_revision)
        if before_revision != after_revision or before_revision != baseline.parser_revision:
            raise DriftError(f"{component} parser revision is incompatible")
        prefix = "proficiency" if component == "proficiencies" else component
        result[f"{prefix}Format"] = before["format"]
        result[f"{prefix}SchemaVersion"] = before["schemaVersion"]
    return result


def _compare_map(
    collector: FindingCollector,
    *,
    family: str,
    component: str,
    before: Mapping[str, Any],
    after: Mapping[str, Any],
    before_prefix: str,
    after_prefix: str,
    dependencies: Sequence[str],
) -> None:
    for key in sorted(set(before) | set(after), key=lambda item: str(item)):
        text_key = str(key)
        if key not in before:
            collector.add(
                family=family, component=component, record_key=text_key,
                change_type="added", comparison_state="compared", dependencies=dependencies,
                before=None, after=after[key], before_pointer=None,
                after_pointer=f"{after_prefix}/{_pointer_token(key)}", include_field_changes=False,
            )
        elif key not in after:
            collector.add(
                family=family, component=component, record_key=text_key,
                change_type="removed", comparison_state="compared", dependencies=dependencies,
                before=before[key], after=None,
                before_pointer=f"{before_prefix}/{_pointer_token(key)}", after_pointer=None,
                include_field_changes=False,
            )
        elif canonical_sha256(before[key]) != canonical_sha256(after[key]):
            collector.add(
                family=family, component=component, record_key=text_key,
                change_type="changed", comparison_state="compared", dependencies=dependencies,
                before=before[key], after=after[key],
                before_pointer=f"{before_prefix}/{_pointer_token(key)}",
                after_pointer=f"{after_prefix}/{_pointer_token(key)}",
            )


def _unique_records(rows: Any, id_key: str, label: str) -> dict[str, dict[str, Any]]:
    if not isinstance(rows, list):
        raise DriftError(f"{label} must be an array")
    result: dict[str, dict[str, Any]] = {}
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise DriftError(f"{label}[{index}] must be an object")
        key = row.get(id_key)
        if not isinstance(key, int) or isinstance(key, bool) or key < 0:
            raise DriftError(f"{label}[{index}].{id_key} must be a non-negative integer")
        text = str(key)
        if text in result:
            raise DriftError(f"{label} contains duplicate {id_key} {key}")
        result[text] = row
    return result


def _staticdata_records(report: Mapping[str, Any]) -> dict[str, dict[str, dict[str, Any]]]:
    categories = report.get("categories")
    if not isinstance(categories, dict):
        raise DriftError("staticdata categories must be an object")
    result: dict[str, dict[str, dict[str, Any]]] = {}
    for category, value in sorted(categories.items()):
        if not isinstance(value, dict):
            raise DriftError(f"staticdata category {category!r} must be an object")
        rows = value.get("records")
        if not isinstance(rows, list):
            raise DriftError(f"staticdata category {category!r}.records must be an array")
        indexed: dict[str, dict[str, Any]] = {}
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                raise DriftError(f"staticdata {category}.records[{index}] must be an object")
            candidate = row.get("id")
            if not isinstance(candidate, int) or isinstance(candidate, bool) or candidate < 0:
                raise DriftError(f"staticdata {category}.records[{index}].id must be a non-negative integer")
            key = str(candidate)
            if key in indexed:
                raise DriftError(f"staticdata {category} contains duplicate id {candidate}")
            indexed[key] = row
        result[str(category)] = indexed
    return result


def _snapshot_descriptor(snapshot: LoadedSnapshot) -> dict[str, Any]:
    reports: dict[str, Any] = {}
    for component in ("staticdata", "staticmapdata", "proficiencies"):
        report = snapshot.reports[component]
        reports[component] = {
            "path": str(snapshot.report_paths[component]),
            "sizeBytes": snapshot.report_sizes[component],
            "sha256": snapshot.report_sha256[component],
            "format": report["format"],
            "schemaVersion": report["schemaVersion"],
            "parserRevision": _report_revision(report, snapshot.parser_revision),
            "source": report["source"],
        }
    return {
        "referenceId": snapshot.reference_id,
        "clientBuild": snapshot.manifest["clientBuild"],
        "parserRevision": snapshot.parser_revision,
        "manifest": {
            "path": str(snapshot.manifest_path),
            "sizeBytes": snapshot.manifest_size,
            "sha256": snapshot.manifest_sha256,
            "format": snapshot.manifest["format"],
            "schemaVersion": snapshot.manifest["schemaVersion"],
        },
        "bootstrapManifest": {
            "path": str(snapshot.bootstrap_path),
            "sizeBytes": snapshot.bootstrap_size,
            "sha256": snapshot.bootstrap_sha256,
        },
        "reports": reports,
    }


def generate_drift(
    baseline: LoadedSnapshot,
    current: LoadedSnapshot,
    *,
    parser_revision: str,
    max_findings: int = DEFAULT_MAX_FINDINGS,
    max_field_changes: int = DEFAULT_MAX_FIELD_CHANGES,
) -> dict[str, Any]:
    parser_revision = _require_revision(parser_revision, "drift parser revision")
    if parser_revision != baseline.parser_revision or parser_revision != current.parser_revision:
        raise DriftError("drift parser revision must equal both manifest parser revisions")
    compatibility = validate_compatibility(baseline, current)
    collector = FindingCollector(max_findings=max_findings, max_field_changes=max_field_changes)

    before_inputs = _manifest_input_map(baseline.manifest, "baseline manifest")
    after_inputs = _manifest_input_map(current.manifest, "current manifest")
    for key in sorted(set(before_inputs) | set(after_inputs)):
        deps = COMPONENT_DEPENDENCIES.get(key, ("tcr.package-identity",))
        if key not in before_inputs:
            collector.add(
                family="input-component", component=key, record_key=key,
                change_type="added", comparison_state="compared", dependencies=deps,
                before=None, after=after_inputs[key], before_pointer=None,
                after_pointer=f"/selectedInputs/{_pointer_token(key)}", include_field_changes=False,
            )
        elif key not in after_inputs:
            collector.add(
                family="input-component", component=key, record_key=key,
                change_type="removed", comparison_state="compared", dependencies=deps,
                before=before_inputs[key], after=None,
                before_pointer=f"/selectedInputs/{_pointer_token(key)}", after_pointer=None,
                include_field_changes=False,
            )
        elif canonical_sha256(before_inputs[key]) != canonical_sha256(after_inputs[key]):
            collector.add(
                family="input-component", component=key, record_key=key,
                change_type="changed", comparison_state="compared", dependencies=deps,
                before=before_inputs[key], after=after_inputs[key],
                before_pointer=f"/selectedInputs/{_pointer_token(key)}",
                after_pointer=f"/selectedInputs/{_pointer_token(key)}",
            )

    before_static = baseline.reports["staticdata"]
    after_static = current.reports["staticdata"]
    before_family = before_static["source"].get("schemaFamily")
    after_family = after_static["source"].get("schemaFamily")
    if before_family not in {"legacy", "newer"} or after_family not in {"legacy", "newer"}:
        raise DriftError("staticdata schemaFamily must be legacy or newer")
    if before_family != after_family:
        collector.add(
            family="staticdata.schema-family", component="staticdata", record_key="schemaFamily",
            change_type="changed", comparison_state="schema-family-changed-record-comparison-skipped",
            dependencies=COMPONENT_DEPENDENCIES["staticdata"],
            before={"schemaFamily": before_family}, after={"schemaFamily": after_family},
            before_pointer="/source/schemaFamily", after_pointer="/source/schemaFamily",
        )
    else:
        before_categories = _staticdata_records(before_static)
        after_categories = _staticdata_records(after_static)
        for category in sorted(set(before_categories) | set(after_categories)):
            _compare_map(
                collector,
                family=f"staticdata.{category}",
                component="staticdata",
                before=before_categories.get(category, {}),
                after=after_categories.get(category, {}),
                before_prefix=f"/categories/{_pointer_token(category)}/recordsById",
                after_prefix=f"/categories/{_pointer_token(category)}/recordsById",
                dependencies=STATICDATA_CATEGORY_DEPENDENCIES.get(category, COMPONENT_DEPENDENCIES["staticdata"]),
            )

    _compare_map(
        collector,
        family="staticmapdata.house",
        component="staticmapdata",
        before=_unique_records(baseline.reports["staticmapdata"].get("houses"), "houseId", "baseline staticmapdata houses"),
        after=_unique_records(current.reports["staticmapdata"].get("houses"), "houseId", "current staticmapdata houses"),
        before_prefix="/housesById",
        after_prefix="/housesById",
        dependencies=COMPONENT_DEPENDENCIES["staticmapdata"],
    )
    _compare_map(
        collector,
        family="proficiency.definition",
        component="proficiencies",
        before=_unique_records(baseline.reports["proficiencies"].get("proficiencies"), "proficiencyId", "baseline proficiencies"),
        after=_unique_records(current.reports["proficiencies"].get("proficiencies"), "proficiencyId", "current proficiencies"),
        before_prefix="/proficienciesById",
        after_prefix="/proficienciesById",
        dependencies=COMPONENT_DEPENDENCIES["proficiencies"],
    )

    findings = sorted(
        collector.rows,
        key=lambda row: (row["component"], row["family"], row["recordKey"], row["changeType"], row["id"]),
    )
    changed_components = sorted({row["component"] for row in findings})
    invalidated = sorted({dependency for row in findings for dependency in row["dependencies"]})
    change_counts: dict[str, int] = {}
    family_counts: dict[str, int] = {}
    component_counts: dict[str, int] = {}
    for row in findings:
        change_counts[row["changeType"]] = change_counts.get(row["changeType"], 0) + 1
        family_counts[row["family"]] = family_counts.get(row["family"], 0) + 1
        component_counts[row["component"]] = component_counts.get(row["component"], 0) + 1

    return {
        "format": FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "parserRevision": parser_revision,
        "baseline": _snapshot_descriptor(baseline),
        "current": _snapshot_descriptor(current),
        "compatibility": compatibility,
        "findings": findings,
        "staleness": {
            "basis": "dependency-scoped-component-change",
            "changedComponents": changed_components,
            "invalidatedConsumers": invalidated,
            "usesTimestamps": False,
        },
        "summary": {
            "findingCount": len(findings),
            "fieldChangeCount": collector.field_change_count,
            "changeTypeCounts": dict(sorted(change_counts.items())),
            "familyCounts": dict(sorted(family_counts.items())),
            "componentCounts": dict(sorted(component_counts.items())),
        },
        "policy": {
            "consumesManifestAndIndexesOnly": True,
            "reparsesClientFiles": False,
            "mutatesInputs": False,
            "gameplayConclusions": False,
            "schemaCompatibilityFailsClosed": True,
            "parserRevisionCompatibilityFailsClosed": True,
            "staticdataFamilyChangeSkipsRecordComparison": True,
            "timestampFreshness": False,
            "appearanceDriftOwner": "canary-appearances-index-v1 canonical comparison path",
            "assetDriftOwner": "canary-client-assets-index-v1 canonical comparison path",
            "maxFindings": max_findings,
            "maxFieldChanges": max_field_changes,
        },
    }


def write_json_atomic(path: Path, value: Mapping[str, Any]) -> None:
    path = path.expanduser().absolute()
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    root.add_argument("--baseline-manifest", type=Path, required=True)
    root.add_argument("--baseline-bootstrap-manifest", type=Path, required=True)
    root.add_argument("--baseline-staticdata", type=Path, required=True)
    root.add_argument("--baseline-staticmapdata", type=Path, required=True)
    root.add_argument("--baseline-proficiencies", type=Path, required=True)
    root.add_argument("--current-manifest", type=Path, required=True)
    root.add_argument("--current-bootstrap-manifest", type=Path, required=True)
    root.add_argument("--current-staticdata", type=Path, required=True)
    root.add_argument("--current-staticmapdata", type=Path, required=True)
    root.add_argument("--current-proficiencies", type=Path, required=True)
    root.add_argument("--parser-revision", required=True)
    root.add_argument("--output", type=Path, required=True)
    root.add_argument("--input-root", type=Path)
    root.add_argument("--max-file-bytes", type=int, default=DEFAULT_MAX_FILE_BYTES)
    root.add_argument("--max-findings", type=int, default=DEFAULT_MAX_FINDINGS)
    root.add_argument("--max-field-changes", type=int, default=DEFAULT_MAX_FIELD_CHANGES)
    return root


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        baseline = load_snapshot(
            SnapshotPaths(
                args.baseline_manifest, args.baseline_bootstrap_manifest,
                args.baseline_staticdata, args.baseline_staticmapdata, args.baseline_proficiencies,
            ),
            label="baseline",
            root=args.input_root,
            max_file_bytes=args.max_file_bytes,
        )
        current = load_snapshot(
            SnapshotPaths(
                args.current_manifest, args.current_bootstrap_manifest,
                args.current_staticdata, args.current_staticmapdata, args.current_proficiencies,
            ),
            label="current",
            root=args.input_root,
            max_file_bytes=args.max_file_bytes,
        )
        result = generate_drift(
            baseline,
            current,
            parser_revision=args.parser_revision,
            max_findings=args.max_findings,
            max_field_changes=args.max_field_changes,
        )
        write_json_atomic(args.output, result)
        print(json.dumps({
            "format": FORMAT,
            "schemaVersion": SCHEMA_VERSION,
            "findingCount": result["summary"]["findingCount"],
            "sha256": file_sha256(args.output),
            "output": str(args.output),
        }, sort_keys=True))
        return 0
    except (DriftError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
