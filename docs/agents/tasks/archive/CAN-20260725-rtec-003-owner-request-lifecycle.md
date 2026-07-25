---
task_id: CAN-20260725-rtec-003-owner-request-lifecycle
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-003
status: completed
agent: "GPT-5.6 Thinking"
branch: feat/rtec-003-owner-request-lifecycle-20260725
base_branch: main
created: 2026-07-25T15:30:00+02:00
updated: 2026-07-25T17:43:43Z
last_verified_commit: "55c6ad13a4ed5c2dde71131df5677476cefb3600"
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
    - docs/agents/real-tibia/OWNER_REQUEST_LIFECYCLE.md
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
completed: 2026-07-25T17:43:43Z
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

- `docs/agents/real-tibia/OWNER_REQUEST_LIFECYCLE.md` defines the operator sequence and proof boundaries.
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

# Ownership incidents

Several delayed builder/review commits introduced temporary workflows and helpers on the shared task branch. All such files and injected write jobs were removed. The final package contains exactly the eight declared paths and no owner implementation path.

# Validation

| Head | Check | Result | Evidence |
|---|---|---|---|
| `2372ce3898e12cc14ffda4626f638ad812b01533` | fresh main/open-PR/active-task/request-state preflight | PASS | RTEC-001/002 merged and archived; no initial RTEC-003 overlap |
| `7f6b612e2c56e86a850370e5c3e80979b1fc0479` | changed-file and ownership boundary review | PASS | exactly eight declared paths; approved repository/base/head; no owner implementation path |
| `7f6b612e2c56e86a850370e5c3e80979b1fc0479` | Real Tibia Evidence Contracts | PASS | run `30163159309`; focused tests, registry, corpus, deterministic indexes and vocations dry-run all passed |
| `7f6b612e2c56e86a850370e5c3e80979b1fc0479` | Agent Task Ownership and Real Tibia Module Registry | PASS | runs `30163159324` and `30163159291` |
| `7f6b612e2c56e86a850370e5c3e80979b1fc0479` | Universal E2E, Upstream Intelligence and CI | PASS | runs `30163159296`, `30163159317` and `30163159388` |

# Remaining work

1. Validate this checkpoint and generate the compact resume bundle.
2. Allow the checkpoint commit to complete the renewed exact-head final gate.
3. Mark PR #921 ready and squash-merge with expected-head protection.
4. Verify canonical lifecycle archival and reconcile RTEC-003 as merged before any RTEC-004 work.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T19:17:35+02:00
head: 7f6b612e2c56e86a850370e5c3e80979b1fc0479
branch: feat/rtec-003-owner-request-lifecycle-20260725
pr: 921
status: ready
context_routes:
  - real-tibia-evidence-collection
  - agent-governance
owned_paths:
  - .github/workflows/real-tibia-evidence.yml
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
  - docs/agents/real-tibia/OWNER_REQUEST_LIFECYCLE.md
  - docs/agents/real-tibia/evidence/README.md
  - docs/agents/tasks/active/CAN-20260725-rtec-003-owner-request-lifecycle.md
  - tools/agents/real_tibia_owner_request.py
  - tools/agents/test_real_tibia_owner_request.py
proven:
  - RTEC-001 and RTEC-002 prerequisites are merged and archived
  - PR 921 targets blakinio/canary main from the dedicated task branch and is mergeable
  - the final package contains exactly eight declared changed paths
  - the lifecycle CLI, focused tests, operator guide, catalogue and programme integration are present
  - owner implementation paths remain unchanged
  - RTREQ-FEATURE-VOCATIONS-0001 remains ready-for-owner-triage without fabricated owner evidence
  - all exact-head GitHub workflows passed on 7f6b612e2c56e86a850370e5c3e80979b1fc0479
  - RTEC-004 has not started
derived:
  - the separate lifecycle CLI reuses schema version 1 without creating another owner execution system
unknown: []
conflicts: []
first_failure:
  marker: none
  evidence: all current exact-head checks are green
rejected_hypotheses:
  - Collector should self-accept or execute the vocations request: owner boundaries and the unchanged production request disprove this
  - Collector should implement missing E2E, OTBM/OWA, TCR, protocol/client or feature capabilities: those paths remain read-only
  - the operator guide belongs inside the strict evidence corpus: fail-closed corpus audit required relocation to docs/agents/real-tibia
changed_paths:
  - .github/workflows/real-tibia-evidence.yml
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
  - docs/agents/real-tibia/OWNER_REQUEST_LIFECYCLE.md
  - docs/agents/real-tibia/evidence/README.md
  - docs/agents/tasks/active/CAN-20260725-rtec-003-owner-request-lifecycle.md
  - tools/agents/real_tibia_owner_request.py
  - tools/agents/test_real_tibia_owner_request.py
validation:
  - command: Real Tibia Evidence Contracts run 30163159309
    result: PASS
    evidence: focused tests, registry, corpus, deterministic indexes and vocations dry-run passed
  - command: Agent Task Ownership and Real Tibia Module Registry
    result: PASS
    evidence: runs 30163159324 and 30163159291
  - command: Universal E2E, Upstream Intelligence and CI
    result: PASS
    evidence: runs 30163159296, 30163159317 and 30163159388
blockers: []
next_action: Mark PR #921 ready and squash-merge exact head after the renewed final gate passes.
```

# Handoff

Use the generated `resume.py` bundle. Do not cross owner boundaries, mutate `RTREQ-FEATURE-VOCATIONS-0001`, or start RTEC-004 before RTEC-003 lifecycle and programme closeout are complete.

## Automated lifecycle completion

- Feature PR: #921.
- Feature head: `d6b9ae490937f07a154205b040e4156355b25cbd`.
- Merge commit: `55c6ad13a4ed5c2dde71131df5677476cefb3600`.
- Merged at: `2026-07-25T17:43:43Z`.
- This record was moved from `tasks/active` by the post-merge lifecycle automation.
