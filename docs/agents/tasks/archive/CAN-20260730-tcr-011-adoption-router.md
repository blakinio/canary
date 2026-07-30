---
task_id: CAN-20260730-tcr-011-adoption-router
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: TCR-011
status: merged
agent: chatgpt
branch: main
base_branch: main
created: 2026-07-30T10:30:00+02:00
updated: 2026-07-30T11:55:00+02:00
last_verified_commit: "094523da1c07eaebcc7096606b690a25cf3474a9"
risk: medium
related_issue: ""
related_pr: "1029"
depends_on:
  - TCR-005 stable canary-otbm-house-reference-parity-v1
  - TCR-006 stable canary-tibia-content-reference-correlation-v1
  - TCR-007 stable canary-tibia-proficiency-reference-correlation-v1
  - TCR-009 stable canary-tibia-client-reference-drift-v1
  - TCR-010 stable canary-tibia-client-reference-evidence-gateway-v1
blocks:
  - OWA-003 dependency-ready after lifecycle merge
owned_paths:
  exclusive:
    - docs/agents/tasks/archive/CAN-20260730-tcr-011-adoption-router.md
    - tools/ai-agent/tibia_reference_adoption_router.py
    - tools/ai-agent/tibia_reference_adoption_router_tool.py
    - tools/ai-agent/test_tibia_reference_adoption_router.py
    - tools/ai-agent/test_tibia_reference_adoption_router_output_safety.py
    - tools/ai-agent/test_tibia_reference_adoption_router_schema.py
    - docs/ai-agent/TIBIA_REFERENCE_ADOPTION_ROUTER.md
    - docs/ai-agent/TIBIA_REFERENCE_ADOPTION_ROUTING_REQUEST.schema.json
    - docs/ai-agent/TIBIA_REFERENCE_ADOPTION_ROUTING.schema.json
    - .github/workflows/tibia-reference-adoption-router.yml
  shared:
    - docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/ai-agent/tibia_client_reference_evidence_gateway.py
    - tools/ai-agent/otbm_repair_recommendation.py
    - exact retained TCR-005, TCR-006, TCR-007, TCR-009 and TCR-010 reports outside Git
modules_touched:
  - OTBM Tibia client reference architecture
  - Tibia reference adoption router
reuses:
  - canary-tibia-client-reference-evidence-gateway-v1
  - canary-otbm-repair-recommendation-v1
  - existing Achievement, Cyclopedia, Spawn/Boss/NPC, Quest/Storage and Weapon Proficiency owners
public_interfaces:
  - canary-tibia-reference-adoption-routing-request-v1
  - canary-tibia-reference-adoption-routing-v1
cross_repo_tasks: []
---

# Goal

Add the smallest deterministic read-only TCR-011 router that consumes one exact executed TCR-010 report plus one explicit reviewed routing request and classifies each selected extract to an existing owner/capability or an explicit unsupported outcome.

# Acceptance criteria

- [x] Require an executed `canary-tibia-client-reference-evidence-gateway-v1` report with valid canonical hashes.
- [x] Pin every route to exact binding ID, kind, extract ID, source ID, JSON Pointer and extract value SHA-256.
- [x] Permit only fixed existing owner/capability pairs appropriate to `house`, `content`, `proficiency` and `drift` evidence.
- [x] Route map-affecting work only to the existing OTBM Repair Recommendation capability; never directly to a writer/materializer.
- [x] Preserve `unsupported` and `blocked` outcomes without expanding a writer or inventing a target state.
- [x] Reject duplicate routes, stale report/request hashes, missing extracts, cross-kind owner/capability pairs and unreviewed free-form capabilities.
- [x] Generate no approval, mutation request, writer execution, deployment, E2E or gameplay claim.
- [x] Add deterministic core, CLI, schema, output-safety and schema-inventory evidence.
- [x] Reconcile programme, module catalogue and changelog.
- [x] Pass exact-final-head workflow evidence and merge.

# Feature result

