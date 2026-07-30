---
task_id: CAN-20260730-owa-003a-tcr-qa-freshness
program_id: CAN-PROGRAM-OTBM-WORLD-ASSURANCE-OPERATIONS
coordination_id: OWA-003A
status: implementing
agent: chatgpt
branch: feat/CAN-20260730-owa-003a-tcr-qa-freshness
base_branch: main
created: 2026-07-30T12:05:00+02:00
updated: 2026-07-30T12:25:00+02:00
last_verified_commit: "02fd828563ec2c2ff861c358b588bb63ebb667fd"
risk: medium
related_issue: ""
related_pr: "1031"
depends_on:
  - TCR-009 stable canary-tibia-client-reference-drift-v1
  - TCR-010 stable canary-tibia-client-reference-evidence-gateway-v1
  - TCR-011 stable canary-tibia-reference-adoption-routing-v1
  - QA-016 stable canary-otbm-release-provenance-v1
blocks:
  - OWA-003 downstream QA-008/002/007 evidence integration
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260730-owa-003a-tcr-qa-freshness.md
    - tools/ai-agent/otbm_tcr_qa_freshness.py
    - tools/ai-agent/otbm_tcr_qa_freshness_tool.py
    - tools/ai-agent/test_otbm_tcr_qa_freshness.py
    - tools/ai-agent/test_otbm_tcr_qa_freshness_output_safety.py
    - tools/ai-agent/test_otbm_tcr_qa_freshness_schema.py
    - docs/ai-agent/OTBM_TCR_QA_FRESHNESS.md
    - docs/ai-agent/OTBM_TCR_QA_FRESHNESS_MANIFEST.schema.json
    - docs/ai-agent/OTBM_TCR_QA_FRESHNESS.schema.json
    - .github/workflows/otbm-tcr-qa-freshness.yml
  shared:
    - docs/agents/programs/OTBM_WORLD_ASSURANCE_OPERATIONS_PROGRAM.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
    - docs/ai-agent/OTBM_WORLD_ASSURANCE_OPERATIONS_ROADMAP.md
  read_only:
    - tools/ai-agent/tibia_reference_adoption_router.py
    - tools/ai-agent/otbm_release_provenance.py
    - exact retained TCR-011 routing and QA-016 provenance reports outside Git
modules_touched:
  - OTBM World Assurance Operations
  - OTBM TCR-to-QA freshness impact
reuses:
  - canary-tibia-reference-adoption-routing-v1
  - canary-otbm-release-provenance-v1
public_interfaces:
  - canary-otbm-tcr-qa-freshness-manifest-v1
  - canary-otbm-tcr-qa-freshness-impact-v1
cross_repo_tasks: []
---

# Goal

Add the smallest deterministic read-only OWA-003A composition that verifies an exact reviewed TCR-011 route-to-QA dependency mapping against an existing QA-016 release-provenance report and emits only the explicitly affected stale certification/assurance dimensions.

# Acceptance criteria

- [x] Require exact file/report SHA-256 pins for one stable TCR-011 routing report and one QA-016 release-provenance report.
- [x] Require a reviewer-authored manifest that pins every route/extract/target and maps only explicit QA-016 component and dimension IDs.
- [x] Verify every mapped component is changed in QA-016 and every mapped dimension is stale because of the declared mapped dependencies.
- [x] Reject missing, duplicate, extra, current/not-compared, removed-dimension, ambiguous and cross-route mappings fail closed.
- [x] Preserve TCR `unsupported` and `blocked` routes as explicit non-routable outcomes rather than inventing QA dependencies.
- [x] Keep unrelated QA-016 dimensions current/not-compared and never broaden staleness beyond the reviewed mapping.
- [x] Emit revalidation requirements without selecting validators, generating Semantic Diff, invoking QA-008/002/007, running Physical E2E or refreshing QA-006.
- [x] Add deterministic core, CLI, schemas, output safety and schema/code inventory tests.
- [ ] Reconcile the OWA programme, roadmap, module catalogue and changelog without marking full OWA-003 complete.
- [ ] Pass exact-final-head CI and merge.

# Design boundary

