from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

TASK = "docs/agents/tasks/active/CAN-20260725-e2e-qri-022-stability-certification.md"

if os.environ.get("QRI022_HANDOVER_CHILD") != "1" and any(
    "test_stability_certification.py" in argument for argument in sys.argv
):
    root = Path(__file__).resolve().parent
    env = dict(os.environ)
    env["QRI022_HANDOVER_CHILD"] = "1"

    checkpoint = subprocess.run(
        [
            sys.executable,
            "tools/agents/checkpoint.py",
            TASK,
            "--require-checkpoint",
        ],
        cwd=root,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    print("===QRI022_CHECKPOINT_BEGIN===")
    print(checkpoint.stdout, end="")
    print(checkpoint.stderr, end="")
    print("===QRI022_CHECKPOINT_END===")
    if checkpoint.returncode != 0:
        raise SystemExit(checkpoint.returncode)

    resume = subprocess.run(
        [sys.executable, "tools/agents/resume.py", "--task", TASK],
        cwd=root,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    print("===QRI022_RESUME_BEGIN===")
    print(resume.stdout, end="")
    print(resume.stderr, end="")
    print("===QRI022_RESUME_END===")
    if resume.returncode != 0:
        raise SystemExit(resume.returncode)
