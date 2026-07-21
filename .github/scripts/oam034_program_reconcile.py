from pathlib import Path
import re

PROGRAM = Path("docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md")
text = PROGRAM.read_text(encoding="utf-8")


def replace_once(old: str, new: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"expected exactly one occurrence, found {count}: {old[:80]!r}")
    text = text.replace(old, new, 1)


replace_once("updated: 2026-07-21T23:22:22+02:00", "updated: 2026-07-22T00:35:00+02:00")
replace_once(
    'last_verified_commit: "d83563943e298df33edd084e944812464b8a3ff2"',
    'last_verified_commit: "0ace0e6802501f1752405c4e15d75619171dd4cf"',
)

oam033_row = "| OAM-033 | `charms → ADAPT` | target `c887318a676998da5ef3224a3aa8d1e0df75e607`; feature `5ecc72762feb6bda8f6549ac4238a75247752449`; lifecycle `d83563943e298df33edd084e944812464b8a3ff2` |"
oam034_row = "| OAM-034 | `creature-definitions → ADAPT` | target `566b3b001987f6f452663b77c380e6405bfc541b`; feature `2a63c4b1efe2a20bf653b419ffd6baea6cb2ee0d`; lifecycle `0ace0e6802501f1752405c4e15d75619171dd4cf` |"
replace_once(oam033_row, oam033_row + "\n" + oam034_row)

durable = """# OAM-034 durable completion

Final disposition:

```text
creature-definitions ADAPT
```

Task-start baselines were Canary `ab2fb5548260544f42f786d11d4dd1b600c39a06`, Otheryn `2fe646dfff3d4fc0672c3fbeca85708dabc4ce87`, fresh upstream Canary `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`, and maintained OTClient `465b7a2192b176cf8cb9d58e000c38863e4a6e4c`. Canonical `creature-definitions` has no fundamental dependencies and owns monster definition data; Creature AI, spawns, raids and boss encounter orchestration remain separately owned.

Merged legacy PR #192 supplied the exact bounded donor. OAM-034 adapted six production corrections that remained absent from task-start Otheryn and fresh upstream while current legacy preserved the reviewed fixes: Agrestic Chicken gained `BESTY_RACE_BIRD`; Terrified Elephant gained `BESTY_RACE_MAMMAL`; alternate Eradicator changed `bossRaceId` from `1225` to `1226`; Monk's Apparition changed Bestiary `raceId` from `1946` to `2636`; Haunted Dragon gained `BESTY_RACE_DRAGON`; and Crypt Warrior gained Bestiary `raceId = 1995` plus `BESTY_RACE_UNDEAD`. PR #192 validator infrastructure, Cyclopedia logs and unrelated governance paths were excluded.

Otheryn PR #69 final head `dabc868c5ff9ca8009f20f1eb90645937ff18e22` changed exactly ten intended paths: six production definitions, focused proof, test registration, target evidence and active task checkpoint. Autofix.ci #193 run `29871761403`, Repository Audit #29 run `29871761411`, CI #235 run `29871761846`, and Required #220 run `29871761506` succeeded. Linux-debug build, Canary datapack runtime smoke, schema import and full `Run Tests` succeeded; the suite completed `423/423`, including both focused `Oam034CreatureDefinitionsAdaptTest` cases. Test-log artifact `8511786128` has digest `sha256:a53b92d60e34069d5fd0f52cd1ad94957edf757c2e8dd29c13ca5f2ec9ae30be`. Comments/reviews/threads were empty, target `main` had no task-start drift, and PR #69 merged by expected-head squash as `566b3b001987f6f452663b77c380e6405bfc541b`.

Canary governance PR #701 final head `37a58be7df77e7875d8faaffa9b5c0939fec6794` changed exactly the OAM-034 revalidation report and active-task record. The initial Ownership failure was limited to a missing checkpoint `pr` field and was repaired without scope or evidence change. Final Agent Task Ownership #3243 run `29872921471` and final-gate CI #4398 run `29872921548` succeeded; comments/reviews/threads were empty, non-overlapping E2E drift was audited, and PR #701 merged by expected-head squash as `2a63c4b1efe2a20bf653b419ffd6baea6cb2ee0d`.

Authoritative lifecycle PR #703 final head `35a9274ba157fc61fb82aed47e8d339499a7a9a6` changed exactly the active-delete/archive-add lifecycle paths. Agent Task Ownership #3245 run `29873136331` and final-gate CI #4399 run `29873136415` succeeded; comments/reviews/threads were empty, Canary `main` had no drift from the governance merge, and PR #703 merged by expected-head squash as `0ace0e6802501f1752405c4e15d75619171dd4cf`.

OAM-034 does not claim full monster catalogue parity, exhaustive creature stats, loot, spells, resistances or immunities, Creature AI, spawn placement, raid behavior, boss encounter mechanics, Bestiary or Bosstiary runtime correctness, protocol/client compatibility, persistence correctness, map/asset/schema/deployment parity, physical-client creature E2E closure, or full Real Tibia parity.

"""
marker = "# Current state\n"
if text.count(marker) != 1:
    raise SystemExit("expected exactly one Current state marker")
