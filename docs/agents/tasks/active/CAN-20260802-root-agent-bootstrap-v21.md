---
task_id: CAN-20260802-root-agent-bootstrap-v21
program_id: CAN-PROGRAM-AGENT-GOVERNANCE
coordination_id: ROOT-AGENT-BOOTSTRAP-V21
status: implementing
agent: "GPT-5.6 Thinking"
branch: docs/root-agent-bootstrap-v21-20260802
base_branch: main
created: 2026-08-02T08:57:00+02:00
updated: 2026-08-02T08:57:00+02:00
last_verified_commit: "aa5887b047dd4c32e2dd6ef43c231bbe3d1b9521"
risk: low
related_issue: ""
related_pr: ""
depends_on: []
blocks: []
owned_paths:
  exclusive:
    - AGENTS.override.md
    - docs/agents/tasks/active/CAN-20260802-root-agent-bootstrap-v21.md
  shared: []
  read_only:
    - AGENTS.md
    - docs/agents/AGENTS.md
    - docs/agents/DELIVERY_COMPLETENESS_AND_CLOSEOUT.md
    - docs/agents/AUTONOMOUS_PROGRAM_CONTINUATION.md
modules_touched:
  - agent-governance
reuses:
  - delivery completeness and closeout v2.1
  - autonomous programme continuation v2.1
public_interfaces: []
cross_repo_tasks:
  - FTAI-20260802-root-agent-bootstrap-v21
  - OTERYN-20260802-root-agent-bootstrap-v21
  - OTH-20260802-root-agent-bootstrap-v21
  - OTC-20260802-root-agent-bootstrap-v21
---

# Root agent bootstrap v2.1

## Goal

Make the automatically loaded repository-root instruction entry point force every Codex agent to read the full local governance stack before acting, so the short autonomous command works consistently.

## Acceptance

- [x] Add root `AGENTS.override.md` without weakening repository safety.
- [x] Require reading root and nested `AGENTS.md`, delivery closeout and autonomous continuation contracts.
- [x] Define `Uruchom/Kontynuuj <program> autonomicznie` as a sufficient short command when repository state identifies the programme.
- [x] Require full vertical slice, audit, real E2E or legitimate N/A, exact-head CI, terminal PRs, archive and ownership release.
- [ ] Pass exact-head governance and CI.
- [ ] Merge and archive this task.

## Context checkpoint

```yaml
checkpoint_version: 1
policy_version: 2
updated_at: 2026-08-02T08:57:00+02:00
head: aa5887b047dd4c32e2dd6ef43c231bbe3d1b9521
branch: docs/root-agent-bootstrap-v21-20260802
pr: null
status: implementing
phase: implementation
session_id: chat-20260802-root-agent-bootstrap-v21
session_role: coordinator
execution_mode: chat
run_scope: autonomous_program
continuation_policy: continue_until_real_stop
task_completion_policy: finalize_archive_and_continue
user_communication: low_noise
context_routes:
  - agent-governance
owned_paths:
  - AGENTS.override.md
  - docs/agents/tasks/active/CAN-20260802-root-agent-bootstrap-v21.md
proven:
  - Root override now contains the mandatory bootstrap and short-command contract.
derived:
  - A new Codex invocation from the repository root will receive the bootstrap automatically.
unknown:
  - Exact-head required workflow outcome after PR creation.
conflicts: []
first_failure:
  marker: none
  evidence: validation pending
rejected_hypotheses:
  - rely on agents to discover nested governance without a root bootstrap
changed_paths:
  - AGENTS.override.md
  - docs/agents/tasks/active/CAN-20260802-root-agent-bootstrap-v21.md
validation: []
blockers: []
next_action: open the feature PR and verify exact-head checks
```
