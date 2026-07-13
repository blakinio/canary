# Real Tibia evidence source registry

> Repository: `blakinio/canary`  
> Last reviewed: 2026-07-14  
> Scope: public evidence and donor candidates for moving this Canary fork closer to current Real Tibia  
> Safety: external repositories, forums, maps, datapacks and client packages are read-only inputs; this registry authorizes no binary or datapack import

## Purpose

This file is the durable source and provenance guide for agents working on Real Tibia parity.

It answers four separate questions:

1. Where can an agent find a candidate map, quest, NPC, spawn, item or protocol implementation?
2. What does that source actually prove?
3. What must be validated before the candidate can influence Canary?
4. Which existing repository tools must be reused to produce reviewable evidence?

No single public source is a complete source of truth for current Real Tibia. Different evidence dimensions require different authorities. A client minimap can be strong geometry evidence while proving nothing about server-side item stacks, action IDs, NPC scripts or spawn intervals. A community quest script can be useful implementation evidence while proving neither exact map geometry nor authentic runtime behavior.

## Non-negotiable rules

- The implementation target and runtime authority is the current `blakinio/canary` branch selected by the task.
- `opentibiabr/canary`, `zimbadev/crystalserver`, OTLand and every other external source are read-only.
- Never copy a complete external datapack or replace the active global map blindly.
- Never mix handlers, storages, spawn files, item definitions or map sidecars from different datapacks without an explicit compatibility analysis.
- A repository or thread label such as `15.x`, `15.24` or `15.25` does not prove complete content coverage for that release.
- OTBM does not provide a trustworthy semantic Tibia release label. Record exact hashes and observed content instead of inventing a version.
- Do not commit `.otbm`, `.widx`, `items.otb`, client assets, downloaded archives, proprietary binaries, generated large reports or renders.
- Downloaded material belongs outside Git and must be treated as untrusted input.
- Preserve exact source URLs, author, publication date, downloaded filename, byte size and SHA-256 before analysis.
- `unresolved`, missing or incompatible evidence remains explicit. Never convert uncertainty into a guessed handler, position, item ID, storage, spawn or mechanic.
- Real gameplay parity requires runtime evidence. Static source/map agreement is not live gameplay proof.

## Evidence dimensions and precedence

Do not apply one global ranking to every question. Use the relevant dimension below.

| Evidence dimension | Strongest available evidence | Useful secondary evidence | Does not prove |
|---|---|---|---|
| Release existence and announced behavior | Official Tibia news/update material | maintained wikis and independent gameplay captures | exact OTBM tiles, server IDs or script implementation |
| Explored geometry and walkability | official-client-derived minimap data, repeated official gameplay observation | audited donor OTBM, screenshots/video | item stacks, AID/UID, teleports, house metadata, quests or spawns |
| Item appearances and client IDs | exact matching official client assets/appearances from the selected client build | maintained public asset catalogues | Canary server IDs, runtime item behavior or map compatibility |
| Canary runtime behavior | current target source, registrations, tests and runtime evidence | upstream Canary and carefully adapted external implementations | official Real Tibia behavior unless separately evidenced |
| Quest/NPC flow | official gameplay observation plus independent documented references | maintained wiki, CrystalServer/Canary scripts, forum implementations | exact parity from one script alone |
| Spawns and boss placement | repeated official observation or maintained official-client-derived data where available | audited spawn XML and definition files | authentic timing, radius or conditional world state without runtime evidence |
| Map mechanics | exact OTBM attributes plus active Canary handler resolution and runtime test | donor scripts and documented gameplay | working behavior from visual geometry alone |

When sources conflict, record the conflict. Do not silently choose whichever source is newer or easier to copy.

## Current target baseline

### `blakinio/canary`

Role: implementation target and repository source of truth.

Current relevant systems include:

- Unified OTBM World Index;
- Quest Map Validator;
- OTBM teleport and reachability validator;
- OTBM spawn, boss and NPC validator;
- OTBM script-resolution audit;
- factual OTBM renderer using compatible real assets.

The externally supplied baseline map used by existing validation has:

```text
SHA-256: a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2
tiles: 17,972,761
item placements: 23,359,571
map-mechanic placements: 9,339
```

The binary is not committed to this repository.

Do not call this map definitively `15.15` without independent provenance. The defensible description is currently:

> Global OTServBR/Canary-lineage baseline that predates the observed CrystalServer Targuna additions.

The server/client protocol target can be 15.25 while the OTBM content baseline is older or incomplete. Record these as separate fields:

```text
server revision
protocol/client build
map SHA-256
map content observations
items/appearances revision
spawn/NPC sidecar revision
datapack revision
```

## Primary public sources

### Official Tibia material

- News archive: <https://www.tibia.com/news/?subtopic=newsarchive>
- Official client/build and its locally supplied assets, appearances and protocol observations.

Use for:

- release dates and feature announcements;
- official naming and visible behavior;
- exact client-side appearances when the build is known;
- packet/runtime observation in a controlled test environment.

Limitations:

- public news does not expose server implementation;
- the client minimap does not contain server-side OTBM item stacks or mechanics;
- proprietary client packages and assets must not be committed.

### TibiaMaps official-client-derived minimap data

- Repository: <https://github.com/tibiamaps/tibia-map-data>
- Conversion tooling: <https://github.com/tibiamaps/tibia-maps-script>

The project describes its data as an almost fully explored official Tibia map and stores per-floor map PNG, pathfinding PNG and marker JSON. Contributors update it using minimap files produced by the official client.

Use for:

- map outline and explored geometry;
- floor coverage;
- minimap walkability/pathfinding reference;
- detecting missing or differently shaped regions in an OTBM donor;
- tracking when newly released areas become publicly explored.

Do not use it as proof of:

- exact ground or decoration item IDs;
- stack order;
- AID/UID;
- teleport destination;
- house tiles or doors;
- NPC/spawn positions or intervals;
- quest mechanics.

### OpenTibiaBR Canary upstream

- Repository: <https://github.com/opentibiabr/canary>

Role: read-only maintained upstream and broad global datapack reference.

Use for:

- current upstream conventions;
- fixes or content missing from this fork;
- cross-checking whether an external candidate is already present upstream;
- maintained global quest/NPC/monster implementations.

Do not assume that upstream protocol support means its OTBM contains every area from that client release.

## CrystalServer registry

### Repository and role

- Repository: <https://github.com/zimbadev/crystalserver>
- Global datapack root: `data-global/`
- Global map: `data-global/world/world.otbm`
- Companion files include `world-house.xml`, `world-npc.xml`, spawn data and zone data.

CrystalServer is a high-value public implementation donor, not an authority over Canary. Its code, map and datapack must be audited independently and adapted to Canary conventions.

### Confirmed high-value content

Targuna-related public content includes:

- `data-global/scripts/quests/targuna/**`;
- Targuna quest-log and storage definitions;
- NPCs including Camilla, Lizzie, Adrian, Morla, Emiliana and Sterling;
- monsters and bosses for Aragonia, Crimson Court and Hidden Lizard Temple;
- house records and map changes;
- Targuna protection-zone, sign and house-door fixes.

Newhaven-related public content includes:

- `data-global/lib/others/newhaven.lua`;
- `data-global/scripts/quests/newhaven/**`;
- Newhaven monsters and NPCs;
- login, death, use, tutorial and vocation-selection flows.

Useful searches:

- <https://github.com/zimbadev/crystalserver/search?q=targuna&type=code>
- <https://github.com/zimbadev/crystalserver/search?q=newhaven&type=code>

### Targuna provenance and limitation

Primary implementation PR:

- <https://github.com/zimbadev/crystalserver/pull/784>

