#!/usr/bin/env python3
"""Temporary bounded discovery scan for RTEC-004 worker B."""

from __future__ import annotations

import json
import re
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


class Rtec004CloudScanTest(unittest.TestCase):
    def test_export_bounded_discovery(self) -> None:
        results: dict[str, list[dict[str, object]]] = {}
        for relative in SELECTED_PATHS:
            path = ROOT / relative
            self.assertTrue(path.is_file(), relative)
            encoding = "iso-8859-1" if path.suffix == ".xml" else "utf-8"
            text = path.read_text(encoding=encoding)
            folded = text.casefold()
            hits: list[dict[str, object]] = []
            for term in TERMS:
                needle = term.casefold()
                offset = 0
                while True:
                    index = folded.find(needle, offset)
                    if index < 0:
                        break
                    hits.append({
                        "term": term,
                        "line": text.count("\n", 0, index) + 1,
                        "excerpt": text[index : index + 140].splitlines()[0],
                    })
                    offset = index + len(needle)
            results[relative] = hits

        xml_text = (ROOT / "data/items/items.xml").read_text(encoding="iso-8859-1")
        exact_id_tags = [
            {"line": xml_text.count("\n", 0, match.start()) + 1, "tag": match.group(0)}
            for match in re.finditer(r'<item\b[^>]*\bid="54651"[^>]*>', xml_text, re.IGNORECASE)
        ]
        cloud_or_bottle_names = [
            {"line": xml_text.count("\n", 0, match.start()) + 1, "tag": match.group(0)}
            for match in re.finditer(r'<item\b[^>]*\bname="[^"]*(?:cloud|bottle)[^"]*"[^>]*>', xml_text, re.IGNORECASE)
        ]
        report = {
            "format": "rtec-004-cloud-in-a-bottle-discovery-v1",
            "selected_paths": SELECTED_PATHS,
            "term_hits": results,
            "items_xml_exact_id_54651": exact_id_tags,
            "items_xml_cloud_or_bottle_names": cloud_or_bottle_names,
            "nonclaims": [
                "Search misses do not prove absence under another name or identifier.",
                "Candidate ID 54651 is not accepted as official or Canary identity proof.",
                "This scan does not prove unlock, acquisition, runtime, client or appearance parity."
            ],
        }
        print("RTEC004_CLOUD_SCAN_BEGIN", flush=True)
        print(json.dumps(report, indent=2, sort_keys=True), flush=True)
        print("RTEC004_CLOUD_SCAN_END", flush=True)
        self.fail("bounded Cloud scan exported; consume diagnostics and remove this test")


if __name__ == "__main__":
    unittest.main()
