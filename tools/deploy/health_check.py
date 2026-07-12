"""Post-switch health checks.

A health check must confirm a real running process, not merely that some
file exists. The reference implementation here reads a PID from a file and
confirms a process with that PID is actually alive via a zero-signal
``kill`` probe - the standard, portable way to test process liveness
without actually signaling it. This is deliberately pluggable: the real
server-integration phase (running the actual compiled Canary binary against
a release) supplies its own checker built on this same primitive, plus
whatever extra liveness signal it can add (e.g. the status port answering).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


@dataclass
class HealthCheckResult:
    healthy: bool
    detail: str


HealthChecker = Callable[[Path], HealthCheckResult]


def is_process_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        # The process exists but is owned by someone else - still alive.
        return True
    return True


def pid_file_health_check(pid_file_path: Path) -> HealthCheckResult:
    """Reference health check: verifies the process named by a PID file is actually running.

    Reading the file and finding a number is not the check; ``is_process_alive``
    with a real ``kill(pid, 0)`` probe is. A stale PID file (process died, PID
    reused by something else) is exactly the case this exists to catch, so a
    missing or unparsable file is unhealthy, not "skipped".
    """
    if not pid_file_path.is_file():
        return HealthCheckResult(healthy=False, detail=f"pid file not found: {pid_file_path}")

    raw = pid_file_path.read_text(encoding="utf-8").strip()
    try:
        pid = int(raw)
    except ValueError:
        return HealthCheckResult(healthy=False, detail=f"pid file does not contain a valid pid: {raw!r}")

    if is_process_alive(pid):
        return HealthCheckResult(healthy=True, detail=f"pid {pid} is alive")
    return HealthCheckResult(healthy=False, detail=f"pid {pid} from {pid_file_path} is not running")


def make_pid_file_health_check(pid_file_path: Path) -> HealthChecker:
    def _check(_release_dir: Path) -> HealthCheckResult:
        return pid_file_health_check(pid_file_path)

    return _check
