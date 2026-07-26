---
task_id: CAN-20260726-security-authenticated-session-transport-recovery
program_id: CAN-PROGRAM-SECURITY-VALIDATION
coordination_id: OTS-SEC-005-RECOVERY
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/security-authenticated-session-transport-recovery
base_branch: main
created: 2026-07-26
updated: 2026-07-26
last_verified_commit: "ad734f81772eb840c7e1ce18b27ac9ed0d2a4c50"
risk: high
related_issue: ""
related_pr: "pending"
depends_on:
  - stale SEC-005 PR 514 at 3fbaba7fe44808b889c5409ff844b796d9283554
blocks:
  - resolution of PR 514 ownership
  - OAM-053 network-transport eligibility
owned_paths:
  exclusive:
    - tools/security/game_session_runtime.py
    - tools/security/game_session_runtime_runner.py
    - tests/security/test_game_session_runtime.py
    - tests/security/test_game_session_runtime_runner.py
    - tests/security/runtime_scenarios/canary-game-session.json
    - docs/security/SECURITY_VALIDATION_SEC005.md
    - docs/security/SECURITY_VALIDATION_SEC005_HANDOVER.md
    - docs/agents/tasks/active/CAN-20260726-security-authenticated-session-transport-recovery.md
  shared:
    - .github/workflows/security-validation.yml
    - docs/agents/CHANGELOG.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/programs/SECURITY_VALIDATION_PROGRAM.md
  read_only:
    - docs/agents/tasks/active/CAN-20260718-security-authenticated-session-transport.md
    - src/server/network/protocol/protocolgame.cpp
    - src/server/network/protocol/protocolgame.hpp
    - src/server/network/protocol/protocol.cpp
    - src/server/network/protocol/protocol_profile.cpp
    - src/server/network/protocol/transport_codec.cpp
    - tools/e2e/run_agent_load_runtime.py
modules_touched:
  - OTS Security Validation Platform runtime validation
  - Canary authenticated game-session and post-login transport evidence
reuses:
  - stale PR 514 SEC-005 package-specific implementation
  - current Security Validation workflow and disposable runtime lifecycle
public_interfaces:
  - ots-security-game-session-plan-v1
  - ots-security-game-session-report-v1
  - canary-game-session-v1 built-in runtime driver
cross_repo_tasks: []
---

# SEC-005 current-main recovery

## Goal

Recover the completed authenticated game-session and post-login sequence/XTEA validation package from stale PR #514 onto current `main` without overwriting newer shared workflow or governance changes.

## Acceptance criteria

- [x] Start from current `main` and record stale PR #514 head, checks, path set and divergence.
- [x] Confirm SEC-005 package-specific files are absent from current `main` and not superseded.
- [ ] Port the package-specific runtime, runner, tests, scenario and documentation without weakening their fail-closed boundaries.
- [ ] Integrate SEC-005 manually into the current Security Validation workflow.
- [ ] Update current programme, catalogue and changelog narrowly without reverting newer entries.
- [ ] Run focused Python compile/tests and scenario validation.
- [ ] Pass exact-head Agent Task Ownership, CI and Security Validation, including the real disposable authenticated-session runtime.
- [ ] Review the full changed-file set and confirm no runtime source, production configuration, credential, map or unrelated path changed.
- [ ] Squash-merge the replacement PR.
- [ ] Close PR #514 as superseded and archive both the stale and recovery task lifecycle records.
- [ ] Notify OAM-053 that interacting transport ownership is released for a fresh eligibility preflight.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-26T21:25:00+02:00
head: ad734f81772eb840c7e1ce18b27ac9ed0d2a4c50
branch: feat/security-authenticated-session-transport-recovery
pr: pending
status: implementing
context_routes:
  - agent-governance
  - cpp-runtime
  - ci-repair
owned_paths:
  - tools/security/game_session_runtime.py
  - tools/security/game_session_runtime_runner.py
  - tests/security/test_game_session_runtime.py
  - tests/security/test_game_session_runtime_runner.py
  - tests/security/runtime_scenarios/canary-game-session.json
  - docs/security/SECURITY_VALIDATION_SEC005.md
  - docs/security/SECURITY_VALIDATION_SEC005_HANDOVER.md
  - docs/agents/tasks/active/CAN-20260726-security-authenticated-session-transport-recovery.md
  - .github/workflows/security-validation.yml
  - docs/agents/CHANGELOG.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/programs/SECURITY_VALIDATION_PROGRAM.md
proven:
  - Current main is ad734f81772eb840c7e1ce18b27ac9ed0d2a4c50.
  - Stale PR 514 remains open at head 3fbaba7fe44808b889c5409ff844b796d9283554 and is not mergeable.
  - Its historical head passed Ownership, CI, Security Validation and autofix.
  - Its package-specific SEC-005 runtime, runner, tests, scenario and docs are absent from current main.
  - Its four shared integration paths have materially diverged and must be reapplied against current contents.
  - No newer open PR supersedes SEC-005.
derived:
  - A fresh replacement branch is safer than merge or wholesale rebase of PR 514.
  - Package-specific files can be transferred exactly, while shared files require narrow current-main integration.
unknown:
  - Whether current runtime/workflow evolution requires bounded compatibility repairs after the first exact-head run.
conflicts:
  - PR 514 retains historical ownership until replacement lifecycle resolves it.
first_failure:
  marker: stale-pr-integration-age
  result: RECOVERY_REQUIRED
  evidence: PR 514 is hundreds of commits behind current main and all shared integration blobs differ.
rejected_hypotheses:
  - merge stale PR 514 directly
  - wholesale rebase and accept shared-file conflicts mechanically
  - reimplement SEC-005 from scratch without preserving proven package behavior
changed_paths:
  - docs/agents/tasks/active/CAN-20260726-security-authenticated-session-transport-recovery.md
validation:
  - command: lean startup and live overlap audit
    result: PASS
    evidence: replacement owns the bounded SEC-005 paths; unrelated security audits remain disjoint.
blockers: []
next_action: Open the draft replacement PR, bind its number to this task, then port the seven package files from PR 514 and manually integrate the four current shared paths.
```
