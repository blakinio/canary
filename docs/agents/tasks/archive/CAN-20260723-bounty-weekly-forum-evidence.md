---
task_id: CAN-20260723-bounty-weekly-forum-evidence
program_id: CAN-PROGRAM-REAL-TIBIA-PARITY
coordination_id: PREY-BOUNTY-WEEKLY-FORUM-EVIDENCE
status: completed
agent: "Codex"
branch: docs/can-20260723-bounty-weekly-forum-evidence
base_branch: main
created: 2026-07-23T19:08:01+02:00
updated: 2026-07-23T17:31:25Z
last_verified_commit: "704eccb3084e9c0261723cb524d7d352e3268b61"
risk: low
related_issue: ""
related_pr: "828"
depends_on: []
blocks: []
owned_paths:
  exclusive:
    - docs/agents/real-tibia/BOUNTY_AND_WEEKLY_TASKS_FORUM_EVIDENCE.md
    - docs/agents/tasks/active/CAN-20260723-bounty-weekly-forum-evidence.md
  shared: []
  read_only:
    - docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md
    - docs/agents/real-tibia/registry/modules/prey.yaml
    - docs/ai-agent/OTS_BOUNTY_AND_WEEKLY_TASKS_REWORK.md
modules_touched:
  - prey-and-hunting-tasks-evidence
reuses:
  - Real Tibia evidence source registry
  - Real Tibia parity playbook
  - OTS Bounty and Weekly Tasks Rework design record
public_interfaces: []
cross_repo_tasks: []
completed: 2026-07-23T17:31:25Z
---

# Goal

Preserve a bounded, provenance-linked aggregation of the official Tibia forum evidence for the Bounty and Weekly Task systems, separating official behavior, player feedback, design implications and implementation-test candidates.

# Acceptance criteria

- [x] Record the official announcement contract and forum clarifications.
- [x] Aggregate community feedback into themes without presenting opinions as official behavior.
- [x] Reconcile preview-era statements with the current official game guide and update notes.
- [x] State the collection boundary and unresolved points explicitly.
- [x] Produce actionable implementation and acceptance-test candidates without claiming Canary parity.
- [x] Pass documentation, ownership and Real Tibia registry checks.
- [x] Publish through a PR targeting `blakinio/canary:main`.

# Confirmed context

- The official forum thread `4989324`, titled `New Task System II`, reports 172 results across 9 pages and is closed.
- The selected Chrome tab exposed the complete first displayed page, including the official-reply index, five official clarifications and the first community responses.
- The official announcement is Tibia news item `8567`; the current official game guide documents the released Bounty and Weekly Task rules.
- The existing `OTS_BOUNTY_AND_WEEKLY_TASKS_REWORK.md` is a product-direction record and remains read-only because a still-active task record claims it.
- This task is documentation only and does not prove current Canary or maintained-client runtime behavior.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| Bounty and Weekly Tasks Rework | Product-design context | `docs/ai-agent/OTS_BOUNTY_AND_WEEKLY_TASKS_REWORK.md` | The forum evidence should inform, not duplicate, the established design direction. |
| Real Tibia parity governance | Evidence labels and proof boundaries | `docs/agents/REAL_TIBIA_PARITY_PLAYBOOK.md` | Prevents forum statements from being promoted into runtime proof. |
| Prey module registry | Module identity and dependencies | `docs/agents/real-tibia/registry/modules/prey.yaml` | Bounty/Weekly Tasks belong to the existing Prey and Hunting Tasks module. |

# Ownership and overlap check

- Program record: `CAN-PROGRAM-REAL-TIBIA-PARITY`.
- Open PRs: searched current open PRs; none owns the planned evidence-report path.
- Active tasks: the merged-but-not-yet-archived Bounty roadmap task exclusively owns the established product-design document, which this task treats as read-only.
- Ownership checker: 28 active task records validated before this task was created.
- Exclusive claims: this evidence report and this task record only.
- Shared claims: none.
- Read-only dependencies: evidence policy, Prey module registry and existing Bounty product design.
- Overlaps: none on writable paths.
- Resolution: create a separate evidence report rather than editing the still-claimed product-design record.

# Current state

The repository already contains product direction for a Bounty/Weekly redesign but lacks a bounded record of the official forum clarifications and player-risk themes that motivated implementation requirements.

The evidence report now records the bounded source set, direct official clarifications, topic-only official reply index, current released behavior, ten captured community themes, implementation requirements, seventeen acceptance-test candidates and explicit unknowns.

# Plan

1. Verify the exact final-head CI on PR #828.
2. If current-head checks are green and scope/review remain clean, mark ready and squash-merge under repository policy.

# Work log

## 2026-07-23T19:08:01+02:00

- Confirmed the live repository and overlap state.
- Captured the first displayed forum page and official-reply index.
- Located the official announcement, current game-guide rules and post-test-server changes.
- Kept the existing Bounty product-design document read-only to avoid ownership overlap.

## 2026-07-23T19:12:37+02:00

