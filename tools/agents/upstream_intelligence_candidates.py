#!/usr/bin/env python3
"""Candidate normalization, mapping, flags, decisions, and local Git evidence."""
from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from real_tibia_registry_lib import Registry
from upstream_intelligence_common import stable_fingerprint

HIGH_FLAGS = {"security", "crash", "protocol", "database", "breaking"}
URGENT_FLAGS = {"security", "crash"}
FLAG_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("security", re.compile(r"\b(?:security|vulnerab|exploit|cve-|auth bypass|injection)\b", re.I)),
    ("crash", re.compile(r"\b(?:crash|segfault|use[- ]after[- ]free|division by zero|deadlock)\b", re.I)),
    ("protocol", re.compile(r"\b(?:protocol|opcode|packet|client version|game session)\b", re.I)),
    ("database", re.compile(r"\b(?:database|mysql|mariadb|sql|schema|migration|connection pool)\b", re.I)),
    ("performance", re.compile(r"\b(?:performance|perf|optimi[sz]|latency|dispatcher|parallel)\b", re.I)),
    ("breaking", re.compile(r"\b(?:breaking|incompatible|remove support|deprecat)\b", re.I)),
    ("release", re.compile(r"\b(?:release|update 20\d\d|summer update|winter update)\b", re.I)),
    ("client", re.compile(r"\b(?:otclient|client|ui|widget|shader|asset)\b", re.I)),
)


def _candidate_common(
    source: Mapping[str, Any],
    *,
    kind: str,
    external_id: str,
    title: str,
    url: str,
    state: str,
    updated_at: str,
    object_sha: str | None,
    author: str,
    labels: Sequence[str],
) -> dict[str, Any]:
    candidate_id = f"{source['id']}:{kind}:{external_id}"
    revision = (
        object_sha
        if object_sha and re.fullmatch(r"[0-9a-f]{40}", object_sha)
        else stable_fingerprint(
            {
                "candidate_id": candidate_id,
                "title": title,
                "url": url,
                "state": state,
                "updated_at": updated_at,
                "labels": sorted(labels),
            }
        )
    )
    return {
        "candidate_id": candidate_id,
        "source_id": source["id"],
        "source_repository": source["repository"],
        "kind": kind,
        "external_id": external_id,
        "title": title.strip()[:300],
        "url": url,
        "state": state,
        "updated_at": updated_at,
        "candidate_revision": revision,
        "object_sha": object_sha if object_sha and re.fullmatch(r"[0-9a-f]{40}", object_sha) else None,
        "author": author,
        "labels": sorted(set(labels)),
        "paths": [],
        "module_ids": [],
        "mapping_state": "not-applicable",
        "mapped_paths": [],
        "unmapped_paths": [],
        "triage_status": "needs-triage",
        "priority": "normal",
        "automation_flags": [],
        "decision_state": "none",
        "local_reference": {"state": "not-checked", "evidence": []},
    }


def _author(row: Mapping[str, Any], key: str = "user") -> str:
    value = row.get(key)
    return value["login"] if isinstance(value, dict) and isinstance(value.get("login"), str) else "unknown"


def commit_candidate(source: Mapping[str, Any], row: Mapping[str, Any]) -> dict[str, Any]:
    commit = row.get("commit") if isinstance(row.get("commit"), dict) else {}
    message = str(commit.get("message") or "")
    author = _author(row, "author")
    if author == "unknown" and isinstance(commit.get("author"), dict):
        author = str(commit["author"].get("name") or "unknown")
    return _candidate_common(
        source,
        kind="commit",
        external_id=str(row.get("sha") or "unknown"),
        title=message.splitlines()[0] if message else str(row.get("sha") or "commit"),
        url=str(row.get("html_url") or ""),
        state="merged",
        updated_at=str(commit.get("committer", {}).get("date") or commit.get("author", {}).get("date") or ""),
        object_sha=str(row.get("sha") or "") or None,
        author=author,
        labels=[],
    )


def pull_candidate(source: Mapping[str, Any], row: Mapping[str, Any]) -> dict[str, Any]:
    head = row.get("head") if isinstance(row.get("head"), dict) else {}
    state = "merged" if row.get("merged_at") else ("draft" if row.get("draft") else str(row.get("state") or "unknown"))
    labels = [str(item.get("name")) for item in row.get("labels", []) if isinstance(item, dict) and item.get("name")]
    return _candidate_common(
        source,
        kind="pull",
        external_id=str(row.get("number") or "unknown"),
        title=str(row.get("title") or ""),
        url=str(row.get("html_url") or ""),
        state=state,
        updated_at=str(row.get("updated_at") or ""),
        object_sha=str(head.get("sha") or "") or None,
        author=_author(row),
        labels=labels,
    )