text = text.replace(marker, durable + marker, 1)

current_state_pattern = re.compile(
    r"# Current state\n\n```text\n.*?```\n\nNo OAM implementation task is active in this reconciliation record\.\n",
    re.S,
)
current_state = """# Current state

```text
Canary reconciliation base: 0ace0e6802501f1752405c4e15d75619171dd4cf
Otheryn target head after OAM-034: 566b3b001987f6f452663b77c380e6405bfc541b
maintained OTClient: 465b7a2192b176cf8cb9d58e000c38863e4a6e4c
OAM-001..OAM-034: feature/lifecycle complete
OAM-034 task: archived in Canary
OAM-035: NOT STARTED
```

No OAM implementation task is active in this reconciliation record.
"""
text, count = current_state_pattern.subn(current_state, text, count=1)
if count != 1:
    raise SystemExit("failed to replace Current state block")

queue_pattern = re.compile(r"# Queue\n\n.*?\n# Invariants and known gaps", re.S)
queue = """# Queue

| Package | Status | Next action |
|---|---|---|
| OAM-001..OAM-034 | completed | preserve durable evidence |
| OAM-035+ | planned, not active | only after this reconciliation merges and the Otheryn OAM-034 target checkpoint is archived: perform fresh live-state/open-PR/ownership and exact target/upstream/legacy preflight, then select one dependency-valid canonical package |

# Invariants and known gaps"""
text, count = queue_pattern.subn(queue, text, count=1)
if count != 1:
    raise SystemExit("failed to replace Queue block")

invariant = "- OAM-034 does not claim full monster catalogue parity, exhaustive creature stats, loot, spells, resistances or immunities, Creature AI, spawn placement, raid behavior, boss encounter mechanics, Bestiary or Bosstiary runtime correctness, protocol/client compatibility, persistence correctness, map/asset/schema/deployment parity, physical-client creature E2E closure, or full Real Tibia parity.\n"
exact_marker = "\n# Exact next task\n"
if text.count(exact_marker) != 1:
    raise SystemExit("expected exactly one Exact next task marker")
text = text.replace(exact_marker, "\n" + invariant + exact_marker, 1)

next_task_pattern = re.compile(r"# Exact next task\n\n.*\Z", re.S)
next_task = """# Exact next task

Merge this program-only OAM-034 completion reconciliation after exact-head Ownership/CI/review gates. Only then may the Otheryn OAM-034 target checkpoint be archived; only after that archive merges may a fresh OAM-035 preflight begin. OAM-035 is NOT STARTED by this record.
"""
text, count = next_task_pattern.subn(next_task, text, count=1)
if count != 1:
    raise SystemExit("failed to replace Exact next task")

PROGRAM.write_text(text, encoding="utf-8")
