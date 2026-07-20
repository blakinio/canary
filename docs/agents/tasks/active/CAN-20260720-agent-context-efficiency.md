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
last_verified_commit: "95eb6bffb5da5b7298948841171ec862a09d3579"
risk: low
related_issue: ""
related_pr: "623"
depends_on:
  - completed ACO-001 through ACO-004 context orchestration foundation
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260720-agent-context-efficiency.md
    - tools/agents/checkpoint.py
    - tools/agents/test_checkpoint_compactness.py
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

- Root `AGENTS.md` is always loaded and already provides lean startup, but did not explicitly prohibit routine tool-call narration or cap progress-update verbosity.
- Full preflight was required at task start but the contract did not explicitly prevent repeating the full preflight after every user/tool interaction.
- Context handoff was bounded at resume time, but checkpoint validation did not reject materially bloated evidence lists, allowing durable task records themselves to grow without bound.
- `CONTEXT_ROUTES.json` evidence-bundle limits were conservative but larger than necessary for routine continuation.
- Existing ACO tooling already solves route selection, mode selection, bounded handoff, and efficiency evaluation; this task extends that foundation instead of introducing another orchestration system.

# Acceptance criteria

- [x] Add a low-noise communication contract: no routine tool-call narration; user updates only for material milestones, blockers, or required decisions; updates remain compact.
- [x] Define one full preflight per bounded task and incremental verification afterwards, with explicit conditions for repeating a full preflight.
- [x] Add hard checkpoint anti-bloat validation limits aligned with bounded continuation needs.
- [x] Tighten default context bundle limits without removing required safety context.
- [x] Add focused tests for checkpoint size enforcement.
- [x] Keep all changes inside `blakinio/canary`; no upstream or cross-repository writes.
- [ ] Pass relevant agent-tooling tests and repository CI on the exact final head.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-20T13:20:00+02:00
head: 95eb6bffb5da5b7298948841171ec862a09d3579
branch: docs/agent-context-efficiency-20260720
pr: 623
status: validating
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
  - tools/agents/test_checkpoint_compactness.py
proven:
  - ACO-001 through ACO-004 remain the reused orchestration foundation; no second framework was introduced
  - root AGENTS.md now prohibits routine tool-call narration and limits progress updates to material milestones blockers decisions or scope-risk changes
  - root AGENTS.md and CONTEXT_ROUTING.md now require one full preflight per bounded task or continuation session followed by incremental verification
  - checkpoint validator now enforces generous hard ceilings on every checkpoint list field before durable task records can grow without bound
  - CONTEXT_ROUTES.json now trims routine continuation evidence more aggressively while leaving required-read limits unchanged
  - focused unit coverage exists for at-limit proven evidence over-limit proven evidence and over-limit validation entries
  - compare main to branch reports exactly eight expected changed files and no runtime map binary or cross-repository changes
  - ci:final-gate is applied to PR 623
  - ownership run 29737828434 proved focused unit tests pass and failed only because tasks/active frontmatter used non-active status validating

derived:
  - the implementation addresses both visible chat noise and durable context growth without weakening repository safety or required evidence
  - keeping task frontmatter implementing while checkpoint status is validating is the smallest metadata-only ownership repair
unknown:
  - exact-final-head GitHub Actions conclusions after the ownership metadata repair
conflicts: []
first_failure:
  marker: Agent Task Ownership active-task status validation
  evidence: run 29737828434 artifact CHANGED_TASK_VALIDATION.txt rejected tasks/active frontmatter status validating
rejected_hypotheses:
  - build a second agent orchestration framework: existing ACO tooling already covers routing handoff evaluation and optional worker planning
  - checkpoint compactness implementation caused the first gate failure: focused unit-test step passed before ownership metadata validation failed
changed_paths:
  - AGENTS.md
  - docs/agents/CONTEXT_HANDOFF.md
  - docs/agents/CONTEXT_ROUTES.json
  - docs/agents/CONTEXT_ROUTING.md
  - docs/agents/programs/AGENT_CONTEXT_ORCHESTRATION_PROGRAM.md
  - docs/agents/tasks/active/CAN-20260720-agent-context-efficiency.md
  - tools/agents/checkpoint.py
  - tools/agents/test_checkpoint_compactness.py
validation:
  - command: live GitHub open-PR overlap audit
    result: PASS
    evidence: no open PR owns the ACO-005 context orchestration scope
  - command: compare main...docs/agent-context-efficiency-20260720
    result: PASS
    evidence: eight expected files only; no runtime map binary or cross-repository changes
  - command: focused patch review for checkpoint.py and test_checkpoint_compactness.py
    result: PASS
    evidence: validator adds list ceilings only and tests cover boundary plus two rejection cases
  - command: Agent Task Ownership run 29737828434 focused unit tests
    result: PASS
    evidence: Run focused unit tests step completed successfully
  - command: Agent Task Ownership run 29737828434 changed-task validation
    result: FAIL
    evidence: active task frontmatter status validating was rejected; repaired to implementing in this commit
blockers:
  - none
next_action: Verify exact-final-head required checks and review state for PR 623 after the ownership metadata repair; if green and mergeable, mark ready and squash-merge without adding another commit.
```