The author explicitly states that the Targuna island section was built while playing Tibia, while other areas used videos as references and may contain errors. The author also requested review of monster and boss spells. The storage namespace in the implementation is `Storage.Quest.U15_24.Targuna`, while the current server/client target may be 15.25.

Therefore classify Crystal Targuna as:

```text
implementation candidate: strong
public completeness: broad
Real Tibia parity: unproven
safe for direct wholesale import: no
required action: bounded semantic audit and adaptation
```

Useful related commits/PRs include:

- Targuna quest and review: CrystalServer PR #784;
- Targuna houses/improvements: commit `20cee2f8260a18ccf9eaf4714bb22fb84f34db64`;
- Targuna Cottage door fix: commit `4fde95c6d14a97f6ea7d14618294f79a1c9591bf`;
- Targuna protection zones and signs: commit `851528e8ff22e1aeb5e882943e4ede011e36447b`;
- later Targuna map bug fixes: commit `181efdf6a3433cc92853544618ce3ceec94d4d2f`.

### Required CrystalServer audit policy

For any Crystal candidate:

1. Pin the exact Crystal commit SHA.
2. Inventory every changed or selected file; do not use a moving branch as provenance.
3. Keep `data-global` separate from `data-crystal`; never mix their maps or sidecars.
4. Compare map hashes, OTBM headers, occupied bounds, towns, houses and sidecars.
5. Run bounded map/mechanic, reachability and spawn/NPC analysis.
6. Compare storages, quest log, scripts, monster/NPC definitions and item references with current Canary.
7. Record features that require Crystal engine APIs not present in Canary.
8. Treat source comments, placeholders, guessed dialogue and video-derived behavior as explicit review findings.
9. Adapt the smallest verified unit; never copy Crystal wholesale.

## OTLand public donor registry

OTLand threads are discovery and donor sources. They are not authoritative merely because an attachment exists or the title contains a version.

Before use, download outside Git, compute hashes, inspect archive members and scan for unexpected executable or script content. VirusTotal links shown by OTLand are useful metadata but are not a substitute for local inventory and review.

### Current verified candidates

