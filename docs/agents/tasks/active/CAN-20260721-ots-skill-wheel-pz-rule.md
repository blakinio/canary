---
task_id: CAN-20260721-ots-skill-wheel-pz-rule
program_id: CAN-PROGRAM-OTS-FUTURE-GAMEPLAY-SYSTEMS
status: review
agent: "GPT-5.6 Thinking"
branch: docs/ots-skill-wheel-pz-20260721
base_branch: main
created: 2026-07-21
updated: 2026-07-21
last_verified_commit: "dbffdc996273bf2bd1315dd3b56881f222b61ce4"
risk: low
related_issue: ""
related_pr: "667"
depends_on: []
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260721-ots-skill-wheel-pz-rule.md
  shared:
    - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md
  read_only: []
modules_touched: []
reuses:
  - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md
public_interfaces: []
cross_repo_tasks: []
---

# CAN-20260721 — OTS skill wheel PZ rule

## Goal

Append the user's requested future gameplay rule for changing the skill wheel outside the temple while preventing changes during PZ/combat lock.

## Scope

- Documentation only.
- Record that the skill wheel may be changed outside the temple.
- Require the character to have no PZ/combat lock when changing it.
- Do not implement server or client behavior in this task.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T10:18:00Z
head: fc7a451037591cc872bfe8ff8f555361ffa8325b
branch: docs/ots-skill-wheel-pz-20260721
pr: 667
status: validating
context_routes:
  - agent-governance
owned_paths:
  - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md
  - docs/agents/tasks/active/CAN-20260721-ots-skill-wheel-pz-rule.md
proven:
  - The user requested that the skill wheel be changeable outside the temple only when the character has no PZ/combat lock.
  - PR #664 merged the durable OTS future gameplay roadmap to main as dbffdc996273bf2bd1315dd3b56881f222b61ce4.
  - PR #667 targets blakinio/canary:main from docs/ots-skill-wheel-pz-20260721.
  - PR #667 changes only the roadmap and this active task record.
  - Roadmap section 26 records that temple presence is not mandatory and that changes are blocked while the character has PZ/combat lock.
  - The merged PR #664 task record still exists under tasks/active on main and exclusively claims docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md.
derived:
  - The requested change is a documentation-only roadmap addition and does not authorize implementation.
  - The roadmap is a shared durable design surface for this follow-up, while this task record remains exclusively owned by PR #667.
unknown:
  - Exact implementation semantics and current Canary/OTClient support must be reverified in a later implementation task.
conflicts: []
first_failure:
  marker: Agent Task Ownership / Validate tasks and render ownership index
  evidence: Run 29821539868 failed global ownership validation while the merged PR #664 active task still held an exclusive claim on the same roadmap path.
rejected_hypotheses: []
changed_paths:
  - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md
  - docs/agents/tasks/active/CAN-20260721-ots-skill-wheel-pz-rule.md
validation:
  - command: GitHub live-state preflight
    result: PASS
    evidence: PR #664 is merged and no other open PR claimed the roadmap before PR #667 was created.
  - command: PR #667 changed-file audit
    result: PASS
    evidence: Exactly the roadmap and bounded task record are changed.
  - command: Roadmap tail verification
    result: PASS
    evidence: Section 26 explicitly permits changes outside the temple only without PZ/combat lock.
  - command: GitHub Actions Agent Task Ownership run 29821539868
    result: FAIL
    evidence: Changed checkpoint validation passed; global ownership index validation failed with the old merged task still exclusively claiming the shared roadmap path.
blockers:
  - Current-head ownership and required checks must pass after changing the roadmap claim from exclusive to shared.
next_action: Verify PR #667 current-head ownership and required CI after the shared-roadmap ownership fix; if all required checks pass and no review blockers remain, keep squash auto-merge enabled.
```
