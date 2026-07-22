---
task_id: CAN-20260722-otbm-qa-018-compact-evidence-gateway
program_id: CAN-PROGRAM-OTBM
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/otbm-qa-018-compact-evidence-gateway-20260722
base_branch: main
created: 2026-07-22
updated: 2026-07-22
last_verified_commit: "8bdeb2747356727df80a3b95073aa29a4dca7818"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - OTBM-QA-017 implementation active on PR 739
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_evidence_gateway.py
    - tools/ai-agent/otbm_evidence_gateway_tool.py
    - tools/ai-agent/test_otbm_evidence_gateway.py
    - tools/ai-agent/test_otbm_evidence_gateway_output_safety.py
    - tools/ai-agent/test_otbm_evidence_gateway_schema.py
    - docs/ai-agent/OTBM_EVIDENCE_GATEWAY.md
    - docs/ai-agent/OTBM_EVIDENCE_GATEWAY_MANIFEST.schema.json
    - docs/ai-agent/OTBM_EVIDENCE_GATEWAY.schema.json
    - docs/agents/tasks/active/CAN-20260722-otbm-qa-018-compact-evidence-gateway.md
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
modules_touched:
  - otbm-evidence-gateway
reuses:
  - versioned JSON reports emitted by existing canonical OTBM tools
public_interfaces:
  - canary-otbm-evidence-gateway-manifest-v1
  - canary-otbm-evidence-bundle-v1
cross_repo_tasks: []
---

# CAN-20260722 — OTBM-QA-018 Compact OTBM Evidence Gateway

## Status

IMPLEMENTING — read-only bounded evidence extraction/composition only; subsystem ownership remains with source producers and downstream consumers.

## Goal

Provide compact exact OTBM evidence bundles for downstream agents without duplicating OTBM parsing, validation, routing or E2E logic.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T23:00:00+02:00
head: 8bdeb2747356727df80a3b95073aa29a4dca7818
branch: feat/otbm-qa-018-compact-evidence-gateway-20260722
pr: none
status: implementing
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - tools/ai-agent/otbm_evidence_gateway.py
  - tools/ai-agent/otbm_evidence_gateway_tool.py
  - tools/ai-agent/test_otbm_evidence_gateway.py
  - tools/ai-agent/test_otbm_evidence_gateway_output_safety.py
  - tools/ai-agent/test_otbm_evidence_gateway_schema.py
  - docs/ai-agent/OTBM_EVIDENCE_GATEWAY.md
  - docs/ai-agent/OTBM_EVIDENCE_GATEWAY_MANIFEST.schema.json
  - docs/ai-agent/OTBM_EVIDENCE_GATEWAY.schema.json
  - docs/agents/tasks/active/CAN-20260722-otbm-qa-018-compact-evidence-gateway.md
proven:
  - Roadmap QA-018 is a read-only/query and evidence-composition boundary over existing canonical contracts.
  - QA-018 must not create another parser, validator, route planner or E2E tool.
derived:
  - Exact SHA/format-pinned JSON sources plus bounded reviewed JSON Pointer extracts can provide compact downstream context without reinterpreting source semantics.
unknown:
  - Downstream subsystem-specific scenario design, runtime execution and acceptance remain outside the gateway.
conflicts: []
first_failure:
  marker: none
  evidence: No implementation validation has run yet.
rejected_hypotheses:
  - Build a new universal OTBM validator in the gateway: roadmap explicitly restricts QA-018 to composition/query.
changed_paths:
  - docs/agents/tasks/active/CAN-20260722-otbm-qa-018-compact-evidence-gateway.md
validation:
  - command: fresh live-state/overlap preflight
    result: PASS
    evidence: main 8bdeb2747356727df80a3b95073aa29a4dca7818; no competing QA-018 PR found.
blockers: []
next_action: Open a draft PR, implement bounded exact-source JSON Pointer extraction and focused tests, then validate current-head workflows.
```
