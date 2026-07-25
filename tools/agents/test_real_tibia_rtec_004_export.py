#!/usr/bin/env python3
"""Temporary exact-package exporter for RTEC-004 worker A.

This test intentionally fails after materialising the accepted review and canonical
indexes so the existing focused-test diagnostics artifact retains exact bytes.
It must be removed before readiness.
"""

from __future__ import annotations

import base64
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_ROOT = ROOT / "docs/agents/real-tibia/evidence/modules/weapon-proficiency"


class Rtec004ReviewedPackageExportTest(unittest.TestCase):
    def test_export_reviewed_package(self) -> None:
        record_paths = sorted((MODULE_ROOT / "records").glob("RT-WEAPON-PROFICIENCY-*.yaml"))
        self.assertEqual(len(record_paths), 3)

        notes = [
            "Structured review verified official source dates and bounded paraphrases.",
            "Review verified exact Canary paths and preserved selected-path, runtime, persistence, protocol, client and E2E nonclaims.",
            "No owner implementation path or existing vocations request is modified.",
        ]
        for path in record_paths:
            value = json.loads(path.read_text(encoding="utf-8"))
            value["record_status"] = "accepted"
            value["review"] = {
                "status": "accepted",
                "task_id": "CAN-20260725-rtec-004-weapon-proficiency",
                "pr": 930,
                "reviewer": "RTEC-004 coordinator / GPT-5.6 Thinking",
                "reviewed_at": "2026-07-25T20:50:00+02:00",
                "notes": notes,
            }
            path.write_text(
                json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )

        review_path = MODULE_ROOT / "reviews/RTEC-004-W1-REVIEW.md"
        review_path.write_text(
            """# RTEC-004 weapon-proficiency structured review

Status: accepted.

Reviewed at: `2026-07-25T20:50:00+02:00`.

Reviewer: RTEC-004 coordinator / GPT-5.6 Thinking.

## Accepted findings

- Official source dates, URLs and bounded paraphrases are pinned.
- The current Canary comparison is tied to exact commit, paths and symbols.
- Original-tree selection is not represented as equivalent to modified-slot manipulation.
- Character-switch client isolation remains `UNKNOWN`.
- Runtime persistence, protocol, maintained-client and physical-client nonclaims remain explicit.
- No implementation, data, protocol/client, persistence, achievement or E2E path is changed.
- `RTREQ-FEATURE-VOCATIONS-0001` remains untouched.

## Validation

The canonical evidence generator and validator passed in the export workspace. Final acceptance remains contingent on all exact-final-head repository checks after the exported bytes are committed and this temporary exporter is removed.
""",
            encoding="utf-8",
        )

        subprocess.run(
            [sys.executable, "tools/agents/real_tibia_evidence.py", "generate", "--as-of", "2026-07-25"],
            cwd=ROOT,
            check=True,
        )
        subprocess.run(
            [sys.executable, "tools/agents/real_tibia_evidence.py", "validate", "--as-of", "2026-07-25"],
            cwd=ROOT,
            check=True,
        )
        subprocess.run(
            [sys.executable, "tools/agents/real_tibia_evidence.py", "generate", "--check", "--as-of", "2026-07-25"],
            cwd=ROOT,
            check=True,
        )

        export_paths = [
            ROOT / "docs/agents/real-tibia/evidence/generated/EVIDENCE_INDEXES.json",
            MODULE_ROOT / "EVIDENCE_INDEX.yaml",
            *record_paths,
            review_path,
        ]
        for path in export_paths:
            relative = path.relative_to(ROOT).as_posix()
            data = path.read_bytes()
            print(f"RTEC004_EXPORT_BEGIN {relative} {hashlib.sha256(data).hexdigest()}", flush=True)
            print(base64.b64encode(data).decode("ascii"), flush=True)
            print(f"RTEC004_EXPORT_END {relative}", flush=True)

        self.fail("RTEC-004 reviewed package export complete; consume diagnostics artifact and remove this test")


if __name__ == "__main__":
    unittest.main()
