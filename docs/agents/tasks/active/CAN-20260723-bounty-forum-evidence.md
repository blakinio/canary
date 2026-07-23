---
task_id: CAN-20260723-bounty-forum-evidence
program_id: CAN-PROGRAM-OTS-FUTURE-GAMEPLAY-SYSTEMS
coordination_id: ""
status: validating
agent: "Codex"
branch: agent/bounty-forum-evidence
base_branch: main
created: 2026-07-23T19:07:45+02:00
updated: 2026-07-23T19:14:41+02:00
last_verified_commit: "bd65e83540a7862427bbf46479e78b666aa01e29"
risk: low
related_issue: ""
related_pr: "829"
depends_on:
  - CAN-20260723-ots-dynamic-spawn-bounty-roadmap-integration
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260723-bounty-forum-evidence.md
    - docs/ai-agent/OTS_BOUNTY_TASKS_FORUM_EVIDENCE.md
  shared: []
  read_only:
    - docs/ai-agent/OTS_BOUNTY_AND_WEEKLY_TASKS_REWORK.md
modules_touched:
  - prey
reuses:
  - docs/ai-agent/OTS_BOUNTY_AND_WEEKLY_TASKS_REWORK.md
  - docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md
  - docs/agents/REAL_TIBIA_PARITY_PLAYBOOK.md
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Create a provenance-aware aggregation of official and community evidence from Tibia forum thread `4989234` that can be used as a bounded input to the existing Bounty and Weekly Tasks design work.

# Acceptance criteria

- [x] The report separates official facts, official clarifications, community feedback, derived requirements and unknowns.
- [x] The report links every official claim to the official news, guide or forum source.
- [x] Forum feedback is paraphrased and grouped instead of copied wholesale.
- [x] Existing Bounty design work is reused without editing its currently recorded owned path.
- [x] Markdown/path review and `git diff --check` pass.
- [ ] Current-head GitHub checks are verified.
- [x] Module catalogue impact is handled as none because no reusable interface changes.
- [x] Cross-repository impact is handled as none because this is server-side research only.

# Confirmed context

- `PROVEN`: `blakinio/canary:main` was `bd65e83540a7862427bbf46479e78b666aa01e29` at task start.
- `PROVEN`: forum thread `4989234`, titled `New Task System I`, reports 203 entries across 11 pages.
- `PROVEN`: the first official post contains a consolidated list of official reply topics.
- `PROVEN`: PR #772 merged the existing `OTS_BOUNTY_AND_WEEKLY_TASKS_REWORK.md` design record.
- `UNKNOWN`: exhaustive per-post transcription of all 203 entries is not required for the design report and is intentionally avoided; coverage must be stated precisely.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| PR #772 | Existing Bounty/Weekly design | `docs/ai-agent/OTS_BOUNTY_AND_WEEKLY_TASKS_REWORK.md` | Prevents a duplicate product specification. |
| Real Tibia parity governance | Evidence labels and source boundaries | `docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md`, `REAL_TIBIA_PARITY_PLAYBOOK.md` | Keeps official behavior separate from community proposals. |
| `prey` registry module | Module identity | `docs/agents/real-tibia/registry/modules/prey.yaml` | The registry includes Prey and Hunting Tasks. |

# Ownership and overlap check

- Program record: no dedicated Bounty program record exists; the merged predecessor task uses `CAN-PROGRAM-OTS-FUTURE-GAMEPLAY-SYSTEMS`.
- Open PRs inspected: focused GitHub search returned no open Bounty/task-system PR.
- Active tasks inspected: merged PR #772 left an active-path task record; its owned design file is read-only here.
- Ownership checker result: passed on starting `main`.
- Exclusive claims: the new report and this task record only.
- Shared claims: none.
- Read-only dependencies: the existing Bounty/Weekly design.
- Overlaps: research intent overlaps PR #772, but edited paths do not.
- Resolution: create a companion evidence report and do not modify the prior design document.

# Current state

The evidence report is written and locally validated. Draft PR #829 is open. Final commit, current-head CI, scope review, and merge-gate verification remain.

# Plan

1. Aggregate official mechanics and staff clarifications.
2. Cluster community feedback into implementable requirements, risks and open questions.
3. Validate the documentation, publish a draft PR and verify current-head checks.

# Work log

## 2026-07-23T19:07:45+02:00

- Changed: created a dedicated branch and bounded task record.
- Learned: PR #772 is merged and provides the design document this report should complement.
- Failed/blocked: full Chrome control was interrupted; the report will state its exact review coverage and will not invent missing posts.
- Result: implementation can proceed on non-overlapping paths.

## 2026-07-23T19:14:41+02:00