OWA-003A consumes stable reports only. It never opens TCR client inputs, parses OTBM, guesses identifier mappings, discovers dependency edges, selects QA-002 validators, constructs QA-007 execution evidence or changes certification. A verified impact means only that an existing QA-016 report already marked the explicitly mapped dimensions stale because the explicitly mapped components changed.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-30T12:25:00+02:00
head: 02fd828563ec2c2ff861c358b588bb63ebb667fd
branch: feat/CAN-20260730-owa-003a-tcr-qa-freshness
pr: 1031
status: implementing
context_routes:
  - agent-governance
  - otbm
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260730-owa-003a-tcr-qa-freshness.md
  - tools/ai-agent/otbm_tcr_qa_freshness.py
  - tools/ai-agent/otbm_tcr_qa_freshness_tool.py
  - tools/ai-agent/test_otbm_tcr_qa_freshness.py
  - tools/ai-agent/test_otbm_tcr_qa_freshness_output_safety.py
  - tools/ai-agent/test_otbm_tcr_qa_freshness_schema.py
  - docs/ai-agent/OTBM_TCR_QA_FRESHNESS.md
  - docs/ai-agent/OTBM_TCR_QA_FRESHNESS_MANIFEST.schema.json
  - docs/ai-agent/OTBM_TCR_QA_FRESHNESS.schema.json
  - .github/workflows/otbm-tcr-qa-freshness.yml
  - docs/agents/programs/OTBM_WORLD_ASSURANCE_OPERATIONS_PROGRAM.md
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
  - docs/ai-agent/OTBM_WORLD_ASSURANCE_OPERATIONS_ROADMAP.md
proven:
  - TCR-011 feature and lifecycle PRs 1029/1030 merged as 094523da1c07eaebcc7096606b690a25cf3474a9 and 292681e424b21bcf938ba204c86f17c864d95393.
  - The OWA programme marks OWA-003 dependency-ready and requires re-derivation from stable merged TCR contracts.
  - QA-016 already owns dependency-scoped staleness and does not rerun validators, Semantic Diff or Physical E2E.
  - QA-002 requires canonical Semantic Diff and QA-007 requires exact executed validator/E2E evidence, so TCR evidence cannot synthesize either contract.
  - The bounded core, CLI, schemas, documentation, output-safety tests and schema inventory are present on PR 1031.
  - The first workflow failure was fixture-only; empty-list defaults, a duplicate fixture mapping ID and a signature-sensitive determinism assertion were corrected without weakening production validation.
derived:
  - The smallest safe first slice is exact TCR-011-to-QA-016 dependency verification plus an explicit downstream revalidation-required state.
unknown:
  - Exact final implementation head and workflow evidence are not yet available.
conflicts: []
first_failure:
  marker: fixture-default-and-signature-expectation
  evidence: OTBM TCR QA Freshness run 30534457196; production contract tests reached the intended fail-closed paths after fixture corrections.
rejected_hypotheses:
  - TCR drift can be converted directly into QA-002 or QA-007 evidence: rejected because those contracts require canonical map-change and executed result inputs owned elsewhere.
  - OWA should rediscover dependencies from TCR names or identifiers: rejected because QA-008 and OWA both require explicit reviewed dependency mappings.
changed_paths:
  - docs/agents/tasks/active/CAN-20260730-owa-003a-tcr-qa-freshness.md
  - tools/ai-agent/otbm_tcr_qa_freshness.py
  - tools/ai-agent/otbm_tcr_qa_freshness_tool.py
  - tools/ai-agent/test_otbm_tcr_qa_freshness.py
  - tools/ai-agent/test_otbm_tcr_qa_freshness_output_safety.py
  - tools/ai-agent/test_otbm_tcr_qa_freshness_schema.py
  - docs/ai-agent/OTBM_TCR_QA_FRESHNESS.md
  - docs/ai-agent/OTBM_TCR_QA_FRESHNESS_MANIFEST.schema.json
  - docs/ai-agent/OTBM_TCR_QA_FRESHNESS.schema.json
  - .github/workflows/otbm-tcr-qa-freshness.yml
validation:
  - command: repository, programme and ownership preflight
    result: PASS
    evidence: main 292681e424b21bcf938ba204c86f17c864d95393; no existing OWA-003 branch/PR and no overlapping open PR found.
  - command: first focused workflow
    result: FIXTURE_FAILURE_CORRECTED
    evidence: run 30534457196 exposed four test-fixture expectation defects; no production validation was relaxed.
blockers: []
next_action: Run the focused workflow on this connector-authored checkpoint, then reconcile the four shared programme/discovery paths and execute the exact-final-head gate.
```
