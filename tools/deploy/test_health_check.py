from __future__ import annotations

import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from health_check import is_process_alive, make_pid_file_health_check, pid_file_health_check


class HealthCheckTests(unittest.TestCase):
    def test_missing_pid_file_is_unhealthy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = pid_file_health_check(Path(tmp) / "does-not-exist.pid")
            self.assertFalse(result.healthy)
            self.assertIn("not found", result.detail)

    def test_garbage_pid_file_is_unhealthy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pid_file = Path(tmp) / "server.pid"
            pid_file.write_text("not-a-pid", encoding="utf-8")
            result = pid_file_health_check(pid_file)
            self.assertFalse(result.healthy)
            self.assertIn("valid pid", result.detail)

    def test_real_running_process_is_healthy(self) -> None:
        process = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
        try:
            with tempfile.TemporaryDirectory() as tmp:
                pid_file = Path(tmp) / "server.pid"
                pid_file.write_text(str(process.pid), encoding="utf-8")

                self.assertTrue(is_process_alive(process.pid))
                result = pid_file_health_check(pid_file)
                self.assertTrue(result.healthy)
                self.assertIn(str(process.pid), result.detail)

                checker = make_pid_file_health_check(pid_file)
                self.assertTrue(checker(Path(tmp)).healthy)
        finally:
            process.terminate()
            process.wait(timeout=10)

    def test_dead_process_is_unhealthy(self) -> None:
        process = subprocess.Popen([sys.executable, "-c", "pass"])
        process.wait(timeout=10)
        # Give the OS a moment; on some platforms pid reuse is not instant,
        # but a just-exited pid should not report alive via kill(pid, 0).
        time.sleep(0.1)

        with tempfile.TemporaryDirectory() as tmp:
            pid_file = Path(tmp) / "server.pid"
            pid_file.write_text(str(process.pid), encoding="utf-8")
            result = pid_file_health_check(pid_file)
            self.assertFalse(result.healthy)
            self.assertIn("not running", result.detail)

    def test_pid_zero_or_negative_is_never_alive(self) -> None:
        self.assertFalse(is_process_alive(0))
        self.assertFalse(is_process_alive(-1))


if __name__ == "__main__":
    unittest.main()
