from __future__ import annotations

import re
import shlex
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools" / "e2e" / "run_physical_e2e.sh"


class FailureEvidenceRetentionTest(unittest.TestCase):
    def script_text(self) -> str:
        return SCRIPT.read_text(encoding="utf-8")

    def extracted_exit_function(self) -> str:
        match = re.search(
            r"emit_workflow_exit\(\) \{\n.*?\n\}",
            self.script_text(),
            flags=re.DOTALL,
        )
        self.assertIsNotNone(match)
        assert match is not None
        return match.group(0)

    def run_exit_function(self, status: int) -> tuple[int, str]:
        with tempfile.TemporaryDirectory() as temporary:
            artifact_dir = Path(temporary)
            script = (
                "set -uo pipefail\n"
                f"ARTIFACT_DIR={shlex.quote(str(artifact_dir))}\n"
                f"{self.extracted_exit_function()}\n"
                f"emit_workflow_exit {status}\n"
                "exit $?\n"
            )
            completed = subprocess.run(
                ["bash", "-c", script],
                text=True,
                capture_output=True,
                check=False,
            )
            recorded = (artifact_dir / "physical-exit-code.txt").read_text(
                encoding="utf-8"
            )
            return completed.returncode, recorded

    def test_zero_status_remains_success_and_is_recorded(self) -> None:
        returncode, recorded = self.run_exit_function(0)
        self.assertEqual(0, returncode)
        self.assertEqual("0\n", recorded)

    def test_signal_style_status_is_normalized_after_recording(self) -> None:
        returncode, recorded = self.run_exit_function(143)
        self.assertEqual(1, returncode)
        self.assertEqual("143\n", recorded)

    def test_evidence_finalization_precedes_workflow_failure(self) -> None:
        text = self.script_text()
        final_finalize = text.rfind('python3 "${ENVELOPE}" finalize')
        final_exit = text.rfind('emit_workflow_exit "${final_status}"')
        self.assertGreater(final_finalize, 0)
        self.assertGreater(final_exit, final_finalize)
        cleanup_text = (
            ROOT / "tools" / "e2e" / "cleanup_certification.py"
        ).read_text(encoding="utf-8")
        self.assertIn("cleanup-certification.json", cleanup_text)

    def test_signal_handlers_preserve_finalization_path(self) -> None:
        text = self.script_text()
        self.assertIn("trap 'handle_signal 143' TERM", text)
        self.assertIn("trap 'handle_signal 130' INT", text)
        self.assertIn('lifecycle_status="${signal_status}"', text)


if __name__ == "__main__":
    unittest.main()
