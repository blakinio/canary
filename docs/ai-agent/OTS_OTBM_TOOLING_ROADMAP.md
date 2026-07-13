# OTS OTBM tooling roadmap and durable handoff

> Repository: `blakinio/canary`  
> Authoritative programme document: this file  
> Observed current `main` at handoff start: `56ee9bc72b91ba1110cd6d957c7eb0d974fc54e1`  
> Observation time: 2026-07-13T12:52:00+02:00  
> Programme state: Phases 1 and 2 merged; Phases 3–8 not started by this handoff  
> Evidence rule: static/source/map evidence is not live gameplay proof

## Mission

Maintain one deterministic, evidence-based OTBM analysis stack that agents can reuse for quests, NPCs, spawns, teleportation, storage progression, geometry, semantic diffs and—only after explicit safety gates—bounded map patching.

This document is the durable programme-level roadmap and handoff. It supersedes the stale status text that described World Index PR #211 as active. It does not authorize implementation, map changes, gameplay changes or creation of competing tools.

## 1. Current repository state

### 1.1 Main and observation

| Field | Value |
|---|---|
| repository | `blakinio/canary` |
| observed `main` | `56ee9bc72b91ba1110cd6d957c7eb0d974fc54e1` |
| observed at | `2026-07-13T12:52:00+02:00` |
| local checkout | unavailable |
| exact failed command | `git ls-remote https://github.com/blakinio/canary.git HEAD` |
| exact error | `fatal: unable to access 'https://github.com/blakinio/canary.git/': Could not resolve host: github.com` |
| mutation path used for this handoff | GitHub API |
| upstream repositories | read-only; no upstream mutation authorized |

After the first confirmed DNS failure, clone/fetch/ls-remote was not repeated. No local unit test, formatter, ownership check, build or runtime result is claimed for this documentation refresh. GitHub API and GitHub Actions evidence are recorded separately.

### 1.2 Completed implementation and lifecycle PRs

| Work | PR | Historical head | Squash merge | State |
|---|---:|---|---|---|
| Unified OTBM World Index | #219 | `452cdc6aaa183a7b4ce05ea83a013046764ecdb1` | `97ff786663b30cafbd933799d8549a6dd3e3370b` | merged |
| World Index lifecycle/archive | #223 | `5cd9fb524e117600e26103b3491ba1b41e866b94` | `97639776bb37c4f9aa1fa301cf43e7693a03a735` | merged |
| Quest Map Validator | #225 | `857985c8c0849fa2b86d8c1d688fbe663d0018fa` | `b23c8a353b09c066e72de178b8e86f0309740211` | merged |
| Quest Map Validator lifecycle/archive | #236 | `68965a9b60d45d95ab8aadb3275820f4929f118f` | `51766f5ebade7f7c3632ba57991472b4f9adec79` | merged |
| The Beginning evidence audit | #204 | `de5dc8bd70f0e2f98681e0bbf531843177508881` | `dfa535cbfdcb14a6fe4f19880a1281016d35b4c9` | merged |
| The Beginning ordered repair plan | #207 | `00e1e390847ccc0a7c2e567e9ac8a117cff330ed` | `f96680987955cde24d4264e9473bde70501ed534` | merged |
| Carlos outfit/trade repair | #157 | `6b68b25d42776747e994b516eca4a16ffd2c6c48` | `813a2ce39daced46802e6801e4abd275709b8672` | merged |
| Zirella collecting wood repair | #149 | `06cc1099f4f57248a43e5be1bdb22da1fc409b53` | `19602c90128f8295d84a8dd673ea71222dcaed2d` | merged |
| Zirella door/reward tutorial refresh | #186 | `68cf95017b5d7aecfaa96adeb5c62596f3e5ddf4` | `c654781f21269f557889ffab393a1e9ab2383b56` | merged |

### 1.3 Open PR and ownership review

GitHub open-PR searches for `OTBM`, `quest`, `teleport`, `storage`, `NPC`, `spawn`, `pathfinding` and related map work found no open PR that owns the World Index, Quest Map Validator or this roadmap.

Adjacent but non-overlapping work:

- PR #245, `feat(e2e): bootstrap universal agent test platform`, is a repository-wide E2E platform draft. At observation time its changed-file list contained only `docs/agents/tasks/active/CAN-20260713-universal-agent-e2e-platform.md`. It may later provide runtime infrastructure, but it does not own OTBM tooling or this roadmap.
- Paused PR #224 remains a Cyclopedia-specific historical physical-client experiment. It is not OTBM validator ownership and is not runtime proof for this programme.

Current overlap decision: **no active ownership overlap for this documentation-only handoff**.

### 1.4 Task records

Canonical completed records:

