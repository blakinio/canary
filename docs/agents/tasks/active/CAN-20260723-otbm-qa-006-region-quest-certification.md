---
task_id: CAN-20260723-otbm-qa-006-region-quest-certification
program_id: CAN-PROGRAM-OTBM
status: validating
agent: "GPT-5.6 Thinking"
branch: feat/otbm-qa-006-007-certification-assurance-20260723
base_branch: main
created: 2026-07-23
updated: 2026-07-23
last_verified_commit: "96375947b358eb3256473b9c9aae80082582baff"
risk: medium
related_issue: ""
related_pr: "759"
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

VALIDATING — bounded certification composition over exact QA-005 Coverage Dashboard evidence. No map, datapack, runtime or E2E execution changes are authorized.

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
updated_at: 2026-07-23T11:20:00+02:00
head: 96375947b358eb3256473b9c9aae80082582baff
branch: feat/otbm-qa-006-007-certification-assurance-20260723
pr: 759
status: validating
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
  - Focused local combined QA-006/007 validation passed 20 semantic, schema and output-safety tests before publication.
  - PR 759 pre-final CI run 29993845854 succeeded on head 96375947b358eb3256473b9c9aae80082582baff.
  - PR 759 pre-final Agent Task Ownership run 29993845514 succeeded on the same head.
  - PR 759 pre-final OTBM Map Tools run 29993845673 succeeded on the same head after dependency-free schema-test correction.
  - PR 759 pre-final AI Agent Tools job in run 29993845590 completed successfully on the same head.
  - ci:final-gate was applied before this final checkpoint cycle.
derived:
  - QA-006 remains a composition layer over QA-005 and does not need a new parser, validator, pathfinder or E2E runner.
unknown:
  - Exact-final-head CI, Ownership, OTBM Map Tools and AI Agent Tools conclusions after the final checkpoint commits.
conflicts: []
first_failure:
  marker: schema-test-runtime-dependency
  evidence: Initial OTBM Map Tools validation exposed test-only jsonschema imports unavailable in the OTBM workflow; both schema tests were rewritten to use the standard library and repository JSON validation, after which pre-final OTBM validation passed.
rejected_hypotheses:
  - Recompute QA-005 evidence inside QA-006.
  - Treat stale evidence as current certification.
  - Certify the whole world from bounded selected targets.
  - Add jsonschema as a production or workflow dependency solely for focused schema tests.
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
validation:
  - command: local focused QA-006/007 test run
    result: PASS
    evidence: 20 targeted semantic, schema and output-safety tests passed before publication.
  - command: GitHub Actions CI 29993845854
    result: PASS
    evidence: Pre-final CI passed on 96375947b358eb3256473b9c9aae80082582baff.
  - command: GitHub Actions Agent Task Ownership 29993845514
    result: PASS
    evidence: Pre-final ownership validation passed.
  - command: GitHub Actions OTBM Map Tools 29993845673
    result: PASS
    evidence: Pre-final focused OTBM suite passed after the test-only dependency correction.
  - command: GitHub Actions AI Agent Tools 29993845590
    result: PASS
    evidence: Pre-final AI Agent Tools job completed successfully.
blockers: []
next_action: Verify all exact-final-head required checks after the final QA-007 checkpoint commit; if green and review/scope audit is clean, mark PR 759 ready and merge without further feature commits.
```
