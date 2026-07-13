#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROGRAM = ROOT / "docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md"


def replace_once(text: str, old: str, new: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"expected exactly one program anchor, found {count}: {old[:80]!r}")
    return text.replace(old, new, 1)


def main() -> None:
    text = PROGRAM.read_text(encoding="utf-8")
    text = replace_once(
        text,
        'updated: 2026-07-14T00:05:00+02:00\nlast_verified_commit: "b2036bd5d56423894b72eaa2ebaff32feba382a5"',
        'updated: 2026-07-14T00:42:00+02:00\nlast_verified_commit: "b06079f9bc75f0c108720e2674438a2f539c8631"',
    )
    text = replace_once(
        text,
        '# Active tasks\n\n| Task/PR | Candidate | Status | Scope |\n|---|---|---|---|\n| `CAN-20260713-conditionlight-zero-level` / [#297](https://github.com/blakinio/canary/pull/297) | `CS-001` | active | Test-first normalization of zero light levels at `ConditionLight` start and deserialization boundaries. |',
        '# Active tasks\n\nNone. Select exactly one bounded queue item and create a new task before implementation.',
    )
    text = replace_once(
        text,
        '| `CS-001` | `a7350014528002fb27ed64d260a96d28a580d41a` | `VALID_FIX_MISSING` | high | `ConditionLight` zero-level division/deserialization | Active in task `CAN-20260713-conditionlight-zero-level` / PR #297; merge only after focused C++ and required CI gates pass. |',
        '| `CS-001` | `a7350014528002fb27ed64d260a96d28a580d41a` | `VALID_FIX_MISSING` | high | `ConditionLight` zero-level division/deserialization | Completed through task `CAN-20260713-conditionlight-zero-level`, PR #297, merge `b06079f9bc75f0c108720e2674438a2f539c8631`; preserve focused regressions. |',
    )
    text = replace_once(
        text,
        '| `CAN-20260713-crystalserver-comparison-inventory` / [#291](https://github.com/blakinio/canary/pull/291) | Stage 1 program, ten-candidate Markdown report, and machine-readable JSON; no functional changes | `bceccba9349d35a1d84f446757e53ac3adb602e1` | Select `CS-001` only through a new test-first task after fresh checks. |',
        '| `CAN-20260713-crystalserver-comparison-inventory` / [#291](https://github.com/blakinio/canary/pull/291) | Stage 1 program, ten-candidate Markdown report, and machine-readable JSON; no functional changes | `bceccba9349d35a1d84f446757e53ac3adb602e1` | Select candidates only through new bounded tasks after fresh checks. |\n| `CAN-20260713-conditionlight-zero-level` / [#297](https://github.com/blakinio/canary/pull/297) | Normalized zero-level `ConditionLight` state at start/deserialization boundaries and added three focused C++ regressions | `b06079f9bc75f0c108720e2674438a2f539c8631` | Preserve the two-boundary invariant and regression tests; no further CS-001 work is open. |',
    )
    text = replace_once(
        text,
        '# Closed candidates\n\n- `CS-002` — equivalent safe iteration already exists.',
        '# Closed candidates\n\n- `CS-001` — implemented and regression-covered through PR #297.\n- `CS-002` — equivalent safe iteration already exists.',
    )
    text = replace_once(
        text,
        '- Local Git/worktree inspection was unavailable during Stage 1 because shell DNS could not resolve GitHub; future tasks must record their own environment.',
        '- Local Git/worktree inspection was unavailable during Stage 1 and CS-001 because shell DNS could not resolve GitHub; future tasks must record their own environment.',
    )
    text = replace_once(
        text,
        '- Which current path can supply zero to `ConditionLight`, and which fixture best proves it?\n',
        '',
    )
    PROGRAM.write_text(text, encoding="utf-8")

    (ROOT / ".github/workflows/apply-archive-conditionlight-zero-level.yml").unlink()
    Path(__file__).unlink()


if __name__ == "__main__":
    main()
