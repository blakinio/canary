---
task_id: CAN-20260721-ots-future-gameplay-roadmap
program_id: CAN-PROGRAM-OTS-FUTURE-GAMEPLAY-SYSTEMS
status: review
agent: "GPT-5.6 Thinking"
branch: docs/ots-future-roadmap-20260721
base_branch: main
created: 2026-07-21
updated: 2026-07-21
last_verified_commit: "994d1ffdfd6828688b1acc6cd7c0c519eab052ba"
risk: low
related_issue: ""
related_pr: "664"
depends_on: []
blocks: []
owned_paths:
  exclusive:
    - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md
    - docs/agents/tasks/active/CAN-20260721-ots-future-gameplay-roadmap.md
  shared: []
  read_only: []
modules_touched: []
reuses: []
public_interfaces: []
cross_repo_tasks: []
---

# CAN-20260721 — OTS future gameplay systems roadmap

## Status

ACTIVE — durable design/handoff record. This task is documentation-only unless a later task explicitly implements one of the systems.

## Goal

Persist the user's OTS gameplay/system redesign discussion so a continuation agent can resume without relying on chat history.

## Owned paths

- `docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md`
- `docs/agents/tasks/active/CAN-20260721-ots-future-gameplay-roadmap.md`

## Live PR

- PR #664 — `docs(ai-agent): persist OTS future gameplay systems roadmap`
- Branch: `docs/ots-future-roadmap-20260721`

## Scope

- Record user-requested future systems, redesign directions, anti-frustration principles, anti-abuse constraints, and open design questions.
- Preserve the RubinOT feature-audit classification discussed with the user as research context, not as implementation truth.
- Do not implement gameplay changes in this task.

## Evidence state

- `PROVEN`: the user explicitly requested the ideas and design directions recorded in the roadmap.
- `DERIVED`: architectural groupings and dependency relationships are organizational conclusions from the discussion.
- `UNKNOWN`: exact balance values, implementation feasibility, current local implementation details, and any external-system behavior not reverified at implementation time.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T09:47:11Z
head: 738981e019c9b0df04f56a587781928362b64fb2
branch: docs/ots-future-roadmap-20260721
pr: 664
status: validating
context_routes:
  - agent-governance
owned_paths:
  - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md
  - docs/agents/tasks/active/CAN-20260721-ots-future-gameplay-roadmap.md
proven:
  - PR #664 is open as a draft against blakinio/canary:main from docs/ots-future-roadmap-20260721.
  - PR #664 changes only the roadmap and this active task record.
  - CI run 29819035316 passed on head 8754737a60c622d9d480e42ce33bf555125dc8e9.
  - AI Agent Tools run 29819035131 passed on head 8754737a60c622d9d480e42ce33bf555125dc8e9.
  - Agent Task Ownership run 29819035179 first failed because the Context checkpoint had no fenced YAML block.
  - Agent Task Ownership run 29819556712 then failed because the active task record had no opening front matter delimiter.
  - The task is documentation-only and does not authorize gameplay, binary, map, datapack, or runtime implementation changes.
derived:
  - The immediate work is task-record contract and CI validation repair; gameplay implementation remains out of scope.
unknown:
  - Required GitHub check results for the post-frontmatter-repair PR head.
conflicts: []
first_failure:
  marker: Agent Task Ownership / Validate changed active task checkpoints
  evidence: Run 29819556712 artifact active-task-ownership/CHANGED_TASK_VALIDATION.txt reports missing opening front matter delimiter.
rejected_hypotheses: []
changed_paths:
  - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md
  - docs/agents/tasks/active/CAN-20260721-ots-future-gameplay-roadmap.md
validation:
  - command: GitHub Actions CI run 29819035316
    result: PASS
    evidence: Completed successfully on head 8754737a60c622d9d480e42ce33bf555125dc8e9.
  - command: GitHub Actions AI Agent Tools run 29819035131
    result: PASS
    evidence: Completed successfully on head 8754737a60c622d9d480e42ce33bf555125dc8e9.
  - command: GitHub Actions Agent Task Ownership run 29819035179
    result: FAIL
    evidence: Missing fenced YAML Context checkpoint.
  - command: GitHub Actions Agent Task Ownership run 29819556712
    result: FAIL
    evidence: Missing opening front matter delimiter after the checkpoint repair.
blockers:
  - Current-head required checks must be reverified after the frontmatter repair.
next_action: Verify PR #664 current-head ownership and required CI after this frontmatter repair; if all required checks pass and no review blockers remain, mark the PR ready and squash-merge it.
```

### User design philosophy

- The game should remain challenging and risky, but avoid legacy friction that mainly causes frustration or player churn.
- Death should be frequent enough to matter and carry loss/risk, but should not erase disproportionate amounts of long-term progression.
- Convenience should generally be earned by engaging with content first rather than granted globally from day one.
- Anti-abuse systems should prefer telemetry, pattern detection, risk scoring, and review over automatic punishment based on one event.
- Money sinks should be desirable/convenient/luxury systems rather than punitive taxes on basic play.
- Modern client/UI work must support large displays, ultrawide, high DPI, 1440p and 4K without creating unfair competitive visibility.

### Durable roadmap

The full backlog and design notes are stored in:

`docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md`

### Important implementation constraint

Every future implementation must independently verify current Canary/OTClient behavior, current Real Tibia behavior when parity is relevant, current repository contracts, and abuse/balance implications. This roadmap is a design source, not proof that a feature already exists or is technically ready.
