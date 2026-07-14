#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from real_tibia_registry_lib import Registry
from upstream_intelligence_lib import (
    UpstreamError,
    apply_decision,
    apply_flags,
    issue_candidate,
    local_reference,
    map_candidate,
    render_issue_body,
    scan,
    stable_fingerprint,
    validate_repository,
    validate_snapshot,
)

NOW = dt.datetime(2026, 7, 14, 12, 0, tzinfo=dt.timezone.utc)


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def source_row(source_id: str = "opentibiabr-canary", repository: str = "opentibiabr/canary") -> dict:
    return {
        "id": source_id,
        "name": source_id,
        "repository": repository,
        "role": "upstream-server",
        "writable": False,
        "default_branch": "main",
        "kinds": ["commits", "pulls", "issues", "releases"],
        "max_items_per_kind": 20,
        "max_pages": 2,
        "daily_file_details": 5,
        "deep_file_details": 10,
        "initial_baseline": {
            "sha": "a" * 40,
            "observed_at": "2026-07-14T10:00:00Z",
        },
    }


def make_root(base: Path, sources: list[dict] | None = None) -> Path:
    root = base / "repo"
    config = {
        "schema_version": 1,
        "report": {
            "repository": "blakinio/canary",
            "issue_title": "[Upstream Intelligence] Current drift report",
            "max_issue_body_chars": 60000,
            "max_report_rows": 100,
        },
        "sources": sources or [source_row()],
    }
    write_json(root / "docs/agents/upstream/registry/sources.yaml", config)
    for name in ("source", "candidate", "decision", "snapshot"):
        write_json(root / f"docs/agents/upstream/schemas/{name}.schema.json", {})
    (root / "docs/agents/upstream/registry/decisions").mkdir(parents=True, exist_ok=True)

    write_json(
        root / "docs/agents/real-tibia/registry/categories.yaml",
        {"categories": [{"id": "platform-tooling"}]},
    )
    write_json(
        root / "docs/agents/real-tibia/registry/sources.yaml",
        {"sources": [{"id": "canary-current"}]},
    )
    write_json(
        root / "docs/agents/real-tibia/registry/versions.yaml",
        {"baselines": [{"id": "test"}]},
    )
    write_json(
        root / "docs/agents/real-tibia/registry/modules/upstream-intelligence.yaml",
        {
            "module_id": "upstream-intelligence",
            "paths": {
                "server": ["src/**"],
                "client": ["modules/**"],
                "data": ["data/**"],
                "tests": ["tests/**"],
                "docs": ["docs/**"],
            },
        },
    )
    return root


class FakeClient:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.calls: list[str] = []

    def get(self, path: str, params: dict | None = None):
        self.calls.append(path)
        if self.fail:
            raise UpstreamError("synthetic source failure")
        if path == "/repos/opentibiabr/canary":
            return {"default_branch": "main", "pushed_at": "2026-07-14T11:59:00Z"}
        if path == "/repos/opentibiabr/canary/branches/main":
            return {"commit": {"sha": "b" * 40}}
        raise AssertionError(f"unexpected get {path}")

    def paged(self, path: str, params: dict, *, max_pages: int, max_items: int):
        del params, max_pages, max_items
        self.calls.append(path)
        prefix = "/repos/opentibiabr/canary"
        if path == f"{prefix}/commits":
            return [
                {
                    "sha": "c" * 40,
                    "html_url": "https://github.com/opentibiabr/canary/commit/" + "c" * 40,
                    "commit": {
                        "message": "fix(protocol): repair packet bounds",
                        "committer": {"date": "2026-07-14T11:00:00Z"},
                    },
                    "author": {"login": "alice"},
                }
            ]
        if path == f"{prefix}/pulls":
            return [
                {
                    "number": 9,
                    "title": "fix: prevent database crash",
                    "html_url": "https://github.com/opentibiabr/canary/pull/9",
                    "state": "open",
                    "draft": False,
                    "updated_at": "2026-07-14T11:30:00Z",
                    "head": {"sha": "d" * 40},
                    "user": {"login": "bob"},
                    "labels": [{"name": "bug"}],
                }
            ]
        if path == f"{prefix}/issues":
            return [
                {
                    "number": 10,
                    "title": "protocol issue",
                    "html_url": "https://github.com/opentibiabr/canary/issues/10",
                    "state": "open",
                    "updated_at": "2026-07-14T10:30:00Z",
                    "user": {"login": "carol"},
                    "labels": [],
                },
                {
                    "number": 9,
                    "title": "duplicate PR object",
                    "pull_request": {},
                    "updated_at": "2026-07-14T11:30:00Z",
                },
            ]
        if path == f"{prefix}/releases":
            return [
                {
                    "id": 4,
                    "tag_name": "v1",
                    "name": "Release v1",
                    "html_url": "https://github.com/opentibiabr/canary/releases/tag/v1",
                    "published_at": "2026-07-14T09:00:00Z",
                    "draft": False,
                    "prerelease": False,
                    "author": {"login": "dora"},
                }
            ]
        if path == f"{prefix}/pulls/9/files":
            return [{"filename": "src/server/network/protocol/protocolgame.cpp"}, {"filename": "unknown/file.txt"}]
        raise AssertionError(f"unexpected paged {path}")


