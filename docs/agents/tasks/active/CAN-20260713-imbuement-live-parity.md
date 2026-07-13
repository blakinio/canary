---
task_id: CAN-20260713-imbuement-live-parity
program_id: ""
coordination_id: ""
status: in_progress
agent: "GPT-5.6 Thinking"
branch: fix/imbuement-live-parity
base_branch: main
created: 2026-07-13T14:20:00+02:00
updated: 2026-07-13T14:20:00+02:00
last_verified_commit: "3ad10132cbd76adc42f946da3ca3077e5bd6bbd0"
risk: medium
related_issue: "IMB-001, IMB-002, IMB-003, IMB-006"
related_pr: "pending"
depends_on:
  - merged Imbuement audit PR #166
  - merged Forgotten Knowledge storage repair PR #206
  - merged Vibrancy scroll repair PR #239
blocks: []
owned_paths:
  exclusive:
    - data/XML/imbuements.xml
    - tools/ai-agent/imbuement_validation.py
    - tools/ai-agent/test_imbuement_validation.py
    - tools/ai-agent/imbuement_storage_validation.py
    - tools/ai-agent/test_imbuement_storage_validation.py
    - tests/fixture/core/XML/imbuements.xml
    - tests/unit/players/imbuements/imbuements_test.cpp
    - docs/ai-agent/IMBUEMENT_VALIDATION_REPORT.md
    - docs/ai-agent/IMBUEMENT_RUNTIME_TEST_PLAN.json
    - docs/agents/CHANGELOG.md
    - docs/agents/tasks/active/CAN-20260713-imbuement-live-parity.md
  shared: []
  read_only:
    - src/creatures/players/imbuements/imbuements.cpp
    - src/creatures/players/imbuements/imbuements.hpp
    - src/creatures/players/player.cpp
    - src/server/network/protocol/protocolgame.cpp
    - data-otservbr-global/lib/core/storages.lua
    - data-otservbr-global/scripts/quests/**
    - data-otservbr-global/npc/**
modules_touched:
  - Imbuement XML registry
  - Imbuement deterministic validators
  - Imbuement focused tests and report
reuses:
  - tools/ai-agent/imbuement_validation.py
  - tools/ai-agent/imbuement_storage_validation.py
  - .github/workflows/imbuement-validation.yml
  - tests/shared/imbuements/imbuements_test_fixture.hpp
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Align the active Canary Imbuement registry with the current live Tibia mechanics for the confirmed IMB-001 fee model, IMB-002 Strike values and IMB-003 Basic Punch materials, and resolve IMB-006 only when exact active quest storage/value evidence exists in the repository.

# Acceptance criteria

- [ ] Base application fees are exactly 7,500 / 60,000 / 250,000 gold with 100% success and no protection surcharge.
- [ ] Basic, Intricate and Powerful Strike are exactly 5% critical chance with +5% / +15% / +40% critical damage.
- [ ] Basic Punch consumes item 10281 x25 and higher tiers retain their verified cumulative material chains.
- [ ] Protocol-visible base price/percent/protection fields match the same live model without a new protocol contract.
- [ ] IMB-006 storages are changed only if exact active completion storage and accepted value semantics are proven; otherwise the blocker remains explicit.
- [ ] Focused deterministic and C++ regression coverage is updated.
- [ ] Validation report, runtime plan and agent changelog are current.
- [ ] Current-head GitHub checks are inspected job-by-job and pass before merge.
- [ ] No map, items.otb, binary asset, database schema, production configuration, client or ACTIVE_WORK.md change.
- [ ] Autonomous merge gate is satisfied and the task is archived in a separate cleanup PR.

# Confirmed context

- Writable repository: `blakinio/canary` only.
- Base main at task start: `3ad10132cbd76adc42f946da3ca3077e5bd6bbd0`.
- User selected current live Tibia mechanics as the authoritative target, not the historical chance/protection model.
- Current XML uses historical base values, Strike values and Basic Punch source data.
- `Player::onApplyImbuement` charges `BaseImbuement::price` and applies deterministically; the current protocol serializes price, percent and protection price from the same base registry.
- Existing validators already encode the current-reference fee, Strike and Punch values.
- IMB-004 and IMB-005 remain preserved and are not reopened.
- Open PR inspection found no Imbuement implementation PR or owned-path overlap. The universal E2E PR #245 is separate and does not own these paths.
- `docs/agents/ACTIVE_WORK.md` is read-only and will remain unchanged.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| PR #166 | deterministic Imbuement audit | validators/report/workflow | canonical scanner and evidence format |
| PR #206 | exact Forgotten Knowledge storage policy | storage validator/tests | preserve repaired 45489..45495 groups |
| PR #239 | Vibrancy scroll mappings and atomicity tests | XML/validator/C++ tests | preserve both repaired scroll paths |
| Current registry loader | base/effect/material parsing | `imbuements.cpp` | no new parser or runtime subsystem required |

# Ownership and overlap check

- Program record: none required for this bounded repair.
- Open PRs inspected: all current open PRs plus Imbuement search; no overlap found.
- Active tasks inspected: current index and exact Imbuement task searches; no active overlap found.
- Ownership checker result: unavailable locally because `github.com` DNS resolution fails; GitHub ownership CI will be used as separate evidence.
- Exclusive claims: listed in frontmatter.
- Shared claims: none.
- Read-only dependencies: Player/runtime/protocol and quest storage sources.
- Resolution: proceed on a new branch and draft PR; do not modify runtime C++ unless XML-only alignment proves insufficient.

# Current state

Branch created. Task claimed before implementation. Reference and current code paths have been inspected. IMB-006 evidence search is in progress.

# Plan

1. Prove or reject candidate Dangerous Depths and Dream Courts completion storages from active scripts.
2. Apply the smallest XML changes for confirmed live values.
3. Update validators and focused tests so the repaired values are exact zero-finding contracts.
4. Update report, runtime plan and changelog.
5. Inspect final diff, run existing focused workflow and full CI, repair failures, merge, then archive.

# Work log

## 2026-07-13T14:20:00+02:00

- Changed: created branch and durable task record.
- Learned: price/percent/protection are registry-driven in both server application and protocol presentation.
- Failed/blocked: local checkout commands remain unavailable because `github.com` cannot be resolved.
- Result: implementation may proceed through GitHub API and CI; no local test is claimed.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Target current live Tibia | explicit user decision | none |
| Reuse XML registry and existing validators | current runtime already consumes these values | none |
| Do not invent IMB-006 storage/value | identifier safety and incomplete quest completion proof | none |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `data/XML/imbuements.xml` | exclusive | live fees, Strike, Punch and proven unlocks | planned |
| existing Imbuement validators/tests | exclusive | exact regression contract | planned |
| report/runtime plan/changelog | exclusive | durable evidence and behavior record | planned |
| Player/protocol/quest sources | read_only | prove runtime and storage semantics | inspected/in progress |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| base `3ad10132...` | `getent hosts github.com` | unavailable | no DNS result |
| base `3ad10132...` | `git ls-remote https://github.com/blakinio/canary.git HEAD` | unavailable | `Could not resolve host: github.com` |
| pending | Agent Task Ownership | not-run | GitHub CI required |
| pending | Imbuement Validation | not-run | existing focused workflow |
| pending | full CI | not-run | concrete jobs must be inspected |

Never write `passed` without verification on the stated commit.

# Failed approaches and dead ends

- Several guessed quest-script paths returned 404; exact paths and storage semantics will be discovered from repository evidence rather than inferred from names.

# Risks and compatibility

- Runtime: wrong fee/effect/material values directly affect gameplay; exact tests required.
- Data/migration: XML-only data change, no schema migration.
- Security: none.
- Backward compatibility: legacy client protocol fields retain their existing shape; values change to the selected live mechanics.
- Cross-repo rollout: none expected; no protocol shape change.
- Rollback: revert the squash merge.

# Remaining work

1. Open a draft PR for discovery.
2. Complete IMB-006 evidence search.
3. Implement and validate confirmed repairs.

# Handoff

## Start here

Continue only on branch `fix/imbuement-live-parity` and its draft PR. Preserve PR #206 and #239 behavior.

## Do not repeat

Do not create a second Imbuement parser, do not restore the historical chance/protection model, and do not invent quest storage IDs or completion values.

## Required reads

- `AGENTS.md`
- `docs/agents/README.md`
- `docs/agents/MODULE_CATALOG.md`
- `docs/ai-agent/IMBUEMENT_VALIDATION_REPORT.md`
- archived task `CAN-20260713-imbuement-vibrancy-scrolls`
- current XML, validators, Player/runtime/protocol and quest storage sources

## Open questions

- Which exact active Dangerous Depths and Dream Courts storage/value pairs represent the current live unlock conditions for Powerful Featherweight and Vibrancy?

# Completion

- Final status: in progress
- PR: pending
- Merge commit: pending
- Program record updated: not applicable
- Catalogue updated: pending determination
- Changelog updated: pending
- Archived at: pending