| ID | Public source | Published | Claimed version | Verified downloadable material | Coordinates/coverage | Known limitations | Status |
|---|---|---:|---|---|---|---|---|
| `OTL-BLUE-15X` | [Blue Valley - Converted to TFS](https://otland.net/threads/15-x-blue-valley-converted-to-tfs-server-id.292806/) | 2025-07-11 | 15.x | `bluevalley.otbm` 530.5 KB; `items.zip` 339.8 KB | `33602,31496,7` | Thread provides no quest, NPC or spawn package; matching item/assets revision is unproven. | high-priority map candidate |
| `OTL-CANARY-1412` | [Canary Map - Converted to TFS](https://otland.net/threads/14-12-canary-map-converted-to-tfs.290897/) | 2025-01-16 | 14.12 | `Canary Map.7z` 27.9 MB; author claims Canary houses and spawns; converted ClientID to ServerID | Thais `32369,32241,7` | Older than current donor targets; forum replies demonstrate missing monster/client compatibility problems on mismatched servers. | comparison/reference only |
| `OTL-AZZILON-1412` | [Azzilon - hunts and boss/reward rooms](https://otland.net/threads/14-12-azzilon-only-hunts-and-boss-room-boss-reward-converted-to-tfs.291265/) | 2025-03-01 | 14.12 | `Azzilon.zip` 310.1 KB | hunt `33857,32411,6`; boss `34032,32330,14` | Title and post explicitly limit coverage to hunts and boss/reward rooms; not the full quest. | partial region candidate |
| `OTL-CANDIA-1340` | [Candia](https://otland.net/threads/13-40-candia.289874/) | 2024-08-27 | 13.40 | `Candia.zip` 160.3 KB; later `candia-spawn.xml` 28.5 KB | `33429,32145,7` | Replies request missing creature definitions; TFS/Canary conversion and items compatibility require review. | partial map+spawn candidate |
| `OTL-PODZILLA-1340` | [Rise of Podzilla Quest - Converted to TFS](https://otland.net/threads/13-40-rise-of-podzilla-quest-converted-to-tfs.290894/) | 2025-01-15 | 13.40 | `The Rise of Podzilla Quest.otbm` 1 MB | `33818,31997,4`; `33821,31994,6` | Author states there is only the map and no spawn XML. | map-only quest candidate |
| `OTL-ROTTEN-1320` | [Rotten Blood Quest Map](https://otland.net/threads/13-20-rotten-blood-quest-map.286632/) | 2023-10-16 | 13.20 | `rotten.otbm` 1.7 MB; later TFS conversion attachment of same named map | `34106,32047,13` | Replies explicitly ask for respawns, mechanics and monster files; map alone does not prove a working quest. | map-only quest candidate |
| `OTL-OSKAYAAT-1320` | [Oskayaat Map](https://otland.net/threads/13-20-oskayaat-map.286638/) | 2023-10-17 | 13.20 | attachment named `okayaat.otbm`, 571.6 KB; later TFS conversion | `32998,32951,7` | Replies request respawn and updated item data; filename is misspelled and version/asset compatibility must be determined from the binary. | map-only region candidate |
| `OTL-WINTER-2026` | [Winter Update 2026 - Isle of Ada, Crypts, etc](https://otland.net/threads/winter-update-2026-isle-of-ada-crypts-etc.304828/) | 2026-06-24 | Winter Update 2026 | Thread existence, title, author and date are visible in the Maps forum index | unknown | Thread body currently returns a cache miss through the available reader; no attachment, completeness or license claim is verified. | watch/unverified |

### OTLand discovery surfaces

- Maps forum: <https://otland.net/forums/maps.50/>
- Data Packs forum: <https://otland.net/forums/data-packs.464/>
- Distributions forum: <https://otland.net/forums/distributions.18/>
- Long-running request thread: <https://otland.net/threads/request-maps-you-need-here.9167/>

Discovery surfaces identify candidates only. A post asking for or advertising a map is not evidence that a usable public package exists.

### Companion asset candidate

Several Nottinghster threads reference:

- <https://github.com/Nottinghster/1098extended>

Treat it only as a compatibility lead for the author’s TFS conversions. Do not replace Canary `items.otb`, items XML or client assets from this repository. Determine whether the donor OTBM stores ClientID or ServerID and use the exact matching catalogue during analysis.

## Community narrative references

Useful examples:

- Targuna Quest on Tibia Fandom: <https://tibia.fandom.com/wiki/Targuna_Quest>
- Targuna Quest on TibiaWiki Brasil: <https://www.tibiawiki.com.br/wiki/Targuna_Quest>

Use maintained wikis for:

- quest names and sequence hypotheses;
- NPC names and visible dialogue leads;
- rewards, access requirements and boss names;
- cross-checking community implementations;
- locating independent references or videos.

Do not use a wiki alone to authorize:

- exact storage numbers;
- exact AID/UID;
- exact coordinates;
- item/server IDs;
- spawn intervals or radii;
- protocol fields;
- unobserved runtime edge cases.

A wiki disagreement is a finding requiring more evidence, not permission to choose one silently.

## Claim-only sources

Example:

- Muximba public project information: <https://github.com/Muximba/.github>

Muximba publicly claims Global 15.25+ content including New Haven and Targuna with quests, NPCs and raids, but its public information repository does not expose a server OTBM or complete datapack.

Classify such sources as `claim-only` until an actual public, auditable package or source revision is available. They may guide searches but cannot be imported or used as implementation proof.

## Mandatory candidate intake workflow

Every candidate map/datapack task must perform the following steps before proposing implementation.

### 1. Provenance capture

Record:

```text
source ID
source URL
source author/uploader
publication and retrieval dates
repository commit or forum post number
original filenames
archive member list
byte sizes
SHA-256 for every downloaded file
claimed Tibia/client version
observed OTBM/client/item schema
license or reuse statement when present
```

If an archive changes at the same URL, treat it as a new candidate and preserve both hashes.

### 2. Quarantine and file inventory

- Download outside the repository.
- Reject path traversal, symlink escape and unexpected executable content.
- Expand to a dedicated candidate directory.
- Inventory OTBM, XML, Lua, JSON, SQL, binaries and client assets separately.
- Never run downloaded executables or scripts merely to inspect a map package.

### 3. Compatibility identification

Determine independently:

- OTBM format/header compatibility;
- whether item values are ClientID or ServerID;
- required `items.otb`/items XML revision;
- required appearances/assets/client build;
- coordinate frame and insertion region;
- companion house, spawn, NPC and zone files;
- engine APIs and Lua conventions assumed by scripts.

Do not “fix red tiles” by deleting or substituting unknown items before the original IDs and matching asset catalogue are understood.

### 4. Deterministic map evidence

Reuse the existing native scanner and Unified OTBM World Index. Record at minimum:

- source map hash and size;
- header versions;
- actual occupied coordinate bounds per floor;
- tile and placement counts;
- distinct item IDs;
- towns, waypoints and house metadata;
- tile flags;
- AID/UID;
- house doors;
- teleport sources and destinations;
- candidate region bounds.

No second OTBM parser is allowed.

### 5. Semantic and bounded comparison

Compare the candidate with the exact target baseline and classify each difference as:

```text
identical
metadata-only
tile/item change
map-mechanic change
house change
teleport/transition change
spawn/NPC change
custom-content-only
unknown/incompatible
```

Until the roadmap semantic-diff phase is implemented, produce bounded queries and explicit reports. Do not perform manual whole-map visual merging.

### 6. Mechanics and quest resolution

Reuse:

- `otbm_item_audit_tool.py`;
- `otbm_script_resolution_tool.py`;
- `quest_map_validation_tool.py`.

Required outcomes:

- every candidate AID/UID/item/position mechanic is correlated with the selected active Canary datapack;
- unresolved handlers remain unresolved;
- donor storages are compared against Canary definitions and reservations;
- donor quest scripts are treated as implementation candidates, not proof of authentic progression;
- dynamic Lua remains explicit.

### 7. Reachability and transitions

Reuse the OTBM reachability validator.

- Indexed teleports are evaluated from exact destinations.
- Stairs, ladders, rope spots, holes and other non-teleport floor transitions require reviewed manifest evidence.
- Do not infer a route from sprites, names, screenshots or memory.
- Report unreachable, conditional, one-way, dead-end and cyclic behavior.

### 8. Spawns, bosses and NPCs

Reuse the spawn/NPC validator with one explicit datapack root.

Check:

- companion spawn/NPC XML exists and is selected intentionally;
- creature and NPC definitions resolve case-insensitively;
- intervals, radii and positions match current loader semantics;
- literal dynamic creations are inventoried;
- duplicate or missing definitions remain findings;
- reward-boss metadata is not confused with runtime spawn-boss behavior.

### 9. Assets and item definitions

For every distinct donor item unavailable in the target catalogue, report:

- donor item value;
- whether it is a client or server ID;
- matching appearance when available;
- sample positions/use count;
- missing Canary `items.xml` or asset dependency;
- whether the region can be reviewed without changing `items.otb`.

Any required `items.otb` or client-asset change is separate manual integration work and remains forbidden unless explicitly authorized under the repository safety gate.

### 10. Factual visual evidence

Use only:

- the real OTBM candidate;
- the exact compatible item/appearance catalogue;
- real client sprites/assets;
- the repository factual renderer.

Do not use image generation as map evidence. Missing sprites or appearances must be reported, not invented.

### 11. Runtime evidence

Static evidence can nominate a bounded implementation task. It cannot close parity by itself.

Runtime validation should cover, where applicable:

- login/access;
- route traversal;
- doors, levers, chests and teleports;
- storage progression;
- NPC dialogue and trade;
- monster/boss creation and reset;
- rewards and cooldowns;
- client UI/protocol behavior;
- persistence and relog behavior.

Use the universal E2E platform when a physical client is required. Feature-specific tasks own scenarios and assertions, not duplicate orchestration.

## Required audit output

Every candidate review must produce a Markdown summary and machine-readable JSON outside Git or as small reviewed fixtures when explicitly approved.

Minimum report fields:

```json
{
  "sourceId": "OTL-BLUE-15X",
  "sourceUrl": "https://otland.net/...",
  "retrievedAt": "ISO-8601",
  "files": [
    {
      "name": "bluevalley.otbm",
      "sizeBytes": 0,
      "sha256": "..."
    }
  ],
  "claims": {
    "clientVersion": "15.x",
    "scope": "Blue Valley"
  },
  "observed": {
    "otbmHeader": {},
    "bounds": {},
    "tileCount": 0,
    "placementCount": 0
  },
  "compatibility": {
    "map": "unknown",
    "items": "unknown",
    "assets": "unknown",
    "scripts": "not-provided",
    "spawns": "not-provided",
    "npcs": "not-provided"
  },
  "findings": [],
  "classification": "candidate",
  "recommendedAction": "bounded-audit"
}
```

Allowed lifecycle classifications:

```text
discovery-only
claim-only
candidate
audit-ready
blocked-incompatible
rejected-duplicate
reference-only
verified-donor
implemented
```

`verified-donor` means the bounded source material passed the selected static compatibility gates. It does not mean Real Tibia runtime parity is proven.

## Current priority queue

1. **Crystal Targuna bundle** — exact bounded OTBM diff, houses, PZ, teleport/transition, quest, NPC, monster/boss and storage analysis against the supplied baseline.
2. **Crystal Newhaven bundle** — determine map coverage and separate engine/protocol dependencies from transferable datapack behavior.
3. **OTLand Blue Valley 15.x** — acquire exact attachment hashes and identify item catalogue before map analysis.
4. **OTLand Winter Update 2026** — verify whether the thread exposes a public attachment or only discussion/screenshots.
5. **Older OTLand regions** — first prove whether Azzilon, Candia, Rise of Podzilla, Rotten Blood and Oskayaat are already fully or partially present in the current baseline; do not import duplicate regions.
6. **TibiaMaps cross-check** — use current explored minimap data to compare candidate outlines and missing coverage.
7. **Semantic OTBM diff tooling** — complete the roadmap safety phase before any bounded map-writing proposal.

## Monitoring vocabulary

Search public sources using both release and content terms:

```text
world.otbm
real map
global map
Canary map
15.x
15.24
15.25
Targuna
Newhaven
New Haven
Blue Valley
Isle of Ada
Crypts
Winter Update 2026
Azzilon
Candia
Rise of Podzilla
Rotten Blood
Oskayaat
spawn.xml
world-npc.xml
world-house.xml
quest scripts
```

For GitHub, search commits and code by rare quest/NPC/storage identifiers, not only repository descriptions. Small forks often contain useful changes without advertising a complete Real Map.

For every new discovery, update this registry only after the public source and its observable contents are verified. Keep unavailable or claim-only leads clearly separated from downloadable candidates.

## Agent completion rule

An agent may recommend a new parity task only when it can state all of the following without guessing:

- exact target baseline revision and map hash;
- exact external source revision or attachment hash;
- bounded scope and coordinates;
- evidence dimension supplied by each source;
- known missing files and dependencies;
- existing Canary tools to reuse;
- static findings and unresolved items;
- required runtime scenario;
- proof that no full-map, `items.otb`, asset or datapack replacement is being proposed.

When any item is unknown, the next task is evidence collection, not implementation.
