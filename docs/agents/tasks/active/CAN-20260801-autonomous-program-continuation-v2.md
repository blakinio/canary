---
task_id: CAN-20260801-autonomous-program-continuation-v2
program_id: CAN-PROGRAM-AGENT-GOVERNANCE
coordination_id: AUTONOMOUS-PROGRAM-CONTINUATION-V2
status: active
agent: "GPT-5.6 Thinking"
branch: docs/autonomous-program-continuation-v2-20260801
base_branch: main
created: 2026-08-01T23:10:00+02:00
updated: 2026-08-01T23:22:00+02:00
last_verified_commit: "e3fc827d1913e94accf48e6e4e9e2ad5bf56e0d0"
risk: low
related_issue: ""
related_pr: "1050"
depends_on: []
blocks: []
owned_paths:
  exclusive:
    - docs/agents/PROMPTING_STANDARD.md
    - docs/agents/PROMPTING_HANDOVER.md
    - docs/agents/AUTONOMOUS_PROGRAM_CONTINUATION.md
    - docs/agents/tasks/active/CAN-20260801-autonomous-program-continuation-v2.md
  shared: []
  read_only:
    - docs/agents/EXECUTION_PROTOCOL.md
    - docs/agents/CONTEXT_HANDOFF.md
    - tools/agents/**
modules_touched:
  - agent-governance
reuses:
  - checkpoint contract v1
  - execution policy v2
  - task lifecycle archive tooling
public_interfaces: []
cross_repo_tasks:
  - blakinio/freqtrade#975
  - blakinio/Oteryn-Platform#440
  - blakinio/Otheryn#296
  - blakinio/otclient#159
---

# CAN-20260801 — Autonomous program continuation v2

## Objective

Make one short owner invocation authorize a long, low-noise autonomous programme run that checkpoints safely, completes and archives terminal tasks, crosses barriers, and continues with the next ready work until a real stop condition is reached.

## Scope

Documentation and agent-governance contracts only. No runtime, production, upstream, asset, protocol, or application mutation is authorized.

## Acceptance criteria

- [x] Distinguish one bounded worker session from one long owner invocation.
- [x] Define `run_scope: autonomous_program` and continue-until-real-stop semantics.
- [x] Require terminal task finalization, archival, ownership release, barrier review, and next-READY continuation.
- [x] Route resolvable short commands into execution instead of returning a long prompt.
- [x] Preserve repository safety, ownership, merge, no-wait, and no-background rules.
- [ ] Pass exact-head ownership and required CI.
- [ ] Merge and archive this governance task.

## Context checkpoint

```yaml
checkpoint_version: 1
policy_version: 2
updated_at: 2026-08-01T23:22:00+02:00
head: e3fc827d1913e94accf48e6e4e9e2ad5bf56e0d0
branch: docs/autonomous-program-continuation-v2-20260801
pr: 1050
status: validating
phase: validate
session_id: chat-20260801-autonomous-v2
session_role: coordinator
execution_mode: chat
run_scope: autonomous_program
continuation_policy: continue_until_real_stop
task_completion_policy: finalize_archive_and_continue
user_communication: low_noise
context_routes:
  - agent-governance
owned_paths:
  - docs/agents/PROMPTING_STANDARD.md
  - docs/agents/PROMPTING_HANDOVER.md
  - docs/agents/AUTONOMOUS_PROGRAM_CONTINUATION.md
  - docs/agents/tasks/active/CAN-20260801-autonomous-program-continuation-v2.md
proven:
  - The standard distinguishes bounded worker sessions from a multi-task owner invocation.
  - The autonomous contract requires terminal task finalization, archival, barrier review, and continuation with the next READY task.
  - The handover routes resolvable short commands into execution rather than returning a prompt.
  - Repository safety, ownership, merge, and no-wait rules remain authoritative.
  - CI run 30718852016 passed and ownership run 30718852016 failed only because the initial task lacked required front matter.
derived:
  - One short programme command can drive long foreground work without treating each checkpoint or completed task as an owner-interaction boundary.
unknown:
  - Required exact-head checks after the front-matter repair.
conflicts: []
first_failure:
  marker: active-task-front-matter-missing
  evidence: Agent Task Ownership run 30718852016 job 91419087106 rejected the initial task before ownership rendering.
rejected_hypotheses:
  - weaken worker stop conditions to obtain long programme continuation
  - treat checkpoints as mandatory pauses
  - claim hidden background execution after the final response
changed_paths:
  - docs/agents/AUTONOMOUS_PROGRAM_CONTINUATION.md
  - docs/agents/PROMPTING_HANDOVER.md
  - docs/agents/PROMPTING_STANDARD.md
  - docs/agents/tasks/active/CAN-20260801-autonomous-program-continuation-v2.md
validation:
  - command: compare main...docs/autonomous-program-continuation-v2-20260801
    result: PASS
    evidence: four authorized documentation/governance paths only
  - command: CI run 30718852116
    result: PASS
    evidence: repository CI succeeded on the pre-front-matter head
  - command: Agent Task Ownership run 30718852016 job 91419087106
    result: FAIL
    evidence: first relevant failure was missing opening front matter delimiter; this commit repairs that exact defect
blockers: []
next_action: verify required exact-head checks for PR 1050 and complete the repository merge gate
```