class UpstreamIntelligenceTests(unittest.TestCase):
    def test_stable_fingerprint_ignores_mapping_order(self) -> None:
        self.assertEqual(stable_fingerprint({"a": 1, "b": 2}), stable_fingerprint({"b": 2, "a": 1}))

    def test_issue_candidate_excludes_pull_objects(self) -> None:
        source = source_row()
        self.assertIsNone(issue_candidate(source, {"number": 1, "pull_request": {}}))

    def test_path_mapping_keeps_partial_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(Path(tmp))
            registry = Registry.load(root)
            candidate = {"paths": ["src/game.cpp", "unknown/file"], "module_ids": [], "mapped_paths": [], "unmapped_paths": []}
            map_candidate(candidate, registry)
            self.assertEqual(candidate["mapping_state"], "partial")
            self.assertEqual(candidate["module_ids"], ["upstream-intelligence"])
            self.assertEqual(candidate["unmapped_paths"], ["unknown/file"])

    def test_flags_raise_security_and_crash_priority(self) -> None:
        candidate = {"title": "security crash fix", "labels": [], "paths": [], "state": "open"}
        apply_flags(candidate)
        self.assertEqual(candidate["priority"], "urgent")
        self.assertIn("security", candidate["automation_flags"])
        self.assertIn("crash", candidate["automation_flags"])

    def test_decision_is_applied_only_to_exact_revision(self) -> None:
        candidate = {
            "candidate_id": "source:pull:1",
            "candidate_revision": "a" * 40,
            "decision_state": "none",
            "triage_status": "needs-triage",
            "module_ids": [],
        }
        decision = {
            "candidate_revision": "a" * 40,
            "status": "partial-value",
            "reason": "bounded subset only",
            "decided_at": "2026-07-14T00:00:00Z",
            "decided_by": "reviewer",
            "local_sha": None,
            "modules": ["combat"],
        }
        apply_decision(candidate, {candidate["candidate_id"]: decision})
        self.assertEqual(candidate["decision_state"], "current")
        self.assertEqual(candidate["triage_status"], "partial-value")
        self.assertEqual(candidate["module_ids"], ["combat"])
        candidate["candidate_revision"] = "b" * 40
        apply_decision(candidate, {candidate["candidate_id"]: decision})
        self.assertEqual(candidate["decision_state"], "stale")
        self.assertEqual(candidate["triage_status"], "stale-decision")

    def test_full_scan_collects_all_kinds_and_maps_pr_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(Path(tmp))
            snapshot = scan(root=root, token=None, days=30, mode="daily", now=NOW, client=FakeClient())
            self.assertEqual(snapshot["summary"]["candidate_count"], 4)
            pull = next(row for row in snapshot["candidates"] if row["kind"] == "pull")
            self.assertEqual(pull["mapping_state"], "partial")
            self.assertEqual(pull["module_ids"], ["upstream-intelligence"])
            self.assertEqual(pull["priority"], "urgent")
            self.assertEqual(snapshot["sources"][0]["head_state"], "different")
            self.assertTrue(validate_snapshot(snapshot, root).ok)

    def test_all_source_failures_refuse_publication(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = make_root(Path(tmp))
            with self.assertRaisesRegex(UpstreamError, "all watched sources failed"):
                scan(root=root, token=None, days=30, mode="daily", now=NOW, client=FakeClient(fail=True))

    def test_repository_validation_rejects_writable_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            source = source_row()
            source["writable"] = True
            root = make_root(Path(tmp), [source])
            result = validate_repository(root)
            self.assertFalse(result.ok)
            self.assertTrue(any("writable must be false" in error for error in result.errors))

    def test_issue_report_truncates_rows_to_bound(self) -> None:
        snapshot = {
            "generated_at": "2026-07-14T12:00:00Z",
            "mode": "daily",
            "window_days": 30,
            "window_start": "2026-06-14T12:00:00Z",
            "sources": [],
            "summary": {
                "source_count": 0,
                "source_errors": 0,
                "candidate_count": 20,
                "unmapped_candidates": 0,
                "by_priority": {"normal": 20},
                "by_status": {"needs-triage": 20},
                "by_module": {},
            },
            "candidates": [
                {
                    "priority": "normal",
                    "triage_status": "needs-triage",
                    "source_id": "source",
                    "kind": "issue",
                    "title": "x" * 200,
                    "url": "https://example.invalid",
                    "module_ids": [],
                    "mapping_state": "not-applicable",
                    "local_reference": {"state": "not-found"},
                    "automation_flags": [],
                }
                for _ in range(20)
            ],
        }
        body = render_issue_body(snapshot, max_chars=2500, max_rows=20)
        self.assertLessEqual(len(body), 2500)
        self.assertIn("canary-upstream-intelligence-v1", body)
        self.assertIn("Report truncated", body)

    def test_local_reference_can_prove_exact_ancestor(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.email", "test@example.invalid"], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.name", "Test"], check=True)
            (root / "a.txt").write_text("a", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "a.txt"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "initial"], check=True)
            sha = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
            result = local_reference({"object_sha": sha, "candidate_revision": sha, "url": ""}, root)
            self.assertEqual(result["state"], "exact-ancestor")


if __name__ == "__main__":
    unittest.main()