- `docs/agents/tasks/archive/CAN-20260712-otbm-world-index.md` — completed World Index task;
- `docs/agents/tasks/archive/CAN-20260713-quest-map-validator.md` — merged Quest Map Validator task.

Historical records that still physically exist under `docs/agents/tasks/active/` even though their linked PRs are merged:

- `CAN-20260712-the-beginning-otbm-audit.md` — `status: ready`, linked to merged #204;
- `CAN-20260712-the-beginning-repair-plan.md` — `status: ready`, linked to merged #207;
- `CAN-20260712-the-beginning-carlos-flow.md` — `status: ready`, linked to merged #157.

These are stale lifecycle locations, not current authorization or active ownership. Do not reactivate them and do not continue their historical branches. Their merged PR and current-main source state are authoritative.

Current handoff task:

- `CAN-20260713-otbm-tooling-program-handoff`;
- branch `docs/otbm-tooling-program-handoff`;
- owns only this roadmap and its own task record;
- `docs/agents/ACTIVE_WORK.md` is read-only and must not be edited.

### 1.5 Historical branches

Treat these as historical merged branches, never as starting points:

- `feat/otbm-world-index-v2`;
- `docs/archive-otbm-world-index`;
- `feat/quest-map-validator`;
- `docs/archive-quest-map-validator`;
- `docs/the-beginning-otbm-audit`;
- `docs/the-beginning-repair-plan`;
- `fix/the-beginning-carlos-flow`;
- `fix/the-beginning-zirella-wood`;
- `fix/the-beginning-zirella-door-rewards-v2`.

GitHub branch searches did not return active `otbm`, `quest` or `the-beginning` branches matching these historical names. Future work must start from current `main` on a new bounded branch.

### 1.6 Review and workflow evidence

Historical implementation review state recorded by the merged task/PR evidence:

- World Index #219: no review threads; mergeable before auto-merge;
- Quest Map Validator #225: no review threads; final changed-file review clear;
- Quest Map Validator lifecycle #236: merged documentation-only cleanup;
- The Beginning audit #204 and repair plan #207: documentation-only and merged.

Last implementation workflow evidence:

| Scope/head | Workflow | Run ID | Result |
|---|---|---:|---|
| World Index `452cdc6a...` | OTBM World Index | `29210711531` | success |
| World Index `452cdc6a...` | OTBM Map Tools | `29210711521` | success |
| World Index `452cdc6a...` | AI Agent Tools | `29210711515` | success |
| World Index ready head | CI | `29210760673` | success, nested `Required` success |
| Quest Map Validator `857985c8...` | Quest Map Validator | `29232010971` | success |
| Quest Map Validator `857985c8...` | Agent Task Ownership | `29232010980` | success |
| Quest Map Validator `857985c8...` | AI Agent Tools | `29232010964` | success |
| Quest Map Validator ready head | CI | `29232043337` | success, Linux compile and nested `Required` success |
| The Beginning audit `de5dc8bd...` | CI | `29233259245` | success |
| The Beginning audit `de5dc8bd...` | Agent Task Ownership | `29233259066` | success |
| The Beginning audit `de5dc8bd...` | AI Agent Tools | `29233259133` | success |
| The Beginning plan `00e1e390...` | CI | `29232510910` | success |
| The Beginning plan `00e1e390...` | Agent Task Ownership | `29232409755` | success |
| The Beginning plan `00e1e390...` | AI Agent Tools | `29232409770` | success |

These runs prove repository checks at their recorded heads. They do not prove full live gameplay.

## 2. Completed phases

## Phase 1 — Unified OTBM World Index

### 2.1 Contract and entrypoints

- Binary contract: magic `OTSWIDX1`, version `1`, fixed 256-byte little-endian header.
- Provenance manifest: `canary-otbm-world-index-v1`.
- Query response contract: `canary-otbm-world-query-v1`.
- Native build report: `canary-otbm-world-index-build-v1`.
- Python CLI: `tools/ai-agent/otbm_world_index_tool.py`.
- Native scanner reused and extended: `tools/ai-agent/otbm_item_audit_scan.cpp`.
- No second OTBM parser was created.

Native build mode:

```bash
c++ -O2 -std=c++20 -Wall -Wextra -Wpedantic -Werror \
  tools/ai-agent/otbm_item_audit_scan.cpp \
  -o /tmp/otbm_item_audit_scan

/tmp/otbm_item_audit_scan --world-index \
  /path/to/world.otbm \
  /path/to/world.widx
```

Canonical Python wrapper:

```bash
python tools/ai-agent/otbm_world_index_tool.py build \
  /path/to/world.otbm \
  --scanner /tmp/otbm_item_audit_scan \
  --output /path/to/world.widx \
  --manifest /path/to/world.widx.json
```

