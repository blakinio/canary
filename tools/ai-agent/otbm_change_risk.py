from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

POLICY_FORMAT = "canary-otbm-change-risk-policy-v1"
INPUT_FORMAT = "canary-otbm-change-risk-input-v1"
REPORT_FORMAT = "canary-otbm-change-risk-v1"
SCHEMA_VERSION = 1
FACTORS = (
    "critical-infrastructure",
    "identifier-semantics",
    "quest-dependency",
    "fragile-route",
    "certification-invalidated",
    "multi-region",
    "unresolved-evidence",
    "asset-walkability",
)
LEVELS = ("low", "medium", "high", "critical")


class ChangeRiskError(RuntimeError):
    pass


def _sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(ch not in "0123456789abcdef" for ch in value.lower()):
        raise ChangeRiskError(f"{label} must be a SHA-256 hex string")
    return value.lower()


def _hash(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _read_json(path: Path, expected: str) -> dict[str, Any]:
    source = path.expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    try:
        value = json.loads(source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ChangeRiskError(f"Cannot read JSON {source}: {exc}") from exc
    if not isinstance(value, dict) or value.get("format") != expected:
        raise ChangeRiskError(f"Unsupported {expected} document: {source}")
    return value


def normalize_policy(document: dict[str, Any]) -> dict[str, Any]:
    if document.get("format") != POLICY_FORMAT:
        raise ChangeRiskError(f"policy.format must be {POLICY_FORMAT}")
    raw_weights = document.get("weights")
    raw_thresholds = document.get("thresholds")
    if not isinstance(raw_weights, dict) or set(raw_weights) != set(FACTORS):
        raise ChangeRiskError(f"weights must contain exactly: {', '.join(FACTORS)}")
    weights: dict[str, int] = {}
    for factor in FACTORS:
        value = raw_weights[factor]
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ChangeRiskError(f"weight {factor} must be an integer >= 0")
        weights[factor] = value
    if not isinstance(raw_thresholds, dict) or set(raw_thresholds) != set(LEVELS):
        raise ChangeRiskError("thresholds must contain low, medium, high and critical")
    thresholds: dict[str, int] = {}
    previous = -1
    for level in LEVELS:
        value = raw_thresholds[level]
        if not isinstance(value, int) or isinstance(value, bool) or value < 0 or value <= previous:
            raise ChangeRiskError("risk thresholds must be strictly increasing non-negative integers")
        thresholds[level] = value
        previous = value
    if thresholds["low"] != 0:
        raise ChangeRiskError("low threshold must be 0")
    return {"format": POLICY_FORMAT, "schemaVersion": SCHEMA_VERSION, "weights": weights, "thresholds": thresholds}


def normalize_input(document: dict[str, Any]) -> dict[str, Any]:
    if document.get("format") != INPUT_FORMAT:
        raise ChangeRiskError(f"input.format must be {INPUT_FORMAT}")
    before = _sha(document.get("beforeMapSha256"), "beforeMapSha256")
    after = _sha(document.get("afterMapSha256"), "afterMapSha256")
    if before == after:
        raise ChangeRiskError("beforeMapSha256 and afterMapSha256 must differ for a change-risk input")
    raw_factors = document.get("factors")
    if not isinstance(raw_factors, list):
        raise ChangeRiskError("factors must be an array")
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, entry in enumerate(raw_factors):
        if not isinstance(entry, dict):
            raise ChangeRiskError(f"factors[{index}] must be an object")
        factor = entry.get("factor")
        status = entry.get("status")
        if factor not in FACTORS or factor in seen:
            raise ChangeRiskError(f"factors[{index}].factor is unsupported or duplicated: {factor!r}")
        if status not in {"present", "unresolved", "absent"}:
            raise ChangeRiskError(f"factors[{index}].status is unsupported: {status!r}")
        evidence = entry.get("evidence", [])
        if not isinstance(evidence, list):
            raise ChangeRiskError(f"factors[{index}].evidence must be an array")
        refs: list[dict[str, Any]] = []
        for ref_index, ref in enumerate(evidence):
            if not isinstance(ref, dict) or not isinstance(ref.get("sourceFormat"), str):
                raise ChangeRiskError(f"factors[{index}].evidence[{ref_index}] must include sourceFormat")
            finding_ids = ref.get("findingIds", [])
            if not isinstance(finding_ids, list) or any(not isinstance(value, str) for value in finding_ids):
                raise ChangeRiskError(f"factors[{index}].evidence[{ref_index}].findingIds must be strings")
            refs.append({"sourceFormat": ref["sourceFormat"], "sha256": _sha(ref.get("sha256"), f"factors[{index}].evidence[{ref_index}].sha256"), "findingIds": sorted(set(finding_ids))})
        if status in {"present", "unresolved"} and not refs:
            raise ChangeRiskError(f"factor {factor} with status {status} requires exact evidence")
        seen.add(factor)
        normalized.append({"factor": factor, "status": status, "evidence": refs})
    for factor in FACTORS:
        if factor not in seen:
            normalized.append({"factor": factor, "status": "absent", "evidence": []})
    normalized.sort(key=lambda value: FACTORS.index(value["factor"]))
    return {"format": INPUT_FORMAT, "schemaVersion": SCHEMA_VERSION, "beforeMapSha256": before, "afterMapSha256": after, "factors": normalized}


def _level(score: int, thresholds: dict[str, int]) -> str:
    result = "low"
    for level in LEVELS:
        if score >= thresholds[level]:
            result = level
    return result


def build_change_risk_report(policy: dict[str, Any], risk_input: dict[str, Any]) -> dict[str, Any]:
    policy = normalize_policy(policy)
    risk_input = normalize_input(risk_input)
    contributions: list[dict[str, Any]] = []
    score = 0
    unresolved: list[str] = []
    for entry in risk_input["factors"]:
        factor = entry["factor"]
        weight = policy["weights"][factor]
        contributes = entry["status"] in {"present", "unresolved"}
        contribution = weight if contributes else 0
        score += contribution
        if entry["status"] == "unresolved":
            unresolved.append(factor)
        contributions.append({"factor": factor, "status": entry["status"], "weight": weight, "contribution": contribution, "evidence": entry["evidence"]})
    report: dict[str, Any] = {
        "format": REPORT_FORMAT,
        "schemaVersion": SCHEMA_VERSION,
        "beforeMapSha256": risk_input["beforeMapSha256"],
        "afterMapSha256": risk_input["afterMapSha256"],
        "score": score,
        "riskLevel": _level(score, policy["thresholds"]),
        "thresholds": policy["thresholds"],
        "contributions": contributions,
        "unresolvedFactors": unresolved,
        "policy": {
            "transparentVersionedWeights": True,
            "opaqueAiScore": False,
            "authorizesValidationSkip": False,
            "authorizesRepair": False,
            "authorizesMerge": False,
            "gameplayRegressionProven": False,
        },
    }
    report["reportSha256"] = _hash(report)
    return report


def load_policy(path: Path) -> dict[str, Any]:
    return normalize_policy(_read_json(path, POLICY_FORMAT))


def load_input(path: Path) -> dict[str, Any]:
    return normalize_input(_read_json(path, INPUT_FORMAT))
