---
task_id: CAN-20260802-delivery-closeout-v21
program_id: CAN-PROGRAM-AGENT-GOVERNANCE
coordination_id: DELIVERY-CLOSEOUT-V21
status: implementing
agent: "GPT-5.6 Thinking"
branch: docs/agent-closeout-vertical-slice-v21-20260802
base_branch: main
created: 2026-08-02T00:14:00+02:00
updated: 2026-08-02T00:14:00+02:00
last_verified_commit: "unknown"
risk: low
related_issue: ""
related_pr: ""
depends_on: []
blocks: []
owned_paths:
  exclusive:
    - docs/agents/AGENTS.md
    - docs/agents/DELIVERY_COMPLETENESS_AND_CLOSEOUT.md
    - docs/agents/tasks/active/CAN-20260802-delivery-closeout-v21.md
  shared: []
  read_only:
    - docs/agents/PROMPTING_STANDARD.md
    - docs/agents/AUTONOMOUS_PROGRAM_CONTINUATION.md
modules_touched:
  - agent-governance
reuses:
  - autonomous programme continuation v2
  - checkpoint and task lifecycle contracts
public_interfaces: []
cross_repo_tasks:
  - blakinio/freqtrade
  - blakinio/Oteryn-Platform
  - blakinio/Otheryn
  - blakinio/otclient
---

# Delivery completeness and closeout v2.1

## Goal

Require eval-driven prompt governance, explicit trust boundaries, complete producer/consumer vertical slices, independent audit, real E2E and terminal PR hygiene before substantial work can be marked complete.

## Acceptance

- [x] Add the normative delivery completeness and closeout contract.
- [x] Route substantial implementation, audit, E2E and closeout through it.
- [x] Make backend-only success insufficient for a user-facing feature when frontend/client consumers are required.
- [x] Require independent audit, E2E and exact-head CI.
- [x] Require every related or superseded PR to reach an intentional terminal state.
- [ ] Pass exact-head governance and CI.
- [ ] Merge and archive this task.

## Context checkpoint

```yaml
checkpoint_version: 1
policy_version: 2
updated_at: 2026-08-02T00:14:00+02:00
head: unknown
branch: docs/agent-closeout-vertical-slice-v21-20260802
pr: ""
status: implementing
phase: implement
session_id: chat-20260802-delivery-closeout-v21
session_role: coordinator
execution_mode: chat
run_scope: autonomous_program
continuation_policy: continue_until_real_stop
task_completion_policy: finalize_archive_and_continue
user_communication: low_noise
context_routes:
  - agent-governance
owned_paths:
  - docs/agents/AGENTS.md
  - docs/agents/DELIVERY_COMPLETENESS_AND_CLOSEOUT.md
  - docs/agents/tasks/active/CAN-20260802-delivery-closeout-v21.md
proven:
  - The new contract defines prompt evals, trust boundaries, vertical-slice completeness, audit, E2E and PR hygiene.
  - Nested agent instructions require the contract before substantial work and closeout.
derived:
  - Future agents cannot truthfully mark user-facing work complete on backend evidence alone.
unknown:
  - Exact PR number and required workflow results.
conflicts: []
first_failure:
  marker: none
  evidence: validation not started
rejected_hypotheses:
  - treat worker narrative as completion evidence
  - leave superseded PRs open after replacement
changed_paths:
  - docs/agents/AGENTS.md
  - docs/agents/DELIVERY_COMPLETENESS_AND_CLOSEOUT.md
  - docs/agents/tasks/active/CAN-20260802-delivery-closeout-v21.md
validation: []
blockers: []
next_action: open the governance PR and verify exact-head checks
```