- Changed: added the forum evidence report with official baseline, teaser-to-release deltas, first-page theme aggregation, 15 parity requirements, 9 open contracts, backlog `BNT-001..008`, acceptance-test outline, and risks.
- Learned: the released system renamed the Ring to Talisman and replaced teaser damage reduction with life leech; current official rules also specify one daily token claim, a 10-token cap, and a 5,000-gold Talisman purchase.
- Failed/blocked: later forum pages remained unavailable to reliable automation; coverage is disclosed and no whole-thread sentiment claim is made.
- Result: local ownership, registry, and whitespace checks pass.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Add a companion evidence report | The merged design is broad and already owned by a predecessor task record. | Not required. |
| Paraphrase community posts | The goal is product input, not a verbatim forum archive. | Not required. |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `docs/ai-agent/OTS_BOUNTY_TASKS_FORUM_EVIDENCE.md` | exclusive | Forum evidence aggregation | complete |
| `docs/agents/tasks/active/CAN-20260723-bounty-forum-evidence.md` | exclusive | Durable task state | active |
| `docs/ai-agent/OTS_BOUNTY_AND_WEEKLY_TASKS_REWORK.md` | read_only | Existing design baseline | reused |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| `bd65e83540a7862427bbf46479e78b666aa01e29` | `python tools/agents/task_ownership.py` | passed | 28 active task records validated before task creation. |
| `bd65e83540a7862427bbf46479e78b666aa01e29` | `python tools/agents/real_tibia_registry.py validate` | passed | Registry valid with zero warnings. |
| working tree | `git diff --check` | passed | No whitespace errors. |
| working tree | `python tools/agents/task_ownership.py` | passed | 29 active task records validated with the new ownership claims. |
| working tree | `python tools/agents/real_tibia_registry.py validate` | passed | Registry remains valid with zero warnings. |

# Failed approaches and dead ends

- Direct unauthenticated HTTP requests to the forum were challenged by Cloudflare.
- Chrome control initially exposed the page but was later interrupted; no inaccessible post content is inferred.

# Risks and compatibility

- Runtime: none; documentation-only.
- Data/migration: none.
- Security: no credentials, cookies, private data or downloaded binaries are stored.
- Backward compatibility: none.
- Cross-repo rollout: none.
- Rollback: revert the documentation commit.

# Remaining work

1. Commit the report and checkpoint, apply the final-gate label, then verify PR #829 on the exact head.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T19:14:41+02:00
head: d7f2bead0792f0db26f50629e6bd0f79080643a0
branch: agent/bounty-forum-evidence
pr: 829
status: validating
context_routes:
  - agent-governance
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260723-bounty-forum-evidence.md
  - docs/ai-agent/OTS_BOUNTY_TASKS_FORUM_EVIDENCE.md
proven:
  - PR 772 merged the existing Bounty and Weekly Tasks design into blakinio/canary.
  - Forum thread 4989234 reports 203 entries on 11 pages.
  - The first official post provides a consolidated official-reply topic list.
  - The current official guide documents three offers, four difficulties, daily and capped reroll tokens, current Talisman effects, equipped-state gating and character-bound upgrades.
  - The report is complete without modifying the predecessor design path.
derived:
  - A separate evidence report is the smallest non-overlapping deliverable.
unknown:
  - Exact exhaustive sentiment counts across all 203 posts.
conflicts: []
first_failure:
  marker: none
  evidence: No current unmet local validation invariant; exact-head GitHub validation has not run yet.
rejected_hypotheses:
  - Modify the merged design directly: rejected because the predecessor active task record still claims that path.
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-bounty-forum-evidence.md
  - docs/ai-agent/OTS_BOUNTY_TASKS_FORUM_EVIDENCE.md
validation:
  - command: python tools/agents/task_ownership.py
    result: PASS
    evidence: Starting main validated 28 active task records.
  - command: python tools/agents/real_tibia_registry.py validate
    result: PASS
    evidence: Registry valid with zero warnings.
  - command: git diff --check
    result: PASS
    evidence: No whitespace errors in the report or task update.
  - command: python tools/agents/task_ownership.py
    result: PASS
    evidence: 29 active task records validated with the new claims.
blockers: []
next_action: Commit the report and checkpoint, apply ci:final-gate, and verify PR 829 on the exact head.
```

# Handoff

## Start here

Verify and deliver PR #829 without editing the existing Bounty/Weekly design document.

## Do not repeat

Do not retry unauthenticated forum scraping or infer unavailable posts.

## Required reads

- `AGENTS.md`
- `docs/agents/README.md`
- `docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md`
- `docs/agents/REAL_TIBIA_PARITY_PLAYBOOK.md`
- `docs/agents/real-tibia/registry/modules/prey.yaml`
- `docs/ai-agent/OTS_BOUNTY_AND_WEEKLY_TASKS_REWORK.md`

## Open questions

- None blocking the documentation-only report.

# Completion

- Final status: validating
- PR: 829
- Merge commit:
- Program record updated: not applicable
- Catalogue updated: not applicable
- Changelog updated: not applicable
- Archived at:
