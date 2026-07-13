---
task_id: CAN-20260713-wheel-15-25-runtime-completion
coordination_id: ""
status: active
agent: GPT-5.6 Thinking
branch: feat/wheel-15-25-runtime-completion
base_branch: main
created: 2026-07-13T06:22:00Z
updated: 2026-07-13T06:22:00Z
last_verified_commit: ac218d540d9b357f6d895d4d1fc38326f47071d4
risk: high
related_issue: ""
related_pr: ""
depends_on:
  - PR #220
  - PR #229
blocks: []
owned_paths:
  - src/creatures/players/components/wheel/**
  - src/creatures/combat/**
  - src/creatures/players/**
  - src/game/**
  - src/server/network/protocol/**
  - data/scripts/spells/**
  - data/modules/scripts/taskboard/**
  - tests/unit/players/**
  - tests/integration/**
  - docs/ai-agent/OTS_AI_WHEEL_OF_DESTINY_VALIDATION.md
  - docs/ai-agent/OTS_AI_WHEEL_OF_DESTINY_VALIDATION_PROJECT.md
  - docs/agents/ACTIVE_WORK.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
modules_touched:
  - Wheel of Destiny runtime
  - spell runtime
  - vocation stance state
  - Taskboard official packet shim
  - Wheel persistence and protocol tests
reuses:
  - PlayerWheel
  - existing spell Combat and chain-target helpers
  - official Taskboard packet shim
  - Wheel validation scanners and runtime plan
public_interfaces:
  - official-client 15.25 vocation-specific player data
  - Wheel spell/augment names
  - persisted purchased Hunting Task Shop Wheel points
cross_repo_tasks: []
---

# Goal

Complete the explicitly tracked Tibia 15.25 Wheel of Destiny runtime gaps without emulating new mechanics through obsolete spells: vocation stances and replacement spells, remaining Revelation/passive behavior, Blessing critical healing, Strong Ice Wave geometry, Hunting Task Shop Wheel points, and end-to-end regression coverage.

# Acceptance criteria

- [ ] New 15.25 stance state is implemented for Knight, Paladin, Sorcerer, and Druid with official restrictions and runtime effects.
- [ ] Shield Bash, Shield Slam, Divine Barrage, Ethereal Barrage, Death Echo, Forked Glacier, Forked Thorns, and Thousand Fist Blows are registered and execute their documented behavior.
- [ ] Wheel augments point to the new spell names and no obsolete spell is silently treated as equivalent.
- [ ] Combat Mastery, Beam Mastery, Lord of Destruction, Focus Mastery, Guiding Presence, Sanctuary, and Blessing critical healing match the captured 15.25 baseline where authoritative values are available.
- [ ] Strong Ice Wave base and augmented geometry are backed by reproducible evidence and deterministic tests.
- [ ] Hunting Task Shop sells a bounded, persisted maximum of 50 Wheel points without treating the whole task-points balance as Wheel points.
- [ ] End-to-end protocol, DB/KV round-trip, failure-injection, and gameplay scenario tests cover the completed behavior.
- [ ] Wheel validation documentation is updated after every behavior change.
- [ ] Module catalogue and changelog impacts are handled.
- [ ] Required CI passes on the final head and the autonomous merge gate is satisfied.

# Confirmed context

- PR #220 and PR #229 are merged to `main`.
- `docs/ai-agent/OTS_AI_WHEEL_OF_DESTINY_VALIDATION.md` explicitly leaves six runtime gaps open.
- PR #169 merged deterministic Wheel, protocol, and Task Shop audit tools; these are reused as evidence and regression checks.
- The June 16, 2026 Tibia 15.25 baseline documents the new spells, stances, passive/Revelation reworks, critical healing, and Task Shop point source.
- The task must not modify `.otbm`, `items.otb`, client assets, secrets, or upstream repositories.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| PlayerWheel | Extend existing Wheel state/effect hooks | `src/creatures/players/components/wheel/**` | Existing authoritative Wheel state and runtime integration |
| Spell Combat runtime | Register new spells and use existing formula/area/chain mechanisms | `data/scripts/spells/**`, `src/creatures/combat/**` | Avoids a second combat system |
| Official Taskboard shim | Extend packet handling and persistence | `data/modules/scripts/taskboard/taskboard.lua` | Existing 15.25 opcode surface |
| Wheel validation audit | Re-run and extend deterministic checks | `tools/ai-agent/wheel_*validation.py` | Existing evidence-based regression tooling |
| PR #220 tests | Extend focused Wheel unit coverage | `tests/unit/players/wheel_validation_test.cpp` | Existing baseline for Wheel invariants |

# Ownership and overlap check

- Open PRs inspected: no open PR matched Wheel, stance, Taskboard, Blessing, or Strong Ice Wave implementation work.
- Active tasks inspected: `docs/agents/ACTIVE_WORK.md`; its Wheel audit row is stale because PR #169 is merged.
- Overlaps: none confirmed.
- Resolution: this task owns the listed runtime/test/docs paths until completion.

# Current state

The existing Wheel is hardened and partially aligned with 15.25, but the six explicit runtime gaps in the validation handoff remain unimplemented.

# Plan

1. Capture exact current source and official 15.25 behavior for every missing mechanic.
2. Implement and test stance state plus replacement spells.
3. Implement remaining Revelation/passive behavior, Blessing critical healing, and Strong Ice Wave geometry.
4. Implement bounded persisted Hunting Task Shop Wheel points.
5. Add protocol, persistence, rollback, and gameplay scenario regression tests.
6. Keep both Wheel validation documents, task record, catalogue, changelog, and PR body synchronized.
7. Run full required CI, repair root causes, review final diff, and squash-merge.

# Work log

## 2026-07-13T06:22:00Z

- Changed: created the task branch and durable task record.
- Learned: PR #169 is merged despite the stale ACTIVE_WORK row; no active implementation PR overlaps the owned paths.
- Failed/blocked: none.
- Result: implementation discovery may proceed.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Extend PlayerWheel and existing spell/Taskboard systems | Repository reuse rules prohibit duplicate managers or parsers | none yet |
| Keep unsupported behavior explicit until authoritative evidence exists | Evidence-based validation rule from Wheel and world-validation docs | none |

# Files and interfaces

| Path/interface/config/schema | Purpose | Status |
|---|---|---|
| `src/creatures/players/components/wheel/**` | 15.25 Wheel/passive integration | discovery |
| `data/scripts/spells/**` | replacement spell registration/runtime | discovery |
| `data/modules/scripts/taskboard/taskboard.lua` | bounded Wheel-point shop | discovery |
| `tests/**` | deterministic unit/integration/runtime coverage | planned |
| `docs/ai-agent/OTS_AI_WHEEL_OF_DESTINY_VALIDATION.md` | durable findings/change log | active |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| ac218d540d9b357f6d895d4d1fc38326f47071d4 | baseline main | verified | PR #220 and #229 merged; prior CI green |

Never write `passed` without verification.

# Failed approaches and dead ends

- Direct sandbox `git clone` cannot resolve `github.com`; repository writes and current-file reads use the GitHub connector. A previously generated source archive is used only for local navigation and must be refreshed file-by-file from current `main` before committing.

# Risks and compatibility

- Runtime: high; combat, healing, cooldown, stance, and packet paths are affected.
- Data/migration: purchased Task Shop points require bounded persistent state and recovery tests.
- Security: malformed official-client packets and duplicate purchases must be rejected atomically.
- Backward compatibility: legacy profiles must remain safe; official 15.25 behavior must be feature-gated where packet layouts differ.
- Cross-repo rollout: no protocol field change is planned; if required, create and register an atomic Canary/OTClient contract before merge.
- Rollback: squash commit can be reverted; new persisted counter must default to zero and tolerate absence.

# Remaining work

1. Publish the draft PR and update ACTIVE_WORK.
2. Map exact current source and packet surfaces.

# Handoff

## Start here

Read this task, both Wheel validation documents, PR #220, and the current branch diff.

## Do not repeat

Do not reopen already fixed WOD-001 through WOD-029 without new evidence. Do not map new spells onto obsolete spell names.

## Required reads

- `AGENTS.md`
- `docs/agents/ACTIVE_WORK.md`
- `docs/agents/MODULE_CATALOG.md`
- `docs/ai-agent/OTS_AI_WHEEL_OF_DESTINY_VALIDATION.md`
- `docs/ai-agent/OTS_AI_WHEEL_OF_DESTINY_VALIDATION_PROJECT.md`

## Open questions

- Exact Strong Ice Wave scene geometry must be reconstructed from authoritative visual evidence before implementation.
- Exact official-client stance packet field mapping must be confirmed from the current protocol profile and maintained client implementation.

# Completion

- Final status: active
- PR:
- Merge commit:
- Catalogue updated: pending
- Changelog updated: pending
- Archived at:
