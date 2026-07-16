---
task_id: CAN-20260714-tibia-system-decomposition-combat-weapons-vocations
program_id: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
coordination_id: REAL-TIBIA-SYSTEM-DECOMPOSITION-TSD-005
status: merged
agent: "GPT-5.6 Thinking"
branch: docs/tibia-system-decomposition-combat-weapons-vocations
base_branch: main
created: 2026-07-14T21:00:00+02:00
updated: 2026-07-14T22:38:41+02:00
last_verified_commit: "68b9836cc8e6f55add9a6f3f8d7919e031defc50"
risk: low
related_issue: ""
related_pr: "#362"
depends_on:
  - completed and archived TSD-004
blocks:
  - TSD-006 creatures hunting raids and bosses decomposition
  - TSD-007 items and economy decomposition
owned_paths:
  exclusive:
    - docs/agents/tasks/archive/CAN-20260714-tibia-system-decomposition-combat-weapons-vocations.md
    - docs/agents/programs/TIBIA_SYSTEM_DECOMPOSITION_PROGRAM.md
  shared: []
  read_only:
    - docs/agents/ACTIVE_WORK.md
    - docs/agents/real-tibia/**
    - tools/agents/**
    - .github/workflows/**
    - src/**
    - data/**
    - tests/**
modules_touched:
  - Real Tibia module registry
  - combat conditions
  - weapons
reuses:
  - existing Real Tibia registry-as-code
  - existing deterministic generator and discovery commands
  - source-role-aware Upstream Intelligence mapper
public_interfaces:
  - bounded combat conditions and weapon discovery records
cross_repo_tasks: []
---

# Goal

Complete TSD-005 as a bounded combat, weapons and vocations inventory while preserving existing combat, spell, vocation, progression, persistence and protocol boundaries.

# Final result

PR #362 was squash-merged on `2026-07-14T20:38:41Z`.

- Task-start base: `f163ed8e3b3d51e65c7fef1bc03830b12b2e6bfa`.
- Final feature head: `af60fffe398ffcc5dcccd659133b7d4796690b19`.
- Squash merge SHA: `68b9836cc8e6f55add9a6f3f8d7919e031defc50`.
- Pull request: #362.
- Changed files: 14.
- Registry records: 39 → 41.
- Registry modules added: 2.
- Registry modules modified: 0.
- Categories/schema/generator/mapper/workflows changed: no.
- Runtime/gameplay/protocol/client/database/map/OTBM/datapack/assets/E2E changed: no.

Records added:

- `combat-conditions`;
- `weapons`.

Stable records preserved unchanged:

- `combat`;
- `spells`;
- `vocations`;
- `weapon-proficiency`;
- `character-progression`;
- `player-persistence`;
- `protocol`.

# Candidate classification

- Targeting, PvP/protection permissions, formulas, damage/healing, mitigation, ordering, areas, chains and critical/leech remain findings/capabilities inside `combat`.
- Condition creation, timed lifecycle, stacking/refresh, execution, subclasses and serialization are represented by `combat-conditions`.
- Weapon registry, wield/use checks, melee/distance/wand implementations, formula/resource surfaces and combat handoff are represented by `weapons`.
- Individual condition, weapon and vocation types remain inside their parent records.
- Spells, vocations and Weapon Proficiency remain already covered.

# Review-fix history

1. The initial client-source focused test incorrectly expected external `src/**` paths to remain unmapped. It was corrected to preserve the explicitly configured client `protocol` bucket while asserting that server-only `combat`, `combat-conditions` and `weapons` are excluded.
2. Older TSD-003/TSD-004 focused tests froze the global registry total at 39. They now assert their package minimum baseline; TSD-005 alone verifies the exact total 41.

Neither repair changed the mapper, module scope or runtime behavior.

# Validation evidence

## Exact final feature head

`af60fffe398ffcc5dcccd659133b7d4796690b19`

- Real Tibia Module Registry #250: success;
- Upstream Intelligence #279: success;
- Agent Task Ownership #1107: success;
- repository CI #2221 / Required: success;
- focused registry tests: success;
- focused source-role mapping tests: success;
- schema and dependency graph validation: success;
- deterministic `generate --check`: success;
- stale/module/lookup-path/exact PR-range `affected`: success;
- changed files reviewed: 14, all within declared task scope;
- PR comments: none;
- reviews requesting changes: none;
- unresolved review threads: none;
- mergeable immediately before merge: yes;
- exact-head merge guard used.

## Ready-state gate

Repository CI #2222 on the unchanged final head:

- Detect Build Scope: success;
- Lua Tests: success;
- Fast Checks: success;
- Linux release: success;
- Required: success.

# Safety boundary confirmed

- documentation, registry metadata, generated navigation and focused tests only;
- no runtime, C++, Lua gameplay, protocol, client, database, map, OTBM, datapack, asset, workflow or E2E implementation change;
- no existing module record changed;
- no second registry, generator, watcher, mapper, parser, renderer or E2E platform;
- no physical source-tree refactor;
- `ACTIVE_WORK.md` unchanged;
- path matching remains discovery-only and does not establish ownership or parity.

# Known limitations

TSD-005 does not prove target legality, PvP permissions, damage/healing formulas, mitigation order, condition timing/stacking/serialization/persistence, weapon hit/damage/resource formulas, vocation interaction, protocol compatibility, runtime behavior, physical-client E2E, Real Tibia parity or Oteryn readiness.

# Next exact task

```text
task: CAN-20260714-tibia-system-decomposition-creatures-hunting-raids-bosses
program: CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
package: TSD-006
branch: docs/tibia-system-decomposition-creatures-hunting-raids-bosses
```

Start only after this lifecycle PR merges and current `main` is re-read.

# Completion

- Final status: merged.
- Feature PR: #362.
- Feature head: `af60fffe398ffcc5dcccd659133b7d4796690b19`.
- Merge commit: `68b9836cc8e6f55add9a6f3f8d7919e031defc50`.
- Merged at: `2026-07-14T20:38:41Z`.
- Archived at: `docs/agents/tasks/archive/CAN-20260714-tibia-system-decomposition-combat-weapons-vocations.md`.
