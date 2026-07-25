---
task_id: CAN-20260725-otbm-crystal-parity-baseline
program_id: CAN-PROGRAM-REAL-TIBIA-PARITY
status: review
agent: "GPT-5.6 Thinking"
owner: OTBM analysis tooling / Real Tibia parity
created: 2026-07-25T08:00:00+02:00
updated: 2026-07-25T19:55:00+02:00
last_verified_commit: "a364ec028105f7663fb40ec75e5c1b0607706d2a"
branch: analysis/otbm-crystal-global-parity-final
base_branch: main
base: main@c468be4c34039b4b3e9f4e320c4b125cb6998d77
related_pr: "923"
module_id: otbm-tooling
routes:
  - otbm
  - real-tibia-parity
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260725-otbm-crystal-parity-baseline.md
    - docs/agents/real-tibia/OTBM_CRYSTAL_PARITY_BASELINE_2026-07-25.md
    - docs/ai-agent/OTBM_SEMANTIC_DIFF.md
    - tools/ai-agent/otbm_semantic_diff_analysis.py
    - tools/ai-agent/otbm_semantic_diff_types.py
    - tools/ai-agent/test_otbm_semantic_diff.py
  shared:
    - docs/agents/CHANGELOG.md
  read_only:
    - tools/ai-agent/otbm_item_audit_scan.cpp
    - tools/ai-agent/otbm_world_index.py
reuse:
  - Unified OTBM World Index
  - Semantic OTBM Diff
  - OTBM item/mechanic audit
dependencies: []
blockers:
  - Content-level adoption requires a separate bounded review with current OTServBR Script Resolution, reachability or other subsystem proof; this baseline does not authorize map mutation.
---

# Goal

Produce a deterministic, read-only comparison between the user-supplied OTServBR OTBM and the exact CrystalServer global-world snapshot, while fixing the existing full-index Semantic OTBM Diff path without adding another parser, renderer, pathfinder or mutation pipeline.

# Exact selected inputs

## Target OTServBR map

- external filename: `otservbr(4).otbm`;
- size: `184776037` bytes;
- SHA-256: `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2`;
- external only; never committed.

## CrystalServer global reference

- repository: `zimbadev/crystalserver`;
- pinned commit: `75e9c72e33ce2c3f193e4f2d2ff17ebae4bbfaac`;
- selected path: `data-global/world/world.otbm`;
- Git blob SHA-1: `ca281acba48de2ebdf785b2d025f1e4696d3cc5f`;
- tracked gzip size: `52836960` bytes;
- tracked gzip SHA-256: `3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034`;
- decompressed OTBM size: `186660172` bytes;
- decompressed OTBM SHA-256: `4b2099f38df05d4be68d1ba1265754e9fd6da09742025d92644fa4b1a12eb120`;
- external read-only input; never committed.

`data-crystal/world/world.otbm` is the separate small Crystal custom/test world. Its initial selection was rejected before merge and every map-derived count was regenerated from `data-global`.

# Acceptance criteria

1. Repository-blob and decompressed-payload provenance are independently pinned.
2. Both maps are indexed by the existing scanner and `canary-otbm-world-index-v1`.
3. `canary-otbm-semantic-diff-v1` completes with exact full-index counters.
4. The area-major correction has focused regression coverage and adds no parser or format.
5. The report separates static evidence from runtime, gameplay and repair claims.
6. The final diff contains exactly seven durable text/source paths and no workflow, OTBM, archive, `.widx`, render or generated full report.
7. Focused checks, ownership and protected final CI pass on the exact final head before squash merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T19:55:00+02:00
head: a364ec028105f7663fb40ec75e5c1b0607706d2a
branch: analysis/otbm-crystal-global-parity-final
pr: 923
status: final-gate
context_routes:
  - agent-governance
  - otbm
  - real-tibia-parity
owned_paths:
  - docs/agents/CHANGELOG.md
  - docs/agents/real-tibia/OTBM_CRYSTAL_PARITY_BASELINE_2026-07-25.md
  - docs/agents/tasks/active/CAN-20260725-otbm-crystal-parity-baseline.md
  - docs/ai-agent/OTBM_SEMANTIC_DIFF.md
  - tools/ai-agent/otbm_semantic_diff_analysis.py
  - tools/ai-agent/otbm_semantic_diff_types.py
  - tools/ai-agent/test_otbm_semantic_diff.py
