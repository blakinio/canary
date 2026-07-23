---
task_id: CAN-20260723-otbm-module-catalog-status-cleanup
program_id: CAN-PROGRAM-OTBM
status: active
agent: "GPT-5.6 Thinking"
branch: docs/otbm-module-catalog-status-cleanup-20260723
base_branch: main
created: 2026-07-23
updated: 2026-07-23
risk: low
related_issue: ""
related_pr: ""
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

- [ ] All three stale status cells are corrected and no other catalogue semantics change.
- [ ] PR scope contains only this task record and `docs/agents/MODULE_CATALOG.md` before lifecycle closure.
- [ ] Shared-path ordering with draft PR #762 / coordination PR #777 is explicitly recorded so TCR reconciliation preserves these corrections.
- [ ] Required current-head CI/ownership checks pass before merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: "2026-07-23T13:30:00+02:00"
branch: "docs/otbm-module-catalog-status-cleanup-20260723"
pr: "pending"
status: "implementing"
next_action: "Open a draft PR, record shared MODULE_CATALOG ordering with PR #762/#777, apply exactly three status replacements, validate final diff/checks, then merge and archive this task."
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
  - "Current main still marks the three corresponding catalogue entries active."
conflicts:
  - "Draft PR #762 and coordination PR #777 also touch MODULE_CATALOG.md; ordering is cleanup first, then TCR reconciliation must preserve these three corrections."
changed_paths:
  - "docs/agents/tasks/active/CAN-20260723-otbm-module-catalog-status-cleanup.md"
blockers: []
```
