---
task_id: CAN-20260722-otbm-qa-014-asset-appearance-compatibility
program_id: CAN-PROGRAM-OTBM
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/otbm-qa-014-asset-appearance-compatibility-20260722
base_branch: main
created: 2026-07-22
updated: 2026-07-22
last_verified_commit: "663de1726e82145f5b8027126dbe434cfa74440b"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - CAN-20260722-otbm-qa-013-identifier-selector-integrity complete
  - Unified OTBM World Index available
  - canary-appearances-index-v1 available
  - canary-client-assets-index-v1 available
blocks:
  - OTBM-QA-017 deterministic change risk
owned_paths:
  exclusive:
    - tools/ai-agent/otbm_asset_compatibility.py
    - tools/ai-agent/otbm_asset_compatibility_tool.py
    - tools/ai-agent/test_otbm_asset_compatibility.py
    - tools/ai-agent/test_otbm_asset_compatibility_output_safety.py
    - tools/ai-agent/test_otbm_asset_compatibility_schema.py
    - docs/ai-agent/OTBM_ASSET_COMPATIBILITY.md
    - docs/ai-agent/OTBM_ASSET_COMPATIBILITY_MANIFEST.schema.json
    - docs/ai-agent/OTBM_ASSET_COMPATIBILITY.schema.json
    - docs/agents/tasks/active/CAN-20260722-otbm-qa-014-asset-appearance-compatibility.md
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/ai-agent/otbm_world_index.py
    - tools/ai-agent/otbm_appearances.py
    - tools/ai-agent/otbm_assets.py
    - tools/ai-agent/otbm_reachability_types.py
modules_touched:
  - otbm-asset-compatibility
reuses:
  - Unified OTBM World Index exact item placement inventory
  - canary-appearances-index-v1 object appearance records
  - canary-client-assets-index-v1 sprite coverage and asset-file evidence
  - canonical Reachability appearance semantics for walkability-relevant flags
public_interfaces:
  - canary-otbm-asset-compatibility-manifest-v1
  - canary-otbm-asset-compatibility-v1
cross_repo_tasks: []
---

# CAN-20260722 — OTBM-QA-014 Asset and Appearance Compatibility Audit

## Status

IMPLEMENTING — bounded QA-014 read-only compatibility composer. No OTBM, items.otb, appearances, sprites or client assets are mutated.

## Goal

Detect exact current-map compatibility gaps and asset-driven semantic drift by composing the canonical World Index with existing appearance and client-asset indexes, without adding a second parser or renderer.

## Safety boundaries

- Missing appearance records or uncovered/missing sprite evidence fail closed for claims that depend on them.
- Reuse the canonical appearance index and client asset index; do not decode protobuf/catalog formats independently.
- Appearance-driven walkability deltas are reported only from explicit canonical flags and only for item IDs actually used by the exact World Index.
- Static compatibility findings do not prove runtime/client rendering failure.
- No map, items.otb, appearances or client-asset mutation.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T21:20:00+02:00
head: 663de1726e82145f5b8027126dbe434cfa74440b
branch: feat/otbm-qa-014-asset-appearance-compatibility-20260722
pr: none
status: implementing
context_routes:
  - otbm
  - agent-governance
owned_paths:
  - tools/ai-agent/otbm_asset_compatibility.py
  - tools/ai-agent/otbm_asset_compatibility_tool.py
  - tools/ai-agent/test_otbm_asset_compatibility.py
  - tools/ai-agent/test_otbm_asset_compatibility_output_safety.py
  - tools/ai-agent/test_otbm_asset_compatibility_schema.py
  - docs/ai-agent/OTBM_ASSET_COMPATIBILITY.md
  - docs/ai-agent/OTBM_ASSET_COMPATIBILITY_MANIFEST.schema.json
  - docs/ai-agent/OTBM_ASSET_COMPATIBILITY.schema.json
  - docs/agents/tasks/active/CAN-20260722-otbm-qa-014-asset-appearance-compatibility.md
proven:
  - QA-013 feature, governance and lifecycle are merged; lifecycle squash merge is 663de1726e82145f5b8027126dbe434cfa74440b.
  - Roadmap QA-014 requires current-map item/appearance/asset compatibility plus appearance-driven walkability deltas and stale-evidence signaling.
  - Existing otbm_appearances.py already produces canary-appearances-index-v1 including object flags, frame groups and sprite IDs.
  - Existing otbm_assets.py already produces canary-client-assets-index-v1 including exact file existence and sprite-range coverage.
  - Existing World Index exposes exact used item IDs and placements; no new OTBM scanner is required.
derived:
  - QA-014 can be implemented as a deterministic report composer over these three existing contracts plus an optional exact baseline appearance index.
unknown:
  - A baseline appearance index is optional; without one, current compatibility is provable but semantic-delta claims remain not-evaluated.
conflicts: []
first_failure:
  marker: none
  evidence: No implementation validation has run yet.
rejected_hypotheses:
  - Reparse appearances protobuf or client asset catalog inside QA-014: existing canonical indexes already expose required evidence.
changed_paths:
  - docs/agents/tasks/active/CAN-20260722-otbm-qa-014-asset-appearance-compatibility.md
validation:
  - command: fresh live-state/overlap preflight
    result: PASS
    evidence: main 663de1726e82145f5b8027126dbe434cfa74440b; no competing QA-014 PR found.
blockers: []
next_action: Open a draft PR, implement the bounded compatibility composer and focused tests, then validate OTBM/AI workflows before shared-doc and final-gate updates.
```
