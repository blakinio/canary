---
task_id: CAN-20260723-otbm-owa-005-qa-contract-hardening
program_id: CAN-PROGRAM-OTBM-WORLD-ASSURANCE-OPERATIONS
status: completed
agent: "GPT-5.6 Thinking"
branch: test/owa-005-qa-contract-hardening-20260723
base_branch: main
created: 2026-07-23
updated: 2026-07-23
last_verified_commit: "8c734c19e7979099e20445dce56bd1606bbec79a"
risk: medium
related_issue: ""
related_pr: "802"
depends_on:
  - OTBM-QA-001..018 delivered and lifecycle-closed
blocks: []
owned_paths:
  exclusive: []
  shared: []
  read_only: []
modules_touched:
  - otbm-map-change-regression
  - otbm-release-provenance
  - otbm-region-quest-certification
  - otbm-continuous-assurance
  - otbm-asset-compatibility
reuses:
  - existing canonical OTBM QA contracts
public_interfaces: []
cross_repo_tasks: []
---

# CAN-20260723 — OWA-005 QA Contract Hardening and Adversarial Fixtures

## Final state

COMPLETED — implementation was squash-merged through PR #802 as merge commit `b9414cadf0b9cce263b3e79c4ac4e3829ba53769` after exact-final-head validation on `8c734c19e7979099e20445dce56bd1606bbec79a`.

## Delivered invariants

- canonical ordering and permutation-invariant deterministic outputs;
- dependency-scoped provenance/freshness invalidation;
- fail-closed stale, mixed and not-evaluated certification evidence;
- exact map and World Index provenance composition across Regression Guard, World Health, Certification and Continuous Assurance;
- bounded or truncated evidence never authorizing a safe skip;
- unknown or missing appearance evidence remaining incompatible;
- read-only input evidence immutability.

Existing owning suites remain the source of truth for candidate-map hash mismatch, dependency/blast-radius unresolved boundaries, Compact Evidence Gateway hash/path failures, output safety and identifier conflicts.

## Proven defect and fix

A deterministic permutation fixture proved that Regression Guard `impactEvidence.sampledMechanics` preserved semantically unordered Semantic Diff input order. The merged minimal fix sorts the emitted list by stable `findingId` without changing selection semantics or evidence contents.

## Validation

Exact final head `8c734c19e7979099e20445dce56bd1606bbec79a`:

- Agent Task Ownership: PASS — run `30015366427`;
- OTBM Map Tools: PASS — run `30015366362`;
- AI Agent Tools: PASS — run `30015366597`;
- CI / Required: PASS — run `30015367223`.

No `.otbm`, `.widx`, `items.otb`, active datapack content, proprietary asset or generated report was committed. No parallel parser, World Index, Script Resolution engine, pathfinder, Semantic Diff engine, renderer, writer/materializer or E2E runner was introduced.

## Remaining hardening gaps

- expand adversarial coverage only when an owning contract exposes a concrete uncovered invariant;
- keep appearance/client-reference invalidation dependency-scoped as stable TCR producer contracts arrive;
- preserve exact provenance composition when OWA-006 operationalizes Continuous Assurance on a bounded real change path.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T17:30:00+02:00
head: 8c734c19e7979099e20445dce56bd1606bbec79a
branch: test/owa-005-qa-contract-hardening-20260723
pr: 802
status: completed
context_routes:
  - otbm
  - agent-governance
owned_paths: []
proven:
  - PR #802 is merged.
  - Exact-final-head Agent Task Ownership, OTBM Map Tools, AI Agent Tools and CI Required passed.
  - The bounded package protects determinism, dependency-scoped invalidation, fail-closed composition, bounded-evidence safety, appearance uncertainty and source immutability.
  - The only production-code change is stable sampledMechanics ordering by findingId.
derived: []
unknown: []
conflicts: []
first_failure:
  marker: regression-guard-sampled-mechanics-order
  evidence: Equivalent Semantic Diff finding permutations previously produced different sampledMechanics ordering.
rejected_hypotheses:
  - Building parallel canonical OTBM infrastructure.
  - Mutating production maps as fuzz targets.
changed_paths:
  - docs/ai-agent/OTBM_QA_CONTRACT_HARDENING.md
  - tools/ai-agent/test_otbm_qa_contract_hardening.py
  - tools/ai-agent/otbm_map_change_regression.py
validation:
  - command: exact-final-head required workflows
    result: PASS
    evidence: PR #802 head 8c734c19e7979099e20445dce56bd1606bbec79a
blockers: []
next_action: none
```
