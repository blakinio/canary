---
task_id: CAN-20260725-rtec-003-owner-request-lifecycle
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-003
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/rtec-003-owner-request-lifecycle-20260725
base_branch: main
created: 2026-07-25T15:30:00+02:00
updated: 2026-07-25T15:35:00+02:00
last_verified_commit: "1b1a056200a878579082397fc3f712e430dc95d9"
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

Implement one bounded, dry-run-first integration layer that safely advances validated Real Tibia owner requests, records stable owner-produced result references and consumes those results into exact evidence records without editing Universal E2E, OTBM/OWA, TCR, protocol/client or feature-owner implementation paths.

# Acceptance criteria

- [ ] Add a standard-library CLI for request transition, owner-result recording and Collector consumption.
- [ ] Require optimistic expected-status checks so stale agents cannot overwrite newer request state.
- [ ] Enforce the existing legal transition graph and owner-controlled state evidence rules.
- [ ] Require stable result references, explicit proof/nonproof boundaries and exact owner task/PR metadata.
- [ ] Permit `consumed` only when referenced evidence records exist, link the request and contain owner-result sources consistent with the request owner kind.
- [ ] Prevent result proof from being promoted beyond owner-produced proof.
- [ ] Keep writes atomic, regenerate deterministic indexes and restore prior files on failure.
- [ ] Add focused positive/negative tests for E2E, OTBM, TCR, protocol and feature routes.
- [ ] Document the operator workflow and keep the existing vocations request unchanged until real owner evidence exists.
- [ ] Preserve all owner implementation paths as read-only and start no RTEC-004 campaign workers.
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

# Implementation plan

1. Add pure request-mutation and consumption checks in a separate reusable CLI module that imports the canonical RTEC v1 contracts.
2. Validate a candidate request against the full in-memory corpus before writing.
3. Write the request and derived indexes transactionally with rollback.
4. Exercise all owner routes and failure modes in isolated temporary corpora.
5. Add operator documentation, workflow coverage and module-catalogue visibility.

# Validation

| Head | Check | Result | Evidence |
|---|---|---|---|
| `2372ce3898e12cc14ffda4626f638ad812b01533` | fresh main / open PR / request-state preflight | PASS | no RTEC-003 overlap; RTEC-002 feature, lifecycle and programme closeout are merged |
| `1b1a056200a878579082397fc3f712e430dc95d9` | early draft PR creation | PASS | PR #921 targets `blakinio/canary:main` from the dedicated task branch |

# Remaining work

Implement the bounded lifecycle CLI and tests, then validate the exact diff and current head.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T15:35:00+02:00
head: 1b1a056200a878579082397fc3f712e430dc95d9
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
  - docs/agents/real-tibia/evidence/README.md
  - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
  - docs/agents/MODULE_CATALOG.md
proven:
  - RTEC-001 and RTEC-002 prerequisites are merged and archived
  - no overlapping RTEC-003 PR or active task was found
  - the v1 request schema and runtime validator already define legal transitions
  - the vocations request has no owner evidence and must remain ready-for-owner-triage
  - draft PR 921 is open on the dedicated branch
derived:
  - a separate dry-run-first mutation tool can reuse the canonical contracts without changing their schema
unknown:
  - exact focused and CI results for the implementation head
conflicts: []
first_failure:
  marker: none
  evidence: none
rejected_hypotheses:
  - RTEC-003 should self-accept or execute the vocations request
  - Collector should implement missing owner capabilities
changed_paths:
  - docs/agents/tasks/active/CAN-20260725-rtec-003-owner-request-lifecycle.md
validation:
  - command: live GitHub preflight
    result: PASS
    evidence: current main 2372ce3898e12cc14ffda4626f638ad812b01533; no overlapping RTEC-003 work
  - command: draft PR safety check
    result: PASS
    evidence: PR 921 uses approved base/head repository and task branch
blockers: []
next_action: Implement the lifecycle CLI and focused tests.
```

# Handoff

Read this task, PR, programme, architecture, current request schema and `RTREQ-FEATURE-VOCATIONS-0001`. Do not cross owner boundaries or invent owner evidence.