- Feature PR: `#1029`.
- Exact final head: `f3512b685dfc3708df0ac1a9831c1031afdf8e2d`.
- Squash merge: `094523da1c07eaebcc7096606b690a25cf3474a9`.
- Readiness/final-gate CI: run `30530210426`, conclusion `success`, including Linux release/debug, Docker image validation, Docker quickstart and `Required`.
- Exact-head subsystem workflows: Adoption Router `30529815706`, Agent Task Ownership `30529815555`, AI Agent Tools `30529815574`, TCR drift `30529815464`, TCR evidence gateway `30529815532` and Universal E2E Stability `30529815480`, all successful.
- Public formats: `canary-tibia-reference-adoption-routing-request-v1` and `canary-tibia-reference-adoption-routing-v1`.
- The router preserves exact gateway/report/bundle/extract hashes, requires complete reviewed coverage and uses a closed owner/capability inventory.
- Map-affecting work routes only through OTBM-QA-003; direct Phase 8 and area-materializer capabilities are excluded.
- No parser, desired-state inference, approval, mutation request, writer execution, deployment, E2E or gameplay authority was added.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-30T11:55:00+02:00
head: 60703e2d608897fa55aed406ab5003b5d9fafe84
branch: docs/CAN-20260730-tcr-011-archive
pr: 1030
status: ready
context_routes:
  - agent-governance
  - otbm
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/archive/CAN-20260730-tcr-011-adoption-router.md
  - docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md
  - docs/agents/MODULE_CATALOG.md
proven:
  - TCR-011 feature PR 1029 squash-merged as 094523da1c07eaebcc7096606b690a25cf3474a9 from exact final head f3512b685dfc3708df0ac1a9831c1031afdf8e2d.
  - Readiness CI 30530210426 passed Linux release/debug, Docker image, quickstart and Required on the exact final head.
  - Adoption Router 30529815706, Ownership 30529815555, AI Agent Tools 30529815574, TCR drift 30529815464, TCR gateway 30529815532 and Universal E2E 30529815480 passed on the exact final head.
  - The feature diff contained only the declared thirteen TCR-011 tool, test, schema, workflow, task and shared-document paths.
  - PR 1030 at live head 60703e2d608897fa55aed406ab5003b5d9fafe84 is mergeable and its net diff contains exactly the module catalogue, TCR programme, active task deletion and archive addition.
  - OWA-003 becomes dependency-ready only after this lifecycle PR marks TCR-011 stable/merged; no OWA implementation starts in this archive PR.
derived:
  - The TCR programme has delivered all required TCR packages; OWA-003 is the next separate bounded package after lifecycle merge.
unknown:
  - Exact checkpoint-update commit SHA and its pull-request workflow results must be verified from live repository state.
conflicts: []
first_failure:
  marker: GitHub Actions / bot-authored lifecycle head
  evidence: runs 30532325891, 30532325934, 30532325943, 30532325906, 30532325927 and 30532326126 concluded action_required on 60703e2d608897fa55aed406ab5003b5d9fafe84; Ownership emitted no jobs.
rejected_hypotheses:
  - Lifecycle cleanup should include runtime or router changes: rejected because feature behavior is already terminal and lifecycle scope is documentation-only.
  - Bot-authored reconciliation head can serve as the final merge-gate head: rejected because its pull-request workflows concluded action_required without runnable ownership jobs.
changed_paths:
  - docs/agents/tasks/active/CAN-20260730-tcr-011-adoption-router.md
  - docs/agents/tasks/archive/CAN-20260730-tcr-011-adoption-router.md
  - docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md
  - docs/agents/MODULE_CATALOG.md
validation:
  - command: feature exact-final-head workflow set
    result: PASS
    evidence: runs 30530210426, 30529815706, 30529815555, 30529815574, 30529815464, 30529815532 and 30529815480 on f3512b685dfc3708df0ac1a9831c1031afdf8e2d.
  - command: post-sync four-path lifecycle diff review
    result: PASS
    evidence: PR 1030 at 60703e2d608897fa55aed406ab5003b5d9fafe84 contains only module catalogue, TCR programme, active task deletion and archive addition.
  - command: post-sync pull-request workflow set
    result: BLOCKED
    evidence: bot-authored head 60703e2d608897fa55aed406ab5003b5d9fafe84 emitted action_required/no-job runs; this checkpoint commit must trigger normal pull-request checks.
blockers: []
next_action: Verify every required workflow on the exact current head, then mark PR 1030 ready and squash-merge without creating another commit.
```
