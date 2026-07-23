---
task_id: CAN-20260724-owa-006-continuous-assurance-operational-adoption
program_id: CAN-PROGRAM-OTBM-WORLD-ASSURANCE-OPERATIONS
coordination_id: OWA-006
status: active
agent: "GPT-5.6 Thinking"
branch: feat/owa-006-continuous-assurance-operational-adoption-20260724
base_branch: main
created: 2026-07-24T00:53:00+02:00
updated: 2026-07-24T00:53:00+02:00
last_verified_commit: "a21142eca8ba6c94e9b8577c6c4a5e898c45ff23"
risk: high
related_issue: ""
related_pr: ""
depends_on:
  - "OWA-004 lifecycle PR #847 merged"
  - "QA-001 World Health"
  - "QA-002 Map Change Regression Guard"
  - "QA-006 Region and Quest Certification"
  - "QA-007 Continuous Assurance"
  - "QA-016 Release Provenance/Freshness"
  - "Semantic OTBM Diff"
  - "OTBM-E2E-008 impacted Physical E2E selection"
  - "OTBM-E2E-009 candidate-map Physical E2E validation"
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260724-owa-006-continuous-assurance-operational-adoption.md
    - docs/ai-agent/OTBM_CONTINUOUS_ASSURANCE_OPERATIONAL_ADOPTION.md
  shared:
    - docs/agents/programs/OTBM_WORLD_ASSURANCE_OPERATIONS_PROGRAM.md
    - docs/ai-agent/OTBM_WORLD_ASSURANCE_OPERATIONS_ROADMAP.md
  read_only:
    - docs/ai-agent/OTBM_MAP_CHANGE_REGRESSION.md
    - docs/ai-agent/OTBM_CONTINUOUS_ASSURANCE.md
    - docs/ai-agent/OTBM_WORLD_HEALTH.md
    - docs/ai-agent/OTBM_REGION_QUEST_CERTIFICATION.md
    - docs/ai-agent/OTBM_RELEASE_PROVENANCE.md
    - docs/ai-agent/OTBM_SEMANTIC_DIFF.md
    - docs/ai-agent/OTBM_E2E_IMPACTED_SELECTION.md
    - docs/ai-agent/OTBM_CANDIDATE_PHYSICAL_VALIDATION.md
    - docs/agents/tasks/archive/CAN-20260720-otbm-e2e-009-candidate-map-physical-validation.md
    - docs/agents/tasks/archive/CAN-20260721-otbm-qa-004-reviewed-candidate-repair.md
    - docs/agents/tasks/archive/CAN-20260717-otbm-repair-materialization-pipeline.md
cross_repo_tasks: []
---

# Goal

Execute `OWA-006 — Continuous Assurance Operational Adoption` against exactly one existing reviewed bounded real Canary map/candidate change path, reusing the already-delivered QA-002/QA-007 assurance contracts and existing owning validators/Universal Physical E2E without creating a second assurance engine, parser, pathfinder, writer or E2E runner.

# Hard boundaries

- QA-002 selects validation scope.
- QA-007 validates only the exact supplied selected-result set and never reruns Semantic Diff, static validators or Physical E2E.
- Missing, extra, mismatched, stale, uncertain or manual selected evidence remains fail closed.
- Candidate/current map SHA mismatch remains fail closed.
- Missing selected Physical E2E remains fail closed.
- Unrelated CI suites are never suppressed.
- A green assurance decision does not authorize merge, deployment or production promotion.
- No generated `.otbm`, `.widx`, evidence bundle, certification report, render or proprietary asset is committed.
- OWA-003 and all TCR-003..011 implementation paths are outside this task.

# Fresh preflight

- `main` at task start: `a21142eca8ba6c94e9b8577c6c4a5e898c45ff23` (OWA-004 lifecycle #847).
- OWA-004 feature #838 and lifecycle #847 are merged.
- No open PR or repository task search result claims OWA-006 ownership.
- The only open OTBM-related PR found is TCR-003 checkpoint PR #844; it starts no StaticMapData implementation and claims only its task record, so no OWA-006 ownership overlap is present.
- OWA-003 remains dependency-gated by stable owning TCR parity/drift outputs and is not entered by this task.

# Target-selection gate

A candidate is eligible only when an existing reviewed retained chain proves all of the following without manufacturing new production evidence:

1. exact before/current/candidate provenance;
2. compatible canonical Semantic OTBM Diff;
3. exact QA-002 selected validation plan;
4. owning static-validator results for every selected validator;
5. selected Universal Physical E2E result when QA-002 requires it;
6. compatible before/after QA-001 World Health;
7. compatible before/after QA-006 certification;
8. exact QA-007 execution/result-set binding.

The task must fail closed at the first concrete missing item when no existing reviewed real candidate path satisfies this chain. Generic tooling capability, synthetic fixtures, plan-only validation and a current-state route are not substitutes for one real candidate adoption path.

# Current evidence checkpoint

The fresh repository audit has not yet proven an eligible concrete real candidate chain.

Strong existing evidence already establishes a likely first gap:

- OTBM-E2E-009 delivered the exact candidate hash-chain and selected-only Physical E2E bridge, but its archived task explicitly states that no specific repaired candidate artifact chain was claimed as physically gameplay-validated by that feature task.
- QA-004 Reviewed Candidate Repair is an evidence-chain validator and does not create a candidate or execute Physical E2E.
- The repair/materialization pipeline publishes generated candidate artifacts outside Git and intentionally deferred physical-client proof.
- The OWA-001 Thais route is a current-state campaign target, not a before/current/candidate change chain, and remains C0 for formal QA-006 certification because no reviewed QA-005 mechanic binding exists.

# Next action

Complete the bounded target-selection audit over retained repository/task/PR evidence. If no reviewed real candidate chain exists, record the exact first missing producer evidence as an explicit OWA-006 external evidence blocker, document that no new QA/assurance integration code is justified, update programme/handoff truthfully, pass governance/final gates, and close task ownership without falsely marking the functional OWA-006 success condition complete.
