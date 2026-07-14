#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from upstream_intelligence_candidates import build_local_history, local_reference
from upstream_intelligence_render import render_markdown


def _candidate(*, title: str, url: str) -> dict:
    return {
        "priority": "normal",
        "triage_status": "needs-triage",
        "source_id": "source",
        "kind": "issue",
        "title": title,
        "url": url,
        "module_ids": [],
        "mapping_state": "not-applicable",
        "local_reference": {"state": "not-found"},
        "automation_flags": [],
    }


def _snapshot(candidate: dict) -> dict:
    return {
        "generated_at": "2026-07-14T12:00:00Z",
        "mode": "daily",
        "window_days": 30,
        "window_start": "2026-06-14T12:00:00Z",
        "sources": [],
        "summary": {
            "source_count": 0,
            "source_errors": 0,
            "candidate_count": 1,
            "unmapped_candidates": 0,
            "by_priority": {"normal": 1},
            "by_status": {"needs-triage": 1},
            "by_module": {},
        },
        "candidates": [candidate],
    }


class UpstreamIntelligenceHardeningTests(unittest.TestCase):
    def test_local_history_excludes_unrelated_fetched_refs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init", "-q", "-b", "main", str(root)], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.email", "test@example.invalid"], check=True)
            subprocess.run(["git", "-C", str(root), "config", "user.name", "Test"], check=True)
            (root / "local.txt").write_text("local", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "local.txt"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", "local target history"], check=True)

            subprocess.run(["git", "-C", str(root), "checkout", "-qb", "donor"], check=True)
            marker = "https://github.com/example/donor/pull/7"
            (root / "donor.txt").write_text("donor", encoding="utf-8")
            subprocess.run(["git", "-C", str(root), "add", "donor.txt"], check=True)
            subprocess.run(["git", "-C", str(root), "commit", "-qm", f"donor candidate {marker}"], check=True)
            donor_sha = subprocess.check_output(
                ["git", "-C", str(root), "rev-parse", "HEAD"], text=True
            ).strip()
            subprocess.run(["git", "-C", str(root), "checkout", "-q", "main"], check=True)

            history = build_local_history(root)
            self.assertNotIn(donor_sha, history.commits)
            self.assertNotIn(marker, history.text)
            result = local_reference(
                {
                    "object_sha": donor_sha,
                    "candidate_revision": donor_sha,
                    "url": marker,
                },
                root,
                history,
            )
            self.assertEqual(result["state"], "not-found")

    def test_report_escapes_external_markdown_and_html(self) -> None:
        candidate = _candidate(
            title="evil](javascript:alert(1)) <script>|`",
            url="javascript:alert(1)",
        )
        report = render_markdown(_snapshot(candidate))
        self.assertIn("&lt;script&gt;", report)
        self.assertIn("\\]", report)
        self.assertIn("\\|", report)
        self.assertNotIn("](javascript:alert(1))", report)
        self.assertNotIn("<script>", report)

    def test_report_links_only_canonical_github_urls(self) -> None:
        url = "https://github.com/opentibiabr/canary/issues/1"
        report = render_markdown(_snapshot(_candidate(title="valid", url=url)))
        self.assertIn(f"[valid]({url})", report)


if __name__ == "__main__":
    unittest.main()
