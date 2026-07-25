---
task_id: CAN-20260725-rtec-003-owner-request-lifecycle
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-003
status: review
agent: "GPT-5.6 Thinking"
branch: feat/rtec-003-owner-request-lifecycle-20260725
base_branch: main
created: 2026-07-25T15:30:00+02:00
updated: 2026-07-25T16:25:00+02:00
last_verified_commit: "3bea0ad0ffb2bcdb4ee6841d6c840277c6ff30d6"
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

Implement a bounded, dry-run-first integration layer that safely advances validated Real Tibia owner requests, records stable owner-produced result references and consumes those results into exact evidence records without taking work from Universal E2E, OTBM/OWA, TCR, protocol/client or feature owners.

# Acceptance criteria

- [x] Add a standard-library CLI for request transition, owner-result recording and Collector consumption.
- [x] Require expected-status checks and optional exact request SHA-256 fencing.
- [x] Enforce the canonical legal transition graph and owner-controlled state evidence requirements.
- [x] Require stable result references, explicit proof/nonproof boundaries and owner task/PR metadata.
- [x] Permit `consumed` only through existing linked evidence records with owner-route-compatible sources.
- [x] Prevent evidence proof levels from exceeding the retained owner result.
- [x] Use atomic writes, deterministic index regeneration and rollback on failure.
- [x] Add focused positive/negative coverage for E2E, OTBM/OWA, TCR, protocol and feature routes.
- [x] Document the operator workflow and keep the real vocations request unclaimed.
- [x] Preserve owner implementation paths as read-only and start no RTEC-004 workers.
- [ ] Verify exact-final-head focused and required GitHub checks, then squash merge.

# Delivered implementation

## Lifecycle CLI

`tools/agents/real_tibia_owner_request.py` provides:

- dry-run by default and explicit `--write`;
- `transition`, `record-result` and `consume-result` commands;
- expected current status and optional request-document SHA-256 guards;
- stable GitHub commit/PR/Actions, repository-file and external-report references;
- dedicated owner-controlled transitions and owner result recording;
- owner-kind evidence-source routing;
- proof-level caps during Collector consumption;
- full candidate-corpus validation;
- atomic request/index writes and rollback.

## Focused tests

`tools/agents/test_real_tibia_owner_request.py` covers:

- stable and rejected result-reference forms;
- stale status and document-digest writers;
- owner-controlled state failures;
- all five owner routes;
- missing request links, wrong source routes, mismatched result references and proof promotion;
- dry-run, successful write and rollback;
- preservation of `RTREQ-FEATURE-VOCATIONS-0001` as `ready-for-owner-triage`.

## Durable integration

- `docs/agents/real-tibia/evidence/OWNER_REQUEST_LIFECYCLE.md` defines the operator sequence and proof boundaries.
- `docs/agents/real-tibia/evidence/README.md` exposes the CLI and validation flow.
- `docs/agents/MODULE_CATALOG.md` registers the reusable tool.
- `docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md` records RTEC-003 as active and leaves RTEC-004 blocked.
- `.github/workflows/real-tibia-evidence.yml` compiles the tool, runs the complete Real Tibia focused suite and verifies the production vocations request is unchanged after a dry run.

# Scope and nonclaims

This task does not:

- accept or execute the vocations request;
- fabricate an owner task, PR, result or proof;
- create or modify an E2E runner;
- parse OTBM or create map assurance infrastructure;
- parse official-client packages or replace TCR;
- modify gameplay, runtime, client, protocol, database, map or datapack behavior;
- populate another module dossier;
- start RTEC-004 parallel workers;
- commit external or proprietary result payloads.

# Ownership incident

During implementation, delayed builder commits introduced undeclared temporary workflows/helpers on the task branch. Every undeclared file and the injected temporary workflow job were removed. The exact final pre-checkpoint diff contains only the eight declared paths and no owner implementation path.

# Validation

