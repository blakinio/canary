#!/usr/bin/env python3
"""Bounded source collection and snapshot validation."""
from __future__ import annotations

import datetime as dt
import urllib.parse
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from real_tibia_registry_lib import Registry, load_json, schema_errors
from upstream_intelligence_candidates import (
    apply_decision, apply_flags, build_local_history, commit_candidate, issue_candidate,
    local_reference, map_candidate, pull_candidate, release_candidate,
)
from upstream_intelligence_common import (
    ROOT, SCHEMA_DIR, SOURCE_CONFIG, GitHubClient, UpstreamError, ValidationResult,
    iso_z, load_decisions, parse_time, utc_now, validate_repository,
)


def _within_window(candidate: Mapping[str, Any], window_start: dt.datetime) -> bool:
    parsed = parse_time(candidate.get("updated_at"))
    return parsed is not None and parsed >= window_start


def collect_source(client: GitHubClient, source: Mapping[str, Any], *, window_start: dt.datetime,
                   mode: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    owner, name = str(source["repository"]).split("/", 1)
    prefix = f"/repos/{owner}/{name}"
    repo = client.get(prefix)
    if not isinstance(repo, dict):
        raise UpstreamError(f"{source['repository']}: repository response is not an object")
    default_branch = str(repo.get("default_branch") or source["default_branch"])
    branch = client.get(f"{prefix}/branches/{urllib.parse.quote(default_branch, safe='')}")
    if not isinstance(branch, dict):
        raise UpstreamError(f"{source['repository']}: branch response is not an object")
    commit = branch.get("commit") if isinstance(branch.get("commit"), dict) else {}
    observed_head = str(commit.get("sha") or "")
    initial = str(source["initial_baseline"]["sha"])
    summary = {
        "source_id": source["id"], "repository": source["repository"], "role": source["role"],
        "default_branch": default_branch, "initial_baseline_sha": initial,
        "observed_head_sha": observed_head or None,
        "head_state": "unchanged" if observed_head == initial else "different",
        "pushed_at": repo.get("pushed_at"), "candidate_count": 0, "error": None,
    }
    max_items, max_pages = int(source["max_items_per_kind"]), int(source["max_pages"])
    candidates: list[dict[str, Any]] = []
    since, kinds = iso_z(window_start), set(source["kinds"])
    if "commits" in kinds:
        candidates.extend(commit_candidate(source, row) for row in client.paged(
            f"{prefix}/commits", {"sha": default_branch, "since": since},
            max_pages=max_pages, max_items=max_items))
    if "pulls" in kinds:
        candidates.extend(pull_candidate(source, row) for row in client.paged(
            f"{prefix}/pulls", {"state": "all", "sort": "updated", "direction": "desc"},
            max_pages=max_pages, max_items=max_items))
    if "issues" in kinds:
        for row in client.paged(f"{prefix}/issues", {
            "state": "all", "sort": "updated", "direction": "desc", "since": since,
        }, max_pages=max_pages, max_items=max_items):
            candidate = issue_candidate(source, row)
            if candidate:
                candidates.append(candidate)
    if "releases" in kinds:
        candidates.extend(release_candidate(source, row) for row in client.paged(
            f"{prefix}/releases", {}, max_pages=max_pages, max_items=max_items))
    candidates = [row for row in candidates if _within_window(row, window_start)]
    candidates.sort(key=lambda row: (str(row["updated_at"]), str(row["candidate_id"])), reverse=True)
    detail_limit = int(source["deep_file_details"] if mode == "deep" else source["daily_file_details"])
    detailed = 0
    for candidate in candidates:
        if candidate["kind"] != "pull" or detailed >= detail_limit:
            continue
        files = client.paged(f"{prefix}/pulls/{candidate['external_id']}/files", {},
                             max_pages=max_pages, max_items=300)
        candidate["paths"] = sorted({str(row.get("filename")) for row in files if row.get("filename")})
        detailed += 1
    summary["candidate_count"] = len(candidates)
    return summary, candidates


def summarise(sources: Sequence[Mapping[str, Any]], candidates: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "source_count": len(sources), "candidate_count": len(candidates),
        "by_status": dict(sorted(Counter(str(row["triage_status"]) for row in candidates).items())),
        "by_kind": dict(sorted(Counter(str(row["kind"]) for row in candidates).items())),
        "by_priority": dict(sorted(Counter(str(row["priority"]) for row in candidates).items())),
        "by_module": dict(sorted(Counter(module for row in candidates for module in row.get("module_ids", [])).items())),
        "by_local_reference": dict(sorted(Counter(str(row["local_reference"]["state"]) for row in candidates).items())),
        "unmapped_candidates": sum(row.get("mapping_state") == "unmapped" for row in candidates),
        "source_errors": sum(bool(row.get("error")) for row in sources),
    }


def scan(*, root: Path = ROOT, token: str | None, days: int, mode: str,
         now: dt.datetime | None = None, client: GitHubClient | None = None) -> dict[str, Any]:
    if mode not in {"daily", "deep"}:
        raise UpstreamError("mode must be daily or deep")
    if not 1 <= days <= 180:
        raise UpstreamError("days must be between 1 and 180")
    validation = validate_repository(root)
    if not validation.ok:
        raise UpstreamError("repository validation failed: " + "; ".join(validation.errors))
    config, registry = load_json(root / SOURCE_CONFIG), Registry.load(root)
    decisions, errors, _ = load_decisions(root, set(registry.modules))
    if errors:
        raise UpstreamError("decision validation failed: " + "; ".join(errors))
    current = (now or utc_now()).astimezone(dt.timezone.utc).replace(microsecond=0)
    window_start, api = current - dt.timedelta(days=days), client or GitHubClient(token)
    source_rows: list[dict[str, Any]] = []
    candidates: list[dict[str, Any]] = []
    configured_sources = {
        str(source["id"]): source
        for source in config["sources"]
        if isinstance(source, dict) and isinstance(source.get("id"), str)
    }
    for source in config["sources"]:
        try:
            summary, rows = collect_source(api, source, window_start=window_start, mode=mode)
        except UpstreamError as exc:
            summary = {
                "source_id": source.get("id"), "repository": source.get("repository"),
                "role": source.get("role"), "default_branch": source.get("default_branch"),
                "initial_baseline_sha": source.get("initial_baseline", {}).get("sha"),
                "observed_head_sha": None, "head_state": "unknown", "pushed_at": None,
                "candidate_count": 0, "error": str(exc)[:1000],
            }
            rows = []
        source_rows.append(summary)
        candidates.extend(rows)
    if source_rows and all(row["error"] for row in source_rows):
        raise UpstreamError("all watched sources failed; refusing to publish an empty report")
    candidates = list({row["candidate_id"]: row for row in candidates}.values())
    history = build_local_history(root)
    for candidate in candidates:
        source = configured_sources.get(str(candidate.get("source_id") or ""))
        map_candidate(candidate, registry, source)
        apply_flags(candidate)
        candidate["local_reference"] = local_reference(candidate, root, history)
        apply_decision(candidate, decisions)
    rank = {"urgent": 0, "high": 1, "normal": 2}
    candidates.sort(key=lambda row: (rank[row["priority"]], row["triage_status"] != "needs-triage",
                                     str(row["source_id"]), str(row["kind"]), str(row["candidate_id"])))
    return {
        "schema_version": 1, "generated_at": iso_z(current), "mode": mode, "window_days": days,
        "window_start": iso_z(window_start), "report_repository": config["report"]["repository"],
        "sources": source_rows, "candidates": candidates, "summary": summarise(source_rows, candidates),
    }


def validate_snapshot(snapshot: Any, root: Path = ROOT) -> ValidationResult:
    errors: list[str] = []
    errors.extend(schema_errors(Path("snapshot.json"), snapshot, root / SCHEMA_DIR / "snapshot.schema.json"))
    if not isinstance(snapshot, dict):
        return ValidationResult(tuple(errors + ["snapshot: expected object"]), ())
    candidates = snapshot.get("candidates")
    if not isinstance(candidates, list):
        return ValidationResult(tuple(sorted(set(errors + ["snapshot.candidates must be an array"]))), ())
    seen: set[str] = set()
    for index, candidate in enumerate(candidates):
        errors.extend(schema_errors(Path(f"snapshot.candidates[{index}]"), candidate,
                                    root / SCHEMA_DIR / "candidate.schema.json"))
        if isinstance(candidate, dict):
            candidate_id = candidate.get("candidate_id")
            if candidate_id in seen:
                errors.append(f"snapshot: duplicate candidate_id {candidate_id}")
            if isinstance(candidate_id, str):
                seen.add(candidate_id)
    if snapshot.get("summary") != summarise(snapshot.get("sources", []), candidates):
        errors.append("snapshot.summary does not match candidates and sources")
    return ValidationResult(tuple(sorted(set(errors))), ())
