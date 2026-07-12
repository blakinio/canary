---
task_id: CAN-20260712-gamestore-balance-packets
coordination_id: ""
status: completed
agent: "OpenAI Codex"
branch: agent/fix-gamestore-balance-packets
base_branch: main
created: 2026-07-12T20:00:00Z
updated: 2026-07-12T20:40:00Z
last_verified_commit: "49dbc17cb8e67fd5f076a06b66074ef02b3f3a13"
risk: low
related_issue: "opentibiabr/canary#3742"
related_pr: "blakinio/canary#187"
depends_on: []
blocks: []
owned_paths:
  - data/libs/gamestore/senders.lua
  - data/libs/gamestore/player.lua
  - data/libs/gamestore/parsers.lua
  - tools/ai-agent/test_gamestore_balance_packets.py
modules_touched:
  - GameStore
reuses:
  - existing modular GameStore sender/player/parser boundaries
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Send one current coin-balance snapshot after each successful GameStore balance mutation, without the stale pre-mutation snapshot and parser-level duplicate reported by upstream #3742.

# Acceptance criteria

- [x] Updating and updated packet states are emitted in mutation order.
- [x] The purchase parser does not repeat the mutation-owned balance packet.
- [x] Opening the Store still sends a completed initial balance update.
- [x] Focused regression contract covers regular, transferable and combined balances.
- [x] Module catalogue impact reviewed: no reusable/public interface change.
- [x] Final applicable CI passed on the merged head.
- [x] Autonomous merge gate satisfied.

# Confirmed context

- Target/base/head repositories are all `blakinio/canary`; upstream is read-only.
- Upstream issue #3742 reports duplicated disabled reasons and duplicated coin balances.
- Current modular `senders.lua` already deduplicates disabled reasons with zero-based indices.
- The remaining defect was `sendStoreBalanceUpdating(..., true)` sending a balance before mutation, followed by a second parser-level balance after `makeCoinTransaction`.
- Closed upstream PRs #3744/#3753 provide corroborating behavior but target the obsolete monolithic GameStore file.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| Modular GameStore | sender/player/parser ownership | `data/libs/gamestore/**` | Preserves current fork architecture |
| Upstream PRs #3744/#3753 | behavioral evidence only | reviewed diffs | Confirms intended packet sequence without copying obsolete layout |

# Ownership and overlap check

- Open PR changed-file lists were inspected before implementation and after main refreshes.
- No open PR touches the three GameStore modules or the focused test.
- Shared agent documentation is refreshed from current main.

# Current state

PR #187 passed all applicable checks and was squash-merged as `49dbc17cb8e67fd5f076a06b66074ef02b3f3a13`.

# Plan

1. Completed. This archive record and changelog are the final documentation follow-up.

# Work log

## 2026-07-12T20:40:00Z

- Changed GameStore packet sequencing in sender, player and parser modules.
- Added focused static contract tests.
- Reviewed complete four-file behavior diff.
- Initial refreshed-head autofix, repository CI, Achievement Validation and AI Agent Tools all passed.
- No map, assets, protocol opcode, database or cross-repository contract changed.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Adapt, do not copy, upstream patch | fork GameStore is modularized | none |
| Mutation helpers own the final balance snapshot | prevents stale and duplicate parser packets | none |

# Files and interfaces

| Path | Purpose | Status |
|---|---|---|
| `data/libs/gamestore/senders.lua` | marker and initial Store balance sequence | complete |
| `data/libs/gamestore/player.lua` | mutation-owned updated balance | complete |
| `data/libs/gamestore/parsers.lua` | remove duplicate snapshot | complete |
| `tools/ai-agent/test_gamestore_balance_packets.py` | regression contract | complete |

# Validation and CI

| Commit | Check | Result | Notes |
|---|---|---|---|
| `b07512e5...` | autofix.ci run 576 | passed | final result verified |
| `b07512e5...` | CI run 830 | passed | final result verified |
| `b07512e5...` | AI Agent Tools run 348 | passed | focused test included |
| `b07512e5...` | Achievement Validation run 58 | passed | final result verified |

# Failed approaches and dead ends

- The raw upstream diff targets the old monolithic `data/modules/scripts/gamestore/init.lua`; applying it directly would discard the fork's modular boundaries.

# Risks and compatibility

- Runtime: low; packet order changes only around existing balance mutations.
- Data/migration: none.
- Security: none.
- Backward compatibility: packet types and payload structure are unchanged.
- Cross-repo rollout: none; no OTClient contract change.
- Rollback: revert the squash merge.

# Remaining work

None.

# Handoff

## Start here

Review PR #187 current head, checks, comments, review threads and exact changed paths.

## Do not repeat

Do not port the obsolete monolithic upstream patch or reimplement disabled-reason deduplication.

## Required reads

- `AGENTS.md`
- `docs/agents/ACTIVE_WORK.md`
- `docs/agents/MODULE_CATALOG.md`
- this task and PR #187

## Open questions

None.

# Completion

- Final status: merged
- PR: https://github.com/blakinio/canary/pull/187
- Merge commit: `49dbc17cb8e67fd5f076a06b66074ef02b3f3a13`
- Catalogue updated: not required; no reusable/public interface changed
- Changelog updated: yes
- Archived at: `docs/agents/tasks/archive/CAN-20260712-gamestore-balance-packets.md`
