---
task_id: CAN-20260722-otbm-qa-015-static-performance-hotspots
program_id: CAN-PROGRAM-OTBM
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/otbm-qa-015-static-performance-hotspots-20260722
base_branch: main
created: 2026-07-22
updated: 2026-07-22
last_verified_commit: "663de1726e82145f5b8027126dbe434cfa74440b"
risk: medium
related_issue: ""
related_pr: ""
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

IMPLEMENTING — deterministic static hotspot candidates only. Runtime performance claims remain outside this task.

## Goal

Identify exact map regions/tiles whose static OTBM density merits targeted runtime profiling, using explicit reviewed thresholds and the existing World Index only.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T21:45:00+02:00
head: 663de1726e82145f5b8027126dbe434cfa74440b
branch: feat/otbm-qa-015-static-performance-hotspots-20260722
pr: none
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
  - Unified World Index exposes exact tile placement counts, item depths, mechanic placements and 256x256 area postings.
  - QA-015 does not require a second parser, pathfinder or runtime profiler.
derived:
  - Explicit policy thresholds over exact World Index metrics are sufficient for a deterministic static candidate report.
unknown:
  - Runtime CPU, memory, network and client-render impact are not established by static density evidence.
conflicts: []
first_failure:
  marker: none
  evidence: No implementation validation has run yet.
rejected_hypotheses:
  - Infer runtime slowness directly from static density: roadmap explicitly limits QA-015 to investigation candidates.
changed_paths:
  - docs/agents/tasks/active/CAN-20260722-otbm-qa-015-static-performance-hotspots.md
validation:
  - command: fresh live-state/overlap preflight
    result: PASS
    evidence: main 663de1726e82145f5b8027126dbe434cfa74440b; no competing QA-015 PR found.
blockers: []
next_action: Open a draft PR, implement explicit-threshold World Index hotspot analysis and focused tests, then validate current-head OTBM/AI workflows.
```
