---
task_id: CAN-20260722-otbm-qa-015-static-performance-hotspots
program_id: CAN-PROGRAM-OTBM
status: ready
agent: "GPT-5.6 Thinking"
branch: feat/otbm-qa-015-static-performance-hotspots-20260722
base_branch: main
created: 2026-07-22
updated: 2026-07-22
last_verified_commit: "0e671304f0c0097d1f685e422802d3246a5ffa13"
risk: medium
related_issue: ""
related_pr: "735"
depends_on:
  - shared-doc governance PR 743 merged
  - Unified OTBM World Index available
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_static_hotspots.py
    - tools/ai-agent/otbm_static_hotspots_tool.py
    - tools/ai-agent/test_otbm_static_hotspots.py
    - tools/ai-agent/test_otbm_static_hotspots_output_safety.py
    - tools/ai-agent/test_otbm_static_hotspots_schema.py
    - docs/ai-agent/OTBM_STATIC_HOTSPOTS.md
    - docs/ai-agent/OTBM_STATIC_HOTSPOT_POLICY.schema.json
    - docs/ai-agent/OTBM_STATIC_HOTSPOTS.schema.json
    - docs/agents/tasks/active/CAN-20260722-otbm-qa-015-static-performance-hotspots.md
modules_touched:
  - otbm-static-hotspots
reuses:
  - Unified OTBM World Index tile, placement, mechanic and area evidence
public_interfaces:
  - canary-otbm-static-hotspot-policy-v1
  - canary-otbm-static-hotspots-v1
cross_repo_tasks: []
---

# CAN-20260722 — OTBM-QA-015 Static Map Performance Hotspot Analyzer

## Status

READY — bounded QA-015 feature implementation is complete on PR #735. Shared governance merged through PR #743. `ci:final-gate` was applied before this final checkpoint commit; no further feature-branch commits are permitted.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T23:21:00+02:00
head: 0e671304f0c0097d1f685e422802d3246a5ffa13
branch: feat/otbm-qa-015-static-performance-hotspots-20260722
pr: 735
status: ready
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - tools/ai-agent/otbm_static_hotspots.py
  - tools/ai-agent/otbm_static_hotspots_tool.py
  - tools/ai-agent/test_otbm_static_hotspots.py
  - tools/ai-agent/test_otbm_static_hotspots_output_safety.py
  - tools/ai-agent/test_otbm_static_hotspots_schema.py
  - docs/ai-agent/OTBM_STATIC_HOTSPOTS.md
  - docs/ai-agent/OTBM_STATIC_HOTSPOT_POLICY.schema.json
  - docs/ai-agent/OTBM_STATIC_HOTSPOTS.schema.json
  - docs/agents/tasks/active/CAN-20260722-otbm-qa-015-static-performance-hotspots.md
proven:
  - PR 735 implements explicit-threshold static tile and 256x256-floor area hotspot candidates using the canonical World Index only.
  - Runtime CPU, memory, network, database and client-render impact are not claimed; the output is an investigation-priority aid only.
  - Pre-final CI 29958979704, Ownership 29958979580, OTBM Map Tools 29958979555 and AI Agent Tools 29958979529 all passed on head 0e671304f0c0097d1f685e422802d3246a5ffa13.
  - Shared governance PR 743 merged as 47759e49fca04526ef24097e9f3cf859b0f66b3a after full final-gate CI 29960786583 succeeded.
  - ci:final-gate was applied to PR 735 before this final checkpoint commit.
derived:
  - QA-015 is ready for immutable exact-final-head validation and merge without further feature changes.
unknown:
  - Actual runtime performance impact remains outside static evidence and requires subsystem-owned profiling.
conflicts: []
first_failure:
  marker: none
  evidence: No unresolved implementation, focused-test or governance failure remains.
rejected_hypotheses:
  - Infer runtime slowness directly from static density.
changed_paths:
  - docs/agents/tasks/active/CAN-20260722-otbm-qa-015-static-performance-hotspots.md
  - tools/ai-agent/otbm_static_hotspots.py
  - tools/ai-agent/otbm_static_hotspots_tool.py
  - tools/ai-agent/test_otbm_static_hotspots.py
  - tools/ai-agent/test_otbm_static_hotspots_output_safety.py
  - tools/ai-agent/test_otbm_static_hotspots_schema.py
  - docs/ai-agent/OTBM_STATIC_HOTSPOTS.md
  - docs/ai-agent/OTBM_STATIC_HOTSPOT_POLICY.schema.json
  - docs/ai-agent/OTBM_STATIC_HOTSPOTS.schema.json
validation:
  - command: GitHub Actions pre-final CI/Ownership/OTBM/AI
    result: PASS
    evidence: 29958979704, 29958979580, 29958979555 and 29958979529 all succeeded.
blockers: []
next_action: Verify exact-final-head CI, Ownership, OTBM Map Tools and AI Agent Tools plus review/mergeability on PR 735, then mark ready, enable auto-merge and complete lifecycle closure after merge.
```
