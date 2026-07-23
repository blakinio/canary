---
task_id: CAN-20260723-otbm-module-catalog-status-cleanup
program_id: CAN-PROGRAM-OTBM
status: review
agent: "GPT-5.6 Thinking"
branch: docs/otbm-module-catalog-status-cleanup-20260723
base_branch: main
created: 2026-07-23
updated: 2026-07-23
last_verified_commit: "e342ef7c9147623f60d523e9ce55831c22cfc249"
risk: low
related_issue: ""
related_pr: "778"
depends_on:
  - merged PR #594
  - merged PR #572
  - merged PR #419
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260723-otbm-module-catalog-status-cleanup.md
  shared:
    - docs/agents/MODULE_CATALOG.md
  read_only:
    - AGENTS.md
    - docs/agents/REPOSITORY_MAP.md
    - docs/agents/CONTEXT_ROUTING.md
modules_touched:
  - OTBM module catalogue governance
reuses:
  - existing MODULE_CATALOG entries and merged PR evidence
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Correct three stale `MODULE_CATALOG.md` status cells whose referenced implementation PRs are already merged.

# Scope

Documentation/governance only. Change only these status values:

- `OTBM exact-map E2E route preflight`: `active (#594)` -> `merged (#594)`;
- `OTBM Route Interaction Registry`: `active (#572)` -> `merged (#572)`;
- `OTBM static map quality gate`: `active (#419)` -> `merged (#419)`.

Do not change module responsibilities, contracts, reuse boundaries, runtime, OTBM tooling, maps, assets, datapacks, workflows, or E2E behavior.

# Acceptance criteria

- [x] All three stale status cells are corrected and no other catalogue semantics change.
- [x] PR scope contains only this task record and `docs/agents/MODULE_CATALOG.md` before lifecycle closure.
- [x] Shared-path ordering with draft PR #762 / coordination PR #777 is explicitly recorded so TCR reconciliation preserves these corrections.
- [ ] Required current-head CI/ownership checks pass before merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: "2026-07-23T13:35:00+02:00"
head: "e342ef7c9147623f60d523e9ce55831c22cfc249"
branch: "docs/otbm-module-catalog-status-cleanup-20260723"
pr: "778"
status: "validating"
next_action: "Make no further commits. Require exact-final-head Agent Task Ownership and repository CI/Required to finish green, recheck changed files/reviews/mergeability, mark PR #778 ready, squash-merge it, then archive this task in a separate lifecycle PR."
context_routes:
  - "agent-governance"
  - "otbm"
owned_paths:
  - "docs/agents/tasks/active/CAN-20260723-otbm-module-catalog-status-cleanup.md"
  - "docs/agents/MODULE_CATALOG.md"
proven:
  - "PR #594 is merged."
  - "PR #572 is merged."
  - "PR #419 is merged."
  - "PR #778 is the dedicated draft cleanup PR."
  - "PR #778 changed-file scope is exactly MODULE_CATALOG.md plus this active task record."
  - "The MODULE_CATALOG patch contains exactly three status substitutions and no other catalogue semantic change."
  - "Coordination comments on PR #762 and PR #777 record cleanup-first ordering and preservation of the three merged statuses during TCR reconciliation."
conflicts:
  - "Draft PR #762 and coordination PR #777 also touch MODULE_CATALOG.md; ordering is resolved as PR #778 first, then TCR reconciliation must preserve these three corrections."
changed_paths:
  - "docs/agents/MODULE_CATALOG.md"
  - "docs/agents/tasks/active/CAN-20260723-otbm-module-catalog-status-cleanup.md"
blockers:
  - "Exact-final-head required checks must be green before merge."
```
