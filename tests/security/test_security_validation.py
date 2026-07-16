from __future__ import annotations

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.security import security_validation as sv  # noqa: E402


class SecurityValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        (self.root / "tests/security/scenarios/server").mkdir(parents=True)
        (self.root / "src").mkdir()
        (self.root / "tests/regression").mkdir(parents=True)
        (self.root / "src/example.lua").write_text("safe_call()\n", encoding="utf-8")
        (self.root / "tests/regression/test_example.py").write_text("# evidence\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.tempdir.cleanup()

    def scenario_data(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "id": "example-check",
            "name": "Example security check",
            "description": "Proves the bounded source-regex executor.",
            "component": "server",
            "target_adapter": "canary-source",
            "mode": "source-regex",
            "severity": "high",
            "authorization": {"scope": "repository", "repository": "blakinio/canary"},
            "source": {
                "files": ["src/example.lua"],
                "forbidden_regex": [r"\bos\.execute\s*\("],
                "required_regex": [r"safe_call\s*\("],
            },
            "evidence": {
                "regression_tests": ["tests/regression/test_example.py"],
                "related_prs": [326],
            },
        }

    def write_scenario(self, data: dict[str, object] | None = None, name: str = "example.json") -> Path:
        path = self.root / "tests/security/scenarios/server" / name
        path.write_text(json.dumps(data or self.scenario_data()), encoding="utf-8")
        return path

    def test_valid_scenario_and_pass_report_are_deterministic(self) -> None:
        scenario = sv.validate_scenario(self.write_scenario(), self.root)
        first = sv.run_scenario(scenario, self.root, "blakinio/canary")
        second = sv.run_scenario(scenario, self.root, "blakinio/canary")
        self.assertEqual(first, second)
        self.assertEqual(first["result"], "pass")
        self.assertEqual(first["schema"], sv.REPORT_SCHEMA)
        self.assertEqual(first["scenario_id"], "example-check")
        self.assertEqual(len(first["sources"][0]["sha256"]), 64)

    def test_forbidden_regex_reports_exact_location(self) -> None:
        (self.root / "src/example.lua").write_text("safe_call()\nos.execute('bad')\n", encoding="utf-8")
        scenario = sv.validate_scenario(self.write_scenario(), self.root)
        report = sv.run_scenario(scenario, self.root, "blakinio/canary")
        self.assertEqual(report["result"], "fail")
        finding = report["findings"][0]
        self.assertEqual(finding["assertion"], "forbidden_regex")
        self.assertEqual(finding["line"], 2)
        self.assertEqual(finding["column"], 1)

    def test_missing_required_regex_fails(self) -> None:
        (self.root / "src/example.lua").write_text("other_call()\n", encoding="utf-8")
        scenario = sv.validate_scenario(self.write_scenario(), self.root)
        report = sv.run_scenario(scenario, self.root, "blakinio/canary")
        self.assertEqual(report["result"], "fail")
        self.assertEqual(report["findings"][0]["assertion"], "required_regex")
        self.assertIsNone(report["findings"][0]["line"])

    def test_unknown_manifest_field_is_rejected(self) -> None:
        data = self.scenario_data()
        data["command"] = "curl example.invalid"
        with self.assertRaisesRegex(sv.SecurityScenarioError, "unsupported field"):
            sv.validate_scenario(self.write_scenario(data), self.root)

    def test_path_escape_is_rejected(self) -> None:
        data = self.scenario_data()
        data["source"]["files"] = ["../outside.lua"]  # type: ignore[index]
        with self.assertRaisesRegex(sv.SecurityScenarioError, "repository-relative path"):
            sv.validate_scenario(self.write_scenario(data), self.root)

    def test_symlink_source_is_rejected(self) -> None:
        target = self.root / "src/real.lua"
        target.write_text("safe_call()\n", encoding="utf-8")
        link = self.root / "src/link.lua"
        try:
            os.symlink(target, link)
        except (OSError, NotImplementedError):
            self.skipTest("symlinks unavailable")
        data = self.scenario_data()
        data["source"]["files"] = ["src/link.lua"]  # type: ignore[index]
        with self.assertRaisesRegex(sv.SecurityScenarioError, "must not traverse a symlink"):
            sv.validate_scenario(self.write_scenario(data), self.root)

    def test_invalid_regex_is_rejected(self) -> None:
        data = self.scenario_data()
        data["source"]["forbidden_regex"] = ["("]  # type: ignore[index]
        with self.assertRaisesRegex(sv.SecurityScenarioError, "not a valid regular expression"):
            sv.validate_scenario(self.write_scenario(data), self.root)

    def test_oversized_source_is_rejected(self) -> None:
        (self.root / "src/example.lua").write_bytes(b"x" * (sv.MAX_SOURCE_BYTES + 1))
        with self.assertRaisesRegex(sv.SecurityScenarioError, "exceeds"):
            sv.validate_scenario(self.write_scenario(), self.root)

    def test_duplicate_ids_are_rejected(self) -> None:
        self.write_scenario(name="one.json")
        self.write_scenario(name="two.json")
        with self.assertRaisesRegex(sv.SecurityScenarioError, "duplicate security scenario id"):
            sv.discover(self.root)

    def test_repository_authorization_mismatch_is_rejected(self) -> None:
        scenario = sv.validate_scenario(self.write_scenario(), self.root)
        with self.assertRaisesRegex(sv.SecurityScenarioError, "authorized for blakinio/canary"):
            sv.run_scenario(scenario, self.root, "example/other")

    def test_write_report_is_atomic_and_stable(self) -> None:
        scenario = sv.validate_scenario(self.write_scenario(), self.root)
        report = sv.run_scenario(scenario, self.root, "blakinio/canary")
        output = self.root / "artifacts/report.json"
        sv.write_report(output, report)
        self.assertEqual(output.read_text(encoding="utf-8"), sv.render_report(report))
        self.assertFalse(output.with_name("report.json.tmp").exists())


if __name__ == "__main__":
    unittest.main()
