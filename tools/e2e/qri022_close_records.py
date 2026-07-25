#!/usr/bin/env python3
from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected exactly one match, found {count}: {old!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


catalog = Path("docs/agents/MODULE_CATALOG.md")
replace_once(catalog, "Last reviewed: 2026-07-24", "Last reviewed: 2026-07-25")
replace_once(
    catalog,
    "| Universal OTS E2E factual stability certification | active (#912) |",
    "| Universal OTS E2E factual stability certification | merged (#912; lifecycle #914) |",
)
replace_once(
    catalog,
    "schema and `.github/workflows/e2e-stability-certification.yml`, task `CAN-20260725-e2e-qri-022-stability-certification` |",
    "schema and `.github/workflows/e2e-stability-certification.yml`, archived task `CAN-20260725-e2e-qri-022-stability-certification` |",
)

program = Path("docs/agents/programs/E2E_AUTOMATION_PROGRAM.md")
replace_once(program, "updated: 2026-07-25T10:40:00+02:00", "updated: 2026-07-25T13:00:00+02:00")
replace_once(
    program,
    'last_verified_commit: "52fc82d5a47727c78d8d58c7fb64823669cb8479"',
    'last_verified_commit: "5463786e682c7820d201eeaff268cb6ef6bfd4f7"',
)
replace_once(
    program,
    "| Factual stability certification | active contract/tooling | PR #912 | reuse `canary-universal-e2e-stability-certification-v1` schema v1; first real repeated-run physical baseline remains separate evidence |",
    "| Factual stability certification | merged | PR #912; lifecycle #914 | reuse `canary-universal-e2e-stability-certification-v1` schema v1; first real repeated-run physical baseline remains separate evidence |",
)
replace_once(
    program,
    "1. complete active `E2E-QRI-022` PR #912 as a deterministic retained-evidence certification contract without adding execution, retry or scheduling;\n2. after the contract merges, select exactly one stable physical scenario and explicit retained artifact population for the first repeated-run baseline;\n3. keep artifact collection/retention and any nightly execution seam separate until that factual baseline proves the need.",
    "1. `E2E-QRI-022` deterministic retained-evidence certification is delivered through PR #912 and lifecycle-closed through PR #914;\n2. select exactly one stable physical scenario and explicit retained artifact population for the first factual repeated-run baseline;\n3. keep artifact collection/retention and any nightly execution seam separate until that baseline proves the need.",
)

changelog = Path("docs/agents/CHANGELOG.md")
text = changelog.read_text(encoding="utf-8")
lines = text.splitlines()
matches = [i for i, line in enumerate(lines) if "canary-universal-e2e-stability-certification-v1" in line]
if len(matches) != 1:
    raise SystemExit(f"{changelog}: expected one stability-certification entry, found {len(matches)}")
lines[matches[0]] = "- Adds the merged `canary-universal-e2e-stability-certification-v1` schema-version-1 contract through PR #912 and lifecycle closure #914 as a deterministic read-only consumer of explicit retained schema-v3 Universal E2E result roots. Exact scenario/server/client/datapack/tier cells preserve every attempt and classify only complete minimum-sized clean-pass sets as `pass`; mixed evidence such as 9/10 is `unstable`, all failures are `fail`, insufficient evidence is `not-evaluated`, and missing provenance, duplicate identities or historical success without cleanup proof are `blocked`. The tool reports exact failure/divergence and nearest-rank duration distributions, adds no scenario runner/retry/downloader/retention/schedule and does not claim a physical repeated-run baseline from contract tests."
changelog.write_text("\n".join(lines) + "\n", encoding="utf-8")

archive = Path("docs/agents/tasks/archive/CAN-20260725-e2e-qri-022-stability-certification.md")
replace_once(archive, 'related_pr: "912"', 'related_pr: "912, 914"')
replace_once(archive, "- Lifecycle closure PR: pending final linkage.", "- Lifecycle closure PR: #914.")
replace_once(
    archive,
    "Delivery PR #912 is merged. This archive record releases all E2E-QRI-022 owned paths; final closure linkage and the fresh physical E2E outcome are added before the docs-only lifecycle PR is merged.",
    "Delivery PR #912 is merged. Lifecycle closure PR #914 releases all E2E-QRI-022 owned paths. The first factual physical repeated-run baseline remains separate follow-up work.",
)
