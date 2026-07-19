from __future__ import annotations

from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

PROGRAM = Path("docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md")
LIFECYCLE_MERGE = "a3896b67e94990712e00e877666f2bd54dceb22a"

text = PROGRAM.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one anchor, found {count}")
    text = text.replace(old, new, 1)


now = datetime.now(ZoneInfo("Europe/Warsaw")).isoformat(timespec="seconds")
replace_once(
    'updated: 2026-07-19T15:55:00+02:00\nlast_verified_commit: "f62481d7ab2e5d13bb74c53e57a5b79bd1d4eb29"',
    f'updated: {now}\nlast_verified_commit: "{LIFECYCLE_MERGE}"',
    "frontmatter",
)

replace_once(
    '| OAM-019 | `imbuements → ADAPT` | target `63547f30fc21e495217b8a92fa44aaad2db188ef`; feature `f38832dd160910e76d1576bb2c1221374a6ae8b1`; lifecycle `f62481d7ab2e5d13bb74c53e57a5b79bd1d4eb29` |',
    '| OAM-019 | `imbuements → ADAPT` | target `63547f30fc21e495217b8a92fa44aaad2db188ef`; feature `f38832dd160910e76d1576bb2c1221374a6ae8b1`; lifecycle `f62481d7ab2e5d13bb74c53e57a5b79bd1d4eb29` |\n'
    '| OAM-020 | `exaltation-forge → ADAPT` | target `d59207d05ab6dd9450b05d0a6b4d9122fda60489`; feature `2b6ae86539640dfc52323e9d5abbde31d6610c5f`; lifecycle `a3896b67e94990712e00e877666f2bd54dceb22a` |',
    "completed package row",
)

section = r'''
# OAM-020 durable completion

Final disposition:

```text
exaltation-forge ADAPT
```

Task-start baselines were Canary `c353b89b5a7f783cf4ee22fe1ba91850de837a68`, Otheryn `63547f30fc21e495217b8a92fa44aaad2db188ef`, fresh upstream comparison `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`, previous upstream pin `691614c1a302aee776002ca3851eca399be1a82c`, and maintained OTClient `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`. Canonical `exaltation-forge` depends on completed `player-persistence` and `protocol`; interactions with completed `combat` and separately owned `market` did not broaden the package.

Whole-module `REUSE` was rejected because the task-start target and fresh upstream lacked multiple coherent reviewed legacy Forge repairs, while broad rebuild was rejected because the clean upstream-based Forge core remained usable. The accepted bounded donor chain is merged Canary PRs #89, #110, #177, #250, #257, #259, #262, #267 and #283: normal Transfer rules/cost/history, stable history item identity, Dust killer/party/cap behavior, server-authoritative Fusion/Transfer validation, transactional mutation/rollback, reviewed Dust/Fiendish defaults, exact Premium Dust semantics, Avatar/Momentum effect correctness and history amount/action-type correctness. No whole-file legacy `player.cpp` or `protocolgame.cpp` copy was accepted.

Target-local adaptation preserved Otheryn build contracts by registering the five new helper headers in tracked `vcproj/canary.vcxproj`, guarding PCH-provided standard-library includes for non-PCH builds, and registering the exact Forge tests in the target's current CMake layout rather than copying stale donor CMake files. A target-specific `Oam020ExaltationForgeAdaptTest` proved accepted default, authority, effect-gate and transaction boundaries.

Otheryn PR #44 final head `f05787db7f165d0dae0584b3e06c6526f89a42cd` changed exactly 24 intended paths: 23 bounded Forge runtime/data/test/build paths plus one target-specific OAM-020 proof test, with no temporary materializer paths. It passed autofix.ci #142 run `29701626292`, Repository Audit #19 run `29701626282`, CI #164 run `29701626343`, Required #149 run `29701626255`, Fast Checks, Lua Tests, Linux release/runtime smoke, Linux debug compile/schema/CTest, macOS runtime smoke, both Windows build paths and Docker image validation. Full Linux debug CTest completed `393/393` and `Oam020ExaltationForgeAdaptTest` passed `2/2`. Primary test artifact `8446751016` has digest `sha256:1bc0b22f42693c2eaa4404de0b4e66846d399a1046c1620254a493b9bcba5eef`. Target comments/reviews/threads were empty, target-main drift was none, and PR #44 merged by expected-head squash as `d59207d05ab6dd9450b05d0a6b4d9122fda60489`.

Canary governance PR #598 final head `607b8a7af2f9025993964f858498a70e4bc29a38` changed exactly the two OAM-020 governance paths. It passed Agent Task Ownership #2708 run `29702328659` and full `ci:final-gate` CI #3855 run `29702328760`; Fast Checks, Lua Tests, Linux debug tests, Linux release, macOS, both Windows build paths and Docker image validation were green. It had zero comments/reviews/threads. One unrelated OTBM/E2E commit had advanced Canary `main` from the immutable task-start baseline, but its actual changed paths did not overlap OAM-020 governance. PR #598 merged by expected-head squash as `2b6ae86539640dfc52323e9d5abbde31d6610c5f`.

Authoritative lifecycle PR #604 final head `222ee3f7d751c30fd3ea5dfdeab0ffb0b4a1835b` changed exactly the active-delete/archive-add lifecycle paths. It passed Agent Task Ownership #2716 run `29702985616`, draft CI #3862 run `29702985584` and ready-state CI #3863 run `29703010827`; comments/reviews/threads were empty and Canary `main` had no drift from the governance merge before lifecycle merge. PR #604 merged by expected-head squash as `a3896b67e94990712e00e877666f2bd54dceb22a`.

OAM-020 preserves OAM-004 SQL/KV non-atomicity and all previously completed persistence, protocol, combat and item ownership boundaries. It does not claim exhaustive current Real Tibia Forge parity, physical-client Forge E2E closure, unresolved F-014 through F-019 bonus/result/protocol/maintained-client parity, evidence-blocked F-009/F-010 rule parity, or generic market/combat/item/persistence/protocol redesign. It changes no maps, OTBM, `items.otb`, assets, schema or deployment and makes no maintained-OTClient or upstream write.
'''.strip()
replace_once("\n# Current state\n", f"\n{section}\n\n# Current state\n", "OAM-020 durable section")