### 2.2 Indexed/query dimensions

The index supports bounded queries for:

- `itemId` placements;
- `actionId` placements;
- `uniqueId` placements;
- house-door ID placements;
- teleport source placement through the placement record;
- teleport destination lookup;
- exact `x,y,z` positions;
- inclusive 3D regions;
- tile metadata, placement stacks, tile flags, house IDs and exact total counts.

Examples:

```bash
python tools/ai-agent/otbm_world_index_tool.py item world.widx 7772 --limit 20
python tools/ai-agent/otbm_world_index_tool.py action world.widx 50999 --limit 20
python tools/ai-agent/otbm_world_index_tool.py unique world.widx 50085 --limit 20
python tools/ai-agent/otbm_world_index_tool.py house-door world.widx 7 --limit 20
python tools/ai-agent/otbm_world_index_tool.py teleport-destination world.widx 32097,32219,7 --limit 20
python tools/ai-agent/otbm_world_index_tool.py position world.widx 32062,32271,7
python tools/ai-agent/otbm_world_index_tool.py region world.widx \
  32055,32265,7 32090,32295,7 \
  --limit 100 --tile-limit 2000
```

### 2.3 Binary layout

Version 1 stores deterministic sections for:

1. 65,536-entry item directory;
2. canonical 256×256×floor area directory;
3. area-to-tile postings;
4. tile records;
5. placement records;
6. mechanic records;
7. item-to-placement postings.

Repeated raw OTBM tile-area nodes are merged by canonical area key. Duplicate exact tile positions are rejected.

### 2.4 Limits and safety

- default query limit is bounded by the library/CLI;
- no query may return more than 10,000 records;
- exact `totalCount` is retained even when returned samples are bounded;
- source map, native scanner and output index hashes are recorded;
- the source map is checked for stability while the index is built;
- corrupt or incompatible headers/sections fail closed;
- duplicate exact tile positions fail the build;
- output is created atomically;
- symlink output targets are rejected;
- an existing output requires explicit overwrite handling;
- legacy `otbm_item_audit_scan MAP OUTPUT.json` remains supported;
- the tool is read-only with respect to the source map.

### 2.5 Tests and workflow

Focused suite: 10 tests covering legacy JSON compatibility, all query dimensions, deterministic output, bounded pagination, repeated area merging, duplicate-tile rejection, corrupt headers, overwrite protection and symlink rejection.

Workflow: `.github/workflows/otbm-world-index.yml`.

The workflow:

- compiles the native scanner with warnings as errors;
- runs `tools/ai-agent/test_otbm_world_index.py`;
- byte-compiles the Python library/CLI/tests;
- validates the JSON Schema syntax.

### 2.6 Generated and committed data boundary

Committed:

- scanner/index source;
- CLI/library;
- tests;
- workflow;
- schema and documentation.

Never committed:

- `.otbm` maps;
- generated `.widx` files;
- generated index manifests/reports from private maps;
- `items.otb`;
- appearances binaries;
- sprite sheets/client packages.

## Phase 2 — Quest Map Validator

### 2.7 Contracts and entrypoints

- Source evidence format: `canary-quest-map-evidence-v1`.
- Correlated validation format: `canary-quest-map-validation-v1`.
- CLI: `tools/ai-agent/quest_map_validation_tool.py`.
- Library: `tools/ai-agent/quest_map_validation.py`.
- Schema: `docs/ai-agent/QUEST_MAP_VALIDATION.schema.json`.

Source scan:

```bash
PYTHONPATH=tools/ai-agent \
python tools/ai-agent/quest_map_validation_tool.py scan \
  --repository-root . \
  --source-root data-otservbr-global \
  --include 'data-otservbr-global/scripts/quests/the_beginning/**/*.lua' \
  --exclude '**/test/**' \
  --output /tmp/QUEST_MAP_EVIDENCE.json
```

Correlation:

```bash
PYTHONPATH=tools/ai-agent \
python tools/ai-agent/quest_map_validation_tool.py validate \
  /tmp/QUEST_MAP_EVIDENCE.json \
  --world-index /path/to/world.widx \
  --script-resolution /path/to/OTBM_SCRIPT_RESOLUTION.json \
  --region-from 32055,32265,7 \
  --region-to 32090,32295,7 \
  --sample-limit 20 \
  --fail-on conflicting \
  --output /tmp/QUEST_MAP_VALIDATION.json
```

### 2.8 Source-selection and provenance contract

