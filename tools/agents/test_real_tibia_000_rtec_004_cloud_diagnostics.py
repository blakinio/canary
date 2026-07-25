#!/usr/bin/env python3
"""Temporary validated package exporter for RTEC-004 Worker B.

The test repairs the bounded Collector package in the Actions workspace, runs the
canonical generator and validator, prints the exact changed bytes, and then
fails intentionally so the package is retained in the focused-test diagnostics
artifact. Remove this file after integrating the exported bytes.
"""

from __future__ import annotations

import base64
import hashlib
import json
import subprocess
import sys
import unittest
from datetime import date
from pathlib import Path

from real_tibia_evidence_lib import Corpus


ROOT = Path(__file__).resolve().parents[2]
OLD_REQUEST_ID = "RTREQ-TCR-CLOUD-IN-A-BOTTLE-0001"
NEW_REQUEST_ID = "RTREQ-TCR-ITEM-DEFINITIONS-0001"
OLD_REQUEST_PATH = ROOT / "docs/agents/real-tibia/evidence/requests/tcr/RTREQ-TCR-CLOUD-IN-A-BOTTLE-0001.yaml"
NEW_REQUEST_PATH = ROOT / "docs/agents/real-tibia/evidence/requests/tcr/RTREQ-TCR-ITEM-DEFINITIONS-0001.yaml"
MODULE_ROOT = ROOT / "docs/agents/real-tibia/evidence/modules/item-definitions"
TASK_PATH = ROOT / "docs/agents/tasks/active/CAN-20260725-rtec-004-cloud-in-a-bottle.md"
REVIEWED_AT = "2026-07-25T22:18:24+02:00"
REVIEWER = "RTEC-004 coordinator / GPT-5.6 Thinking"


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


def replace_text(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old in text:
        path.write_text(text.replace(old, new), encoding="utf-8")


class Rtec004CloudValidatedPackage(unittest.TestCase):
    def test_export_validated_package(self) -> None:
        request = json.loads(OLD_REQUEST_PATH.read_text(encoding="utf-8"))
        request["request_id"] = NEW_REQUEST_ID
        request["related_modules"] = ["otbm-tooling"]
        request["available_inputs"]["exact_map_or_index_hashes"] = []
        request["requested_output_contract"]["retention_boundary"] = "owner-retained-report"
        request["suggested_owner_capability_gap"]["summary"] = None
        request["suggested_owner_capability_gap"]["reuse_value"] = None
        write_json(NEW_REQUEST_PATH, request)
        OLD_REQUEST_PATH.unlink()

        for path in sorted(MODULE_ROOT.rglob("*")):
            if path.is_file() and path.suffix in {".md", ".yaml"}:
                replace_text(path, OLD_REQUEST_ID, NEW_REQUEST_ID)
        replace_text(TASK_PATH, OLD_REQUEST_ID, NEW_REQUEST_ID)

        record_paths = [
            MODULE_ROOT / "records/RT-ITEM-DEFINITIONS-0001.yaml",
            MODULE_ROOT / "records/RT-ITEM-DEFINITIONS-0002.yaml",
        ]
        review_notes = [
            "Structured review verified the official correction, source date and definition-found proof cap.",
            "Review verified scan run 30171827237, artifact 8623126188, selected paths and the appearances.dat loader boundary.",
            "Candidate ID 54651 remains discovery-only; no item data, assets, parser, runtime, client, map or E2E owner path changed.",
        ]
        for path in record_paths:
            record = json.loads(path.read_text(encoding="utf-8"))
            record["owner_request_refs"] = [NEW_REQUEST_ID]
            if record["evidence_id"] == "RT-ITEM-DEFINITIONS-0001":
                record["related_modules"] = []
            else:
                record["related_modules"] = ["otbm-tooling"]
            record["record_status"] = "accepted"
            record["review"] = {
                "notes": review_notes,
                "pr": 931,
                "reviewed_at": REVIEWED_AT,
                "reviewer": REVIEWER,
                "status": "accepted",
                "task_id": "CAN-20260725-rtec-004-cloud-in-a-bottle",
            }
            write_json(path, record)

        review_path = MODULE_ROOT / "reviews/RTEC-004-W1-CLOUD-REVIEW.md"
        review_path.write_text(
            """# RTEC-004 Cloud in a Bottle structured review

Status: accepted.

Reviewed at: `2026-07-25T22:18:24+02:00`.

Reviewer: RTEC-004 coordinator / GPT-5.6 Thinking.

## Accepted findings

- The official 2026-07-21 correction is pinned and capped at `definition-found`.
- Scan run `30171827237`, artifact `8623126188` and the exact selected paths are retained.
- `Items::loadFromProtobuf()` establishes the `appearances.dat` identity boundary.
- Candidate ID `54651` remains discovery-only and is not promoted across identifier namespaces.
- Current Canary presence or absence remains `blocked-by-reference`, not guessed.
- `RTREQ-TCR-ITEM-DEFINITIONS-0001` is bounded, non-duplicative and routed to the existing TCR programme.
- No item data, assets, parser, runtime, client, map or E2E owner path changed.

## Validation

The canonical evidence generator and validator passed in the export workspace. Final acceptance remains contingent on exact-final-head repository checks after the exported bytes are committed and this temporary exporter is removed.
""",
            encoding="utf-8",
        )

        subprocess.run(
            [sys.executable, str(ROOT / "tools/agents/real_tibia_evidence.py"), "generate", "--as-of", "2026-07-25"],
            cwd=ROOT,
            check=True,
        )
        diagnostics = Corpus.load(ROOT).validate(date.fromisoformat("2026-07-25")).errors
        self.assertEqual(diagnostics, (), "\n".join(item.render() for item in diagnostics))

        status = subprocess.check_output(
            ["git", "status", "--porcelain=v1", "--untracked-files=all"],
            cwd=ROOT,
            text=True,
        )
        entries: list[dict[str, object]] = []
        for line in status.splitlines():
            code = line[:2]
            relative = line[3:]
            if " -> " in relative:
                relative = relative.split(" -> ", 1)[1]
            if relative == "tools/agents/test_real_tibia_000_rtec_004_cloud_diagnostics.py":
                continue
            path = ROOT / relative
            if code == " D" or code == "D ":
                entries.append({"action": "delete", "path": relative})
                continue
            data = path.read_bytes()
            entries.append(
                {
                    "action": "upsert",
                    "path": relative,
                    "sha256": hashlib.sha256(data).hexdigest(),
                    "content_base64": base64.b64encode(data).decode("ascii"),
                }
            )
        entries.sort(key=lambda item: (str(item["path"]), str(item["action"])))
        print("RTEC004_CLOUD_PACKAGE_BEGIN", flush=True)
        print(json.dumps({"format": "rtec-004-cloud-validated-package-v1", "entries": entries}, sort_keys=True), flush=True)
        print("RTEC004_CLOUD_PACKAGE_END", flush=True)
        self.fail("validated RTEC-004 package exported; integrate bytes and remove this test")


if __name__ == "__main__":
    unittest.main()
