from __future__ import annotations

import re
import shlex
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "tools" / "e2e" / "run_physical_e2e.sh"


class PhysicalSessionIsolationTest(unittest.TestCase):
    def extracted_function(self) -> str:
        text = SCRIPT.read_text(encoding="utf-8")
        match = re.search(
            r"run_isolated_physical\(\) \{\n.*?\n\}",
            text,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(match)
        assert match is not None
        return match.group(0)

    def run_child(self, child_body: str) -> tuple[int, str]:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            marker = root / "marker.txt"
            child = root / "child.sh"
            child.write_text(
                "#!/usr/bin/env bash\n"
                "set -uo pipefail\n"
                f"MARKER={shlex.quote(str(marker))}\n"
                f"{child_body}\n",
                encoding="utf-8",
            )
            child.chmod(0o755)
            harness = (
                "set -uo pipefail\n"
                f"{self.extracted_function()}\n"
                f"run_isolated_physical {shlex.quote(str(child))}\n"
                "exit $?\n"
            )
            completed = subprocess.run(
                ["bash", "-c", harness],
                text=True,
                capture_output=True,
                check=False,
            )
            recorded = marker.read_text(encoding="utf-8") if marker.exists() else ""
            return completed.returncode, recorded

    def test_normal_failure_status_is_preserved(self) -> None:
        returncode, marker = self.run_child('printf "normal\\n" > "${MARKER}"; exit 7')
        self.assertEqual(7, returncode)
        self.assertEqual("normal\n", marker)

    def test_signal_termination_is_isolated_and_normalized(self) -> None:
        returncode, marker = self.run_child(
            'printf "signal\\n" > "${MARKER}"; kill -TERM "$$"; sleep 1'
        )
        self.assertEqual(1, returncode)
        self.assertEqual("signal\n", marker)

    def test_script_enters_isolated_capture_session_once(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('if [[ "${AGENT_E2E_CAPTURE_SESSION:-}" != "1" ]]', text)
        self.assertIn('AGENT_E2E_CAPTURE_SESSION=1 setsid bash "${script}"', text)


if __name__ == "__main__":
    unittest.main()
