---
task_id: CAN-20260723-otbm-owa-005-qa-contract-hardening
program_id: CAN-PROGRAM-OTBM-WORLD-ASSURANCE-OPERATIONS
status: validating
agent: "GPT-5.6 Thinking"
branch: test/owa-005-qa-contract-hardening-20260723
base_branch: main
created: 2026-07-23
updated: 2026-07-23
last_verified_commit: "f6c399a4dc0e88eaf201b6e194bab99212a157ce"
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

VALIDATING — bounded implementation is complete in PR #802 and the PR carries `ci:final-gate`. The first labelled exact-head attempt exposed only the task-checkpoint compactness limit (`proven` had 17 items; maximum 16). This final checkpoint removes one redundant proven item and records the failure; no implementation, fixture, ownership or scope behavior changes.

The adversarial permutation fixture exposed one narrow deterministic-output defect in the existing Regression Guard: `impactEvidence.sampledMechanics` preserved the input Semantic Diff finding order even though findings are semantically unordered and sibling output dimensions are canonicalized. The production change is limited to sorting that emitted evidence list by stable `findingId`; selection semantics and evidence contents are unchanged.

## Goal

Harden the delivered canonical OTBM QA contracts with deterministic synthetic/property-style fixtures. Test existing implementations only; do not add a parallel parser, World Index, Script Resolution engine, pathfinder, Semantic Diff engine, renderer, writer/materializer or E2E runner.

## Bounded slice

The package protects:

- canonical ordering and permutation-invariant deterministic outputs;
- dependency-scoped provenance/freshness invalidation;
- fail-closed stale/mixed/not-evaluated certification evidence;
- exact map/World Index provenance composition across Regression Guard, World Health, Certification and Continuous Assurance;
- bounded/truncated evidence never authorizing safe skip;
- unknown/missing appearance evidence remaining an explicit incompatibility;
- input evidence immutability for pure composition contracts.

Candidate/current hash mismatch, dependency unresolved boundaries and compact evidence hash/path mismatch were inspected and intentionally not duplicated because direct focused regression coverage already exists in their owning suites.

Use only deterministic synthetic JSON/object fixtures and Python standard library infrastructure. No generated `.otbm`, `.widx`, reports or production-map fixtures are committed.

## Ownership and concurrency

- Initial preflight found no OWA-001 PR or branch.
- OWA-001 subsequently started as PR #801 and owns campaign-specific task/tool/schema/target paths.
- PR #802 owns only this task record, the hardening note, the focused hardening test suite and the one Regression Guard implementation path needed for the proven deterministic-output defect.
- OWA-001 PR #801 currently changes only its task record and declares different exclusive campaign paths; no exclusive-path overlap exists with OWA-005.
- OWA-005 does not edit OWA-001 campaign target manifests or campaign implementation paths.
- Shared programme/catalogue/changelog paths are intentionally not edited in PR #802.

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
updated_at: 2026-07-23T16:28:00+02:00
head: f6c399a4dc0e88eaf201b6e194bab99212a157ce
branch: test/owa-005-qa-contract-hardening-20260723
pr: 802
status: validating
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/CAN-20260723-otbm-owa-005-qa-contract-hardening.md
  - docs/ai-agent/OTBM_QA_CONTRACT_HARDENING.md
  - tools/ai-agent/test_otbm_qa_contract_hardening.py
  - tools/ai-agent/otbm_map_change_regression.py
