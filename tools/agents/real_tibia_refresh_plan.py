#!/usr/bin/env python3
"""Build a deterministic, read-only Real Tibia evidence refresh/drift plan."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))
from real_tibia_evidence import validate_for_publication
from real_tibia_evidence_lib import (
    COMMIT_RE,
    SHA256_RE,
    MODULE_ID_RE,
    ROOT,
    SOURCE_ID_RE,
    VERSION_AXES,
    VERSION_VALUE_RE,
    Corpus,
    EvidenceError,
    safe_repo_path,
)

PLAN_FORMAT = "canary-real-tibia-refresh-plan-v1"
SCHEMA_VERSION = 1
INDEX_DIAGNOSTICS = frozenset(
    {
        "RTEC-GENERATED-INDEX-MISSING",
        "RTEC-GENERATED-INDEX-DRIFT",
        "RTEC-MODULE-INDEX-MISSING",
        "RTEC-MODULE-INDEX-DRIFT",
    }
)
NONACTIONABLE_STATES = frozenset({"REJECTED", "SUPERSEDED"})
NONACTIONABLE_STATUSES = frozenset({"rejected", "superseded"})
PRIORITY_ORDER = {"critical": 0, "high": 1, "normal": 2}
HIGH_PRIORITY_REASONS = frozenset({"version-delta", "changed-path", "changed-source"})
CRITICAL_FRESHNESS_CODES = frozenset({"explicit-state", "invalidation-window-expired"})
WILDCARD_CHARACTERS = frozenset("*?[]")


class RefreshPlanError(ValueError):
    """Raised when a refresh plan cannot be produced safely."""


def parse_date(value: str) -> dt.date:
    try:
        parsed = dt.date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("date must use YYYY-MM-DD") from exc
    if parsed.isoformat() != value:
        raise argparse.ArgumentTypeError("date must use YYYY-MM-DD")
    return parsed


def canonical_json(value: Any) -> str:
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise RefreshPlanError("refresh plan value is not canonical JSON") from exc


def canonical_sha256(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def _trimmed(value: object, label: str) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise RefreshPlanError(f"{label} must be a non-empty trimmed string")
    return value


def _normalize_unique(values: Iterable[str], label: str) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for raw in values:
        value = _trimmed(raw, label)
        if value in seen:
            raise RefreshPlanError(f"{label} contains duplicate value {value!r}")
        seen.add(value)
        normalized.append(value)
    return sorted(normalized)


def _validate_version_value(axis: str, value: str) -> None:
    if axis in {"canary_commit", "maintained_otclient_commit"}:
        if not COMMIT_RE.fullmatch(value):
            raise RefreshPlanError(
                f"target version {axis} must be an exact lowercase 40-character commit SHA"
            )
        return
    if axis == "map_sha256":
        if not SHA256_RE.fullmatch(value):
            raise RefreshPlanError(
                "target version map_sha256 must be an exact lowercase SHA-256"
            )
        return
    if not VERSION_VALUE_RE.fullmatch(value):
        raise RefreshPlanError(
            f"target version {axis} contains an invalid exact version value"
        )


def parse_target_versions(values: Iterable[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for raw in values:
        item = _trimmed(raw, "--target-version")
        if "=" not in item:
            raise RefreshPlanError(
                "--target-version must use AXIS=VALUE with one canonical version axis"
            )
        axis, value = item.split("=", 1)
        axis = _trimmed(axis, "target version axis")
        value = _trimmed(value, f"target version {axis}")
        if axis not in VERSION_AXES:
            raise RefreshPlanError(f"unknown target version axis {axis!r}")
        if axis in result:
            raise RefreshPlanError(f"duplicate target version axis {axis!r}")
        _validate_version_value(axis, value)
        result[axis] = value
    return {axis: result[axis] for axis in sorted(result)}


def normalize_changed_paths(values: Iterable[str]) -> list[str]:
    paths = _normalize_unique(values, "--changed-path")
    for value in paths:
        if not safe_repo_path(value) or any(character in value for character in WILDCARD_CHARACTERS):
            raise RefreshPlanError(
                f"changed path {value!r} must be a safe exact repository-relative path without wildcards"
            )
    return paths


def normalize_source_ids(values: Iterable[str]) -> list[str]:
    source_ids = _normalize_unique(values, "--changed-source")
    for value in source_ids:
        if not SOURCE_ID_RE.fullmatch(value):
            raise RefreshPlanError(
                f"changed source identifier {value!r} must match {SOURCE_ID_RE.pattern}"
            )
    return source_ids


def normalize_module_ids(values: Iterable[str], modules: frozenset[str]) -> list[str]:
    module_ids = _normalize_unique(values, "--module")
    for value in module_ids:
        if not MODULE_ID_RE.fullmatch(value):
            raise RefreshPlanError(
                f"module identifier {value!r} must match {MODULE_ID_RE.pattern}"
            )
        if value not in modules:
            raise RefreshPlanError(f"unknown canonical module_id {value!r}")
    return module_ids


def _record_paths(value: Mapping[str, Any]) -> list[str]:
    paths: set[str] = set()
    comparison = value.get("current_canary_comparison")
    if isinstance(comparison, Mapping):
        exact_paths = comparison.get("exact_paths")
        if isinstance(exact_paths, list):
            paths.update(item for item in exact_paths if isinstance(item, str))
    sources = value.get("sources")
    if isinstance(sources, list):
        for raw_source in sources:
            if not isinstance(raw_source, Mapping):
                continue
            selected = raw_source.get("selected")
            if isinstance(selected, Mapping):
                files = selected.get("files")
                if isinstance(files, list):
                    paths.update(item for item in files if isinstance(item, str))
            locator = raw_source.get("locator")
            if not isinstance(locator, Mapping):
                continue
            repository = locator.get("repository")
            repository_path = locator.get("repository_path")
            if repository in {None, "blakinio/canary"} and isinstance(repository_path, str):
                paths.add(repository_path)
    return sorted(paths)


def _record_source_ids(value: Mapping[str, Any]) -> list[str]:
    source_ids: set[str] = set()
    sources = value.get("sources")
    if isinstance(sources, list):
        for source in sources:
            if isinstance(source, Mapping) and isinstance(source.get("source_id"), str):
                source_ids.add(source["source_id"])
    return sorted(source_ids)


def _add_exact_axes(target: dict[str, set[str]], axes: object) -> None:
    if not isinstance(axes, Mapping):
        return
    for axis in VERSION_AXES:
        value = axes.get(axis)
        if isinstance(value, str):
            target[axis].add(value)


def _record_exact_versions(value: Mapping[str, Any]) -> dict[str, list[str]]:
    exact: dict[str, set[str]] = {axis: set() for axis in VERSION_AXES}
    comparison = value.get("current_canary_comparison")
    if isinstance(comparison, Mapping):
        _add_exact_axes(exact, comparison.get("baseline"))
    applicability = value.get("applicability")
    if isinstance(applicability, Mapping):
        observed = applicability.get("observed_in")
        if isinstance(observed, list):
            for marker in observed:
                if isinstance(marker, Mapping) and marker.get("mode") == "EXACT":
                    _add_exact_axes(exact, marker.get("exact"))
    return {axis: sorted(values) for axis, values in exact.items() if values}


def _paths_overlap(left: str, right: str) -> bool:
    return left == right or left.startswith(right + "/") or right.startswith(left + "/")


def _reason_sort_key(reason: Mapping[str, Any]) -> tuple[str, str]:
    return str(reason.get("kind")), canonical_json(reason)


def _priority(reasons: Sequence[Mapping[str, Any]]) -> str:
    for reason in reasons:
        if reason.get("kind") == "freshness" and reason.get("code") in CRITICAL_FRESHNESS_CODES:
            return "critical"
    if any(reason.get("kind") in HIGH_PRIORITY_REASONS for reason in reasons):
        return "high"
    return "normal"


def _blocking_validation_errors(result: object) -> list[object]:
    errors = getattr(result, "errors", ())
    return sorted(
        (item for item in errors if getattr(item, "code", None) not in INDEX_DIAGNOSTICS),
        key=lambda item: (
            str(getattr(item, "code", "")),
            str(getattr(item, "path", "")),
            str(getattr(item, "message", "")),
        ),
    )


def build_refresh_plan(
    root: Path,
    *,
    as_of: dt.date,
    target_versions: Iterable[str] = (),
    changed_paths: Iterable[str] = (),
    changed_source_ids: Iterable[str] = (),
    module_ids: Iterable[str] = (),
) -> dict[str, Any]:
    """Return a deterministic refresh plan without mutating the corpus."""
    corpus = Corpus.load(root)
    published, validation = validate_for_publication(corpus, as_of)
    blocking = _blocking_validation_errors(validation)
    if blocking:
        rendered = "; ".join(item.render() for item in blocking)
        raise RefreshPlanError(
            "evidence corpus is invalid for refresh planning: " + rendered
        )

    selectors = {
        "target_versions": parse_target_versions(target_versions),
        "changed_paths": normalize_changed_paths(changed_paths),
        "changed_source_ids": normalize_source_ids(changed_source_ids),
        "module_ids": normalize_module_ids(module_ids, published.modules),
    }

    input_identity = {
        "format": PLAN_FORMAT,
        "schema_version": SCHEMA_VERSION,
        "as_of": as_of.isoformat(),
        "selectors": selectors,
        "canonical_modules": sorted(published.modules),
        "published_evidence": [
            {"path": document.relative_path, "sha256": document.sha256}
            for document in sorted(
                published.evidence_documents, key=lambda item: item.relative_path
            )
        ],
    }
    input_sha256 = canonical_sha256(input_identity)

    stale_by_id = {
        row["evidence_id"]: row
        for row in published.stale_rows(as_of)
        if isinstance(row.get("evidence_id"), str)
    }
    selected: list[dict[str, Any]] = []
    nonactionable = 0

    for document in sorted(
        published.evidence_documents,
        key=lambda item: (
            str(item.value.get("module_id")), str(item.value.get("evidence_id"))
        ),
    ):
        value = document.value
        evidence_id = value.get("evidence_id")
        module_id = value.get("module_id")
        if not isinstance(evidence_id, str) or not isinstance(module_id, str):
            raise RefreshPlanError(
                f"validated evidence record lacks a stable identity: {document.relative_path}"
            )
        if (
            value.get("evidence_state") in NONACTIONABLE_STATES
            or value.get("record_status") in NONACTIONABLE_STATUSES
        ):
            nonactionable += 1
            continue

        record_paths = _record_paths(value)
        source_ids = _record_source_ids(value)
        exact_versions = _record_exact_versions(value)
        reasons: list[dict[str, Any]] = []

        stale = stale_by_id.get(evidence_id)
        if stale is not None:
            freshness = value.get("freshness")
            freshness = freshness if isinstance(freshness, Mapping) else {}
            reasons.append(
                {
                    "kind": "freshness",
                    "code": stale["reason"],
                    "age_days": stale["age_days"],
                    "observed_or_verified_at": freshness.get(
                        "observed_or_verified_at"
                    ),
                    "warning_after_days": freshness.get("warning_after_days"),
                    "invalid_after_days": freshness.get("invalid_after_days"),
                }
            )

        if value.get("authority_dimension") != "historical-version":
            for axis, target_value in selectors["target_versions"].items():
                recorded_values = exact_versions.get(axis, [])
                if recorded_values and target_value not in recorded_values:
                    reasons.append(
                        {
                            "kind": "version-delta",
                            "axis": axis,
                            "recorded_values": recorded_values,
                            "target_value": target_value,
                        }
                    )

        for changed_path in selectors["changed_paths"]:
            matches = [
                record_path
                for record_path in record_paths
                if _paths_overlap(changed_path, record_path)
            ]
            if matches:
                reasons.append(
                    {
                        "kind": "changed-path",
                        "changed_path": changed_path,
                        "matched_paths": sorted(matches),
                    }
                )

        for source_id in selectors["changed_source_ids"]:
            if source_id in source_ids:
                reasons.append({"kind": "changed-source", "source_id": source_id})

        if module_id in selectors["module_ids"]:
            reasons.append({"kind": "module", "module_id": module_id})

        if not reasons:
            continue
        reasons.sort(key=_reason_sort_key)
        freshness = value.get("freshness")
        observed = (
            freshness.get("observed_or_verified_at")
            if isinstance(freshness, Mapping)
            else None
        )
        age_days = (
            (as_of - dt.date.fromisoformat(observed)).days
            if isinstance(observed, str)
            else None
        )
        selected.append(
            {
                "evidence_id": evidence_id,
                "module_id": module_id,
                "authority_dimension": value.get("authority_dimension"),
                "record_status": value.get("record_status"),
                "evidence_state": value.get("evidence_state"),
                "priority": _priority(reasons),
                "record_path": document.relative_path,
                "record_sha256": document.sha256,
                "observed_or_verified_at": observed,
                "age_days": age_days,
                "exact_versions": exact_versions,
                "exact_paths": record_paths,
                "source_ids": source_ids,
                "owner_request_refs": sorted(value.get("owner_request_refs", [])),
                "reasons": reasons,
                "next_action": (
                    "Re-verify this bounded record through the normal RTEC collection "
                    "and review lifecycle; this planner performs no mutation."
                ),
            }
        )

    selected.sort(
        key=lambda row: (
            PRIORITY_ORDER[row["priority"]], row["module_id"], row["evidence_id"]
        )
    )
    priority_counts = Counter(row["priority"] for row in selected)
    reason_counts = Counter(
        reason["kind"] for row in selected for reason in row["reasons"]
    )
    plan: dict[str, Any] = {
        "format": PLAN_FORMAT,
        "schema_version": SCHEMA_VERSION,
        "as_of": as_of.isoformat(),
        "input_sha256": input_sha256,
        "selection": selectors,
        "summary": {
            "corpus_evidence_records": len(corpus.evidence_documents),
            "published_evidence_records": len(published.evidence_documents),
            "prepublication_evidence_records": (
                len(corpus.evidence_documents) - len(published.evidence_documents)
            ),
            "nonactionable_published_records": nonactionable,
            "selected_evidence_records": len(selected),
            "by_priority": {
                priority: priority_counts.get(priority, 0)
                for priority in ("critical", "high", "normal")
            },
            "by_reason": {
                reason: reason_counts[reason] for reason in sorted(reason_counts)
            },
        },
        "items": selected,
        "nonclaims": [
            "This plan does not mutate evidence, dossiers, owner requests or generated indexes.",
            "Selection is a review trigger, not proof of a Canary defect, Real Tibia behavior change or parity drift.",
            "Unknown version baselines are not converted into version-delta findings.",
            "Historical-version records are not selected solely because a newer target version is supplied.",
        ],
    }
    plan["plan_sha256"] = canonical_sha256(plan)
    return plan


def verify_plan_sha256(plan: Mapping[str, Any]) -> bool:
    provided = plan.get("plan_sha256")
    if not isinstance(provided, str):
        return False
    unsigned = dict(plan)
    unsigned.pop("plan_sha256", None)
    return canonical_sha256(unsigned) == provided


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--root", type=Path, default=ROOT)
    result.add_argument("--as-of", type=parse_date, required=True)
    result.add_argument(
        "--target-version",
        action="append",
        default=[],
        metavar="AXIS=VALUE",
        help="exact current target version; repeat for multiple canonical axes",
    )
    result.add_argument(
        "--changed-path",
        action="append",
        default=[],
        metavar="REPO_PATH",
        help="exact changed repository path or directory; repeat as needed",
    )
    result.add_argument(
        "--changed-source",
        action="append",
        default=[],
        metavar="SOURCE_ID",
        help="changed evidence source_id; repeat as needed",
    )
    result.add_argument(
        "--module",
        action="append",
        default=[],
        metavar="MODULE_ID",
        help="explicit canonical module to re-verify; repeat as needed",
    )
    return result


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        plan = build_refresh_plan(
            args.root,
            as_of=args.as_of,
            target_versions=args.target_version,
            changed_paths=args.changed_path,
            changed_source_ids=args.changed_source,
            module_ids=args.module,
        )
    except (RefreshPlanError, EvidenceError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(plan, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
