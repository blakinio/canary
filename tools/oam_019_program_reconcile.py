from pathlib import Path

PROGRAM = Path("docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


text = PROGRAM.read_text(encoding="utf-8")

text = replace_once(
    text,
    'updated: 2026-07-19T13:54:27+02:00\nlast_verified_commit: "5f0656442d6b7856dcc5099e29a78782abaa1170"',
    'updated: 2026-07-19T15:55:00+02:00\nlast_verified_commit: "f62481d7ab2e5d13bb74c53e57a5b79bd1d4eb29"',
    "frontmatter",
)

text = replace_once(
    text,
    '| OAM-018 | `item-decay → REUSE` | target proof `7ba76d2754a060a9a9eec0a23c686aefac725af2`; feature `df97440551ca141b340ff424b1d644430bbb3c28`; lifecycle `5f0656442d6b7856dcc5099e29a78782abaa1170` |',
    '| OAM-018 | `item-decay → REUSE` | target proof `7ba76d2754a060a9a9eec0a23c686aefac725af2`; feature `df97440551ca141b340ff424b1d644430bbb3c28`; lifecycle `5f0656442d6b7856dcc5099e29a78782abaa1170` |\n| OAM-019 | `imbuements → ADAPT` | target `63547f30fc21e495217b8a92fa44aaad2db188ef`; feature `f38832dd160910e76d1576bb2c1221374a6ae8b1`; lifecycle `f62481d7ab2e5d13bb74c53e57a5b79bd1d4eb29` |',
    "completed package row",
)

oam019 = r'''# OAM-019 durable completion

Final disposition:

```text
imbuements ADAPT
```

Task-start baselines were Canary `e551f3fd33c9642399bb1e70d1f2f6383464b936`, Otheryn `7ba76d2754a060a9a9eec0a23c686aefac725af2`, upstream `691614c1a302aee776002ca3851eca399be1a82c`, and OTClient `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`. Canonical `imbuements` depends on completed `combat` and `player-persistence`; `protocol` is an interaction boundary. Fresh task-start ownership review found no overlapping live Imbuement runtime/data writer.

Whole-module `REUSE` was rejected because task-start Otheryn lacked a coherent chain of delivered legacy correctness and data repairs. The accepted bounded donor chain is merged Canary PR #86 for configured-storage filtering, #206 for Powerful Forgotten Knowledge storage reconciliation, #239 for Vibrancy scroll mappings, #251 for the selected confirmed fee/Strike/Punch/Featherweight/Vibrancy data contract, and #282 for direct numeric-ID premium/storage authorization before relevant resource mutation. OAM-019 did not bulk-copy legacy `player.cpp`; only reviewed Imbuement-specific hunks, two isolated policy helpers, exact registry data and focused tests were adapted into the target.

Otheryn PR #43 final head `4e993c4ee160fe03d8575c1b830ef71dde450562` changed exactly ten intended Imbuement runtime/data/test paths and no temporary materializer paths. It passed autofix.ci #121 run `29687711140`, Repository Audit #12 run `29687711133`, CI #142 run `29687711219`, Required #128 run `29687711131`, Linux debug build/runtime smoke/schema import and full CTest `367/367`. The eight new focused OAM-019 tests passed `8/8`. Primary test artifact `8442743109` has digest `sha256:a0ef33bd15be8d004dce89ce5014782990961cb239c50e9f48f19d906694c6e0`. The first macOS smoke wrapper attempt was transient: its artifact showed successful online startup and clean shutdown with empty stderr, and one permitted same-head rerun passed without code changes. Target comments/reviews/threads were empty, target-main drift was none, and PR #43 merged by expected-head squash as `63547f30fc21e495217b8a92fa44aaad2db188ef`.

Canary governance PR #588 final head `42d46421df0f0c5191eaf857f19aa4fa3fe42df9` passed Agent Task Ownership #2607 run `29688560927`, Imbuement Validation #326 run `29688560945`, and full `ci:final-gate` CI #3750 run `29688564115`. Every platform build/test job passed. The first workflow attempt failed only in the Docker Quickstart/Required tail; one permitted same-head failed-jobs rerun passed Docker Quickstart and the overall CI completed successfully without a head change. The PR had exactly two governance paths, zero comments/reviews/threads and no Canary-main drift before merge, then merged by expected-head squash as `f38832dd160910e76d1576bb2c1221374a6ae8b1`.

Authoritative lifecycle PR #590 final head `9b26a10519fbeb3e5bff8587bf48e0b780129bc9` passed Agent Task Ownership #2610 run `29689465413`, Imbuement Validation #328 run `29689465406` and CI #3752 run `29689465487` with Required PASS; heavy build jobs were correctly skipped for lifecycle-only scope. The only Canary-main drift before merge was unrelated E2E work with no overlap in the active/archive OAM-019 paths. The PR had zero comments/reviews/threads and merged by expected-head squash as `f62481d7ab2e5d13bb74c53e57a5b79bd1d4eb29`. No automation-created duplicate archive PR for governance #588 was found, so no duplicate closure was required.

OAM-019 preserves OAM-004 SQL/KV non-atomicity and all previously completed combat, persistence, item and protocol ownership boundaries. It does not claim exhaustive current Real Tibia Imbuement parity, exhaustive equipment eligibility, full live quest-unlock visibility, exact protocol/UI presentation across all clients, physical-client E2E closure, exhaustive combat-math parity, production crash/restart persistence completeness, generic resource transaction atomicity, or changes to generic items, Exaltation Forge, maps, assets, `items.otb`, schema or client code.
'''

marker = 'OAM-018 preserves OAM-004 SQL/KV non-atomicity and completed OAM-003 scheduler/OAM-007 item ownership. It does not claim scheduler fairness or starvation freedom, exact wall-clock decay timing, restart/crash decay recovery, persistence completeness, item move/container transaction atomicity, duplication/loss freedom, static decay metadata parity, exhaustive transform correctness, protocol/client UI parity, or full Real Tibia decay semantics.\n\n# Current state'
text = replace_once(
    text,
    marker,
    'OAM-018 preserves OAM-004 SQL/KV non-atomicity and completed OAM-003 scheduler/OAM-007 item ownership. It does not claim scheduler fairness or starvation freedom, exact wall-clock decay timing, restart/crash decay recovery, persistence completeness, item move/container transaction atomicity, duplication/loss freedom, static decay metadata parity, exhaustive transform correctness, protocol/client UI parity, or full Real Tibia decay semantics.\n\n' + oam019 + '\n# Current state',
    "OAM-019 durable section",
)

text = replace_once(
    text,
    '''Canary reconciliation base: 5f0656442d6b7856dcc5099e29a78782abaa1170
Otheryn target head after OAM-018: 7ba76d2754a060a9a9eec0a23c686aefac725af2
maintained OTClient: 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
OAM-001..OAM-018: feature/lifecycle complete
OAM-018 task: archived
OAM-019: NOT STARTED''',
    '''Canary reconciliation base: f62481d7ab2e5d13bb74c53e57a5b79bd1d4eb29
Otheryn target head after OAM-019: 63547f30fc21e495217b8a92fa44aaad2db188ef
maintained OTClient: 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
OAM-001..OAM-019: feature/lifecycle complete
OAM-019 task: archived
OAM-020: NOT STARTED''',
    "current state",
)

text = replace_once(
    text,
    '| OAM-001..OAM-018 | completed | preserve durable evidence |\n| OAM-019+ | planned, not active | only after this reconciliation merges: perform fresh live-state/open-PR/ownership and exact target/upstream/legacy preflight, then select one dependency-valid canonical package |',
    '| OAM-001..OAM-019 | completed | preserve durable evidence |\n| OAM-020+ | planned, not active | only after this reconciliation merges: perform fresh live-state/open-PR/ownership and exact target/upstream/legacy preflight, then select one dependency-valid canonical package |',
    "queue",
)

text = replace_once(
    text,
    '- OAM-018 does not claim scheduler fairness/starvation freedom, exact wall-clock decay timing, restart/crash recovery, persistence completeness, movement/container atomicity, duplication/loss freedom, static metadata parity, exhaustive transform correctness, protocol/client UI parity, or full Real Tibia decay semantics.\n\n# Exact next task',
    '- OAM-018 does not claim scheduler fairness/starvation freedom, exact wall-clock decay timing, restart/crash recovery, persistence completeness, movement/container atomicity, duplication/loss freedom, static metadata parity, exhaustive transform correctness, protocol/client UI parity, or full Real Tibia decay semantics.\n- OAM-019 does not claim exhaustive Imbuement parity, exhaustive equipment eligibility, full live quest-unlock visibility, client/UI parity, physical-client E2E closure, exhaustive combat math, crash/restart persistence completeness, or generic resource transaction atomicity.\n\n# Exact next task',
    "OAM-019 invariant",
)

text = replace_once(
    text,
    'Merge this program-only OAM-018 completion reconciliation after exact-head Ownership/CI/review gates. Only then may a fresh OAM-019 preflight begin. OAM-019 is NOT STARTED by this record.',
    'Merge this program-only OAM-019 completion reconciliation after exact-head Ownership/CI/review gates. Only then may a fresh OAM-020 preflight begin. OAM-020 is NOT STARTED by this record.',
    "exact next task",
)

PROGRAM.write_text(text, encoding="utf-8")
