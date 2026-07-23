---
task_id: CAN-20260723-otbm-owa-005-qa-contract-hardening
program_id: CAN-PROGRAM-OTBM-WORLD-ASSURANCE-OPERATIONS
status: active
agent: "GPT-5.6 Thinking"
branch: test/owa-005-qa-contract-hardening-20260723
base_branch: main
created: 2026-07-23
updated: 2026-07-23
last_verified_commit: "489607174f22b8b36663fe2251cdba0423388fbd"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - OTBM-QA-001..018 delivered and lifecycle-closed
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260723-otbm-owa-005-qa-contract-hardening.md
    - docs/ai-agent/OTBM_QA_CONTRACT_HARDENING.md
    - tools/ai-agent/test_otbm_qa_contract_hardening.py
  shared: []
  read_only:
    - tools/ai-agent/otbm_world_health.py
    - tools/ai-agent/otbm_map_change_regression.py
    - tools/ai-agent/otbm_coverage_dashboard.py
    - tools/ai-agent/otbm_region_quest_certification.py
    - tools/ai-agent/otbm_continuous_assurance.py
    - tools/ai-agent/otbm_asset_compatibility.py
    - tools/ai-agent/otbm_release_provenance.py
    - tools/e2e/otbm_candidate_physical_validation.py
    - docs/agents/programs/OTBM_WORLD_ASSURANCE_OPERATIONS_PROGRAM.md
    - docs/ai-agent/OTBM_WORLD_ASSURANCE_OPERATIONS_ROADMAP.md
    - docs/ai-agent/OTBM_WORLD_QUALITY_REPAIR_ROADMAP.md
modules_touched:
  - otbm-map-change-regression
  - otbm-release-provenance
  - otbm-region-quest-certification
  - otbm-continuous-assurance
  - otbm-asset-compatibility
reuses:
  - Unified OTBM World Index
  - OTBM Script Resolution
  - OTBM Reachability
  - Semantic OTBM Diff
  - OTBM World Health
  - OTBM Map Change Regression Guard
  - OTBM Coverage Dashboard
  - OTBM Region and Quest Certification
  - OTBM Continuous Assurance
  - OTBM Dependency and Blast-Radius Graph
  - OTBM Asset Compatibility
  - OTBM Release Provenance and Freshness
  - OTBM Compact Evidence Gateway
  - existing bounded repair/materialization validation
  - existing OTBM candidate Physical E2E validation
public_interfaces: []
cross_repo_tasks: []
---

# CAN-20260723 — OWA-005 QA Contract Hardening and Adversarial Fixtures

## Status

ACTIVE — fresh preflight completed from `main@489607174f22b8b36663fe2251cdba0423388fbd`. This task owns only a new focused adversarial regression suite, its hardening note, and this task record unless a failing invariant proves a minimal existing-contract defect.

## Goal

Harden the delivered canonical OTBM QA contracts with deterministic synthetic/property-style fixtures. Test existing implementations only; do not add a parallel parser, World Index, Script Resolution engine, pathfinder, Semantic Diff engine, renderer, writer/materializer or E2E runner.

## Bounded slice

Prioritize missing cross-contract regression coverage for:

- canonical ordering and permutation-invariant deterministic outputs;
- dependency-scoped provenance/freshness invalidation;
- fail-closed stale/mixed/not-evaluated certification evidence;
- exact map/World Index provenance composition across Regression Guard, World Health, Certification and Continuous Assurance;
- bounded/truncated evidence never authorizing safe skip;
- unknown/missing appearance evidence remaining an explicit incompatibility;
- input evidence immutability for pure composition contracts;
- candidate/current hash mismatch behavior where the existing candidate Physical E2E contract exposes a bounded pure validation seam.

Use only deterministic synthetic JSON/object fixtures and Python standard library infrastructure. Do not commit generated `.otbm`, `.widx`, reports or production-map fixtures.

## Ownership and concurrency

- OWA-001 was rechecked before task creation: no open PR or branch named for OWA-001 was found in current GitHub state.
- No OWA-001 campaign target manifest or campaign implementation path is owned or edited by this task.
- Open OTBM/TCR work remains independent; shared catalogue/changelog files are intentionally not claimed.
- Any newly discovered path overlap is a stop condition until ownership is reconciled.

## Acceptance criteria

- A focused deterministic/property-style suite covers the selected high-value invariant families.
- Semantically unordered input permutations yield identical canonical outputs where the owning contract requires determinism.
- Dependency SHA changes stale exactly dependent dimensions and do not stale independent dimensions.
- Bounded/truncated/uncertain evidence cannot authorize static or represented Physical E2E skips.
- Stale/mixed/not-evaluated current-map provenance cannot retain formal certification above C0.
- Cross-contract map/World Index provenance mismatches fail closed before assurance can pass.
- Missing appearance evidence cannot produce a compatible result.
- Test inputs remain unchanged after read-only composition.
- Any implementation change is minimal and directly justified by a red adversarial test.
- Focused tests and applicable Agent Task Ownership, OTBM Map Tools, AI Agent Tools, CI/Required and exact-final-head gates pass on the final PR head.

## Explicit non-goals

- No production map/datapack/runtime mutation.
- No new canonical OTBM implementation.
- No external fuzz/property dependency.
- No full production map as mutable fuzz input.
- No generated map/index/report artifacts committed.
- No automatic identifier repair.
- No deployment or production promotion authorization.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T15:00:00+02:00
head: 489607174f22b8b36663fe2251cdba0423388fbd
branch: test/owa-005-qa-contract-hardening-20260723
pr: null
status: active
context_routes:
  - otbm
  - agent-governance
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260723-otbm-owa-005-qa-contract-hardening.md
    - docs/ai-agent/OTBM_QA_CONTRACT_HARDENING.md
    - tools/ai-agent/test_otbm_qa_contract_hardening.py
  shared: []
proven:
  - Current main is 489607174f22b8b36663fe2251cdba0423388fbd at task start.
  - CAN-PROGRAM-OTBM-WORLD-ASSURANCE-OPERATIONS is active and explicitly permits OWA-005 in parallel where path ownership is disjoint.
  - OTBM-QA-001..018 are delivered and lifecycle-closed; OWA-005 must harden those canonical contracts rather than create replacements.
  - No open GitHub PR or branch named for OWA-001 was found during preflight.
  - Existing QA implementations already provide focused unit/output-safety/schema suites; this task adds cross-contract adversarial/property-style coverage rather than duplicating them.
  - Local checkout execution is unavailable in this session because the environment cannot resolve github.com; GitHub repository state and CI will be used for execution evidence.
derived:
  - The smallest useful package is one cross-contract synthetic suite plus a durable invariant/gap note, with implementation edits only if a new regression test exposes an existing deterministic/fail-closed contract violation.
unknown:
  - Whether semantic finding-order permutation is already canonical end-to-end until the focused adversarial test executes.
  - Exact candidate Physical E2E pure-function seam suitable for a new bounded hash-mismatch test until its current source/test is inspected.
conflicts: []
first_failure: null
rejected_hypotheses:
  - Building a new OTBM parser, index, pathfinder, diff or E2E harness for hardening.
  - Mutating a production OTBM as a fuzz target.
  - Editing OWA-001 campaign targets or TCR-owned paths.
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-otbm-owa-005-qa-contract-hardening.md
validation: []
blockers: []
next_action: Open the draft PR, bind related_pr in this task record, then add the focused adversarial suite and run/inspect applicable GitHub validation on the exact head.
```