proven:
  - Current main remains b8a88f073b2609b444fa15370aae30ac9f80b908; its post-preflight delta was merged auth PR #722 and does not overlap OWA-005 exclusive paths.
  - OWA-001 subsequently started as PR #801; its declared exclusive campaign paths are disjoint from OWA-005 exclusive paths and PR #802 does not edit its shared programme paths.
  - OTBM-QA-001..018 are delivered and lifecycle-closed; OWA-005 hardens those canonical contracts rather than creating replacements.
  - Candidate Physical E2E already has direct mismatch coverage for pipeline candidate SHA, Semantic Diff candidate SHA and selected Semantic Diff hash binding.
  - Dependency/Blast-Radius already covers unresolved evidence boundaries and exact current map/World Index provenance mismatches.
  - Compact Evidence Gateway already covers exact source hash mismatch, format mismatch and unsafe source path rejection.
  - The new OWA-005 suite adds missing permutation, dependency-scoped freshness, cross-contract provenance, stale-certification and immutability coverage instead of duplicating those focused tests.
  - The only production-code diff is a stable findingId sort for Regression Guard impactEvidence.sampledMechanics.
  - Agent Task Ownership run 30014666361 passed on ce41e78101259d8f3bdc885fdd37b9ea0a2752a1 after task/checkpoint format corrections.
  - AI Agent Tools run 30014672577 passed on ce41e78101259d8f3bdc885fdd37b9ea0a2752a1; the workflow discovers all tools/ai-agent/test_*.py tests.
  - OTBM Map Tools run 30014670468 completed its focused OTBM test job successfully on ce41e78101259d8f3bdc885fdd37b9ea0a2752a1.
  - CI run 30014667667 completed its Required aggregator successfully on ce41e78101259d8f3bdc885fdd37b9ea0a2752a1.
  - PR #802 has no reviews or unresolved review threads.
  - The full changed-file list contains only the four owned OWA-005 files; no .otbm, .widx, items.otb, active datapack content or secret path is changed.
  - The ci:final-gate label was applied before the final checkpoint cycle.
  - Local checkout execution is unavailable in this session because the environment cannot resolve github.com; GitHub repository state and CI are used for execution evidence.
derived:
  - The previous Regression Guard sampled mechanic list was input-order dependent; stable sorting by findingId is the minimal contract-preserving deterministic fix.
  - The first labelled exact-head ownership failure was checkpoint compactness only; reducing proven from 17 to the allowed 16 is the complete root-cause fix.
unknown:
  - Exact final-head workflow conclusions until GitHub Actions completes on the commit produced by this compact checkpoint update.
conflicts: []
first_failure:
  marker: regression-guard-sampled-mechanics-order
  evidence: OWA-005 permutation fixture creates equivalent Semantic Diff reports with reversed finding order; previous _static_plan emitted sampledMechanics by input order rather than canonical finding ID order.
rejected_hypotheses:
  - Building a new OTBM parser, index, pathfinder, diff or E2E harness for hardening.
  - Mutating a production OTBM as a fuzz target.
  - Editing OWA-001 campaign targets or campaign implementation paths.
  - Broadly reordering or rewriting Semantic Diff evidence instead of fixing the one emitted unordered Regression Guard list.
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-otbm-owa-005-qa-contract-hardening.md
  - docs/ai-agent/OTBM_QA_CONTRACT_HARDENING.md
  - tools/ai-agent/test_otbm_qa_contract_hardening.py
  - tools/ai-agent/otbm_map_change_regression.py
validation:
  - command: Agent Task Ownership / Validate changed active task checkpoints
    result: PASS
    evidence: Run 30014666361 passed on ce41e78101259d8f3bdc885fdd37b9ea0a2752a1 after initial task/checkpoint format failures were corrected without weakening scope or checks.
  - command: AI Agent Tools
    result: PASS
    evidence: Run 30014672577 passed on ce41e78101259d8f3bdc885fdd37b9ea0a2752a1.
  - command: OTBM Map Tools
    result: PASS
    evidence: Run 30014670468 focused OTBM test job completed successfully on ce41e78101259d8f3bdc885fdd37b9ea0a2752a1.
  - command: CI / Required
    result: PASS
    evidence: Run 30014667667 Required aggregator completed successfully on ce41e78101259d8f3bdc885fdd37b9ea0a2752a1.
  - command: ci:final-gate Agent Task Ownership
    result: FAIL
    evidence: Run 30014974379 on f6c399a4dc0e88eaf201b6e194bab99212a157ce rejected only checkpoint compactness because proven had 17 items; this commit reduces it to the allowed maximum 16.
blockers: []
next_action: Require the full ci:final-gate validation set to pass on this compact checkpoint commit's exact head; then mark PR #802 ready and squash-merge without further commits.
```