- at least one explicit `--include` glob is mandatory;
- optional `--exclude` globs narrow the selected quest/questline;
- selected files must remain inside the repository root;
- only selected Lua/XML files are scanned;
- every selected source file receives a SHA-256;
- evidence records include exact repository path, line and bounded source context;
- evidence IDs are deterministic 20-character lowercase hexadecimal hashes;
- the complete selected evidence set receives a deterministic source digest;
- comments and strings are masked before Lua pattern extraction;
- dynamic Lua is never executed.

### 2.9 Extracted evidence

The current scanner inventories static evidence for:

- Action/MoveEvent/XML `actionId` registrations and comparisons;
- `uniqueId` registrations and comparisons;
- `itemId` registrations;
- item creation through `Game.createItem`, `createItem` and `doCreateItem` forms;
- item rewards through `addItem`/`addItemEx`;
- item consumption through `removeItem`/`removeItemOfType`;
- item type/condition checks;
- exact `Position(x,y,z)` literals and statically resolvable constants;
- teleport destinations passed directly or through resolvable position constants;
- storage reads;
- storage writes.

Direct aliases rooted at `Storage`, for example:

```lua
local tutorialStorage = Storage.Quest.U8_2.TheBeginningQuest
player:getStorageValue(tutorialStorage.ZirellaQuestLog)
```

are canonicalized to the full symbolic `Storage...` path without evaluating Lua.

### 2.10 Reused dependencies

- World Index provides exact map placement/tile/region evidence.
- Existing `otbm_script_resolution.py` provides Action/MoveEvent/XML handler evidence.
- Quest Map Validator does not create a competing parser or handler resolver.
- Reviewed script statuses such as `unresolved`, `referenced-only`, `partially-resolved` and `conflicting` are preserved.

### 2.11 Classifications

- `confirmed`: required source evidence and required map placement exist; AID/UID handler confirmation uses script-resolution when supplied.
- `map-only`: map mechanic exists, but a confirmed selected source handler/reference was not established.
- `script-only`: selected source evidence requires an identifier or map-required position absent from the index.
- `unresolved`: evidence is insufficient or intentionally deferred.
- `conflicting`: competing active handler evidence exists.

Conservative rules:

- an item ID absent from static OTBM is `unresolved`, not automatically `script-only`, because rewards, inventory and dynamic creation do not require static map placement;
- a generic missing `Position()` is `unresolved`, because it may be a bound, center or transient coordinate;
- an absent explicit position registration or teleport destination is `script-only`, because that mechanic requires a real tile;
- storage facts are inventory only and remain `unresolved` until the storage-graph phase.

### 2.12 Output safety and bounds

- JSON reports are written through a temporary file and atomically replaced;
- existing symlink output targets are rejected;
- static registration ranges larger than 4,096 values remain unresolved;
- default placement sample limit is 20;
- maximum sample limit is 1,000;
- explicit region correlation is limited to 1,000,000 coordinate positions;
- returned samples are bounded while exact placement counts are retained.

### 2.13 Tests, workflow and artifacts

Focused suite: 15 tests covering comments/strings, static registrations, item/position/teleport/storage extraction, direct Storage aliases, dynamic unresolved evidence, deterministic include/exclude selection, explicit-glob enforcement, conservative map semantics, conflict preservation, reviewed-unresolved preservation, regional map-only mechanics, bounded samples, storage deferral, atomic/symlink safety and malformed/oversized input rejection.

Workflow: `.github/workflows/quest-map-validation.yml`.

It:

1. compiles the existing native scanner;
2. runs focused synthetic source/map tests;
3. byte-compiles Python modules;
4. validates schema syntax;
5. scans one explicit Zirella source file;
6. verifies format, counts, hashes and unique deterministic IDs;
7. uploads source evidence and diagnostics;
8. uploads a local-correlation toolkit containing the scanner and required modules.

CI artifacts:

- `quest-map-evidence-the-beginning`;
- `quest-map-validator-local-toolkit`.

The workflow does not upload a private map or generated `.widx`.

## 3. Evidence boundaries

These rules are mandatory for all later phases and quest repairs:

- Dynamic Lua is not executed.
- Dynamic expressions remain `unresolved`.
- `unresolved` must never be promoted to handled without direct evidence.
- `map-only` is a review candidate, not automatic proof of a defect.
- `script-only` does not universally mean a missing static item placement; classification depends on whether the mechanic semantically requires a map tile.
- Storage read/write inventory is not a complete transition or reachability graph.
- AID/UID presence and handler resolution do not prove that a player can reach or successfully execute the mechanic.
- Source evidence does not prove gameplay.
- Green CI does not prove live gameplay, persistence, client behavior or player reachability.
- World Index does not write maps.
- Quest Map Validator is not a map writer.
- The renderer shows factual OTBM/client-asset data; it does not prove runtime behavior.
- A source/map match can still be blocked by doors, quest state, walkability, direction, account state, protocol or dynamic runtime conditions.

