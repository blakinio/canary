# OTBM Critical Access Integrity

`tools/ai-agent/otbm_critical_access_integrity_tool.py` implements the bounded OTBM-QA-012 current-state integrity slice for explicitly reviewed critical landmarks, houses and spawn/NPC/boss access contexts.

It is a read-only evidence composer. It does not parse OTBM, build a second World Index, pathfind, classify geometry, rescan spawn/NPC source, infer semantic importance, execute Lua or modify a map.

## Public contracts

Reviewed target manifest:

- format: `canary-otbm-critical-access-targets-v1`;
- schema: `docs/ai-agent/OTBM_CRITICAL_ACCESS_TARGETS.schema.json`.

Output report:

- format: `canary-otbm-critical-access-integrity-v1`;
- schema: `docs/ai-agent/OTBM_CRITICAL_ACCESS_INTEGRITY.schema.json`.

Both contracts are version 1.

## Required evidence

The tool requires:

1. one reviewed critical-access target manifest;
2. the exact canonical `canary-otbm-world-index-v1` file pinned by that manifest;
3. one reviewed `canary-otbm-semantic-landmarks-v1` registry;
4. one compatible `canary-otbm-connectivity-resilience-v1` report;
5. one complete compatible `canary-otbm-geometry-audit-v1` report;
6. one compatible `canary-otbm-spawn-npc-validation-v1` report.

The target manifest pins the exact source-map and World Index SHA-256 values. Semantic Landmark, Connectivity and Geometry evidence must prove the same source map and World Index. Spawn/NPC validation must prove the same World Index. The actual `.widx` file is hashed again before analysis.

Missing or mismatched provenance fails closed.

## Reviewed target model

Criticality and access intent are caller-reviewed metadata. They are never inferred from item names, sprites, map appearance, proximity or chat history.

### Critical landmarks

A critical-landmark target declares:

- stable target ID;
- reviewed criticality: `temple-recovery`, `depot`, `bank`, `transport-hub`, `city-entrance`, `quest-hub` or `other-reviewed-critical`;
- exact Semantic Landmark ID;
- exact anchor ID;
- exact existing Connectivity Resilience route ID;
- one or more review references.

The existing Semantic Landmark resolver is reused with exact map/World Index provenance. QA-012 then checks only that the referenced reviewed route targets the resolved anchor and reports its already-computed strict/optimistic/executable evidence. No route is recomputed.

### Houses

A house target declares:

- stable target ID;
- exact `houseId`;
- exact `houseDoorId`;
- exact door position;
- exact reviewed interior/access target position;
- exact existing Connectivity Resilience route ID;
- review references.

The canonical World Index is queried at the exact door position. A confirmed door requires exactly one matching placement carrying the declared `houseDoorId` on the declared house tile. Missing, mismatched or duplicate selectors remain unresolved/conflicting.

Existing Geometry Audit findings are correlated by exact `houseId` for:

- `house-disconnected-components`;
- `house-component-mixed-pz`.

QA-012 does not recompute components or PZ semantics. If Geometry findings are truncated, absence of a house finding cannot prove a clear result.

The reviewed route must terminate at the declared interior/access target and its existing complete baseline path must contain the exact declared door position. This is static route evidence only; it does not prove a live door state, storage condition or successful runtime interaction.

### Spawn, NPC and boss access

A spawn-access target declares:

- stable target ID;
- entity role: `monster`, `npc` or `boss`;
- exact existing Spawn/NPC validation placement ID;
- exact placement/access position;
- exact existing Connectivity Resilience route ID;
- access expectation: `reviewed-context` or explicitly `public`;
- review references.

The referenced placement must match the declared position and role. A `boss` target requires existing `rewardBossLiteral=true` placement evidence; QA-012 does not infer bosses from names.

If the Spawn/NPC report is truncated and a referenced placement is not visible, the result is unresolved rather than missing. Existing placement statuses are preserved: confirmed, conditional and problem states are not promoted.

Declaring `accessExpectation: public` records that public accessibility is part of the reviewed target intent. It still does not prove public accessibility or runtime reachability.

## Classifications

Each target receives one of:

- `confirmed` — exact target evidence and the referenced existing route are confirmed in the selected static evidence;
- `conditional` — required route or placement evidence is conditional/optimistic;
- `unreachable-in-reviewed-context` — the selected reviewed route is not reachable in its existing evidence mode;
- `review-required` — existing evidence contains a relevant integrity concern, such as a house geometry finding or blocked/missing spawn placement state;
- `unresolved` — required exact evidence is absent, truncated or unavailable;
- `conflicting` — exact selectors, positions, roles or route relationships disagree.

These are bounded static classifications. `unreachable-in-reviewed-context` is not global impossibility.

## Run

```bash
PYTHONPATH=tools/ai-agent \
python tools/ai-agent/otbm_critical_access_integrity_tool.py \
  --targets /path/to/OTBM_CRITICAL_ACCESS_TARGETS.json \
  --world-index /path/to/world.widx \
  --landmarks /path/to/OTBM_SEMANTIC_LANDMARKS.json \
  --connectivity /path/to/OTBM_CONNECTIVITY_RESILIENCE.json \
  --geometry /path/to/OTBM_GEOMETRY_AUDIT.json \
  --spawn-validation /path/to/OTBM_SPAWN_NPC_VALIDATION.json \
  --output /tmp/OTBM_CRITICAL_ACCESS_INTEGRITY.json
```

Inputs must be distinct regular files and may not be symlinks. Output is create-new by default. Existing output requires `--overwrite`; symlink targets, input/output collisions and hard-link aliases are rejected. Overwrite uses atomic replacement.

## Policy boundary

The report explicitly records that:

- criticality was not inferred;
- the existing Semantic Landmark resolver and World Index were reused;
- existing Connectivity evidence was consumed and no pathfinding occurred;
- Geometry was not recomputed;
- Spawn/NPC source was not rescanned;
- dynamic Lua was not executed;
- runtime access and public accessibility were not inferred or proven;
- Physical E2E was not executed;
- the map was not modified;
- v1 does not claim a before/after entrance bypass or sever regression.

The roadmap's change-based house entrance bypass/sever check requires a separately compatible before/after Semantic Diff evidence contract. It is deliberately not inferred from current-state evidence in this v1 slice.

## Limitations

A green report does not prove:

- intended public accessibility unless that intent was explicitly declared, and even then it does not prove runtime accessibility;
- a live door is open or its handler/storage prerequisite succeeds;
- a player can enter or leave a house at runtime;
- an NPC, monster or boss is interactable or fightable at runtime;
- global world connectivity;
- quest completion;
- physical-client behavior.

Use existing Universal Physical E2E or feature-owned runtime validation when those proof levels are required.