| Head | Check | Result | Evidence |
|---|---|---|---|
| `2372ce3898e12cc14ffda4626f638ad812b01533` | fresh main/open-PR/active-task/request-state preflight | PASS | RTEC-001/002 merged and archived; no initial RTEC-003 overlap |
| `3bea0ad0ffb2bcdb4ee6841d6c840277c6ff30d6` | changed-file and ownership boundary review | PASS | exactly eight declared paths; no temporary builder/helper paths |
| `3bea0ad0ffb2bcdb4ee6841d6c840277c6ff30d6` | production request inspection | PASS | vocations request remains `ready-for-owner-triage` with no owner task/PR/result |
| exact final head | Real Tibia Evidence Contracts, Agent Task Ownership, Registry and CI | IN_PROGRESS | final-gate label applied before this checkpoint commit; GitHub runners queued |

# Remaining work

1. Inspect exact-final-head workflow results and logs.
2. Repair only genuine current-head failures; any repair requires a renewed final gate.
3. Verify the final changed-file list, PR comments and review threads.
4. Mark ready and squash merge only after every required current-head check passes.
5. Verify lifecycle archival and reconcile RTEC-003 as merged before starting RTEC-004.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T16:25:00+02:00
head: 3bea0ad0ffb2bcdb4ee6841d6c840277c6ff30d6
branch: feat/rtec-003-owner-request-lifecycle-20260725
pr: 921
status: validating
context_routes:
  - real-tibia-evidence-collection
  - agent-governance
owned_paths:
  - .github/workflows/real-tibia-evidence.yml
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
  - docs/agents/real-tibia/evidence/OWNER_REQUEST_LIFECYCLE.md
  - docs/agents/real-tibia/evidence/README.md
  - docs/agents/tasks/active/CAN-20260725-rtec-003-owner-request-lifecycle.md
  - tools/agents/real_tibia_owner_request.py
  - tools/agents/test_real_tibia_owner_request.py
proven:
  - RTEC-001 and RTEC-002 prerequisites are merged and archived
  - PR 921 uses the approved repository, main base and dedicated task branch
  - the final pre-checkpoint diff contains exactly eight declared paths
  - the lifecycle CLI, tests, docs, catalogue and programme integration are present
  - owner implementation paths remain unchanged
  - the real vocations request remains ready-for-owner-triage without owner evidence
  - every undeclared builder/helper path was removed
derived:
  - the separate lifecycle CLI reuses schema version 1 without creating another owner execution system
unknown:
  - exact-final-head focused and required workflow conclusions
conflicts: []
first_failure:
  marker: none
  evidence: none
rejected_hypotheses:
  - Collector should self-accept or execute the vocations request
  - Collector should implement missing E2E, OTBM/OWA, TCR, protocol/client or feature capabilities
  - temporary builder workflows/helpers belong in the final package
changed_paths:
  - .github/workflows/real-tibia-evidence.yml
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
  - docs/agents/real-tibia/evidence/OWNER_REQUEST_LIFECYCLE.md
  - docs/agents/real-tibia/evidence/README.md
  - docs/agents/tasks/active/CAN-20260725-rtec-003-owner-request-lifecycle.md
  - tools/agents/real_tibia_owner_request.py
  - tools/agents/test_real_tibia_owner_request.py
validation:
  - command: live GitHub preflight and exact changed-file review
    result: PASS
    evidence: current PR metadata and eight declared changed paths
  - command: exact-final-head GitHub workflows
    result: IN_PROGRESS
    evidence: final checkpoint commit must trigger the protected final-head gate
blockers:
  - GitHub Actions runners must complete the exact-final-head checks
next_action: Inspect the exact-final-head Real Tibia Evidence Contracts run and repair only a proven failure.
```

# Handoff

Read this task, PR #921, the programme, Collector architecture, request schema and `RTREQ-FEATURE-VOCATIONS-0001`. Do not cross owner boundaries or invent owner evidence.