## 4. Real map and client assets

### 4.1 Provenance

The validated local map used by Phases 1–2:

```text
map SHA-256: a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2
source size: 184,776,037 bytes
index size: 842,280,592 bytes
tiles: 17,972,761
placements: 23,359,571
used item IDs: 23,852
mechanic placements: 9,339
unknown attribute tails: 0
```

Canonical Phase 1 build measurement:

```text
build wall time: 32.72 s
peak RSS: 419,140 KiB
canonical areas: 1,171
raw OTBM tile-area nodes: 1,175,983
maximum item depth: 2
```

Later Phase 2 local rebuild/correlation measurement of the same map and same final index size:

```text
index build: 40.21 s
peak RSS: 418,956 KiB
```

The timing/RSS values are separate observed runs, not contradictory format values. Preserve their labels rather than merging them into one invented measurement.

### 4.2 Non-committed artifacts

Never commit:

- the map binary;
- `.widx` cache;
- client asset ZIP/root;
- appearances binaries;
- sprite sheets;
- large local scanner/resolver/validation reports;
- generated PNG/SVG renders;
- generated sprite exports or HD packs.

Only source code, tests, schemas, workflows and reviewed documentation belong in Git.

## 5. Factual rendering and sprite export

### 5.1 Factual renderer

Entrypoint:

```text
tools/ai-agent/otbm_render_tool.py
```

Implementation:

```text
tools/ai-agent/otbm_renderer.py
```

Required inputs:

- the real `.otbm` map;
- a client root, assets directory, or OTClient `data/things/<version>` directory containing exactly one compatible appearances catalogue and the referenced sprite sheets.

The renderer:

- validates and hashes the asset package;
- parses object appearances;
- reads the bounded map region;
- requires exactly one floor per render invocation;
- orders ground/bottom/common/top items from actual map stack and appearance flags;
- selects real sprite IDs and patterns;
- applies real displacement/elevation/alpha;
- reports missing appearances and missing sprites;
- emits `canary-otbm-render-report-v1` with map/asset/appearance hashes, bounds, dimensions and diagnostics.

Reproducible single-floor render:

```bash
PYTHONPATH=tools/ai-agent \
python tools/ai-agent/otbm_render_tool.py \
  /path/to/world.otbm \
  /path/to/client-assets \
  --from 32054,32261,7 \
  --to 32076,32278,7 \
  --output /tmp/the-beginning-zirella-floor7.png \
  --report /tmp/the-beginning-zirella-floor7.json \
  --padding-tiles 4 \
  --max-tiles 4096
```

For a multi-floor area, run one command per floor with identical `x,y` bounds and `z` fixed to each required floor. Do not composite floors into a claim unless the composition method is explicitly documented.

Missing asset proof is read from:

```text
summary.missingAppearanceCount
summary.missingSpriteCount
errors[]
```

Do not use `--allow-errors` when a render is being presented as complete evidence.

### 5.2 Bounded semantic export

Use the existing map tool to determine and review exact bounds before rendering:

```bash
PYTHONPATH=tools/ai-agent \
python tools/ai-agent/otbm_map_tool.py export \
  /path/to/world.otbm \
  --from 32054,32261,7 \
  --to 32076,32278,7 \
  --items-xml data/items/items.xml \
  --require-catalog \
  --output /tmp/the-beginning-zirella-region.json \
  --preview /tmp/the-beginning-zirella-region.svg \
  --max-tiles 4096
```

Coordinates must come from World Index/item audit, known source positions, companion XML or a previously verified bounded export. Never invent coordinates from visual memory.

### 5.3 Sprite export

The existing HD pipeline exports exact source sprites referenced by a bounded factual region:

```bash
PYTHONPATH=tools/ai-agent \
python tools/ai-agent/otbm_hd_tool.py export \
  /path/to/world.otbm \
  /path/to/client-assets \
  --from 33377,32631,7 \
  --to 33417,32671,7 \
  --output-dir /tmp/cobra-hd-export
```

The export records map/asset hashes, region bounds, item-to-appearance-to-sprite mapping and exact source PNG hashes. The preparation/validation/render stages must preserve geometry, source alpha and fallback behavior described in `OTBM_HD_PIPELINE.md`.

### 5.4 Absolute visual rule

**DO NOT USE AI IMAGE GENERATION TO VISUALIZE OR MODIFY THE MAP.**

Every image represented as a map render must originate from:

- the real OTBM;
- the real compatible client assets;
- the existing factual renderer pipeline.

