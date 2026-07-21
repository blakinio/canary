---
task_id: CAN-20260721-ots-skill-wheel-pz-rule
program_id: CAN-PROGRAM-OTS-FUTURE-GAMEPLAY-SYSTEMS
status: implementing
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
    - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md
    - docs/agents/tasks/active/CAN-20260721-ots-skill-wheel-pz-rule.md
  shared: []
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
updated_at: 2026-07-21T10:11:00Z
head: 7c9670370ed20777693336919991b32a590dffe3
branch: docs/ots-skill-wheel-pz-20260721
pr: 667
status: implementing
context_routes:
  - agent-governance
owned_paths:
  - docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md
  - docs/agents/tasks/active/CAN-20260721-ots-skill-wheel-pz-rule.md
proven:
  - The user requested that the skill wheel be changeable outside the temple only when the character has no PZ/combat lock.
  - PR #664 merged the durable OTS future gameplay roadmap to main as dbffdc996273bf2bd1315dd3b56881f222b61ce4.
  - Draft PR #667 targets blakinio/canary:main from docs/ots-skill-wheel-pz-20260721.
derived:
  - The requested change is a documentation-only roadmap addition and does not authorize implementation.
unknown:
  - Exact implementation semantics and current Canary/OTClient support must be reverified in a later implementation task.
conflicts: []
first_failure:
  marker: none
  evidence: no validation failure observed before the bounded documentation edit
rejected_hypotheses: []
changed_paths:
  - docs/agents/tasks/active/CAN-20260721-ots-skill-wheel-pz-rule.md
validation:
  - command: GitHub live-state preflight
    result: PASS
    evidence: PR #664 is merged and no open PR was found claiming OTS_FUTURE_GAMEPLAY_SYSTEMS.md before PR #667 was created.
blockers: []
next_action: Append the skill-wheel no-PZ-lock rule to docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md, update this checkpoint to the resulting head, and validate PR #667.
```
