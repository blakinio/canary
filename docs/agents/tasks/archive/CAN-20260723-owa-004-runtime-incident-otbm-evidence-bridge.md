---
task_id: CAN-20260723-owa-004-runtime-incident-otbm-evidence-bridge
program_id: CAN-PROGRAM-OTBM-WORLD-ASSURANCE-OPERATIONS
coordination_id: OWA-004
status: completed
agent: "GPT-5.6 Thinking"
branch: feat/owa-004-runtime-incident-evidence-bridge-20260723
base_branch: main
created: 2026-07-23T19:55:32+02:00
updated: 2026-07-24T00:31:43+02:00
completed: 2026-07-24T00:31:43+02:00
last_verified_commit: "a3e7571303c5ce87ed85c054a8a7607cd4433d5c"
risk: medium
related_issue: ""
related_pr: "838"
depends_on:
  - "OWA-002 lifecycle PR #834"
  - "QA-018 Compact Evidence Gateway"
  - "existing OTBM route/preflight/failure-triage evidence contracts"
blocks: []
owned_paths:
  exclusive:
    - docs/ai-agent/OTBM_RUNTIME_INCIDENT_EVIDENCE_BRIDGE.md
    - docs/ai-agent/OTBM_RUNTIME_INCIDENT_EVIDENCE_BINDINGS.schema.json
    - docs/ai-agent/OTBM_RUNTIME_INCIDENT_EVIDENCE_BRIDGE.schema.json
    - tools/ai-agent/otbm_runtime_incident_evidence_bridge.py
    - tools/ai-agent/otbm_runtime_incident_evidence_bridge_tool.py
    - tools/ai-agent/test_otbm_runtime_incident_evidence_bridge.py
    - tools/ai-agent/test_otbm_runtime_incident_evidence_bridge_output_safety.py
    - tools/ai-agent/test_otbm_runtime_incident_evidence_bridge_schema.py
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - docs/ai-agent/OTBM_EVIDENCE_GATEWAY.md
    - tools/ai-agent/otbm_evidence_gateway.py
    - tools/e2e/otbm_route_failure_triage.py
cross_repo_tasks: []
---

# Goal

Deliver `OWA-004 — Runtime Incident to OTBM Evidence Bridge` as a bounded deterministic bridge from one explicit reviewed incident selector to exact compatible existing OTBM evidence through the canonical QA-018 Compact Evidence Gateway.

# Completion

- [x] Supports exactly one explicit selector: exact position, transition ID, interaction ID, landmark ID, route ID or reviewed preflight reference.
- [x] Rejects missing, unsupported and ambiguous selector bindings.
- [x] Delegates source/extract normalization to `otbm_evidence_gateway.normalize_manifest()`.
- [x] Delegates executed extraction to `otbm_evidence_gateway.build_evidence_bundle()`.
- [x] Preserves QA-018 fail-closed source SHA-256, format and JSON Pointer compatibility checks.
- [x] Preserves opaque downstream failure-triage references without reclassifying runtime failures.
- [x] Provides deterministic plan-only and executed outputs with exact binding/bundle provenance.
- [x] Covers create-new/no-clobber, explicit overwrite, symlink/path confinement and input/output collision safety.
- [x] Does not parse runtime logs, infer selectors, diagnose root cause, pathfind, run Physical E2E, mutate maps or emit `NEXT_ACTION`.
- [x] Public schemas, documentation and focused schema/output-safety/behavior tests are delivered.
- [x] Exact feature head `01246f0c37c1656141302408bd139967b39f05fb` passed Agent Task Ownership, OTBM Map Tools, AI Agent Tools and repository CI.
- [x] Ready-state protected full CI run `30049111197` (`CI #5211`) passed on the unchanged exact feature head.
- [x] Review/thread audit found no unresolved reviews, requested changes, comments or review threads.
- [x] PR #838 squash-merged as `a3e7571303c5ce87ed85c054a8a7607cd4433d5c`.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T22:31:43Z
head: 01246f0c37c1656141302408bd139967b39f05fb
branch: feat/owa-004-runtime-incident-evidence-bridge-20260723
pr: 838
status: completed
context_routes:
  - agent-governance
  - otbm
proven:
  - QA-018 remains the sole bounded exact evidence extractor and owns source hash/format/pointer validation.
  - The bridge accepts only explicit reviewed selectors and does not perform fuzzy discovery or arbitrary log parsing.
  - Existing OTBM Physical E2E failure triage remains the runtime failure-classification owner.
  - Exact feature head 01246f0c37c1656141302408bd139967b39f05fb passed Agent Task Ownership run 30048976497, OTBM Map Tools run 30048976234, AI Agent Tools run 30048976525 and CI run 30048976533.
  - Protected ready-state CI run 30049111197 completed successfully on the unchanged exact feature head.
  - PR 838 was squash-merged as a3e7571303c5ce87ed85c054a8a7607cd4433d5c.
  - No generated OTBM, WIDX, evidence bundle, render or proprietary asset was committed.
derived:
  - Reviewed exact selector bindings are the narrowest safe incident-to-static-evidence bridge without taking runtime diagnosis ownership.
unknown: []
conflicts: []
first_failure:
  marker: none
  evidence: no unresolved implementation, CI, review or merge failure remained at feature merge
rejected_hypotheses:
  - Parse arbitrary runtime logs or perform fuzzy selector discovery.
  - Reclassify Physical E2E failures inside OWA-004.
  - Add a second evidence extractor, OTBM parser, World Index, pathfinder or E2E runner.
validation:
  - command: focused OWA-004 unit/schema/output-safety suites through AI Agent Tools and OTBM Map Tools
    result: PASS
    evidence: exact feature head workflow runs 30048976525 and 30048976234
  - command: Agent Task Ownership
    result: PASS
    evidence: run 30048976497
  - command: repository CI exact-final-head
    result: PASS
    evidence: run 30048976533
  - command: protected ready-state full CI
    result: PASS
    evidence: run 30049111197 / CI #5211
blockers: []
next_action: Close OWA-004 lifecycle, update the OWA programme queue/handoff, then perform a fresh OWA-006 target-selection and ownership preflight without entering TCR-owned work.
```

## Automated lifecycle completion

- Feature PR: #838.
- Final feature head: `01246f0c37c1656141302408bd139967b39f05fb`.
- Merge commit: `a3e7571303c5ce87ed85c054a8a7607cd4433d5c`.
- Merged at: `2026-07-23T22:31:43Z`.
- Ready-state protected CI: run `30049111197`, success.
- This archive releases OWA-004 task ownership after lifecycle merge.