Never generate an “enhanced”, beautified, reconstructed or imagined location through an image generator. Never present AI-generated imagery as an OTBM render. AI sprite-upscale artifacts, where separately reviewed, are renderer artifacts and must never be confused with factual source-map visualization.

## 6. The Beginning Quest Map Validator smoke result

Selected source:

```text
data-otservbr-global/scripts/quests/the_beginning/the_beginning_zirella_wood.lua
```

Source evidence:

```text
source files: 1
evidence: 12
item evidence: 5
position evidence: 1
storage evidence: 6
source unresolved: 0
```

Real-map bounded correlation region:

```text
32055,32265,7 -> 32090,32295,7
```

Result:

```text
confirmed: 6
map-only region mechanics: 10
script-only: 0
unresolved storage semantics: 6
conflicting: 0
```

Interpretation:

- the 10 `map-only` entries are candidates for review, not proven defects;
- the 6 unresolved storage findings are deliberate storage-semantics deferrals, not conflicts;
- this test does not confirm the complete The Beginning runtime chain;
- this test does not confirm player persistence, reconnect behavior, NPC shop callbacks, walkability, directionality or physical-client behavior.

## 7. The Beginning current baseline

The evidence authority is `THE_BEGINNING_OTBM_AUDIT.md` from merged #204, but historical findings must be reconciled with later merged repairs and current `main`. The ordered plan is `THE_BEGINNING_REPAIR_PLAN.md` from merged #207.

### 7.1 Confirmed existing behavior on current main

- Current tutorial MoveEvents handle the map-present tutorial AIDs in the audited route.
- Four generic AID `2000` reward chests provide the audited tutorial rewards.
- Zirella collecting wood/cart progression is present from merged #149: five verified dead trees, branch `7772`, exact cart `7751` at `32062,32271,7`, stage `6 -> 7`, one branch consumed.
- UID `50085` door remains sealed until the required Zirella stage and uses the current door pair.
- Shovel/rope tutorial rewards use current UIDs `50093` and `50094` from merged #186.
- NPC placements for Santiago, Zirella and Carlos were confirmed by companion XML in the audit.
- Cockroach, deer and rabbit spawns and the required loot inputs were confirmed by the audit.
- Cockroach legs `7882`, meat `3577` and ham `3582` have current quest consumers.
- Carlos outfit/trade progression is repaired on current main by merged #157: `outfit` uses the stage-2 lesson; trade callback is registered; tutorial 13 is sent on first valid stage-6 opening; an actual positive meat/ham sale advances stage 6 to 7.

### 7.2 Finding status reconciled against current main

| Finding | Current status | Current evidence/decision |
|---|---|---|
| Carlos `outfit` bypass, trade callback and successful-sale transition | `repaired` | merged #157; current `carlos.lua` contains `teachOutfit`, registered `CALLBACK_ON_TRADE_REQUEST`, trade-open state and positive meat/ham sale transition to stage 7 |
| Santiago `easy` persistence | `still-open` | current `santiago.lua` normal path writes greet 12/log 10; `easy` still writes greet 11/log 10 |
| Repeatable rope-success hint | `still-open` | current `onUseRope` checks `TutorialHintsStorage < 22`, sends the success message and does not write 22 |
| AID `50999` terminal border | `unresolved` | four map placements remain map-only; exact direction/destination/town/tutorial/idempotence contract is not proven; no code or map edit authorized |
| Cockroach first-kill/chase/corpse hooks | `unresolved` | route/spawns/loot are confirmed, but exact current tutorial IDs, ownership, event and storage contract remain unproved; non-blocking |
| Snake-head lever | `unresolved` | map objects exist without a confirmed current quest dependency or safe handler contract; preserve |
| Advertised `skip tutorial` | `unresolved` | dialogue/catalogue advertise it, but current Santiago has no complete safe contract; do not implement by historical analogy |
| Static cart branch `7772` | `unresolved` | static placement exists, but intended movability/visual/mechanic role is unproved; preserve |
| Two `0,0,0` teleport attributes | `unresolved` | items `1758` at audited positions retain unknown purpose; separate map-mechanic audit only |
| Three non-whitelisted ambient dead trees | `no-longer-applicable` as an automatic repair | they remain map-only scenery candidates; existence does not prove they should generate branches |
| Zirella door and shovel/rope UIDs | `repaired` | merged #186 and present in current baseline |
| Zirella wood/cart stage 6→7 | `repaired` | merged #149 and present in current baseline |

### 7.3 The Beginning proof limits

- Audit #204 is evidence-only and explicitly states runtime E2E was not proven.
- Plan #207 is sequencing documentation, not gameplay authorization.
- Carlos #157 repairs the NPC flow but does not prove a clean live character can finish the entire quest.
- AID `50999` remains the terminal core-chain blocker until a separate contract-resolution task proves direction, destination, town and idempotence.
- Player persistence across focus loss/relogin remains unproved for the complete quest.

