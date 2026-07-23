---
task_id: CAN-20260723-otbm-qa-006-region-quest-certification
program_id: CAN-PROGRAM-OTBM
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/otbm-qa-006-007-certification-assurance-20260723
base_branch: main
created: 2026-07-23
updated: 2026-07-23
last_verified_commit: "419536ce3dfe452f7af0a23c8c1f771d190d2eb5"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - CAN-20260721-otbm-qa-005-coverage-dashboard complete
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_region_quest_certification.py
    - tools/ai-agent/otbm_region_quest_certification_tool.py
    - tools/ai-agent/test_otbm_region_quest_certification.py
    - tools/ai-agent/test_otbm_region_quest_certification_output_safety.py
    - tools/ai-agent/test_otbm_region_quest_certification_schema.py
    - docs/ai-agent/OTBM_REGION_QUEST_CERTIFICATION.md
    - docs/ai-agent/OTBM_REGION_QUEST_CERTIFICATION_MANIFEST.schema.json
    - docs/ai-agent/OTBM_REGION_QUEST_CERTIFICATION.schema.json
    - docs/agents/tasks/active/CAN-20260723-otbm-qa-006-region-quest-certification.md
  shared: []
  read_only:
    - tools/ai-agent/otbm_coverage_dashboard.py
    - docs/ai-agent/OTBM_COVERAGE_DASHBOARD.schema.json
    - docs/ai-agent/OTBM_WORLD_QUALITY_REPAIR_ROADMAP.md
modules_touched:
  - otbm-region-quest-certification
reuses:
  - canary-otbm-coverage-dashboard-v1
public_interfaces:
  - canary-otbm-certification-targets-v1
  - canary-otbm-region-quest-certification-v1
cross_repo_tasks: []
---

# CAN-20260723 — OTBM-QA-006 Region and Quest Certification

## Status

IMPLEMENTING — bounded certification composition over exact QA-005 Coverage Dashboard evidence. No map, datapack, runtime or E2E execution changes are authorized.

## Goal

Assign deterministic C0-C7 certification levels to explicitly reviewed bounded region, landmark-route, quest and mechanic-set targets while preserving exact current-map provenance and fail-closed stale evidence semantics.

## Scope

- Consume one exact `canary-otbm-coverage-dashboard-v1` report.
- Consume one reviewed `canary-otbm-certification-targets-v1` target-selection manifest.
- Require the strongest certification level to be a contiguous evidence chain.
- Collapse formal certification to C0 when current-map provenance is stale, mixed or not evaluated.
- Cap region/landmark-route targets at C5 and quest/mechanic-set targets at C7.
- Emit no opaque score and perform no parser, validator, route, Physical E2E or candidate execution.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T10:35:00+02:00
head: 419536ce3dfe452f7af0a23c8c1f771d190d2eb5
branch: feat/otbm-qa-006-007-certification-assurance-20260723
pr: null
status: implementing
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - tools/ai-agent/otbm_region_quest_certification.py
  - tools/ai-agent/otbm_region_quest_certification_tool.py
  - tools/ai-agent/test_otbm_region_quest_certification.py
  - tools/ai-agent/test_otbm_region_quest_certification_output_safety.py
  - tools/ai-agent/test_otbm_region_quest_certification_schema.py
  - docs/ai-agent/OTBM_REGION_QUEST_CERTIFICATION.md
  - docs/ai-agent/OTBM_REGION_QUEST_CERTIFICATION_MANIFEST.schema.json
  - docs/ai-agent/OTBM_REGION_QUEST_CERTIFICATION.schema.json
  - docs/agents/tasks/active/CAN-20260723-otbm-qa-006-region-quest-certification.md
proven:
  - QA-005 deliberately exposes factual dimensions and leaves formalCertificationLevel null.
  - The durable roadmap defines QA-006 as bounded C0-C7 certification over exact current evidence.
derived:
  - QA-006 can remain a composition layer over QA-005 and does not need a new parser, validator, pathfinder or E2E runner.
unknown:
  - Exact feature-head CI outcomes until the implementation branch is validated.
conflicts: []
first_failure:
  marker: none
  evidence: No implementation failure observed before branch validation.
rejected_hypotheses:
  - Recompute QA-005 evidence inside QA-006.
  - Treat stale evidence as current certification.
  - Certify the whole world from bounded selected targets.
changed_paths:
  - tools/ai-agent/otbm_region_quest_certification.py
  - tools/ai-agent/otbm_region_quest_certification_tool.py
  - tools/ai-agent/test_otbm_region_quest_certification.py
  - tools/ai-agent/test_otbm_region_quest_certification_output_safety.py
  - tools/ai-agent/test_otbm_region_quest_certification_schema.py
  - docs/ai-agent/OTBM_REGION_QUEST_CERTIFICATION.md
  - docs/ai-agent/OTBM_REGION_QUEST_CERTIFICATION_MANIFEST.schema.json
  - docs/ai-agent/OTBM_REGION_QUEST_CERTIFICATION.schema.json
  - docs/agents/tasks/active/CAN-20260723-otbm-qa-006-region-quest-certification.md
validation: []
blockers: []
next_action: Implement and validate the bounded QA-006 feature on its dedicated branch.
```
