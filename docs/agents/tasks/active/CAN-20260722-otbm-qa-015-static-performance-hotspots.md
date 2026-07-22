---
task_id: CAN-20260722-otbm-qa-015-static-performance-hotspots
program_id: CAN-PROGRAM-OTBM
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/otbm-qa-015-static-performance-hotspots-20260722
base_branch: main
created: 2026-07-22
updated: 2026-07-22
last_verified_commit: "1bd9f96c2b4c8a5188315fa46c5c9a43f5ad55b5"
risk: medium
related_issue: ""
related_pr: "735"
depends_on:
  - OTBM-QA-014 implementation pre-final validated on PR 734
  - Unified OTBM World Index available
blocks:
  - OTBM-QA-017 deterministic change risk
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
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/ai-agent/otbm_world_index.py
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

IMPLEMENTING — deterministic static hotspot candidate composer is implemented on draft PR #735; current-head validation is running. Runtime performance claims remain outside this task.

## Goal

Identify exact map regions/tiles whose static OTBM density merits targeted runtime profiling, using explicit reviewed thresholds and the existing World Index only.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T22:00:00+02:00
head: 1bd9f96c2b4c8a5188315fa46c5c9a43f5ad55b5
branch: feat/otbm-qa-015-static-performance-hotspots-20260722
pr: 735
status: implementing
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
  - Roadmap QA-015 requires static hotspot candidates and explicitly forbids runtime performance claims without subsystem-owned profiling.
  - Unified World Index exposes exact tile placement counts, item depths, mechanic placements and area-local density evidence.
  - PR 735 implements explicit-threshold tile and 256x256-floor area candidates without a second parser, pathfinder or runtime profiler.
derived:
  - Exact static density can prioritize bounded runtime investigation but cannot prove runtime impact.
unknown:
  - Runtime CPU, memory, network and client-render impact are not established by static density evidence.
conflicts: []
first_failure:
  marker: none
  evidence: Current-head validation is running; no completed failure is known.
rejected_hypotheses:
  - Infer runtime slowness directly from static density: roadmap explicitly limits QA-015 to investigation candidates.
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
  - command: fresh live-state/overlap preflight
    result: PASS
    evidence: main 663de1726e82145f5b8027126dbe434cfa74440b; no competing QA-015 PR found.
blockers: []
next_action: Wait for CI, Ownership, OTBM Map Tools and AI Agent Tools on the current implementation head; fix only evidence-backed failures before final-gate checkpointing.
```
