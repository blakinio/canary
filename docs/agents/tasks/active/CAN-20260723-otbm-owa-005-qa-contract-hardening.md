---
task_id: CAN-20260723-otbm-owa-005-qa-contract-hardening
program_id: CAN-PROGRAM-OTBM-WORLD-ASSURANCE-OPERATIONS
status: implementing
agent: "GPT-5.6 Thinking"
branch: test/owa-005-qa-contract-hardening-20260723
base_branch: main
created: 2026-07-23
updated: 2026-07-23
last_verified_commit: "b8a88f073b2609b444fa15370aae30ac9f80b908"
risk: medium
related_issue: ""
related_pr: "802"
depends_on:
  - OTBM-QA-001..018 delivered and lifecycle-closed
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260723-otbm-owa-005-qa-contract-hardening.md
    - docs/ai-agent/OTBM_QA_CONTRACT_HARDENING.md
    - tools/ai-agent/test_otbm_qa_contract_hardening.py
    - tools/ai-agent/otbm_map_change_regression.py
  shared: []
  read_only:
    - tools/ai-agent/otbm_world_health.py
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

IMPLEMENTING — bounded task is published in draft PR #802. Initial preflight used `main@489607174f22b8b36663fe2251cdba0423388fbd`; `main` then advanced to `b8a88f073b2609b444fa15370aae30ac9f80b908` through merged auth PR #722. Its changed paths are auth/runtime/shared governance only and do not overlap this task's exclusive OTBM hardening paths.

The new permutation fixture exposed one narrow deterministic-output defect by inspection of the current Regression Guard path: `impactEvidence.sampledMechanics` preserved the input Semantic Diff finding order even though findings are semantically unordered and sibling output dimensions are canonicalized. The canonical Regression Guard implementation path is explicitly claimed for the minimal ordering fix only.

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
updated_at: 2026-07-23T16:18:00+02:00
head: 597d3e50ec98c908977bb3e03a907f633f3b4e50
branch: test/owa-005-qa-contract-hardening-20260723
pr: 802
status: implementing
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/CAN-20260723-otbm-owa-005-qa-contract-hardening.md
  - docs/ai-agent/OTBM_QA_CONTRACT_HARDENING.md
  - tools/ai-agent/test_otbm_qa_contract_hardening.py
  - tools/ai-agent/otbm_map_change_regression.py
proven:
  - Initial main at task creation was 489607174f22b8b36663fe2251cdba0423388fbd; main then advanced to b8a88f073b2609b444fa15370aae30ac9f80b908 through merged auth PR #722.
  - PR #722 changed auth/runtime/unit-test/shared-governance paths only and does not overlap this task's exclusive OTBM hardening paths.
  - Draft PR #802 targets blakinio/canary:main from blakinio/canary:test/owa-005-qa-contract-hardening-20260723.
  - CAN-PROGRAM-OTBM-WORLD-ASSURANCE-OPERATIONS is active and explicitly permits OWA-005 in parallel where path ownership is disjoint.
  - OTBM-QA-001..018 are delivered and lifecycle-closed; OWA-005 must harden those canonical contracts rather than create replacements.
  - No open GitHub PR or branch named for OWA-001 was found during preflight.
  - Candidate Physical E2E already has direct mismatch coverage for pipeline candidate SHA, Semantic Diff candidate SHA and selected Semantic Diff hash binding.
  - Dependency/Blast-Radius already covers unresolved evidence boundaries and exact current map/World Index provenance mismatches.
  - Compact Evidence Gateway already covers exact source hash mismatch, format mismatch and unsafe source path rejection.
  - The new OWA-005 suite adds missing permutation/cross-contract composition coverage instead of duplicating those focused tests.
  - AI Agent Tools run 30014279914 and OTBM Map Tools run 30014282487 passed on ca3f17a8f159707c66f5a4d233bf8da4493f8b6c after the canonical-ordering fix; AI Agent Tools discovers every tools/ai-agent/test_*.py test.
  - CI run 30014280323 passed on ca3f17a8f159707c66f5a4d233bf8da4493f8b6c.
  - Local checkout execution is unavailable in this session because the environment cannot resolve github.com; GitHub repository state and CI are used for execution evidence.
derived:
  - The Regression Guard's sampled mechanic list was built from Semantic Diff findings in input order; because the list was emitted directly, permuting otherwise equivalent findings changed deterministic JSON/hash output.
  - The minimal fix is one stable sort of sampled mechanic entries by findingId after filtering, leaving selection semantics and evidence contents unchanged.
unknown:
  - GitHub validation result on the latest documentation/task-record head.
conflicts: []
first_failure:
  marker: regression-guard-sampled-mechanics-order
  evidence: OWA-005 permutation fixture creates equivalent Semantic Diff reports with reversed finding order; previous _static_plan emitted sampledMechanics by input order rather than canonical finding ID order.
rejected_hypotheses:
  - Building a new OTBM parser, index, pathfinder, diff or E2E harness for hardening.
  - Mutating a production OTBM as a fuzz target.
  - Editing OWA-001 campaign targets or TCR-owned paths.
  - Broadly reordering or rewriting Semantic Diff evidence instead of fixing the one emitted unordered Regression Guard list.
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-otbm-owa-005-qa-contract-hardening.md
  - docs/ai-agent/OTBM_QA_CONTRACT_HARDENING.md
  - tools/ai-agent/test_otbm_qa_contract_hardening.py
  - tools/ai-agent/otbm_map_change_regression.py
validation:
  - command: Agent Task Ownership / Validate changed active task checkpoints
    result: FAIL
    evidence: Initial runs exposed repository-format errors in checkpoint owned_paths and task/checkpoint status; all were corrected without scope changes.
  - command: AI Agent Tools
    result: PASS
    evidence: Run 30014279914 passed on ca3f17a8f159707c66f5a4d233bf8da4493f8b6c after the determinism fix.
  - command: OTBM Map Tools
    result: PASS
    evidence: Run 30014282487 passed on ca3f17a8f159707c66f5a4d233bf8da4493f8b6c after the determinism fix.
  - command: CI
    result: PASS
    evidence: Run 30014280323 passed on ca3f17a8f159707c66f5a4d233bf8da4493f8b6c after the determinism fix.
blockers: []
next_action: Recheck ownership validation on the corrected task status, review the full PR diff and current-main delta, then enter the labelled exact-final-head validation sequence.
```
