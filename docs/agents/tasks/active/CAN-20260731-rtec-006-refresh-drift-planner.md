---
task_id: CAN-20260731-rtec-006-refresh-drift-planner
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-006
status: active
agent: "GPT-5.6 Thinking"
branch: feat/rtec-006-refresh-drift-planner-20260731
base_branch: main
created: 2026-07-31T00:17:45+02:00
updated: 2026-07-31T00:17:45+02:00
last_verified_commit: "dcc09b1d012cbf4462aecc9970ae8540353ea8e3"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - RTEC-001
  - populated Real Tibia evidence dossiers
blocks:
  - RTEC-007
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260731-rtec-006-refresh-drift-planner.md
    - tools/agents/real_tibia_refresh_plan.py
    - tools/agents/test_real_tibia_refresh_plan.py
    - docs/agents/real-tibia/REFRESH_OPERATION.md
  shared: []
  read_only:
    - AGENTS.md
    - docs/agents/AGENTS.md
    - docs/agents/REPOSITORY_MAP.md
    - docs/agents/CONTEXT_HANDOFF.md
    - docs/agents/CONTEXT_ROUTING.md
    - docs/agents/PROJECT_STATE.md
    - docs/agents/ACTIVE_WORK.md
    - docs/agents/BUILD_TEST_MATRIX.md
    - docs/agents/programs/README.md
    - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
    - docs/agents/prompts/RTEC_COMMON_AGENT_RULES.md
    - docs/agents/real-tibia/evidence/**
    - docs/agents/real-tibia/registry/modules/**
    - tools/agents/real_tibia_evidence.py
    - tools/agents/real_tibia_evidence_lib.py
    - tools/agents/real_tibia_evidence_test_support.py
    - .github/workflows/real-tibia-evidence.yml
modules_touched:
  - real-tibia-evidence-collection
  - platform-tooling
reuses:
  - canary-real-tibia-evidence-record-v1
  - Corpus publication validation
  - deterministic freshness diagnostics
public_interfaces:
  - read-only deterministic Real Tibia refresh/drift planner CLI
cross_repo_tasks: []
---

# Goal

Implement the bounded RTEC-006 read-only planner that deterministically selects published Real Tibia evidence records requiring re-verification because of freshness windows, explicit stale state, exact version-baseline deltas, changed Canary paths, changed source identifiers or an explicit module selector.

# Acceptance criteria

- [ ] Add a Python 3.12 standard-library CLI with an explicit `--as-of` date and deterministic JSON output.
- [ ] Reuse the validated publication view; never publish or act on prepublication records.
- [ ] Select inclusive freshness warning/invalidation boundaries and explicit `STALE` state without mutating records.
- [ ] Select exact target-version deltas across the canonical version axes while preserving historical-version records as historical evidence.
- [ ] Select changed repository paths and source identifiers from exact evidence provenance.
- [ ] Produce stable priorities, reasons, input identity and plan digest independent of argument order.
- [ ] Fail closed on malformed selectors, invalid corpus state, unsafe paths and duplicate/conflicting target axes.
- [ ] Exclude rejected and superseded evidence from actionable output.
- [ ] Add focused positive, negative, determinism and no-mutation tests.
- [ ] Document the operator workflow, output contract, priority rules and nonclaims.
- [ ] Change no global evidence index, owner request, dossier module or RTEC programme file.
- [ ] Pass focused local/CI validation on the exact final head, then squash-merge the source PR.
- [ ] Archive this task in a separate lifecycle PR and merge it.

# Scope boundaries

This task only plans future review work. It does not refresh evidence, change evidence state, accept owner results, regenerate shared indexes, edit dossiers, infer Real Tibia behavior, claim a defect, claim parity drift or execute owner-programme work.

`docs/agents/PROJECT_STATE.md` and `docs/agents/prompts/RTEC_COMMON_AGENT_RULES.md` are absent from current `main@dcc09b1d012cbf4462aecc9970ae8540353ea8e3`. Their contents remain `UNKNOWN`; no historical or invented substitute is used. The explicit user-owned paths, current root/nested governance and current RTEC programme boundary remain authoritative for this bounded implementation.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-31T00:17:45+02:00
head: 4c691df0833be48b14befce862a53dbd5adaeb26
branch: feat/rtec-006-refresh-drift-planner-20260731
pr: none
status: implementing
context_routes:
  - agent-governance
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260731-rtec-006-refresh-drift-planner.md
  - tools/agents/real_tibia_refresh_plan.py
  - tools/agents/test_real_tibia_refresh_plan.py
  - docs/agents/real-tibia/REFRESH_OPERATION.md
proven:
  - current main is dcc09b1d012cbf4462aecc9970ae8540353ea8e3
  - no live PR or branch claims RTEC-006 or the three implementation paths
  - RTEC-006 is planned to add deterministic stale/version-delta selection
  - the existing corpus exposes validated publication filtering, canonical version axes and deterministic stale rows
  - global evidence indexes, owner requests, dossier modules and the RTEC programme are forbidden for this task
  - docs/agents/PROJECT_STATE.md is absent on current main
  - docs/agents/prompts/RTEC_COMMON_AGENT_RULES.md is absent on current main
  - the dedicated Real Tibia workflow discovers test_real_tibia*.py but its path trigger does not currently list the new planner files
derived:
  - the smallest complete implementation is a read-only planner over the existing validated publication view
unknown:
  - missing RTEC common rules cannot be evaluated because the current repository has no such file
  - missing project state cannot be evaluated because the current repository has no such file
conflicts: []
first_failure:
  marker: none
  evidence: startup and ownership preflight passed
rejected_hypotheses:
  - the planner should edit evidence or shared indexes: user scope and programme boundaries forbid those writes
  - historical evidence should become stale solely because a newer target version exists: historical-version records preserve bounded historical facts
changed_paths:
  - docs/agents/tasks/active/CAN-20260731-rtec-006-refresh-drift-planner.md
validation:
  - command: live GitHub main, branch, PR and overlap preflight
    result: PASS
    evidence: main dcc09b1d012cbf4462aecc9970ae8540353ea8e3; no RTEC-006 branch or PR; no owned-path overlap
blockers: []
next_action: Open the draft source PR, then implement the planner, focused tests and operator documentation on this branch.
```
