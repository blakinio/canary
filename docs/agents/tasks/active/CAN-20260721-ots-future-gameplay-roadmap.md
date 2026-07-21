---
task_id: CAN-20260721-ots-future-gameplay-roadmap
program_id: CAN-PROGRAM-OTS-FUTURE-GAMEPLAY-SYSTEMS
status: ready
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

READY — durable documentation roadmap is complete on PR #664; only the exact-final-head merge gate remains. Future gameplay implementation requires a separate bounded task.

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
updated_at: 2026-07-21T09:49:38Z
head: f103540934d2ba71b6e0d65763c82cc4da63b631
branch: docs/ots-future-roadmap-20260721
pr: 664
status: ready
context_routes:
  - agent-governance
owned_paths:
  - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md
  - docs/agents/tasks/active/CAN-20260721-ots-future-gameplay-roadmap.md
proven:
  - PR #664 is an in-repository draft against main and changes only the roadmap plus this active task record.
  - Earlier task-record failures were repaired by adding the required fenced YAML checkpoint and structured frontmatter.
  - CI run 29819684765 passed on repair head f103540934d2ba71b6e0d65763c82cc4da63b631.
  - Agent Task Ownership run 29819684580 passed on repair head f103540934d2ba71b6e0d65763c82cc4da63b631.
  - AI Agent Tools run 29819684455 passed on repair head f103540934d2ba71b6e0d65763c82cc4da63b631.
  - PR #664 had no comments, reviews, or review threads before the final-gate commit.
  - The ci:final-gate label was applied before this final checkpoint commit.
  - The task is documentation-only and does not authorize gameplay, binary, map, datapack, or runtime implementation changes.
derived:
  - The documentation change is ready for exact-final-head validation and merge if the final-gate checks remain green.
unknown:
  - Exact-final-head required check conclusions after this final checkpoint commit.
  - Squash merge SHA for PR #664.
conflicts: []
first_failure:
  marker: none
  evidence: The latest pre-final-gate repair head passed CI, Agent Task Ownership, and AI Agent Tools.
rejected_hypotheses:
  - A fenced checkpoint alone would satisfy the active-task contract: run 29819556712 proved structured frontmatter was also required.
changed_paths:
  - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md
  - docs/agents/tasks/active/CAN-20260721-ots-future-gameplay-roadmap.md
validation:
  - command: GitHub Actions CI run 29819684765
    result: PASS
    evidence: Completed successfully on repair head f103540934d2ba71b6e0d65763c82cc4da63b631.
  - command: GitHub Actions Agent Task Ownership run 29819684580
    result: PASS
    evidence: Changed active task checkpoint and ownership validation completed successfully on repair head f103540934d2ba71b6e0d65763c82cc4da63b631.
  - command: GitHub Actions AI Agent Tools run 29819684455
    result: PASS
    evidence: Completed successfully on repair head f103540934d2ba71b6e0d65763c82cc4da63b631.
blockers: []
next_action: Verify PR #664 exact-final-head CI, Agent Task Ownership, AI Agent Tools, mergeability, comments, reviews, and review threads; if all required gates pass, mark the PR ready and expected-head squash-merge it.
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
