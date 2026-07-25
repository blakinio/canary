---
task_id: CAN-20260725-otbm-crystal-parity-baseline
program_id: CAN-PROGRAM-REAL-TIBIA-PARITY
status: validating
agent: "GPT-5.6 Thinking"
owner: OTBM analysis tooling / Real Tibia parity
created: 2026-07-25T08:00:00+02:00
updated: 2026-07-25T16:00:00+02:00
last_verified_commit: "9c80397111f0e0c70be3b3fff23c3a85b2e35ce9"
branch: analysis/otbm-crystal-parity-baseline
base_branch: main
base: main@c468be4c34039b4b3e9f4e320c4b125cb6998d77
related_pr: "913"
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
  - OTBM Script Resolution as a later selected-scope evidence layer
dependencies: []
blockers:
  - Content-level adoption requires bounded reviewed regions or landmarks plus current OTServBR correlation evidence; this global baseline alone does not authorize map mutation.
---

# Goal

Produce a deterministic, read-only comparison between the user-supplied OTServBR OTBM and the exact CrystalServer global-world snapshot from the user-selected `main` branch without adding another parser, renderer, pathfinder or mutation pipeline.

# Exact selected inputs

## Target map

- role: current user/server map;
- local filename: `otservbr(4).otbm`;
- size: `184776037` bytes;
- SHA-256: `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2`;
- repository status: external input; never committed.

## CrystalServer global reference

- repository: `zimbadev/crystalserver`;
- branch selected by user: `main`;
- pinned commit: `75e9c72e33ce2c3f193e4f2d2ff17ebae4bbfaac`;
- canonical path: `data-global/world/world.otbm`;
- Git blob SHA-1: `ca281acba48de2ebdf785b2d025f1e4696d3cc5f`;
- tracked blob size: `52836960` bytes;
- tracked blob SHA-256: `3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034`;
- tracked format: gzip content despite the `.otbm` filename;
- decompressed OTBM size: `186660172` bytes;
- decompressed OTBM SHA-256: `4b2099f38df05d4be68d1ba1265754e9fd6da09742025d92644fa4b1a12eb120`;
- repository status: external read-only input; never committed.

The separate `data-crystal/world/world.otbm` file is the small Crystal custom/test world and is not the selected global reference. The first draft selected it incorrectly; PR #913 was returned to draft before merge and every map-derived count was regenerated from `data-global`.

# Scope

Included:

- exact immutable provenance for the repository blob, decompressed Crystal OTBM payload and target OTBM;
- canonical World Index build and summary for both maps;
- exact full-index Semantic OTBM Diff;
- exact tile, item-stack, house, AID, UID, house-door and teleport difference counts with bounded samples;
- the narrow correction to the existing full-index area-major merge;
- bounded exact-count paths after the sample budget is full;
- explicit unsupported and unresolved boundaries instead of heuristic item or gameplay matching;
- one durable factual report with commands, hashes, formats, counts and limitations.

Excluded:

- committing either OTBM, compressed map transport, generated `.widx`, item scan or full diff JSON;
- combining supplemental Crystal event, quest, custom or world-change map fragments;
- map mutation, copying Crystal regions or automatically selecting repairs;
- visual/AI comparison or a second renderer;
- name-, sprite-, proximity- or guessed-purpose matching;
- treating numeric IDs as automatically shared namespaces;
- Crystal Lua/XML runtime parity, gameplay correctness or Physical E2E in this baseline;
- treating CrystalServer as map authority.

# Acceptance criteria

1. The exact Crystal global repository blob is acquired from the pinned commit and verified against Git blob SHA-1 plus SHA-256.
2. Gzip transport and decompressed OTBM payload provenance are recorded separately.
3. Both maps are indexed with the existing native scanner and `canary-otbm-world-index-v1` contract.
4. `canary-otbm-semantic-diff-v1` completes for the full compatible scope with exact counts.
5. The full-index area-order defect has focused regression coverage and no new parser/index/format.
6. The report separates exact structural/static/mechanic evidence from runtime, gameplay and repair claims.
7. No `.otbm`, `.widx`, archive, external asset, generated full JSON report or render is present in the final PR diff.
8. Temporary acquisition/export workflows and run-locator files are absent from the final PR diff.
9. Relevant focused tests and final required checks pass on the final head.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T16:00:00+02:00
head: 9c80397111f0e0c70be3b3fff23c3a85b2e35ce9
branch: analysis/otbm-crystal-parity-baseline
pr: 913
status: ready
context_routes:
  - agent-governance
  - otbm
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260725-otbm-crystal-parity-baseline.md
  - docs/agents/real-tibia/OTBM_CRYSTAL_PARITY_BASELINE_2026-07-25.md
  - docs/ai-agent/OTBM_SEMANTIC_DIFF.md
  - docs/agents/CHANGELOG.md
  - tools/ai-agent/otbm_semantic_diff_analysis.py
  - tools/ai-agent/otbm_semantic_diff_types.py
  - tools/ai-agent/test_otbm_semantic_diff.py
