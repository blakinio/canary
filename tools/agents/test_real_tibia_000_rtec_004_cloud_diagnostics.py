#!/usr/bin/env python3
"""Temporary full diagnostic exporter for RTEC-004 Worker B."""

from __future__ import annotations

import json
import unittest
from datetime import date
from pathlib import Path

from real_tibia_evidence_lib import Corpus


ROOT = Path(__file__).resolve().parents[2]


class Rtec004CloudDiagnostics(unittest.TestCase):
    def test_print_all_corpus_diagnostics(self) -> None:
        diagnostics = Corpus.load(ROOT).validate(date.fromisoformat("2026-07-25")).errors
        print("RTEC004_CLOUD_DIAGNOSTICS_BEGIN", flush=True)
        print(json.dumps([{"code": item.code, "path": item.path, "message": item.message} for item in diagnostics], indent=2, sort_keys=True), flush=True)
        print("RTEC004_CLOUD_DIAGNOSTICS_END", flush=True)
        self.fail("RTEC-004 diagnostics exported; consume artifact and remove this test")


if __name__ == "__main__":
    unittest.main()
