from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github/workflows/cyclopedia-validation.yml"


class CyclopediaWorkflowContractTests(unittest.TestCase):
    def read_workflow(self) -> str:
        return WORKFLOW.read_text(encoding="utf-8")

    def test_all_cyclopedia_tests_trigger_and_run(self) -> None:
        text = self.read_workflow()
        self.assertGreaterEqual(
            text.count('"tools/ai-agent/test_cyclopedia*.py"'),
            2,
            "push and pull_request filters must cover every Cyclopedia test",
        )
        self.assertIn(
            'python -m unittest discover -s tools/ai-agent -p "test_cyclopedia*.py" -v',
            text,
        )
        self.assertIn(
            "python -m py_compile tools/ai-agent/cyclopedia_validation.py tools/ai-agent/test_cyclopedia*.py",
            text,
        )

    def test_generated_audit_is_a_zero_finding_gate(self) -> None:
        text = self.read_workflow()
        self.assertIn("--fail-on error", text)
        self.assertNotIn("--fail-on none", text)
        self.assertIn(
            'assert report["summary"]["findingCount"] == 0, report["findings"]',
            text,
        )
        self.assertIn('assert report["findings"] == []', text)


if __name__ == "__main__":
    unittest.main()