## 8. Remaining tooling roadmap

Each phase is a separate bounded task/branch/PR. Do not combine phases and do not implement any phase from this handoff task.

### Phase 3 — Teleports, stairs and reachability

Deliverables:

- validate teleport sources and destinations;
- require destination tile existence;
- evaluate floor/ground and conservative walkability evidence;
- correlate stairs, holes, ladders and cross-floor relationships;
- identify unreachable mechanics, one-way transitions, loops and dead ends;
- accept explicit bounded regions and start/goal pairs only;
- report dynamic/door/quest-state uncertainty separately;
- make no gameplay or map modification.

Reuse World Index, item/appearance metadata, script resolution and factual renderer. Do not create a new OTBM parser.

### Phase 4 — Spawns, bosses and NPCs

Deliverables:

- verify spawn/NPC position existence and walkability;
- resolve monster/NPC definitions;
- check region containment and suspicious radius relationships;
- record statically resolvable dynamic spawn evidence;
- distinguish companion XML placement from `Game.createMonster`/runtime creation;
- compare quest expectations with static/dynamic creation;
- preserve active/inactive datapack separation;
- never invent names, positions or spawn times.

### Phase 5 — Storage graph

Deliverables:

- inventory reads, writes, comparisons and increments;
- build explicit stage transitions;
- identify unreachable values and conflicting writers;
- keep player, account, KV and database state separate;
- preserve dynamic expressions as unresolved;
- link transitions to NPC dialogue, Actions, MoveEvents, kills and rewards where proven;
- do not infer execution order from source proximity alone.

### Phase 6 — Semantic map diff

Deliverables:

- report tiles added/removed;
- report items/stacks added/removed;
- report AID/UID changes;
- report teleport target changes;
- report walkability-relevant flags/items;
- correlate affected handlers and quest evidence;
- generate factual before/after/context renders from approved real artifacts;
- keep maps, indexes, reports and images outside Git unless explicitly approved as small fixtures.

### Phase 7 — Geometry audit

Deliverables:

- missing floor/item-without-floor;
- broken walls and borders;
- invalid/inconsistent borders;
- invisible blockers;
- orphan/isolated tiles;
- suspicious duplicate ground;
- invalid house/PZ continuity;
- exact positions, confidence levels and bounded factual renders;
- visual style warnings remain non-blocking unless backed by deterministic contracts.

### Phase 8 — Safe OTBM patch writer

Programme Phase 8 remains blocked until audits and semantic diff gates are complete. Existing older bounded patch surfaces in `otbm_map_tool.py` are not programme authorization to edit production maps.

Every future approved operation must:

- operate on a copy, never the source map in place;
- require exact expected previous state;
- pin source hash and format/version;
- use a bounded region and operation allowlist;
- create a machine-readable manifest;
- generate a semantic diff;
- reparse and fully validate the result;
- prove equality outside the intended change;
- render the affected region from real map/client assets;
- write atomically;
- produce backup and rollback instructions.

No Phase 8 implementation or map mutation belongs in the current handoff or the next gameplay/Lua follow-up.

## 9. Exact next bounded scope

The first package in #207, Carlos, is already repaired by merged #157. The next still-open, implementation-ready, owner-free and map-free package is **Santiago `easy` persistence parity**.

### 9.1 Proposed task

```text
task_id: CAN-20260713-the-beginning-santiago-easy
branch: fix/the-beginning-santiago-easy-persistence
PR title: fix(quest): align Santiago easy persistence
risk: low/medium
```

### 9.2 Exact finding

In current `data-otservbr-global/npc/santiago.lua`:

- the normal continuation from conversation state 8 writes `SantiagoNpcGreetStorage = 12` and `SantiagoQuestLog = 10`;
- the `MsgContains(message, "easy")` branch reaches the same Zirella question but writes greet stage `11` and log stage `10`;
- focus loss/relogin after `easy` can therefore resume the previous fish stage instead of the Zirella question.

No map edit, AID guess, new storage, new parser or new resolver is required.

### 9.3 Proposed ownership

Exclusive:

- `data-otservbr-global/npc/santiago.lua`;
- `tools/ai-agent/test_the_beginning_santiago_flow.py`;
- `docs/agents/tasks/active/CAN-20260713-the-beginning-santiago-easy.md`.

Shared only if repository policy requires it:

- `docs/agents/CHANGELOG.md`.

Read-only dependencies:

- `docs/ai-agent/THE_BEGINNING_OTBM_AUDIT.md`;
- `docs/ai-agent/THE_BEGINNING_REPAIR_PLAN.md`;
- `data-otservbr-global/lib/core/storages.lua`;
- `data-otservbr-global/lib/core/quests/catalog/018_the_beginning.lua`;
- existing NPC-focused test conventions;
- Quest Map Validator/World Index only as read-only context, not modified.

Do not include `docs/agents/ACTIVE_WORK.md` in ownership.

### 9.4 Acceptance criteria

- both normal and `easy` paths that reach the Zirella question persist greet stage 12 and log stage 10;
- `easy` does not grant another fish `3578`;
- reconnect/focus-loss simulation from persisted greet 12 resumes the Zirella question;
- fish reward remains only in the preceding transition;
- final Zirella response still writes greet 13/log 11 and retains the existing map mark;
- no dialogue, XP, reward, coat, weapon, cockroach-leg, map, AID, UID, protocol or other NPC behavior change;
- focused deterministic contract test passes;
- Lua syntax/format, relevant AI Agent Tools and global datapack runtime smoke pass on the final head;
- full changed-file list contains no map, World Index, Quest Map Validator, asset or upstream file.

### 9.5 Rollback and first actions

Rollback: revert the single bounded repair PR; no data migration or map cleanup is required. Players already persisted at greet 11 are not silently migrated by this scope unless a separate evidence-backed migration decision is approved.

First file:

```text
data-otservbr-global/npc/santiago.lua
```

First function/branch:

```text
creatureSayCallback
  -> MsgContains(message, "easy")
  -> storeTalkCid[playerId] == 8
```

First command from a fresh current-main checkout:

```bash
rg -n 'MsgContains\(message, "easy"\)|SantiagoNpcGreetStorage|SantiagoQuestLog|addItem\(3578' \
  data-otservbr-global/npc/santiago.lua \
  tools/ai-agent/test_the_beginning_*
```

Before any write, recheck current `main`, open PRs, active structured ownership and whether a later repair already landed.

## 10. Hard prohibitions and next-agent handoff

**DO NOT REOPEN PR #225.**

**DO NOT CONTINUE `feat/quest-map-validator`.**

**DO NOT REACTIVATE THE ARCHIVED QUEST MAP VALIDATOR TASK.**

**DO NOT CREATE A NEW OTBM PARSER.**

**DO NOT CREATE A NEW MAP RENDERER.**

**DO NOT CREATE A COMPETING SCRIPT RESOLVER.**

**DO NOT EXECUTE OR GUESS DYNAMIC LUA.**

**DO NOT PROMOTE UNRESOLVED TO HANDLED.**

**DO NOT EDIT `docs/agents/ACTIVE_WORK.md`.**

**DO NOT COMMIT OTBM, WIDX OR CLIENT ASSETS.**

**DO NOT USE AI IMAGE GENERATION FOR MAP VISUALIZATION.**

**DO NOT MODIFY THE MAP IN THE NEXT GAMEPLAY/LUA FOLLOW-UP.**

**DO NOT MODIFY UPSTREAM REPOSITORIES.**

### Start here

1. Repository: `blakinio/canary`.
2. Fetch current `main`; do not rely on the observed SHA in this historical snapshot if main advanced.
3. Read `AGENTS.md`, `docs/agents/README.md`, this roadmap, the two archived Phase 1/2 tasks, `THE_BEGINNING_OTBM_AUDIT.md`, `THE_BEGINNING_REPAIR_PLAN.md`, current Santiago source and all open PR/task ownership.
4. Confirm no later Santiago repair exists.
5. Create `CAN-20260713-the-beginning-santiago-easy` from current main on `fix/the-beginning-santiago-easy-persistence`.
6. Open a draft PR before implementation grows.
7. Change only the exact Santiago persistence branch and focused contract test.
8. Run focused checks plus final-head repository CI/runtime smoke.
9. Merge only after exact changed-file, review-thread and required-job inspection.
10. Archive the new task in a separate lifecycle cleanup PR.

### Programme status summary

```text
repository: blakinio/canary
authoritative programme document: docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md
World Index: merged and archived (#219/#223)
Quest Map Validator: merged and archived (#225/#236)
The Beginning audit: merged (#204)
The Beginning repair plan: merged (#207)
completed phases: 1, 2
not completed: phases 3, 4, 5, 6, 7, 8
real-map SHA-256: a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2
next bounded scope: Santiago easy persistence parity
next branch: fix/the-beginning-santiago-easy-persistence
next task: CAN-20260713-the-beginning-santiago-easy
first file: data-otservbr-global/npc/santiago.lua
first function: creatureSayCallback / easy branch
blockers: none for the bounded Santiago source repair after current-main/ownership recheck; full quest E2E and AID 50999 contract remain separate
```
