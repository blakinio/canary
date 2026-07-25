#!/usr/bin/env python3
"""Temporary bounded scan exporter for RTEC-004 worker B.

This test intentionally fails after printing one deterministic JSON report. The
canonical Real Tibia Evidence Contracts workflow retains the report in its
focused-test diagnostics artifact. Remove this test before readiness.
"""

from __future__ import annotations

import json
import re
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SELECTED_PATHS = [
    "data/items/items.xml",
    "src/items/items.cpp",
    "src/items/items.hpp",
    "src/items/functions/item/item_parse.cpp",
    "src/items/functions/item/item_parse.hpp",
]
TERMS = ["cloud in a bottle", "cloud in bottle", "radiant nimbus", "moonsilver", "54651"]


class Rtec004CloudScanExportTest(unittest.TestCase):
    def test_export_cloud_item_scan(self) -> None:
        selected_hits: dict[str, list[dict[str, object]]] = {}
        for relative in SELECTED_PATHS:
            path = ROOT / relative
            self.assertTrue(path.is_file(), relative)
            encoding = "iso-8859-1" if path.suffix == ".xml" else "utf-8"
            text = path.read_text(encoding=encoding)
            folded = text.casefold()
            hits: list[dict[str, object]] = []
            for term in TERMS:
                needle = term.casefold()
                start = 0
                while True:
                    index = folded.find(needle, start)
                    if index < 0:
                        break
                    hits.append({
                        "term": term,
                        "line": text.count("\n", 0, index) + 1,
                        "excerpt": text[index:index + 160].splitlines()[0],
                    })
                    start = index + len(needle)
            selected_hits[relative] = hits

        xml_text = (ROOT / "data/items/items.xml").read_text(encoding="iso-8859-1")
        exact_id = [
            {"line": xml_text.count("\n", 0, match.start()) + 1, "tag": match.group(0)}
            for match in re.finditer(r'<item\b[^>]*\bid="54651"[^>]*>', xml_text, re.IGNORECASE)
        ]
        cloud_or_bottle_names = [
            {"line": xml_text.count("\n", 0, match.start()) + 1, "tag": match.group(0)}
            for match in re.finditer(r'<item\b[^>]*\bname="[^"]*(?:cloud|bottle)[^"]*"[^>]*>', xml_text, re.IGNORECASE)
        ]
        grep = subprocess.run(
            ["git", "grep", "-n", "-i", "-E", "cloud[[:space:]]+in[[:space:]]+(a[[:space:]]+)?bottle|radiant[[:space:]]+nimbus|moonsilver|54651"],
            cwd=ROOT,
            check=False,
            text=True,
            capture_output=True,
        )
        self.assertIn(grep.returncode, (0, 1), grep.stderr)

        report = {
            "format": "rtec-004-cloud-in-a-bottle-discovery-v1",
            "canary_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
            "selected_paths": SELECTED_PATHS,
            "selected_path_hits": selected_hits,
            "items_xml_exact_id_54651": exact_id,
            "items_xml_cloud_or_bottle_names": cloud_or_bottle_names,
            "repository_grep_matches": grep.stdout.splitlines(),
            "nonclaims": [
                "Search misses do not prove absence under another name or identifier.",
                "Candidate ID 54651 is not accepted as official or Canary identity proof.",
                "This scan does not prove unlock authorization, acquisition, runtime, client or appearance parity."
            ],
        }
        print("RTEC004_CLOUD_SCAN_BEGIN", flush=True)
        print(json.dumps(report, indent=2, sort_keys=True), flush=True)
        print("RTEC004_CLOUD_SCAN_END", flush=True)
        self.fail("bounded Cloud scan exported; consume diagnostics and remove this test")


if __name__ == "__main__":
    unittest.main()