proven:
  - Crystal main at commit 75e9c72e33ce2c3f193e4f2d2ff17ebae4bbfaac contains separate global and Crystal custom maps; the selected global blob is ca281acba48de2ebdf785b2d025f1e4696d3cc5f.
  - The selected repository blob is gzip transport content, size 52836960 and SHA-256 3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034.
  - The decompressed Crystal OTBM payload is size 186660172 and SHA-256 4b2099f38df05d4be68d1ba1265754e9fd6da09742025d92644fa4b1a12eb120.
  - The OTServBR input is external-only, size 184776037 and SHA-256 a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2.
  - Both maps use OTBM version 4 and items major/minor 4/4 and were indexed by the same scanner and World Index format.
  - Crystal global contains 18997668 tiles, 24504223 placements, 9323 mechanic placements and 1197 canonical areas.
  - OTServBR contains 17972761 tiles, 23359571 placements, 9339 mechanic placements and 1171 canonical areas.
  - The indexes share 1159 exact floor-aware area keys and 17871388 exact tile positions.
  - Full Semantic Diff found 17214872 unchanged tiles and 1884169 positions with at least one finding.
  - The exact report contains 3277274 findings and has SHA-256 e093fefdf603120933a52faf3bcd625cb94c650f7acba87acf4d95f66a56b04a.
  - The full-index correction uses canonical area/tile ordering without a new parser or format and passes 34 focused tests.
  - PR 913 contains exactly seven durable text/source paths and no map, archive, generated index/report, workflow or run-locator file.
derived:
  - The two maps represent the same broad global coordinate frame and can be compared at exact positions without a coordinate transform.
  - A bounded city, quest or mechanic review can reuse exact-position Semantic Diff plus current OTServBR correlation evidence.
  - Global finding totals prioritize investigation but do not identify which divergence is intentional or safe to adopt.
unknown:
  - Which Crystal-only or OTServBR-only positions are intentional version/content divergence versus missing current content.
  - Crystal Lua/XML handler and runtime behavior parity because the baseline does not execute or resolve Crystal handlers.
  - Walkability deltas because no compatible appearances catalogue was supplied to this full run.
conflicts: []
first_failure:
  marker: wrong-crystal-map-selection
  evidence: The initial draft selected data-crystal/world/world.otbm, a separate small Crystal custom/test world; the user identified the global map before merge, PR 913 was returned to draft and every invalid map-derived count was replaced.
rejected_hypotheses:
  - Treating data-crystal/world/world.otbm as the full global donor map.
  - Feeding the gzip repository blob directly to the OTBM scanner as if it were the decompressed payload.
  - Preserving the superseded zero-shared-area conclusion from the first draft.
  - Treating exact numeric item, house, action or unique IDs as automatically equivalent intent.
  - Creating a second OTBM parser, renderer or pathfinder for this comparison.
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
    evidence: exact pinned global blob was verified and published as one-day external artifact 8619590722
  - command: gzip verification and decompression
    result: PASS
    evidence: repository transport and decompressed OTBM payload hashes and sizes were recorded separately
  - command: canonical World Index builds and full exact-position Semantic Diff
    result: PASS
    evidence: exact report completed with 3277274 findings and SHA-256 e093fefdf603120933a52faf3bcd625cb94c650f7acba87acf4d95f66a56b04a
  - command: python -m unittest -v tools/ai-agent/test_otbm_semantic_diff.py
    result: PASS
    evidence: 34 focused tests passed using source exported from head f6ddfe37bc55b04e29c0ea1fa94cb1146abc2161
  - command: exact-head focused workflow set on 624f31a5898407f31c8bd58e1a50ad8dd511f193
    result: PASS
    evidence: Ownership 30159732619, OTBM Map Tools 30159732622, Semantic Diff 30159732625, Registry 30159732631, Upstream 30159732634 and AI Agent Tools 30159732641 succeeded
  - command: pre-ready CI workflow run 30159732754
    result: PASS
    evidence: Fast Checks, Lua Tests, Linux compile and Required aggregation succeeded
  - command: current-main synchronization merge
    result: PASS
    evidence: current main was merged with both OTBM and QRI-022 changelog entries preserved
  - command: protected final-head workflow set after current-main synchronization
    result: NOT_RUN
    evidence: exact-head workflows must run on a connector-authored head after this checkpoint commit
blockers:
  - Selected content adoption requires bounded reviewed evidence and the relevant current OTServBR Script Resolution, reachability or other subsystem proof.
next_action: Trigger and validate the exact-head workflow set after current-main synchronization, then apply ci:final-gate and squash-merge PR 913 without further code changes.
```