def issue_candidate(source: Mapping[str, Any], row: Mapping[str, Any]) -> dict[str, Any] | None:
    if "pull_request" in row:
        return None
    labels = [str(item.get("name")) for item in row.get("labels", []) if isinstance(item, dict) and item.get("name")]
    return _candidate_common(
        source,
        kind="issue",
        external_id=str(row.get("number") or "unknown"),
        title=str(row.get("title") or ""),
        url=str(row.get("html_url") or ""),
        state=str(row.get("state") or "unknown"),
        updated_at=str(row.get("updated_at") or ""),
        object_sha=None,
        author=_author(row),
        labels=labels,
    )


def release_candidate(source: Mapping[str, Any], row: Mapping[str, Any]) -> dict[str, Any]:
    target = str(row.get("target_commitish") or "")
    return _candidate_common(
        source,
        kind="release",
        external_id=str(row.get("id") or row.get("tag_name") or "unknown"),
        title=str(row.get("name") or row.get("tag_name") or ""),
        url=str(row.get("html_url") or ""),
        state="draft" if row.get("draft") else ("prerelease" if row.get("prerelease") else "published"),
        updated_at=str(row.get("published_at") or row.get("created_at") or ""),
        object_sha=target if re.fullmatch(r"[0-9a-f]{40}", target) else None,
        author=_author(row, "author"),
        labels=[],
    )


def map_candidate(candidate: dict[str, Any], registry: Registry) -> None:
    paths = candidate.get("paths", [])
    if not paths:
        candidate["mapping_state"] = "not-applicable"
        return
    mapped: list[dict[str, str]] = []
    unmapped: list[str] = []
    modules: set[str] = set()
    for path in paths:
        matches = registry.matched_modules(path)
        if not matches:
            unmapped.append(path)
        for module_id, bucket, pattern in matches:
            mapped.append({"path": path, "module_id": module_id, "bucket": bucket, "pattern": pattern})
            modules.add(module_id)
    candidate["mapped_paths"] = sorted(
        mapped,
        key=lambda row: (row["path"], row["module_id"], row["bucket"], row["pattern"]),
    )
    candidate["unmapped_paths"] = sorted(set(unmapped))
    candidate["module_ids"] = sorted(modules)
    candidate["mapping_state"] = "partial" if mapped and unmapped else ("mapped" if mapped else "unmapped")


def apply_flags(candidate: dict[str, Any]) -> None:
    haystack = " ".join(
        [
            candidate.get("title", ""),
            " ".join(candidate.get("labels", [])),
            " ".join(candidate.get("paths", [])),
        ]
    )
    flags = {name for name, pattern in FLAG_PATTERNS if pattern.search(haystack)}
    if candidate.get("state") == "draft":
        flags.add("draft")
    candidate["automation_flags"] = sorted(flags)
    candidate["priority"] = "urgent" if flags & URGENT_FLAGS else ("high" if flags & HIGH_FLAGS else "normal")


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=20,
    )


@dataclass(frozen=True)
class LocalHistory:
    commits: frozenset[str]
    text: str


def build_local_history(root: Path) -> LocalHistory:
    """Index only the target checkout's HEAD history.

    Scheduled scans may fetch donor refs for bounded ancestry inspection. Those
    refs must never make a donor candidate look present in the maintained fork.
    """

    commits = _git(root, "rev-list", "HEAD")
    messages = _git(root, "log", "HEAD", "--format=%H%n%B%n")
    if commits.returncode != 0 or messages.returncode != 0:
        return LocalHistory(frozenset(), "")
    return LocalHistory(
        frozenset(line for line in commits.stdout.splitlines() if line),
        messages.stdout,
    )


def local_reference(
    candidate: Mapping[str, Any],
    root: Path,
    history: LocalHistory | None = None,
) -> dict[str, Any]:
    indexed = history or build_local_history(root)
    object_sha = candidate.get("object_sha")
    if isinstance(object_sha, str) and object_sha in indexed.commits:
        if _git(root, "merge-base", "--is-ancestor", object_sha, "HEAD").returncode == 0:
            return {"state": "exact-ancestor", "evidence": [f"{object_sha} is an ancestor of local HEAD"]}
    evidence = [
        f"local HEAD history references {probe}"
        for probe in (
            str(candidate.get("candidate_revision") or ""),
            str(candidate.get("url") or ""),
        )
        if probe and probe in indexed.text
    ]
    return {"state": "reference-found" if evidence else "not-found", "evidence": evidence}


def apply_decision(
    candidate: dict[str, Any],
    decisions: Mapping[str, Mapping[str, Any]],
) -> None:
    decision = decisions.get(candidate["candidate_id"])
    if not decision:
        return
    if decision.get("candidate_revision") != candidate["candidate_revision"]:
        candidate["decision_state"] = "stale"
        candidate["triage_status"] = "stale-decision"
        return
    candidate["decision_state"] = "current"
    candidate["triage_status"] = str(decision["status"])
    candidate["reviewed_decision"] = {
        "status": decision["status"],
        "reason": decision["reason"],
        "decided_at": decision["decided_at"],
        "decided_by": decision["decided_by"],
        "local_sha": decision.get("local_sha"),
    }
    candidate["module_ids"] = sorted(
        set(candidate.get("module_ids", [])) | set(decision.get("modules", []))
    )