old_state = '''```text
Canary reconciliation base: f62481d7ab2e5d13bb74c53e57a5b79bd1d4eb29
Otheryn target head after OAM-019: 63547f30fc21e495217b8a92fa44aaad2db188ef
maintained OTClient: 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
OAM-001..OAM-019: feature/lifecycle complete
OAM-019 task: archived
OAM-020: NOT STARTED
```

No OAM implementation task is active in this reconciliation record.'''
new_state = '''```text
Canary reconciliation base: a3896b67e94990712e00e877666f2bd54dceb22a
Otheryn target head after OAM-020: d59207d05ab6dd9450b05d0a6b4d9122fda60489
maintained OTClient: 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
OAM-001..OAM-020: feature/lifecycle complete
OAM-020 task: archived
OAM-021: NOT STARTED
```

No OAM implementation task is active in this reconciliation record.'''
replace_once(old_state, new_state, "current state")

old_queue = '''| OAM-001..OAM-019 | completed | preserve durable evidence |
| OAM-020+ | planned, not active | only after this reconciliation merges: perform fresh live-state/open-PR/ownership and exact target/upstream/legacy preflight, then select one dependency-valid canonical package |'''
new_queue = '''| OAM-001..OAM-020 | completed | preserve durable evidence |
| OAM-021+ | planned, not active | only after this reconciliation merges: perform fresh live-state/open-PR/ownership and exact target/upstream/legacy preflight, then select one dependency-valid canonical package |'''
replace_once(old_queue, new_queue, "queue")

replace_once(
    '- OAM-019 does not claim exhaustive Imbuement parity, exhaustive equipment eligibility, full live quest-unlock visibility, client/UI parity, physical-client E2E closure, exhaustive combat math, crash/restart persistence completeness, or generic resource transaction atomicity.',
    '- OAM-019 does not claim exhaustive Imbuement parity, exhaustive equipment eligibility, full live quest-unlock visibility, client/UI parity, physical-client E2E closure, exhaustive combat math, crash/restart persistence completeness, or generic resource transaction atomicity.\n'
    '- OAM-020 does not claim exhaustive Forge parity, physical-client Forge E2E closure, unresolved F-014 through F-019 server/client result parity, evidence-blocked F-009/F-010 rule parity, or generic cross-domain transaction/persistence redesign.',
    "OAM-020 invariant",
)

replace_once(
    'Merge this program-only OAM-019 completion reconciliation after exact-head Ownership/CI/review gates. Only then may a fresh OAM-020 preflight begin. OAM-020 is NOT STARTED by this record.',
    'Merge this program-only OAM-020 completion reconciliation after exact-head Ownership/CI/review gates. Only then may a fresh OAM-021 preflight begin. OAM-021 is NOT STARTED by this record.',
    "exact next task",
)

PROGRAM.write_text(text, encoding="utf-8")
