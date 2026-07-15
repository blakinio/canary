# OTBM real-map repair preflight

## Purpose

`tools/ai-agent/otbm_repair_preflight_tool.py` is a read-only bridge between a reported real-map defect and the existing Phase 8 bounded attribute patcher.

It does not parse OTBM independently and it never writes an OTBM. It orchestrates and correlates existing evidence:

1. the existing OTBM item/mechanic audit;
2. the native scanner's existing `--patch-anchors` mode;
3. the existing OTBM script-resolution audit;
4. the existing `canary-otbm-bounded-patch-plan-v1` contract when a review-only draft plan is requested.

The tool exists to answer the pre-patch questions precisely: which mechanic placement is being discussed, which exact Phase 8 anchor identifies it, what the current attribute value is, and what active Lua/XML or engine evidence resolves the mechanic.

A successful preflight is not approval to patch. It does not prove gameplay correctness, player intent, Real Tibia parity or runtime behavior.

## Safety boundary

The preflight:

- opens the source map read-only through the existing item scanner;
- rejects a symlink source map;
- hashes and stats the source before analysis and requires the same hash, size and modification timestamp afterward;
- hashes and stats the native scanner before analysis and rejects a scanner that changes during the run;
- refuses to use the source map, a source-map hard link or a symlink as the report/draft-plan destination;
- requires report and draft-plan outputs to be new paths;
- runs subprocesses as argument vectors with `shell=False`;
- never imports or calls `otbm_bounded_patch.apply_bounded_patch`;
- never executes `otbm_bounded_patch_tool.py`;
- never creates a patched map copy;
- never inserts/removes attributes, items or tiles;
- never changes item IDs, stack order, geometry, house IDs or tile flags.

Only a later, separately reviewed invocation of the existing Phase 8 patcher may mutate a distinct map copy.

Generated preflight reports and draft plans are external review artifacts. Source/target maps, `.widx` files, client assets, generated reports and renders must not be committed.

## Required inputs

The same real assets used by the existing OTBM audit are required:

- source `.otbm`;
- compiled `otbm_item_audit_scan` scanner;
- matching appearances index;
- matching Canary `items.xml`;
- repository root containing the active datapack scripts;
- explicit active script roots when the defaults are not appropriate.

By default, script resolution uses its existing active-root policy (`data` and `data-otservbr-global`). Alternative datapacks are not mixed implicitly.

## Inspect an exact mechanic

Example:

```bash
python tools/ai-agent/otbm_repair_preflight_tool.py \
  /external/world.otbm \
  --scanner tools/ai-agent/otbm_item_audit_scan \
  --appearances-index /external/appearances-index.json \
  --items-xml data/items/items.xml \
  --repository-root . \
  --script-root data \
  --script-root data-otservbr-global \
  --position 32541,32123,7 \
  --action-id 4501 \
  --output /external/artifacts/repair-preflight.json
```

At least one selector is required. Selectors are combined with logical AND:

- `--position x,y,z`;
- `--item-id ID`;
- `--action-id ID`;
- `--unique-id ID`;
- `--house-door-id ID`;
- `--teleport-destination x,y,z`.

The result contains every item-audit mechanic placement matching all supplied selectors. The tool never chooses one candidate heuristically.

For each candidate it correlates the native Phase 8 patch anchors by exact:

- position;
- item ID;
- item depth;
- complete current mechanic attribute set.

The correlation state is one of:

- `exact` — exactly one tile-local placement group matches;
- `missing` — no patch-anchor group proves the placement;
- `ambiguous` — more than one tile-local placement group matches and the tool refuses to guess.

An exact candidate exposes the scanner-proven `tilePlacementIndex` and existing attribute anchors required by Phase 8.

## Script-resolution evidence

Each selected item-audit placement is correlated by its stable item-audit placement index with the output of the existing script resolver.

Existing statuses are preserved. In particular:

- `unresolved` remains `unresolved`;
- `referenced-only` remains `referenced-only`;
- `partially-resolved` remains `partially-resolved`;
- `conflicting` remains `conflicting`.

Review rules do not convert unresolved runtime evidence into handled runtime evidence.

Teleport destinations and house-door IDs continue to use the resolver's existing engine-handled classification.

## Produce a review-only Phase 8 draft plan

A draft can be requested only for the four operations already supported by Phase 8:

- `set-action-id`;
- `set-unique-id`;
- `set-house-door-id`;
- `set-teleport-destination`.

Example:

```bash
python tools/ai-agent/otbm_repair_preflight_tool.py \
  /external/world.otbm \
  --scanner tools/ai-agent/otbm_item_audit_scan \
  --appearances-index /external/appearances-index.json \
  --items-xml data/items/items.xml \
  --repository-root . \
  --position 32541,32123,7 \
  --action-id 4501 \
  --operation-kind set-action-id \
  --replacement 4502 \
  --operation-id repair-quest-switch \
  --output /external/artifacts/repair-preflight.json \
  --draft-plan /external/artifacts/repair-plan.json
```

A draft plan is emitted only when all of these are true:

1. exactly one mechanic placement matches the selectors;
2. native patch-anchor correlation is `exact`;
3. the requested Phase 8 attribute already exists on that exact item placement;
4. the replacement differs from the current scanner-proven value;
5. every replacement logical byte preserves the existing OTBM physical escape width;
6. the generated plan validates through the existing `PatchPlan.from_raw()` Phase 8 contract.

The tool does not add missing attributes and does not invent a tile placement index.

The draft region is the exact selected `x,y,z` coordinate. The generated operation contains the existing Phase 8 redundant identity fields: position, `tilePlacementIndex`, `itemId`, `itemDepth`, exact expected value and replacement.

## Hypothetical replacement script resolution

When a draft plan is ready, the tool creates an in-memory copy of the item-audit JSON, changes only the selected existing mechanic value in that copy, and reruns the existing script resolver.

The report records:

- current placement status;
- hypothetical replacement placement status;
- whether the static runtime-resolution status changed;
- the full hypothetical placement resolution evidence.

This does not modify the map. It is static resolver evidence only.

A transition such as:

```text
handled-directly -> unresolved
```

is surfaced exactly as unresolved evidence. It is not silently approved or reclassified.

## Report contract

The final CLI report uses:

```text
canary-otbm-repair-preflight-v1
```

The normative schema is `docs/ai-agent/OTBM_REPAIR_PREFLIGHT_REPORT.schema.json`.

The report includes:

- exact source pin and scanner hash evidence;
- normalized selectors;
- matched mechanic placements;
- exact/missing/ambiguous anchor correlation;
- existing script-resolution evidence;
- unresolved/conflict counts;
- optional existing Phase 8 draft plan;
- optional hypothetical replacement script resolution;
- explicit statements that human review is required and that gameplay correctness/player intent are not proven.

## Required next step after review

A reviewed draft plan is only input preparation for the already-existing Phase 8 workflow.

Any actual real-map repair must still use the existing bounded patcher on a distinct copy and retain all Phase 8 gates:

1. expected old state verification;
2. exact native patch-anchor matching;
3. physical escape-width confinement;
4. byte equality outside planned payload offsets;
5. full scanner reparse;
6. regenerated before/after World Index evidence;
7. bounded Semantic OTBM Diff containing exactly the planned mechanic changes;
8. rollback evidence preserving the original source;
9. factual real-assets renderer evidence when visual review is useful.

Structural success remains separate from gameplay correctness and player intent.

## Tests

Focused tests are part of the normal AI Agent Tools suite:

```bash
python -m unittest tools/ai-agent/test_otbm_repair_preflight.py -v
```

The integration test compiles the existing native scanner, builds a tiny synthetic map, runs the real item audit and script resolver, creates a review-only Phase 8 draft plan, proves that a replacement can change static resolution from handled to unresolved, and verifies byte-for-byte source map immutability.
