---
task_id: CAN-20260720-agent-context-efficiency
program_id: CAN-PROGRAM-AGENT-ORCHESTRATION
coordination_id: ACO-005
status: implementing
agent: "GPT-5.5 Thinking"
branch: docs/agent-context-efficiency-20260720
base_branch: main
created: 2026-07-20
updated: 2026-07-20
last_verified_commit: "0de75bd2de28c80e9d9587bd3a2520c29c5f267c"
risk: low
related_issue: ""
related_pr: ""
depends_on:
  - completed ACO-001 through ACO-004 context orchestration foundation
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260720-agent-context-efficiency.md
    - tools/agents/checkpoint.py
    - tools/agents/test_context_orchestration.py
  shared:
    - AGENTS.md
    - docs/agents/CONTEXT_HANDOFF.md
    - docs/agents/CONTEXT_ROUTES.json
    - docs/agents/CONTEXT_ROUTING.md
    - docs/agents/programs/AGENT_CONTEXT_ORCHESTRATION_PROGRAM.md
  read_only:
    - docs/agents/EXECUTION_MODE_ROUTING.md
    - tools/agents/context.py
    - tools/agents/resume.py
modules_touched:
  - autonomous agent context governance
  - bounded checkpoint validation
reuses:
  - ACO-001 context routing and resume bundles
  - ACO-003 efficiency proxy model
public_interfaces:
  - repository agent operating contract
  - context checkpoint schema validation
cross_repo_tasks: []
---

# Goal

Reduce autonomous-agent context consumption and chat noise without weakening repository safety, ownership, CI, or evidence requirements.

# Audit findings

- Root `AGENTS.md` is always loaded and already provides lean startup, but does not explicitly prohibit routine tool-call narration or cap progress-update verbosity.
- Full preflight is required at task start but the contract does not explicitly prevent repeating the full preflight after every user/tool interaction.
- Context handoff is bounded at resume time, but checkpoint validation does not reject materially bloated evidence lists, allowing durable task records themselves to grow without bound.
- `CONTEXT_ROUTES.json` default bundle limits are conservative but still larger than the focused test profile and can be reduced for routine continuation bundles.
- Existing ACO tooling already solves route selection, mode selection, bounded handoff, and efficiency evaluation; this task extends that foundation instead of introducing another orchestration system.

# Acceptance criteria

- [ ] Add a low-noise communication contract: no routine tool-call narration; user updates only for material milestones, blockers, or required decisions; updates remain compact.
- [ ] Define one full preflight per bounded task and incremental verification afterwards, with explicit conditions for repeating a full preflight.
- [ ] Add hard checkpoint anti-bloat validation limits aligned with bounded continuation needs.
- [ ] Tighten default context bundle limits without removing required safety context.
- [ ] Add focused tests for checkpoint size enforcement.
- [ ] Keep all changes inside `blakinio/canary`; no upstream or cross-repository writes.
- [ ] Pass relevant agent-tooling tests and repository CI on the exact final head.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-20T12:00:00+02:00
head: 0de75bd2de28c80e9d9587bd3a2520c29c5f267c
branch: docs/agent-context-efficiency-20260720
pr: none
status: implementing
context_routes:
  - agent-governance
owned_paths:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/CONTEXT_ROUTES.json
  - docs/agents/CONTEXT_ROUTING.md
  - docs/agents/programs/AGENT_CONTEXT_ORCHESTRATION_PROGRAM.md
  - docs/agents/tasks/active/CAN-20260720-agent-context-efficiency.md
  - tools/agents/checkpoint.py
  - tools/agents/test_context_orchestration.py
proven:
  - ACO-001 through ACO-004 are completed and provide deterministic routing, resume bundles, efficiency evaluation, and optional supervisor queue
  - root AGENTS.md mandates lean startup and compact checkpoints but has no explicit user-facing progress communication budget
  - checkpoint validator checks schema and evidence-state conflicts but currently has no list-size limits
  - open PR review found no agent-context-orchestration task competing for this scope
  - repository write allowlist permits mutations only in blakinio/canary

derived:
  - the smallest safe improvement is to tighten the existing contracts and validator rather than add a new orchestration layer
unknown:
  - exact final CI result on the implementation head
conflicts: []
first_failure:
  marker: none
  evidence: audit-only preflight found no implementation failure before changes
rejected_hypotheses:
  - build a second agent orchestration framework: existing ACO tooling already covers routing and handoff
changed_paths:
  - docs/agents/tasks/active/CAN-20260720-agent-context-efficiency.md
validation:
  - command: live GitHub open-PR overlap audit
    result: PASS
    evidence: no open PR matched agent context orchestration scope; existing open PRs are unrelated or only share generic indexes
blockers:
  - none
next_action: Open an early draft PR, then implement low-noise communication, incremental-preflight, tighter bundle limits, and checkpoint anti-bloat validation with focused tests.
```
