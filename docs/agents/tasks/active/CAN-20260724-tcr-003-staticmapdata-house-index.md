---
task_id: CAN-20260724-tcr-003-staticmapdata-house-index
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: OTBM-TIBIA-CLIENT-REFERENCE
status: planned
agent: "GPT-5.6 Thinking"
branch: docs/tcr-003-continuation-checkpoint-20260724
base_branch: main
created: 2026-07-24T00:04:21+02:00
updated: 2026-07-24T00:04:21+02:00
last_verified_commit: "d1ad83056ec7930f067986909f66b8f20f1a1f44"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - TCR-001 merged stable canary-tibia-client-reference-manifest-v1
  - TCR-002 merged stable canary-tibia-staticdata-index-v1
blocks:
  - TCR-005
  - TCR-009
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260724-tcr-003-staticmapdata-house-index.md
  shared: []
  read_only:
    - docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md
    - docs/ai-agent/OTBM_TIBIA_CLIENT_REFERENCE_ARCHITECTURE.md
    - tools/ai-agent/tibia_client_reference_manifest.py
    - tools/ai-agent/tibia_staticdata_reference_index.py
modules_touched:
  - OTBM analysis tooling
  - official-client reference evidence
reuses:
  - canary-tibia-client-reference-manifest-v1 exact provenance contract
  - canary-tibia-staticdata-index-v1 stable StaticData reference evidence
  - existing otbm-tooling discovery ownership
public_interfaces:
  - canary-tibia-staticmapdata-index-v1
cross_repo_tasks: []
---

# Goal

Continue the programme with a fresh, bounded TCR-003 preflight for the planned read-only StaticMapData House Index. No TCR-003 implementation has started in this checkpoint-only handoff.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T00:04:21+02:00
head: d1ad83056ec7930f067986909f66b8f20f1a1f44
branch: docs/tcr-003-continuation-checkpoint-20260724
pr: none
status: investigating
context_routes:
  - agent-governance
  - otbm
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260724-tcr-003-staticmapdata-house-index.md
proven:
  - TCR-002 feature PR 827 merged as 24d106b5eea40371833ce20de96184b55cd9b661.
  - TCR-002 lifecycle closure PR 842 merged as d1ad83056ec7930f067986909f66b8f20f1a1f44 and current main equals that merge.
  - The programme marks canary-tibia-staticdata-index-v1 stable/merged and TCR-003 StaticMapData House Index as the next candidate after a fresh ownership/reuse preflight.
  - Open-PR and branch searches found no TCR-003 or StaticMapData-index owner before this checkpoint branch was created.
  - Repository code search found no existing canary-tibia-staticmapdata-index-v1 implementation.
  - No TCR-003 implementation, parser, workflow or proprietary client data was added by this handoff.
derived:
  - The next session should perform only the fresh TCR-003 ownership/reuse/source-format preflight before claiming implementation paths.
unknown:
  - Whether any equivalent StaticMapData parser/index exists under a differently named module not surfaced by the narrow searches.
  - Exact reviewed fixture and user-supplied StaticMapData file shape to use for opt-in real-file validation.
conflicts: []
first_failure:
  marker: none
  evidence: no current blocker or failed validation; implementation has not started
rejected_hypotheses:
  - Continue TCR-003 implementation inside TCR-002 lifecycle closure: TCR-002 is fully merged and archived, and the programme requires a separate bounded package.
changed_paths:
  - docs/agents/tasks/active/CAN-20260724-tcr-003-staticmapdata-house-index.md
validation:
  - command: GitHub open PR and branch search for TCR-003 StaticMapData ownership
    result: PASS
    evidence: no matching open PR or branch existed before checkpoint branch creation
  - command: GitHub repository search for canary-tibia-staticmapdata-index-v1
    result: PASS
    evidence: no canonical implementation surfaced in the narrow search
blockers: []
next_action: Perform a fresh current-main TCR-003 ownership/reuse/source-format preflight, verify no equivalent canonical StaticMapData index exists, then claim exact implementation paths and open the bounded TCR-003 draft PR before substantive code changes.
```
