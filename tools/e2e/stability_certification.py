#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping, Sequence

CONTRACT = "canary-universal-e2e-stability-certification-v1"
SCHEMA_VERSION = 1
DEFAULT_MINIMUM_RUNS = 10
STABILITY_STATES = {"not-evaluated", "pass", "fail", "unstable", "blocked"}
RESULT_STATUSES = {"success", "failure", "cancelled", "timeout"}
EXECUTION_TIERS = {
    "pr-required",
    "scheduled",
    "release-certification",
    "on-demand",
    "unknown",
}
PROVENANCE_FIELDS = (
    "server_revision",
    "client_revision",
    "datapack",
    "execution_tier",
)
_COVERAGE_DASHBOARD = None


class StabilityCertificationError(ValueError):
    """Raised when stability evidence or output violates the factual contract."""


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise StabilityCertificationError(f"cannot load required module: {path.name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _coverage_dashboard_module():
    global _COVERAGE_DASHBOARD
    if _COVERAGE_DASHBOARD is None:
        _COVERAGE_DASHBOARD = _load_module(
            "canary_e2e_stability_coverage_dashboard",
            Path(__file__).with_name("coverage_dashboard.py"),
        )
    return _COVERAGE_DASHBOARD


def _parse_timestamp(value: Any, label: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise StabilityCertificationError(
            f"{label} must be a non-empty ISO-8601 timestamp"
        )
    candidate = value.strip()
    if candidate.endswith("Z"):
        candidate = candidate[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise StabilityCertificationError(
            f"{label} must be an ISO-8601 timestamp"
        ) from exc
    if parsed.tzinfo is None:
        raise StabilityCertificationError(f"{label} must include a timezone")
    return parsed.astimezone(timezone.utc)


def _format_timestamp(value: datetime) -> str:
    if not isinstance(value, datetime) or value.tzinfo is None:
        raise StabilityCertificationError("timestamp must be timezone-aware")
    return (
        value.astimezone(timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def _require_non_negative_int(value: Any, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise StabilityCertificationError(f"{label} must be a non-negative integer")
    return value


def _require_positive_int(value: Any, label: str) -> int:
    result = _require_non_negative_int(value, label)
    if result == 0:
        raise StabilityCertificationError(f"{label} must be positive")
    return result


def _safe_text(value: Any, label: str, *, allow_none: bool = False) -> str | None:
    if value is None and allow_none:
        return None
    if not isinstance(value, str) or not value:
        raise StabilityCertificationError(f"{label} must be a non-empty string")
    if "\x00" in value or "\r" in value or "\n" in value:
        raise StabilityCertificationError(f"{label} contains unsafe characters")
    return value


def _first_divergence(value: Any) -> str | None:
    if not isinstance(value, Mapping):
        return None
    identifier = value.get("id")
    phase = value.get("phase")
    if not isinstance(identifier, str) or not identifier:
        return None
    if isinstance(phase, str) and phase:
        return f"{phase}/{identifier}"
    return identifier


def _failure_fields(
    *,
    status: str,
    cleanup: Mapping[str, Any],
    failure: Any,
    first_failed_step: Any,
) -> tuple[str | None, str | None, str | None, str]:
    cleanup_pass = (
        cleanup.get("contract_valid") is True
        and cleanup.get("cleanup_certified") is True
    )
    if status == "success" and cleanup_pass:
        return None, None, None, "clean-pass"
    if status == "success":
        return (
            "cleanup",
            "test-contract",
            "cleanup/cleanup-certification",
            "failed",
        )
    classification = None
    category = None
    if isinstance(failure, Mapping):
        raw_classification = failure.get("classification")
        raw_category = failure.get("category")
        if isinstance(raw_classification, str) and raw_classification:
            classification = raw_classification
        if isinstance(raw_category, str) and raw_category:
            category = raw_category
    if classification is None:
        classification = status if status in {"cancelled", "timeout"} else "unknown"
    if category is None:
        category = status if status in {"cancelled", "timeout"} else "unknown"
    return (
        classification,
        category,
        _first_divergence(first_failed_step) or "unknown",
        "failed",
    )


def _attempt_source(
    source: Mapping[str, Any], *, history_index: int | None
) -> dict[str, Any]:
    result = {"root_id": source["root_id"], "path": source["path"]}
    result["attempt_history_index"] = history_index
    return result


def _normalize_history_attempt(
    raw: Mapping[str, Any],
    *,
    parent: Mapping[str, Any],
    history_index: int,
    is_current: bool,
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    run_id = _safe_text(raw.get("run_id"), f"attempt_history[{history_index}].run_id")
    attempt_number = _require_positive_int(
        raw.get("attempt"), f"attempt_history[{history_index}].attempt"
    )
    status = raw.get("status")
    if status not in RESULT_STATUSES:
        raise StabilityCertificationError(
            f"attempt_history[{history_index}].status is unsupported"
        )

    if is_current:
        if status != parent["status"]:
            raise StabilityCertificationError(
                f"attempt_history[{history_index}].status disagrees with the current envelope"
            )
        started_at = parent["started_at"]
        ended_at = parent["ended_at"]
        duration_ms = parent["duration_ms"]
        cleanup = dict(parent["cleanup"])
        failure = payload.get("failure")
        first_failed_step = payload.get("first_failed_step")
        classification, category, divergence, outcome = _failure_fields(
            status=parent["status"],
            cleanup=cleanup,
            failure=failure,
            first_failed_step=first_failed_step,
        )
        status = parent["status"]
    else:
        started_at = raw.get("started_at")
        ended_at = raw.get("ended_at")
        duration_ms = raw.get("duration_ms")
        _parse_timestamp(started_at, f"attempt_history[{history_index}].started_at")
        _parse_timestamp(ended_at, f"attempt_history[{history_index}].ended_at")
        _require_non_negative_int(
            duration_ms, f"attempt_history[{history_index}].duration_ms"
        )
        cleanup = {
            "status": "unknown",
            "cleanup_certified": False,
            "contract_valid": False,
        }
        classification = raw.get("failure_classification")
        if status == "success":
            classification = "cleanup-unknown"
            category = "unknown"
            divergence = "cleanup/unknown-historical-attempt"
            outcome = "blocked"
        else:
            if not isinstance(classification, str) or not classification:
                classification = status if status in {"cancelled", "timeout"} else "unknown"
            category = (
                status if status in {"cancelled", "timeout"} else "unknown"
            )
            divergence = _first_divergence(raw.get("first_failed_step")) or "unknown"
            outcome = "failed"

    started = _parse_timestamp(started_at, "attempt.started_at")
    ended = _parse_timestamp(ended_at, "attempt.ended_at")
    if started > ended:
        raise StabilityCertificationError(
            f"attempt {run_id}#{attempt_number} starts after it ends"
        )
    if isinstance(duration_ms, bool) or not isinstance(duration_ms, int) or duration_ms < 0:
        raise StabilityCertificationError(
            f"attempt {run_id}#{attempt_number} has invalid duration_ms"
        )
    return {
        "identity": f"{run_id}#{attempt_number}",
        "run_id": run_id,
        "attempt": attempt_number,
        "status": status,
        "outcome": outcome,
        "clean_pass": outcome == "clean-pass",
        "started_at": _format_timestamp(started),
        "ended_at": _format_timestamp(ended),
        "ended_at_epoch": ended.timestamp(),
        "duration_ms": duration_ms,
        "failure_classification": classification,
        "failure_category": category,
        "first_divergence": divergence,
        "cleanup": cleanup,
        "source": _attempt_source(
            parent["source"], history_index=history_index
        ),
    }


def normalize_envelope(
    payload: Mapping[str, Any], *, root_id: str, relative_path: str
) -> dict[str, Any]:
    coverage = _coverage_dashboard_module()
    try:
        normalized = coverage.normalize_result(
            payload, root_id=root_id, relative_path=relative_path
        )
    except Exception as exc:
        raise StabilityCertificationError(f"invalid result envelope: {exc}") from exc

    history = payload.get("attempt_history")
    if not isinstance(history, list) or not history:
        raise StabilityCertificationError(
            "result attempt_history must contain at least one attempt"
        )
    current_candidates = [
        index
        for index, raw in enumerate(history)
        if isinstance(raw, Mapping) and raw.get("run_id") == normalized["run_id"]
    ]
    current_index = current_candidates[-1] if current_candidates else None
    attempts: list[dict[str, Any]] = []
    for index, raw in enumerate(history):
        if not isinstance(raw, Mapping):
            raise StabilityCertificationError(
                f"attempt_history[{index}] must be an object"
            )
        attempts.append(
            _normalize_history_attempt(
                raw,
                parent=normalized,
                history_index=index,
                is_current=index == current_index,
                payload=payload,
            )
        )

    if current_index is None:
        current = {
            "run_id": normalized["run_id"],
            "attempt": 1,
            "status": normalized["status"],
        }
        attempts.append(
            _normalize_history_attempt(
                current,
                parent=normalized,
                history_index=len(history),
                is_current=True,
                payload=payload,
            )
        )

    provenance = {
        "server_revision": normalized["server_revision"],
        "client_revision": normalized["client_revision"],
        "datapack": normalized["datapack"],
        "execution_tier": normalized["execution_tier"],
    }
    missing = [
        key
        for key, value in provenance.items()
        if not isinstance(value, str) or not value or value == "unknown"
    ]
    attempts.sort(
        key=lambda item: (
            item["ended_at_epoch"],
            item["run_id"],
            item["attempt"],
            item["source"]["attempt_history_index"],
        )
    )
    return {
        "scenario": normalized["scenario"],
        "provenance": provenance,
        "missing_provenance": missing,
        "attempts": attempts,
        "warnings": list(normalized["warnings"]),
        "unknowns": list(normalized["unknowns"]),
        "source": dict(normalized["source"]),
    }


def discover_evidence(
    evidence_roots: Sequence[Path],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    coverage = _coverage_dashboard_module()
    try:
        normalized, invalid, roots = coverage.discover_result_evidence(evidence_roots)
    except Exception as exc:
        raise StabilityCertificationError(f"cannot discover result evidence: {exc}") from exc

    root_map = {
        f"evidence-{index}": raw.resolve()
        for index, raw in enumerate(evidence_roots, start=1)
    }
    envelopes: list[dict[str, Any]] = []
    for item in normalized:
        source = item["source"]
        root = root_map[source["root_id"]]
        path = root / source["path"]
        try:
            resolved = path.resolve()
            try:
                resolved.relative_to(root)
            except ValueError as exc:
                raise StabilityCertificationError(
                    "result.json resolves outside the evidence root"
                ) from exc
            payload = json.loads(resolved.read_text(encoding="utf-8"))
            if not isinstance(payload, Mapping):
                raise StabilityCertificationError(
                    "result envelope root must be an object"
                )
            envelopes.append(
                normalize_envelope(
                    payload,
                    root_id=source["root_id"],
                    relative_path=source["path"],
                )
            )
        except OSError as exc:
            reason = exc.strerror or exc.__class__.__name__
            invalid.append(
                {
                    "source": dict(source),
                    "error": f"cannot read result evidence: {reason}",
                }
            )
        except json.JSONDecodeError as exc:
            invalid.append(
                {
                    "source": dict(source),
                    "error": (
                        f"invalid JSON at line {exc.lineno}, "
                        f"column {exc.colno}: {exc.msg}"
                    ),
                }
            )
        except StabilityCertificationError as exc:
            invalid.append(
                {
                    "source": dict(source),
                    "error": str(exc),
                }
            )
    envelopes.sort(
        key=lambda item: (
            item["scenario"],
            item["source"]["root_id"],
            item["source"]["path"],
        )
    )
    invalid.sort(
        key=lambda item: (
            item["source"]["root_id"],
            item["source"]["path"],
            item["error"],
        )
    )
    return envelopes, invalid, roots


def _cell_id(scenario: str, provenance: Mapping[str, Any]) -> str:
    material = json.dumps(
        {"scenario": scenario, **dict(provenance)},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )
    return sha256(material.encode("utf-8")).hexdigest()[:20]


def _percentile(values: Sequence[int], percentile: float) -> int | None:
    if not values:
        return None
    ordered = sorted(values)
    rank = max(1, math.ceil(percentile * len(ordered)))
    return ordered[rank - 1]


def _duration_distribution(attempts: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    values = [int(item["duration_ms"]) for item in attempts]
    if not values:
        return {
            "count": 0,
            "min_ms": None,
            "p50_ms": None,
            "p95_ms": None,
            "max_ms": None,
        }
    return {
        "count": len(values),
        "min_ms": min(values),
        "p50_ms": _percentile(values, 0.50),
        "p95_ms": _percentile(values, 0.95),
        "max_ms": max(values),
    }


def _classification(
    *,
    attempts: Sequence[Mapping[str, Any]],
    minimum_runs: int,
    missing_provenance: Sequence[str],
    duplicate_identities: Sequence[str],
) -> tuple[str, str]:
    if missing_provenance:
        return "blocked", "incomplete-provenance"
    if duplicate_identities:
        return "blocked", "duplicate-attempt-identity"
    if any(item["outcome"] == "blocked" for item in attempts):
        return "blocked", "incomplete-attempt-evidence"
    if len(attempts) < minimum_runs:
        return "not-evaluated", "insufficient-runs"
    clean_passes = sum(item["clean_pass"] is True for item in attempts)
    if clean_passes == len(attempts):
        return "pass", "complete-clean-pass-set"
    if clean_passes == 0:
        return "fail", "all-attempts-failed"
    return "unstable", "mixed-outcomes"


def _distribution(
    attempts: Sequence[Mapping[str, Any]], field: str
) -> dict[str, int]:
    return dict(
        sorted(
            Counter(
                value
                for item in attempts
                if isinstance((value := item.get(field)), str) and value
            ).items()
        )
    )


def _attempt_reference(item: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: item[key]
        for key in (
            "identity",
            "run_id",
            "attempt",
            "status",
            "outcome",
            "clean_pass",
            "started_at",
            "ended_at",
            "duration_ms",
            "failure_classification",
            "failure_category",
            "first_divergence",
            "cleanup",
            "source",
        )
    }


def build_report(
    *,
    envelopes: Sequence[Mapping[str, Any]],
    invalid_evidence: Sequence[Mapping[str, Any]],
    evidence_roots: Sequence[Mapping[str, Any]],
    as_of: datetime,
    minimum_runs: int = DEFAULT_MINIMUM_RUNS,
) -> dict[str, Any]:
    if not isinstance(as_of, datetime) or as_of.tzinfo is None:
        raise StabilityCertificationError("as_of must be timezone-aware")
    as_of = as_of.astimezone(timezone.utc)
    minimum_runs = _require_positive_int(minimum_runs, "minimum_runs")

    grouped: dict[
        tuple[str, str | None, str | None, str | None, str | None],
        list[tuple[Mapping[str, Any], Mapping[str, Any]]],
    ] = defaultdict(list)
    all_identities: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for envelope in envelopes:
        scenario = _safe_text(envelope.get("scenario"), "envelope.scenario")
        provenance = envelope.get("provenance")
        if not isinstance(provenance, Mapping) or set(provenance) != set(
            PROVENANCE_FIELDS
        ):
            raise StabilityCertificationError(
                f"envelope {scenario} has invalid provenance"
            )
        key = (
            scenario,
            provenance.get("server_revision"),
            provenance.get("client_revision"),
            provenance.get("datapack"),
            provenance.get("execution_tier"),
        )
        attempts = envelope.get("attempts")
        if not isinstance(attempts, list) or not attempts:
            raise StabilityCertificationError(
                f"envelope {scenario} has no normalized attempts"
            )
        for attempt in attempts:
            ended = _parse_timestamp(
                attempt.get("ended_at"), f"{scenario} attempt ended_at"
            )
            if ended > as_of:
                raise StabilityCertificationError(
                    f"attempt {attempt.get('identity')} ends after as_of"
                )
            grouped[key].append((envelope, attempt))
            all_identities[(scenario, attempt["identity"])].append(
                {
                    "source": dict(attempt["source"]),
                    "cell_key": key,
                }
            )

    duplicate_records: list[dict[str, Any]] = []
    duplicate_by_cell: dict[
        tuple[str, str | None, str | None, str | None, str | None],
        set[str],
    ] = defaultdict(set)
    for (scenario, identity), occurrences in sorted(all_identities.items()):
        if len(occurrences) <= 1:
            continue
        duplicate_records.append(
            {
                "scenario": scenario,
                "identity": identity,
                "occurrences": sorted(
                    (item["source"] for item in occurrences),
                    key=lambda source: (
                        source["root_id"],
                        source["path"],
                        source["attempt_history_index"],
                    ),
                ),
            }
        )
        for occurrence in occurrences:
            duplicate_by_cell[occurrence["cell_key"]].add(identity)

    certifications: list[dict[str, Any]] = []
    for key in sorted(
        grouped,
        key=lambda value: tuple("" if item is None else str(item) for item in value),
    ):
        scenario, server_revision, client_revision, datapack, execution_tier = key
        pairs = grouped[key]
        attempts = sorted(
            (attempt for _, attempt in pairs),
            key=lambda item: (
                item["ended_at_epoch"],
                item["run_id"],
                item["attempt"],
                item["source"]["root_id"],
                item["source"]["path"],
                item["source"]["attempt_history_index"],
            ),
        )
        provenance = {
            "server_revision": server_revision,
            "client_revision": client_revision,
            "datapack": datapack,
            "execution_tier": execution_tier,
        }
        missing = sorted(
            {
                field
                for envelope, _ in pairs
                for field in envelope.get("missing_provenance", [])
            }
        )
        duplicates = sorted(duplicate_by_cell.get(key, set()))
        state, reason = _classification(
            attempts=attempts,
            minimum_runs=minimum_runs,
            missing_provenance=missing,
            duplicate_identities=duplicates,
        )
        clean_pass_count = sum(item["clean_pass"] is True for item in attempts)
        failed_count = sum(item["outcome"] == "failed" for item in attempts)
        blocked_count = sum(item["outcome"] == "blocked" for item in attempts)
        cleanup_failure_count = sum(
            item["cleanup"].get("contract_valid") is True
            and item["cleanup"].get("cleanup_certified") is False
            for item in attempts
        )
        cleanup_unknown_count = sum(
            item["cleanup"].get("contract_valid") is False for item in attempts
        )
        warnings = sorted(
            {
                warning
                for envelope, _ in pairs
                for warning in envelope.get("warnings", [])
            }
        )
        unknowns = sorted(
            {
                unknown
                for envelope, _ in pairs
                for unknown in envelope.get("unknowns", [])
            }
        )
        if missing:
            unknowns.append(
                "Comparability provenance is incomplete: " + ", ".join(missing)
            )
        if blocked_count:
            unknowns.append(
                "At least one historical successful attempt lacks independent cleanup certification."
            )
        unknowns = sorted(set(unknowns))
        certifications.append(
            {
                "scenario": scenario,
                "cell_id": _cell_id(scenario, provenance),
                "provenance": provenance,
                "state": state,
                "reason": reason,
                "minimum_runs": minimum_runs,
                "run_count": len(attempts),
                "clean_pass_count": clean_pass_count,
                "failed_attempt_count": failed_count,
                "blocked_attempt_count": blocked_count,
                "success_ratio": round(clean_pass_count / len(attempts), 6),
                "cleanup_failure_count": cleanup_failure_count,
                "cleanup_unknown_count": cleanup_unknown_count,
                "failure_class_distribution": _distribution(
                    attempts, "failure_classification"
                ),
                "first_divergence_distribution": _distribution(
                    attempts, "first_divergence"
                ),
                "duration_ms": _duration_distribution(attempts),
                "duplicate_attempt_identities": duplicates,
                "missing_provenance": missing,
                "warnings": warnings,
                "unknowns": unknowns,
                "attempts": [_attempt_reference(item) for item in attempts],
            }
        )

    certifications.sort(key=lambda item: (item["scenario"], item["cell_id"]))
    state_counts = Counter(item["state"] for item in certifications)
    all_attempts = [
        attempt
        for certification in certifications
        for attempt in certification["attempts"]
    ]
    report = {
        "contract": CONTRACT,
        "schema_version": SCHEMA_VERSION,
        "generated_at": _format_timestamp(as_of),
        "policy": {
            "minimum_runs": minimum_runs,
            "comparability_fields": list(PROVENANCE_FIELDS),
            "pass_definition": "every counted attempt has status success and exact cleanup certification pass",
            "mixed_result_state": "unstable",
            "insufficient_result_state": "not-evaluated",
            "incomplete_evidence_state": "blocked",
            "retry_policy": "all-attempts-retained-no-hidden-retry",
        },
        "evidence_boundary": {
            "source": "explicit-local-extracted-artifact-roots",
            "roots": list(evidence_roots),
            "valid_envelope_count": len(envelopes),
            "invalid_result_count": len(invalid_evidence),
            "collection_execution_and_retention": "external-to-this-contract",
        },
        "summary": {
            "scenario_count": len({item["scenario"] for item in certifications}),
            "certification_cell_count": len(certifications),
            "attempt_count": len(all_attempts),
            "clean_pass_count": sum(
                attempt["clean_pass"] is True for attempt in all_attempts
            ),
            "failed_attempt_count": sum(
                attempt["outcome"] == "failed" for attempt in all_attempts
            ),
            "blocked_attempt_count": sum(
                attempt["outcome"] == "blocked" for attempt in all_attempts
            ),
            "cleanup_failure_count": sum(
                item["cleanup_failure_count"] for item in certifications
            ),
            "duplicate_attempt_identity_count": len(duplicate_records),
            "state_counts": dict(sorted(state_counts.items())),
        },
        "certifications": certifications,
        "duplicate_attempt_identities": duplicate_records,
        "invalid_evidence": list(invalid_evidence),
    }
    validate_report(report)
    return report


def _validate_source(value: Any, label: str) -> None:
    if not isinstance(value, Mapping) or set(value) != {
        "root_id",
        "path",
        "attempt_history_index",
    }:
        raise StabilityCertificationError(f"{label} has an invalid field set")
    _safe_text(value.get("root_id"), f"{label}.root_id")
    _safe_text(value.get("path"), f"{label}.path")
    index = value.get("attempt_history_index")
    if index is not None:
        _require_non_negative_int(index, f"{label}.attempt_history_index")


def _validate_cleanup(value: Any, label: str) -> None:
    if not isinstance(value, Mapping) or set(value) != {
        "status",
        "cleanup_certified",
        "contract_valid",
    }:
        raise StabilityCertificationError(f"{label} has an invalid field set")
    if not isinstance(value.get("cleanup_certified"), bool) or not isinstance(
        value.get("contract_valid"), bool
    ):
        raise StabilityCertificationError(f"{label} booleans are invalid")


def validate_report(report: Mapping[str, Any]) -> None:
    expected = {
        "contract",
        "schema_version",
        "generated_at",
        "policy",
        "evidence_boundary",
        "summary",
        "certifications",
        "duplicate_attempt_identities",
        "invalid_evidence",
    }
    if not isinstance(report, Mapping) or set(report) != expected:
        raise StabilityCertificationError(
            "stability certification root has an invalid field set"
        )
    if report.get("contract") != CONTRACT or report.get("schema_version") != SCHEMA_VERSION:
        raise StabilityCertificationError(
            "unsupported stability certification contract or schema"
        )
    _parse_timestamp(report.get("generated_at"), "generated_at")

    policy = report.get("policy")
    policy_keys = {
        "minimum_runs",
        "comparability_fields",
        "pass_definition",
        "mixed_result_state",
        "insufficient_result_state",
        "incomplete_evidence_state",
        "retry_policy",
    }
    if not isinstance(policy, Mapping) or set(policy) != policy_keys:
        raise StabilityCertificationError("policy has an invalid field set")
    minimum_runs = _require_positive_int(policy.get("minimum_runs"), "policy.minimum_runs")
    if policy.get("comparability_fields") != list(PROVENANCE_FIELDS):
        raise StabilityCertificationError("policy comparability fields are invalid")
    if policy.get("mixed_result_state") != "unstable":
        raise StabilityCertificationError("policy mixed-result state is invalid")
    if policy.get("insufficient_result_state") != "not-evaluated":
        raise StabilityCertificationError("policy insufficient-result state is invalid")
    if policy.get("incomplete_evidence_state") != "blocked":
        raise StabilityCertificationError("policy incomplete-evidence state is invalid")
    if policy.get("retry_policy") != "all-attempts-retained-no-hidden-retry":
        raise StabilityCertificationError("policy retry state is invalid")

    boundary = report.get("evidence_boundary")
    boundary_keys = {
        "source",
        "roots",
        "valid_envelope_count",
        "invalid_result_count",
        "collection_execution_and_retention",
    }
    if not isinstance(boundary, Mapping) or set(boundary) != boundary_keys:
        raise StabilityCertificationError("evidence_boundary has an invalid field set")
    if boundary.get("source") != "explicit-local-extracted-artifact-roots":
        raise StabilityCertificationError("evidence_boundary source is invalid")
    if boundary.get("collection_execution_and_retention") != "external-to-this-contract":
        raise StabilityCertificationError("evidence boundary policy is invalid")
    _require_non_negative_int(
        boundary.get("valid_envelope_count"),
        "evidence_boundary.valid_envelope_count",
    )
    _require_non_negative_int(
        boundary.get("invalid_result_count"),
        "evidence_boundary.invalid_result_count",
    )
    roots = boundary.get("roots")
    if not isinstance(roots, list):
        raise StabilityCertificationError("evidence_boundary.roots must be an array")

    certifications = report.get("certifications")
    if not isinstance(certifications, list):
        raise StabilityCertificationError("certifications must be an array")
    sort_keys: list[tuple[str, str]] = []
    attempt_total = 0
    clean_total = 0
    failed_total = 0
    blocked_total = 0
    cleanup_failure_total = 0
    state_counts: Counter[str] = Counter()
    for index, cell in enumerate(certifications):
        label = f"certifications[{index}]"
        cell_keys = {
            "scenario",
            "cell_id",
            "provenance",
            "state",
            "reason",
            "minimum_runs",
            "run_count",
            "clean_pass_count",
            "failed_attempt_count",
            "blocked_attempt_count",
            "success_ratio",
            "cleanup_failure_count",
            "cleanup_unknown_count",
            "failure_class_distribution",
            "first_divergence_distribution",
            "duration_ms",
            "duplicate_attempt_identities",
            "missing_provenance",
            "warnings",
            "unknowns",
            "attempts",
        }
        if not isinstance(cell, Mapping) or set(cell) != cell_keys:
            raise StabilityCertificationError(f"{label} has an invalid field set")
        scenario = _safe_text(cell.get("scenario"), f"{label}.scenario")
        cell_id = _safe_text(cell.get("cell_id"), f"{label}.cell_id")
        sort_keys.append((scenario, cell_id))
        if cell.get("state") not in STABILITY_STATES:
            raise StabilityCertificationError(f"{label}.state is invalid")
        if cell.get("minimum_runs") != minimum_runs:
            raise StabilityCertificationError(f"{label}.minimum_runs disagrees with policy")
        provenance = cell.get("provenance")
        if not isinstance(provenance, Mapping) or set(provenance) != set(
            PROVENANCE_FIELDS
        ):
            raise StabilityCertificationError(f"{label}.provenance is invalid")
        attempts = cell.get("attempts")
        if not isinstance(attempts, list) or not attempts:
            raise StabilityCertificationError(f"{label}.attempts must be non-empty")
        clean_count = 0
        failed_count = 0
        blocked_count = 0
        for attempt_index, attempt in enumerate(attempts):
            attempt_label = f"{label}.attempts[{attempt_index}]"
            attempt_keys = {
                "identity",
                "run_id",
                "attempt",
                "status",
                "outcome",
                "clean_pass",
                "started_at",
                "ended_at",
                "duration_ms",
                "failure_classification",
                "failure_category",
                "first_divergence",
                "cleanup",
                "source",
            }
            if not isinstance(attempt, Mapping) or set(attempt) != attempt_keys:
                raise StabilityCertificationError(
                    f"{attempt_label} has an invalid field set"
                )
            _safe_text(attempt.get("identity"), f"{attempt_label}.identity")
            _safe_text(attempt.get("run_id"), f"{attempt_label}.run_id")
            _require_positive_int(attempt.get("attempt"), f"{attempt_label}.attempt")
            if attempt.get("status") not in RESULT_STATUSES:
                raise StabilityCertificationError(f"{attempt_label}.status is invalid")
            if attempt.get("outcome") not in {"clean-pass", "failed", "blocked"}:
                raise StabilityCertificationError(f"{attempt_label}.outcome is invalid")
            if not isinstance(attempt.get("clean_pass"), bool):
                raise StabilityCertificationError(f"{attempt_label}.clean_pass is invalid")
            if attempt.get("clean_pass") != (
                attempt.get("outcome") == "clean-pass"
            ):
                raise StabilityCertificationError(
                    f"{attempt_label}.clean_pass is inconsistent"
                )
            started = _parse_timestamp(
                attempt.get("started_at"), f"{attempt_label}.started_at"
            )
            ended = _parse_timestamp(
                attempt.get("ended_at"), f"{attempt_label}.ended_at"
            )
            if started > ended:
                raise StabilityCertificationError(
                    f"{attempt_label} timestamps are inconsistent"
                )
            _require_non_negative_int(
                attempt.get("duration_ms"), f"{attempt_label}.duration_ms"
            )
            _validate_cleanup(attempt.get("cleanup"), f"{attempt_label}.cleanup")
            _validate_source(attempt.get("source"), f"{attempt_label}.source")
            clean_count += attempt.get("outcome") == "clean-pass"
            failed_count += attempt.get("outcome") == "failed"
            blocked_count += attempt.get("outcome") == "blocked"
        expected_order = sorted(
            attempts,
            key=lambda item: (
                _parse_timestamp(item["ended_at"], "attempt.ended_at"),
                item["run_id"],
                item["attempt"],
                item["source"]["root_id"],
                item["source"]["path"],
                -1
                if item["source"]["attempt_history_index"] is None
                else item["source"]["attempt_history_index"],
            ),
        )
        if attempts != expected_order:
            raise StabilityCertificationError(f"{label}.attempts must be sorted")
        run_count = _require_positive_int(cell.get("run_count"), f"{label}.run_count")
        if run_count != len(attempts):
            raise StabilityCertificationError(f"{label}.run_count is inconsistent")
        if cell.get("clean_pass_count") != clean_count:
            raise StabilityCertificationError(f"{label}.clean_pass_count is inconsistent")
        if cell.get("failed_attempt_count") != failed_count:
            raise StabilityCertificationError(f"{label}.failed_attempt_count is inconsistent")
        if cell.get("blocked_attempt_count") != blocked_count:
            raise StabilityCertificationError(f"{label}.blocked_attempt_count is inconsistent")
        expected_ratio = round(clean_count / run_count, 6)
        if cell.get("success_ratio") != expected_ratio:
            raise StabilityCertificationError(f"{label}.success_ratio is inconsistent")
        durations = _duration_distribution(attempts)
        if cell.get("duration_ms") != durations:
            raise StabilityCertificationError(f"{label}.duration_ms is inconsistent")
        duplicates = cell.get("duplicate_attempt_identities")
        missing = cell.get("missing_provenance")
        if not isinstance(duplicates, list) or duplicates != sorted(set(duplicates)):
            raise StabilityCertificationError(f"{label} duplicate identities are invalid")
        if not isinstance(missing, list) or missing != sorted(set(missing)):
            raise StabilityCertificationError(f"{label} missing provenance is invalid")
        expected_state, expected_reason = _classification(
            attempts=attempts,
            minimum_runs=minimum_runs,
            missing_provenance=missing,
            duplicate_identities=duplicates,
        )
        if cell.get("state") != expected_state or cell.get("reason") != expected_reason:
            raise StabilityCertificationError(f"{label} classification is inconsistent")
        for field in ("warnings", "unknowns"):
            values = cell.get(field)
            if not isinstance(values, list) or values != sorted(set(values)):
                raise StabilityCertificationError(f"{label}.{field} must be sorted unique")
        for field in (
            "failure_class_distribution",
            "first_divergence_distribution",
        ):
            distribution = cell.get(field)
            if not isinstance(distribution, Mapping):
                raise StabilityCertificationError(f"{label}.{field} is invalid")
            for key, count in distribution.items():
                _safe_text(key, f"{label}.{field} key")
                _require_positive_int(count, f"{label}.{field}.{key}")
        attempt_total += run_count
        clean_total += clean_count
        failed_total += failed_count
        blocked_total += blocked_count
        cleanup_failure_total += _require_non_negative_int(
            cell.get("cleanup_failure_count"), f"{label}.cleanup_failure_count"
        )
        _require_non_negative_int(
            cell.get("cleanup_unknown_count"), f"{label}.cleanup_unknown_count"
        )
        state_counts[cell["state"]] += 1
    if sort_keys != sorted(sort_keys):
        raise StabilityCertificationError(
            "certification cells must be unique and sorted by scenario/cell_id"
        )

    duplicates = report.get("duplicate_attempt_identities")
    if not isinstance(duplicates, list):
        raise StabilityCertificationError(
            "duplicate_attempt_identities must be an array"
        )
    duplicate_keys = [
        (item.get("scenario"), item.get("identity"))
        for item in duplicates
        if isinstance(item, Mapping)
    ]
    if len(duplicate_keys) != len(duplicates) or duplicate_keys != sorted(
        duplicate_keys
    ):
        raise StabilityCertificationError(
            "duplicate attempt records must be sorted"
        )

    invalid = report.get("invalid_evidence")
    if not isinstance(invalid, list):
        raise StabilityCertificationError("invalid_evidence must be an array")

    summary = report.get("summary")
    summary_keys = {
        "scenario_count",
        "certification_cell_count",
        "attempt_count",
        "clean_pass_count",
        "failed_attempt_count",
        "blocked_attempt_count",
        "cleanup_failure_count",
        "duplicate_attempt_identity_count",
        "state_counts",
    }
    if not isinstance(summary, Mapping) or set(summary) != summary_keys:
        raise StabilityCertificationError("summary has an invalid field set")
    expected_summary = {
        "scenario_count": len({item["scenario"] for item in certifications}),
        "certification_cell_count": len(certifications),
        "attempt_count": attempt_total,
        "clean_pass_count": clean_total,
        "failed_attempt_count": failed_total,
        "blocked_attempt_count": blocked_total,
        "cleanup_failure_count": cleanup_failure_total,
        "duplicate_attempt_identity_count": len(duplicates),
        "state_counts": dict(sorted(state_counts.items())),
    }
    if dict(summary) != expected_summary:
        raise StabilityCertificationError("summary is inconsistent")


def serialize_report(report: Mapping[str, Any]) -> str:
    validate_report(report)
    return json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def render_markdown(report: Mapping[str, Any]) -> str:
    validate_report(report)
    summary = report["summary"]
    lines = [
        "# Universal E2E stability certification",
        "",
        f"- Contract: `{CONTRACT}` schema {SCHEMA_VERSION}",
        f"- Generated at: `{report['generated_at']}`",
        f"- Explicit minimum runs: `{report['policy']['minimum_runs']}`",
        f"- Certification cells: `{summary['certification_cell_count']}`",
        f"- Counted attempts: `{summary['attempt_count']}`",
        f"- Invalid result files: `{report['evidence_boundary']['invalid_result_count']}`",
        f"- Duplicate attempt identities: `{summary['duplicate_attempt_identity_count']}`",
        "",
        "A pass requires every counted attempt to have gameplay status `success` and exact cleanup certification `pass`. Mixed evidence is `unstable`; no retry is hidden.",
        "",
        "## Certification cells",
        "",
        "| Scenario | Cell | State | Runs | Clean pass | Failed | Blocked | Ratio | Cleanup failures | p50 / p95 ms |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for cell in report["certifications"]:
        durations = cell["duration_ms"]
        lines.append(
            "| {scenario} | `{cell_id}` | {state} | {runs} | {clean} | {failed} | {blocked} | {ratio:.6f} | {cleanup} | {p50} / {p95} |".format(
                scenario=cell["scenario"],
                cell_id=cell["cell_id"],
                state=cell["state"],
                runs=cell["run_count"],
                clean=cell["clean_pass_count"],
                failed=cell["failed_attempt_count"],
                blocked=cell["blocked_attempt_count"],
                ratio=cell["success_ratio"],
                cleanup=cell["cleanup_failure_count"],
                p50=durations["p50_ms"],
                p95=durations["p95_ms"],
            )
        )
    if not report["certifications"]:
        lines.append("| _none_ | - | not-evaluated | 0 | 0 | 0 | 0 | 0.000000 | 0 | - / - |")

    lines.extend(["", "## Evidence details", ""])
    for cell in report["certifications"]:
        lines.extend(
            [
                f"### {cell['scenario']} / `{cell['cell_id']}`",
                "",
                f"- State: **{cell['state']}** (`{cell['reason']}`)",
                f"- Provenance: server `{cell['provenance']['server_revision']}`, client `{cell['provenance']['client_revision']}`, datapack `{cell['provenance']['datapack']}`, tier `{cell['provenance']['execution_tier']}`",
                f"- Failure classes: `{json.dumps(cell['failure_class_distribution'], sort_keys=True)}`",
                f"- First divergences: `{json.dumps(cell['first_divergence_distribution'], sort_keys=True)}`",
                "",
            ]
        )
        if cell["unknowns"]:
            lines.append("Unknowns:")
            lines.extend(f"- {item}" for item in cell["unknowns"])
            lines.append("")
        lines.append("Attempts:")
        for attempt in cell["attempts"]:
            lines.append(
                f"- `{attempt['identity']}`: {attempt['outcome']}, status={attempt['status']}, cleanup={attempt['cleanup']['status']}, duration_ms={attempt['duration_ms']}, source=`{attempt['source']['root_id']}:{attempt['source']['path']}`"
            )
        lines.append("")

    if report["invalid_evidence"]:
        lines.extend(["## Invalid evidence", ""])
        for item in report["invalid_evidence"]:
            lines.append(
                f"- `{item['source']['root_id']}:{item['source']['path']}`: {item['error']}"
            )
        lines.append("")
    lines.append("No opaque stability score is calculated.")
    return "\n".join(lines).rstrip() + "\n"


def _read_report(path: Path) -> Mapping[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise StabilityCertificationError(f"cannot read report: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise StabilityCertificationError(
            f"invalid report JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc
    if not isinstance(payload, Mapping):
        raise StabilityCertificationError("report root must be an object")
    return payload


def _write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(content, encoding="utf-8")
    temporary.replace(path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build and validate factual Universal E2E stability certification."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser(
        "build", help="Build JSON and optional Markdown from extracted result roots."
    )
    build.add_argument(
        "--evidence-root", type=Path, action="append", required=True
    )
    build.add_argument("--as-of", required=True)
    build.add_argument(
        "--minimum-runs", type=int, default=DEFAULT_MINIMUM_RUNS
    )
    build.add_argument("--output-json", type=Path, required=True)
    build.add_argument("--output-markdown", type=Path)

    validate = subparsers.add_parser("validate", help="Validate an existing report.")
    validate.add_argument("path", type=Path)

    render = subparsers.add_parser(
        "render", help="Render Markdown from an existing valid report."
    )
    render.add_argument("path", type=Path)
    render.add_argument("--output", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "build":
            as_of = _parse_timestamp(args.as_of, "--as-of")
            envelopes, invalid, roots = discover_evidence(args.evidence_root)
            report = build_report(
                envelopes=envelopes,
                invalid_evidence=invalid,
                evidence_roots=roots,
                as_of=as_of,
                minimum_runs=args.minimum_runs,
            )
            _write_text(args.output_json, serialize_report(report))
            if args.output_markdown:
                _write_text(args.output_markdown, render_markdown(report))
        elif args.command == "validate":
            validate_report(_read_report(args.path))
            print(f"Validated {args.path}: {CONTRACT} schema {SCHEMA_VERSION}")
        elif args.command == "render":
            rendered = render_markdown(_read_report(args.path))
            if args.output:
                _write_text(args.output, rendered)
            else:
                print(rendered, end="")
        else:  # pragma: no cover
            raise StabilityCertificationError(
                f"unsupported command: {args.command}"
            )
    except (StabilityCertificationError, OSError) as exc:
        print(f"stability certification error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