- Added the 402-line evidence report.
- Reconciled preview rules with the current official guide and final test-server changes.
- Converted the captured community discussion into ten risk themes and seventeen bounded test candidates.
- Passed documentation diff, ownership and registry validation.
- Opened draft PR #828 in `blakinio/canary` and applied `ci:final-gate` before the final checkpoint commit.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Store forum research as a separate Real Tibia evidence report. | The existing product-design file is already owned by another active task and mixes user direction with design direction. | none |
| Treat uncaptured pages as a declared collection limitation. | The thread reports 9 pages; only the first displayed page and its official-reply index were captured directly. | none |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `docs/agents/real-tibia/BOUNTY_AND_WEEKLY_TASKS_FORUM_EVIDENCE.md` | exclusive | Forum evidence, current-state reconciliation and test candidates | complete |
| `docs/agents/tasks/active/CAN-20260723-bounty-weekly-forum-evidence.md` | exclusive | Durable task state and handoff | ready |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| `88a9dd47f8f8ba12c297db0a26c231084bce2c11` | `git diff --check` | PASS | No whitespace errors. |
| `88a9dd47f8f8ba12c297db0a26c231084bce2c11` | `python tools/agents/task_ownership.py` | PASS | 29 active task records validated. |
| `88a9dd47f8f8ba12c297db0a26c231084bce2c11` | `python tools/agents/real_tibia_registry.py validate` | PASS | Registry valid with 0 warnings. |
| final head | GitHub Actions | NOT_RUN | Exact final-head checks start after the checkpoint push. |

# Failed approaches and dead ends

- Direct HTTP collection of later forum pages was blocked by Cloudflare.
- Chrome control became unavailable after the first-page capture; no claim is made that every post on pages 2-9 was read.
- Search indexing did not expose the missing forum replies reliably enough to quote or count them.

# Risks and compatibility

- Runtime: none; documentation only.
- Data/migration: none.
- Security: no credentials, cookies or private data are recorded.
- Backward compatibility: no code or configuration changes.
- Cross-repo rollout: none; any future maintained-client or server implementation requires a separate task.
- Rollback: revert the documentation commit.

# Remaining work

1. Verify exact final-head CI, review and mergeability for PR #828.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T19:12:37+02:00
head: 88a9dd47f8f8ba12c297db0a26c231084bce2c11
branch: docs/can-20260723-bounty-weekly-forum-evidence
pr: 828
status: ready
context_routes:
  - real-tibia-parity
  - agent-governance
owned_paths:
  - docs/agents/real-tibia/BOUNTY_AND_WEEKLY_TASKS_FORUM_EVIDENCE.md
  - docs/agents/tasks/active/CAN-20260723-bounty-weekly-forum-evidence.md
proven:
  - Current main is bd65e83540a7862427bbf46479e78b666aa01e29.
  - The official thread reports 172 results across 9 pages and is closed.
  - The first displayed page and official-reply index were captured on 2026-07-23.
  - Official news item 8567 and the current official game guide document the released system.
  - The evidence report records the bounded source set, direct forum clarifications, current released rules, ten feedback themes and seventeen test candidates.
  - Local documentation, ownership and registry validation pass.
derived:
  - The report can define implementation requirements and test candidates but cannot prove Canary parity.
unknown:
  - Full per-post content outside the captured first displayed page.
  - Exact current Canary and maintained-client implementation coverage.
  - Exact final-head GitHub Actions conclusions after the checkpoint commit.
conflicts: []
first_failure:
  marker: none
  evidence: none
rejected_hypotheses:
  - Forum feedback proves implementation parity: announcement and opinions do not prove runtime behavior.
changed_paths:
  - docs/agents/real-tibia/BOUNTY_AND_WEEKLY_TASKS_FORUM_EVIDENCE.md
  - docs/agents/tasks/active/CAN-20260723-bounty-weekly-forum-evidence.md
validation:
  - command: git diff --check
    result: PASS
    evidence: no whitespace errors at content head 88a9dd47f8f8ba12c297db0a26c231084bce2c11
  - command: python tools/agents/task_ownership.py
    result: PASS
    evidence: 29 active task records validated
  - command: python tools/agents/real_tibia_registry.py validate
    result: PASS
    evidence: registry valid with 0 warnings
blockers:
  - none
next_action: Verify exact final-head CI, review and mergeability for PR 828; if green, mark ready and squash-merge.
```

# Handoff

Start with this task record and the evidence report. Do not infer packet fields, persistence, formulas or client behavior beyond the cited official statements.

# Completion

- Final status: ready
- PR: https://github.com/blakinio/canary/pull/828
- Merge commit: none
- Program record updated: not required
- Catalogue updated: not required
- Changelog updated: not required
- Archived at: none

## Automated lifecycle completion

- Feature PR: #828.
- Feature head: `347bb173db64b3c0a3a037c92382747ef47e16fc`.
- Merge commit: `704eccb3084e9c0261723cb524d7d352e3268b61`.
- Merged at: `2026-07-23T17:31:25Z`.
- This record was moved from `tasks/active` by the post-merge lifecycle automation.
