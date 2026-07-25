from __future__ import annotations

import re
import shlex
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools" / "e2e" / "run_physical_e2e.sh"
WORKFLOW = ROOT / ".github" / "workflows" / "universal-agent-e2e.yml"


class FailureEvidenceRetentionTest(unittest.TestCase):
    def script_text(self) -> str:
        return SCRIPT.read_text(encoding="utf-8")

    def workflow_text(self) -> str:
        return WORKFLOW.read_text(encoding="utf-8")

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

    def test_evidence_finalization_precedes_script_failure(self) -> None:
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

    def test_workflow_uploads_before_propagating_physical_failure(self) -> None:
        text = self.workflow_text()
        capture = text.index("      - name: Run selected physical-client scenario")
        upload = text.index("      - name: Upload universal E2E evidence")
        propagate = text.index("      - name: Propagate physical-client scenario result")
        self.assertLess(capture, upload)
        self.assertLess(upload, propagate)

        capture_block = text[capture:upload]
        self.assertIn("        id: physical", capture_block)
        self.assertIn("          status=$?", capture_block)
        self.assertIn("          printf 'status=%s\\n'", capture_block)
        self.assertTrue(capture_block.rstrip().endswith("exit 0"))

        upload_block = text[upload:propagate]
        self.assertIn("        if: always()", upload_block)
        self.assertIn("        uses: actions/upload-artifact@v4", upload_block)

        propagate_block = text[propagate:]
        self.assertIn("        if: always()", propagate_block)
        self.assertIn(
            "          PHYSICAL_STATUS: ${{ steps.physical.outputs.status }}",
            propagate_block,
        )
        self.assertIn(
            "physical scenario failed with captured status",
            propagate_block,
        )


if __name__ == "__main__":
    unittest.main()
