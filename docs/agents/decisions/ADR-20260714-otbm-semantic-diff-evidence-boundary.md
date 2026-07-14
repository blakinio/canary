# ADR-20260714: Semantic OTBM diff evidence boundary

- Status: accepted for Phase 6
- Date: 2026-07-14
- Coordination: `OTS-OTBM-VALIDATION`
- Task: `CAN-20260714-otbm-semantic-diff`

## Context

Phases 1–5 already provide one native OTBM scanner, one deterministic World Index, quest/source correlation, Phase 3 walkability/reachability, Phase 4 spawn/NPC evidence, Phase 5 storage evidence and one factual renderer. A semantic map diff must reuse these contracts. Parsing maps again, duplicating walkability or treating static changes as gameplay defects would create contradictory evidence systems.

## Decision

Phase 6 consumes two compatible `canary-otbm-world-index-v1` binaries and their manifests. It never reads OTBM structure itself. Optional real map paths are hash-verified only. The implementation streams sorted tile records, compares exact tile/stack/mechanic evidence and calls the existing Phase 3 tile classifier for ground/blocker/walkability state.

### Cross-index identity

World Index ordinals and tile indexes are stable only inside one build. They are not cross-index identities.

Cross-index identity is:

- tile: exact `x,y,z`;
- item base: exact `(itemId,itemDepth,source)` under the deterministic edit contract;
- item evidence: item base plus literal AID, UID, house-door and teleport destination values.

Pure exact-multiset reorder is reported independently. Other edits use a deterministic minimum edit script with fixed tie order. No fuzzy matching or neighboring-position inference is allowed.

### Walkability reuse

The Phase 3 implementation in `otbm_reachability_transition._classify_tile` is the single classifier used by Phase 6. Phase 6 does not copy its ground, static blocker, conditional blocker, unknown appearance, strict or optimistic rules. The leading underscore is an existing module-boundary limitation; Phase 6 pins and documents the exact implementation rather than creating a competing public model. A future API-only refactor may expose the same function without changing semantics, but is outside this PR.

### Correlation

Only exact positions and literal mechanic values from explicitly supplied, format-validated reports are indexed. Correlation is selected-scope evidence. Missing correlation does not prove global absence, and no report scope is expanded.

### Visual evidence

Phase 6 calls `otbm_renderer.render_region` or emits commands for `otbm_render_tool.py`. It does not create a renderer or an AI image. The render manifest pairs factual before/after/context artifacts. PNGs and private inputs remain external.

## Safety and determinism

- verify binary World Index structure through the existing reader;
- verify index, manifest, source and scanner provenance;
- require compatible World Index, scanner-build, OTBM and item versions;
- preserve exact counts while bounding samples;
- derive stable IDs from exact change evidence, independent of optional correlation;
- sort output deterministically;
- confine paths below an explicit artifact root;
- reject direct symlink inputs/outputs and accidental overwrite;
- bound index, report input, correlation node and output sizes;
- write JSON atomically;
- never modify a map, execute Lua or infer gameplay intent.

## Evidence classification

`structural`, `static`, `semantic`, `correlated`, `regression`, `runtime`, `gameplay` and `factual-visual-evidence` remain distinct. Phase 6 may claim the first five when their direct contracts are met. It never claims runtime or gameplay proof.

A `walkability-regression` means only that the same exact position moved to a less permissive state under the existing Phase 3 semantics. It does not authorize map repair.

## Consequences

- Two maps can be compared without committing either map or index.
- Full-world comparison remains streaming and bounded in output, though it is proportional to indexed tiles and placements.
- Appearance evidence is required for ground/walkability findings; structural and mechanic diffs remain valid without it.
- Different compatible scanner binaries are disclosed, not silently treated as identical. Incompatible formats/versions fail closed.
- Runtime behavior, quest intent, NPC behavior, storage progression and gameplay correctness remain follow-up evidence questions.

## Rejected alternatives

- A second OTBM parser: duplicates Phase 1 and risks divergent parsing.
- Diffing renderer pixels: loses exact item/mechanic semantics and depends on private assets.
- Treating placement ordinals as cross-index identity: ordinals shift after unrelated earlier changes.
- Heuristic item pairing: creates unprovable replacements and mechanic changes.
- Copying Phase 3 walkability logic: creates a second engine.
- Executing Lua for correlation: violates the static evidence boundary.
- Generating or styling map imagery with AI: not factual OTBM evidence.
- Repairing findings in the Phase 6 PR: mixes detection with gameplay/map mutation and bypasses Phase 7/8 gates.
