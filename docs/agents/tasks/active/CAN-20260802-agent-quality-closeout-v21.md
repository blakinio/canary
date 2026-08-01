---
task_id: CAN-20260802-agent-quality-closeout-v21
program_id: CAN-PROGRAM-AGENT-GOVERNANCE
coordination_id: AGENT-QUALITY-CLOSEOUT-V21
status: review
agent: "GPT-5.6 Thinking"
branch: docs/agent-quality-closeout-v21-20260802
base_branch: main
created: 2026-08-02T00:20:00+02:00
updated: 2026-08-02T00:24:00+02:00
last_verified_commit: "75ea987d040e0ef1543dd277d2004049ac0c71ac"
risk: low
related_issue: ""
related_pr: "1053"
depends_on: []
blocks: []
owned_paths:
  exclusive:
    - docs/agents/AGENT_QUALITY_AND_CLOSEOUT.md
    - docs/agents/PROMPTING_HANDOVER.md
    - docs/agents/tasks/active/CAN-20260802-agent-quality-closeout-v21.md
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
  - blakinio/freqtrade#988
  - blakinio/Oteryn-Platform#443
  - blakinio/Otheryn#299
  - blakinio/otclient#162
---

# CAN-20260802 — Agent quality and closeout v2.1

## Objective

Make outcome-based evals, trust boundaries, full-stack vertical slices, independent audit, real E2E, exact-final-head CI, related-PR cleanup, and terminal task archival mandatory for substantial agent work.

## Acceptance

- [x] Add the normative v2.1 contract.
- [x] Make the prompting handover require it.
- [x] Cover all agreed quality and closeout gates.
- [ ] Pass exact-head ownership and CI.
- [ ] Merge and archive.

## Context checkpoint

```yaml
checkpoint_version: 1
policy_version: 2
updated_at: 2026-08-02T00:24:00+02:00
head: 75ea987d040e0ef1543dd277d2004049ac0c71ac
branch: docs/agent-quality-closeout-v21-20260802
pr: 1053
status: validating
phase: validate
session_id: chat-20260802-quality-v21
session_role: coordinator
execution_mode: chat
run_scope: autonomous_program
continuation_policy: continue_until_real_stop
task_completion_policy: finalize_archive_and_continue
user_communication: low_noise
owned_paths:
  - docs/agents/AGENT_QUALITY_AND_CLOSEOUT.md
  - docs/agents/PROMPTING_HANDOVER.md
  - docs/agents/tasks/active/CAN-20260802-agent-quality-closeout-v21.md
proven:
  - The v2.1 contract exists and the handover makes it mandatory.
  - PR 1053 owns exactly the governance contract, handover integration, and task record.
derived:
  - Future substantial work must pass the integrated quality and closeout gate.
unknown:
  - Exact-head ownership and CI results after this PR binding update.
conflicts: []
changed_paths:
  - docs/agents/AGENT_QUALITY_AND_CLOSEOUT.md
  - docs/agents/PROMPTING_HANDOVER.md
  - docs/agents/tasks/active/CAN-20260802-agent-quality-closeout-v21.md
validation: []
blockers: []
next_action: verify exact-head ownership and CI for PR 1053, then complete the merge and archive gates
```
