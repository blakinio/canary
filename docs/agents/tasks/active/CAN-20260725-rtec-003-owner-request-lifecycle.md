---
task_id: CAN-20260725-rtec-003-owner-request-lifecycle
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-003
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/rtec-003-owner-request-lifecycle-20260725
base_branch: main
created: 2026-07-25T15:30:00+02:00
updated: 2026-07-25T16:00:00+02:00
last_verified_commit: "552301ea062ce80b920c15fe41f41f5f71adbc6a"
risk: medium
related_issue: ""
related_pr: "921"
depends_on:
  - RTEC-001
  - RTEC-002
blocks:
  - RTEC-004
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260725-rtec-003-owner-request-lifecycle.md
    - tools/agents/real_tibia_owner_request.py
    - tools/agents/test_real_tibia_owner_request.py
    - docs/agents/real-tibia/evidence/OWNER_REQUEST_LIFECYCLE.md
    - .github/workflows/rtec-003-integration-patch.yml
  shared:
    - .github/workflows/real-tibia-evidence.yml
    - docs/agents/real-tibia/evidence/README.md
    - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
    - docs/agents/MODULE_CATALOG.md
  read_only:
    - AGENTS.md
    - docs/agents/REPOSITORY_MAP.md
    - docs/agents/CONTEXT_ROUTING.md
    - docs/ai-agent/REAL_TIBIA_EVIDENCE_COLLECTOR_ARCHITECTURE.md
    - docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md
    - docs/agents/REAL_TIBIA_PARITY_PLAYBOOK.md
    - docs/agents/real-tibia/evidence/schemas/**
    - docs/agents/real-tibia/evidence/requests/**
    - docs/agents/real-tibia/evidence/modules/**
    - tools/agents/real_tibia_evidence.py
    - tools/agents/real_tibia_evidence_lib.py
    - tools/agents/real_tibia_evidence_test_support.py
    - tools/e2e/**
    - tools/ai-agent/**
modules_touched:
  - real-tibia-evidence-collection
  - platform-tooling
reuses:
  - canary-real-tibia-owner-request-v1
  - canary-real-tibia-evidence-record-v1
  - canary-real-tibia-generated-indexes-v1
  - Universal E2E retained results
  - OTBM/OWA stable outputs
  - TCR stable outputs
public_interfaces:
  - dry-run-first owner-request lifecycle CLI
cross_repo_tasks: []
---

# Goal

Implement one bounded, dry-run-first integration layer that safely advances validated Real Tibia owner requests, records stable owner-produced result references and consumes those results into exact evidence records without editing Universal E2E, OTBM/OWA, TCR, protocol/client or feature-owner implementation paths.

# Acceptance criteria

- [x] Add a standard-library CLI for request transition, owner-result recording and Collector consumption.
- [x] Require optimistic expected-status checks so stale agents cannot overwrite newer request state.
- [x] Enforce the existing legal transition graph and owner-controlled state evidence rules.
- [x] Require stable result references, explicit proof/nonproof boundaries and exact owner task/PR metadata.
- [x] Permit `consumed` only when referenced evidence records exist, link the request and contain owner-result sources consistent with the request owner kind.
- [x] Prevent result proof from being promoted beyond owner-produced proof.
- [x] Keep writes atomic, regenerate deterministic indexes and restore prior files on failure.
- [x] Add focused positive/negative tests for E2E, OTBM, TCR, protocol and feature routes.
- [x] Document the operator workflow and keep the existing vocations request unchanged until real owner evidence exists.
- [x] Preserve all owner implementation paths as read-only and start no RTEC-004 campaign workers.
- [ ] Run exact applicable tests and protected final-head checks before squash merge.

# Confirmed context

- RTEC-000 architecture is merged and archived.
- RTEC-001 contracts/tooling are merged and archived.
- RTEC-002 vocations pilot is merged and archived.
- `RTREQ-FEATURE-VOCATIONS-0001` remains `ready-for-owner-triage`; runtime level-gain and promotion execution remain `UNKNOWN`.
- Existing schema version 1 already defines the legal status graph and owner-controlled states.

# Scope boundaries

This task does not:

- accept or execute the vocations owner request;
- fabricate an owner result;
- create another E2E runner, OTBM parser/index/pathfinder/certifier or TCR parser;
- modify gameplay, runtime, protocol, client, database, map or datapack behavior;
- populate another module dossier;
- start parallel Collector workers;
- commit external/proprietary result payloads.

# Delivered implementation

1. `tools/agents/real_tibia_owner_request.py`:
   - dry-run default and explicit `--write`;
   - expected-status and optional request SHA-256 fencing;
   - legal transition enforcement;
   - stable GitHub/repository/artifact result-reference grammar;
   - dedicated owner-result and Collector-consumption commands;
   - owner-kind source routing and proof-level caps;
   - atomic request/index writes and rollback.
2. `tools/agents/test_real_tibia_owner_request.py`:
   - all five owner routes;
   - stale-writer checks;
   - owner-control failures;
   - missing link, wrong route/reference and proof-promotion failures;
   - dry-run, write and rollback behavior;
   - regression guard that the vocations request remains unclaimed.
3. Operator documentation and dedicated workflow coverage.

# Ownership incident

Three undeclared files appeared on the shared task branch while the task was active:

- `.github/workflows/rtec-003-bootstrap.yml`;
- `.github/workflows/rtec-003-implementation.yml`;
- `tools/agents/rtec_003_apply_patch.py`.

They were not part of the task ownership contract and were removed before readiness. The current changed-file set contains only the six declared implementation/documentation paths. No owner implementation path was changed.

# Validation

| Head | Check | Result | Evidence |
|---|---|---|---|
| `2372ce3898e12cc14ffda4626f638ad812b01533` | fresh main / open PR / request-state preflight | PASS | no RTEC-003 overlap; RTEC-002 feature, lifecycle and programme closeout are merged |
| `1b1a056200a878579082397fc3f712e430dc95d9` | early draft PR creation | PASS | PR #921 targets `blakinio/canary:main` from the dedicated task branch |
| `552301ea062ce80b920c15fe41f41f5f71adbc6a` | changed-file boundary review | PASS | six declared paths; undeclared builder workflows/helper removed |
| current | Real Tibia Evidence Contracts / ownership / CI | IN_PROGRESS | exact implementation-head workflows queued |

# Remaining work

1. Inspect focused workflow results and repair root causes.
2. Add the reusable catalogue row and mark RTEC-003 active in the programme.
3. Review the exact final diff, apply `ci:final-gate`, update this checkpoint and run the full final-head gate.
4. Mark ready and squash-merge only after every required current-head check passes.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T16:00:00+02:00
head: 552301ea062ce80b920c15fe41f41f5f71adbc6a
branch: feat/rtec-003-owner-request-lifecycle-20260725
pr: 921
status: implementing
context_routes:
  - real-tibia-evidence-collection
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/CAN-20260725-rtec-003-owner-request-lifecycle.md
  - tools/agents/real_tibia_owner_request.py
  - tools/agents/test_real_tibia_owner_request.py
  - docs/agents/real-tibia/evidence/OWNER_REQUEST_LIFECYCLE.md
  - .github/workflows/real-tibia-evidence.yml
  - .github/workflows/rtec-003-integration-patch.yml
  - docs/agents/real-tibia/evidence/README.md
  - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
  - docs/agents/MODULE_CATALOG.md
proven:
  - RTEC-001 and RTEC-002 prerequisites are merged and archived
  - no overlapping RTEC-003 task was present at preflight
  - v1 request contracts define legal transitions and owner-controlled states
  - vocations has no owner evidence and remains ready-for-owner-triage
  - PR 921 is open on the dedicated branch
  - bounded lifecycle CLI, tests, docs and workflow integration exist
  - undeclared branch files were removed before readiness
derived:
  - the separate lifecycle CLI safely reuses canonical contracts without changing schema version 1
unknown:
  - exact focused and required CI results for the current implementation head
conflicts:
  - undeclared workflow/helper commits appeared on the branch; their files are removed and no current path overlap remains
first_failure:
  marker: none
  evidence: none
rejected_hypotheses:
  - RTEC-003 should self-accept or execute the vocations request
  - Collector should implement missing owner capabilities
  - undeclared builder workflows should remain in the final diff
changed_paths:
  - .github/workflows/real-tibia-evidence.yml
  - docs/agents/real-tibia/evidence/OWNER_REQUEST_LIFECYCLE.md
  - docs/agents/real-tibia/evidence/README.md
  - docs/agents/tasks/active/CAN-20260725-rtec-003-owner-request-lifecycle.md
  - tools/agents/real_tibia_owner_request.py
  - tools/agents/test_real_tibia_owner_request.py
validation:
  - command: live GitHub preflight
    result: PASS
    evidence: main 2372ce3898e12cc14ffda4626f638ad812b01533 and no initial RTEC-003 overlap
  - command: changed-file boundary review
    result: PASS
    evidence: PR 921 currently contains six declared paths only
  - command: exact implementation-head workflows
    result: IN_PROGRESS
    evidence: Real Tibia Evidence Contracts, Agent Task Ownership and CI queued
blockers: []
next_action: Inspect the focused Real Tibia Evidence Contracts run, then repair or complete shared catalogue/program integration.
```

# Handoff

Read this task, PR #921, programme, architecture, current request schema and `RTREQ-FEATURE-VOCATIONS-0001`. Do not cross owner boundaries or invent owner evidence.