proven:
  - Crystal global and OTServBR use OTBM version 4 and items major/minor 4/4 and were indexed by the same canonical scanner and World Index format.
  - Crystal global contains 18997668 tiles, 24504223 placements, 9323 mechanic placements and 1197 canonical areas.
  - OTServBR contains 17972761 tiles, 23359571 placements, 9339 mechanic placements and 1171 canonical areas.
  - The indexes share 1159 area keys and 17871388 exact tile positions.
  - Full Semantic Diff found 17214872 unchanged tiles, 1884169 changed positions and 3277274 exact findings.
  - The exact report SHA-256 is e093fefdf603120933a52faf3bcd625cb94c650f7acba87acf4d95f66a56b04a.
  - The correction uses canonical area/tile ordering and passes 34 focused tests without a new parser or format.
  - PR 923 contains exactly seven durable paths and no binary map, generated index, archive, workflow or temporary run locator.
  - PR 913 was closed without merge; PR 923 is the authoritative clean branch and no wrong-map baseline entered main.
derived:
  - The maps share the same broad global coordinate frame and require no coordinate transform.
  - Bounded city, quest or mechanic reviews can reuse this exact-position baseline with current OTServBR correlation evidence.
unknown:
  - Which divergences are intentional version/content changes versus missing content.
  - Crystal Lua/XML runtime and gameplay parity.
  - Walkability deltas because no compatible appearances catalogue was supplied to the full run.
conflicts: []
first_failure:
  marker: wrong-crystal-map-selection
  evidence: The first draft selected data-crystal/world/world.otbm; the user identified the global map before merge and all invalid map-derived evidence was replaced.
rejected_hypotheses:
  - Treating data-crystal/world/world.otbm as the global donor map.
  - Feeding the gzip repository blob directly to the OTBM scanner.
  - Preserving the superseded zero-shared-area conclusion.
  - Treating matching numeric identifiers as automatically equivalent intent.
  - Creating a second parser, renderer or pathfinder.
changed_paths:
  - docs/agents/CHANGELOG.md
  - docs/agents/real-tibia/OTBM_CRYSTAL_PARITY_BASELINE_2026-07-25.md
  - docs/agents/tasks/active/CAN-20260725-otbm-crystal-parity-baseline.md
  - docs/ai-agent/OTBM_SEMANTIC_DIFF.md
  - tools/ai-agent/otbm_semantic_diff_analysis.py
  - tools/ai-agent/otbm_semantic_diff_types.py
  - tools/ai-agent/test_otbm_semantic_diff.py
validation:
  - command: Crystal global acquisition workflow run 30158472867
    result: PASS
    evidence: exact pinned global blob was verified in one-day external artifact 8619590722
  - command: canonical World Index builds and full Semantic Diff
    result: PASS
    evidence: report completed with 3277274 findings and SHA-256 e093fefdf603120933a52faf3bcd625cb94c650f7acba87acf4d95f66a56b04a
  - command: python -m unittest -v tools/ai-agent/test_otbm_semantic_diff.py
    result: PASS
    evidence: 34 focused tests passed on the corrected implementation source
  - command: previous corrected implementation head 624f31a5898407f31c8bd58e1a50ad8dd511f193
    result: PASS
    evidence: Ownership, Semantic Diff, OTBM Map Tools, AI Agent Tools and CI were green before the branch was superseded by clean PR 923
  - command: PR 923 head a364ec028105f7663fb40ec75e5c1b0607706d2a
    result: BLOCKED
    evidence: pull-request workflow records ended action_required before creating jobs because the head was emitted by github-actions bot
  - command: protected exact-head workflow set after final checkpoint commit
    result: NOT_RUN
    evidence: ci:final-gate was applied before this connector-authored checkpoint commit
blockers:
  - No merge blocker remains outside exact-head final CI.
next_action: Verify all required workflows on the connector-authored final checkpoint head and squash-merge PR 923 only when every required check is green.
```
