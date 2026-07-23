---
program_id: CAN-PROGRAM-OTBM-WORLD-ASSURANCE-OPERATIONS
name: OTBM World Assurance Operations
status: active
owner: OTBM analysis tooling / world assurance operations
created: 2026-07-23T14:25:00+02:00
updated: 2026-07-23T14:25:00+02:00
last_verified_commit: "54ce97b3bcaac8c2e1a0d4cc6162a6ff975bbee9"
primary_paths:
  - docs/agents/programs/OTBM_WORLD_ASSURANCE_OPERATIONS_PROGRAM.md
  - docs/ai-agent/OTBM_WORLD_QUALITY_REPAIR_ROADMAP.md
shared_integration_paths:
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/CHANGELOG.md
  - docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md
related_programs:
  - CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
  - CAN-PROGRAM-OTBM-E2E-ROUTING
cross_repo_contracts: []
---

# Mission

Turn the completed OTBM-QA-001..018 stack into an operational world-assurance practice over reviewed real Canary map targets without reopening the closed QA programme or creating parallel canonical infrastructure.

The programme owns the long-lived operational loop:

```text
reviewed real-world targets
  -> exact current-map evidence
  -> QA-005 factual coverage dimensions
  -> QA-006 bounded certification
  -> existing Physical E2E where the target requires runtime proof
  -> QA-016 freshness tracking
  -> QA-007 continuous-assurance decisions for relevant changes
  -> refreshed certification state
```

The programme does not claim that the whole world is healthy merely because the tooling exists. Every health, certification, impact, freshness and runtime claim remains bounded by exact compatible provenance and the proof level required by the underlying contract.

# Scope

Included:

- systematic certification campaigns over explicitly reviewed world, region, landmark-route, quest and mechanic-set targets;
- factual visualization of coverage, certification, blockers and stale evidence using the existing factual OTBM renderer and compatible real assets;
- dependency-gated consumption of stable Tibia Client Reference drift/parity evidence to invalidate or refresh only affected QA/certification dimensions;
- compact OTBM-owned static correlation for runtime-reported positions, transitions and interactions through the existing QA-018 Evidence Gateway;
- deterministic property/adversarial/fuzz-style hardening of existing canonical QA contracts using bounded synthetic fixtures;
- operational adoption of the existing QA-002/007 regression and continuous-assurance contracts for relevant reviewed map/candidate changes;
- durable campaign sequencing, proof boundaries and handoff for future bounded tasks.

# Explicit exclusions

- Do not create `OTBM-QA-019` or reopen OTBM-QA-001..018.
- Do not create a second OTBM parser, scanner, World Index, Script Resolution engine, pathfinder/BFS, factual renderer, mutation engine, E2E runner or E2E workflow.
- Do not treat client reference, minimap, screenshot, visual similarity or AI-generated imagery as authoritative map/mechanic proof.
- Do not use AI-generated map imagery as evidence; factual visualizations must use the existing renderer and compatible real assets.
- Do not mutate source maps, `items.otb`, active datapacks or proprietary client assets.
- Do not commit generated `.otbm`, `.widx`, certification reports, evidence bundles, coverage renders or proprietary client/reference files.
- Do not generate feature-specific Universal E2E expectations, fixtures or acceptance decisions from OTBM coverage gaps.
- Do not let a convenience score, heatmap colour or dashboard percentage become the sole gate for merge, certification or release.
- Do not consume unstable or unproven TCR formats; TCR remains a separate programme and ownership domain.
- Do not authorize deployment or production promotion from QA evidence alone.

# Existing systems to reuse

| Module/tool/contract | Source | Required reuse rule |
|---|---|---|
| Unified OTBM World Index | existing OTBM stack | The only canonical full-world OTBM index; operational tasks consume it and never rescan with a parallel parser. |
| OTBM Script Resolution | existing OTBM stack | Preserve `unresolved`, `partially-resolved`, `referenced-only` and `conflicting` states; never guess handled mechanics. |
| OTBM Reachability | existing OTBM stack | The only canonical pathfinder/BFS and predecessor graph; no second route engine. |
| Semantic OTBM Diff | existing OTBM stack | Exact before/after semantic change evidence and finding IDs; no visual-diff substitution. |
| QA-001 World Health | OTBM-QA-001 | Current compatible health dimensions; not a global gameplay-correctness claim. |
| QA-002 Regression Guard | OTBM-QA-002 | Fail-closed impacted validation selection; uncertain evidence selects more validation, never less. |
| QA-005 Coverage Dashboard | OTBM-QA-005 | Independent factual coverage dimensions for reviewed targets; percentages remain presentation only. |
| QA-006 Region and Quest Certification | OTBM-QA-006 | Canonical C0-C7 bounded certification over exact current provenance. |
| QA-007 Continuous Assurance | OTBM-QA-007 | Existing fail-closed assurance composition; operational adoption must not rerun or replace validators/E2E. |
| QA-008 Blast-Radius Graph | OTBM-QA-008 | Only reviewer-declared/proven dependency edges; no inferred dependency discovery. |
| QA-009..013 | OTBM-QA-009..013 | Completeness, quest-state, connectivity, critical-access and identifier evidence for reviewed campaign targets. |
| QA-014 Asset Compatibility | OTBM-QA-014 | Exact map-used appearance/asset compatibility and stale-evidence triggers. |
| QA-016 Release Provenance/Freshness | OTBM-QA-016 | Exact component hashes and dependency-scoped staleness; timestamps are not freshness proof. |
| QA-017 Change Risk | OTBM-QA-017 | Transparent review aid only; never authorizes validation skip or merge. |
| QA-018 Compact Evidence Gateway | OTBM-QA-018 | Compact exact evidence transport for downstream consumers; no semantic reinterpretation or runtime ownership. |
| Factual OTBM renderer | existing OTBM rendering pipeline | Only factual map visualization path for coverage/certification overlays; generated imagery stays external. |
| Universal Physical E2E | CAN-PROGRAM-E2E-PLATFORM / OTBM-E2E routing | Owns physical execution and runtime proof; this programme may consume retained results only. |
| Tibia Client Reference Programme | CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE | Owns client-reference manifest/index/parity/drift formats; OWA consumes only stable exact outputs after their owning TCR packages merge. |

# Active tasks

| Task ID | Branch | PR | State | Exact next action |
|---|---|---:|---|---|
| CAN-20260723-otbm-world-assurance-operations-program | `docs/otbm-world-assurance-operations-20260723` | #795 | active | Finish programme/roadmap bootstrap, validate current head, merge, archive the bootstrap task, then select OWA-001 in a new bounded task. |

# Queue

| ID | Scope | Status | Dependencies | Risk | Exact next action |
|---|---|---|---|---|---|
| OWA-001 | Real-World Certification Campaign | planned | completed QA-005/006/016/018 and current compatible map evidence | medium | Define the first reviewed campaign target set and external campaign-result ledger by composing existing certification contracts; use an already reviewed target such as `thais.temple -> thais.depot` only if current provenance remains exact. |
| OWA-002 | Factual Certification and Coverage Map | planned | OWA-001 pilot evidence + existing factual renderer | medium | Define a render-manifest/overlay composition over exact QA-005/006/016 evidence without changing the renderer or treating colours/percentages as gates. |
| OWA-003 | TCR-to-QA Drift and Freshness Integration | blocked on stable TCR outputs | stable TCR-005/006/007/009 outputs as applicable + QA-008/016/002/007 | medium | After owning TCR packages merge, define exact dependency mappings from reference drift/parity findings to certification staleness, blast radius and impacted validation; do not parse TCR inputs in OWA. |
| OWA-004 | Runtime Incident to OTBM Evidence Bridge | planned | QA-018 + existing route/failure-triage evidence | medium | Define a bounded consumer that accepts explicit incident selectors such as position/transition/interaction identifiers and returns exact OTBM-owned static context while leaving runtime diagnosis and E2E ownership downstream. |
| OWA-005 | QA Contract Hardening and Adversarial Fixtures | planned | delivered QA contracts | medium | Add deterministic generated/synthetic fixtures and property-style invariants for provenance invalidation, fail-closed uncertainty, safe path/output handling and byte-stable deterministic reports without introducing a new parser or mutating real maps. |
| OWA-006 | Continuous Assurance Operational Adoption | planned | OWA-001 campaign model + QA-002/007 + existing CI/release governance | high | Select one bounded relevant map/candidate change path and integrate existing assurance evidence into its review gate without suppressing unrelated suites or authorizing deployment. |

# Package contracts

## OWA-001 — Real-World Certification Campaign

**Goal:** move from capability delivery to measured certification of reviewed real-world targets.

The campaign composes existing evidence; it does not create a new certification algorithm.

Target classes may include:

- world-level reviewed population summaries;
- city/region targets;
- landmark routes;
- one explicitly selected quest chain;
- one teleport/transition network;
- one dungeon/region;
- reviewed critical house-door or infrastructure sets;
- reviewed mechanic sets.

For every target retain, as applicable:

```text
exact map / World Index provenance
QA-005 factual coverage dimensions
QA-006 C0-C7 certification
QA-016 dependency/freshness state
exact blockers and unresolved/conflicting evidence
existing Physical E2E references where required
```

Operational rules:

- certification target definitions must be reviewed and exact; do not infer semantic importance from names, sprites or proximity;
- C5/C6/C7 claims require the exact physical/candidate proof required by QA-006;
- region/landmark-route targets retain the QA-006 certification cap rules;
- campaign outputs are artifacts/operational evidence and are not committed as generated repository data;
- absence of coverage remains a gap, not an instruction to invent an E2E scenario;
- the first pilot should prefer an already reviewed semantic target with existing route evidence rather than inventing coordinates.

Completion signal for the package is not “world healthy”; it is a reproducible reviewed target inventory with exact current certification states and blockers.

## OWA-002 — Factual Certification and Coverage Map

**Goal:** make exact QA state visually inspectable without creating a second renderer or turning presentation into proof.

Inputs:

- exact current factual renderer map baseline;
- QA-005 coverage targets/results;
- QA-006 certification results;
- QA-016 freshness/staleness evidence;
- optional exact QA-001/011/012/013 findings for explicitly supported overlay categories.

Candidate overlay dimensions:

- C0-C7 certification level;
- stale certification;
- unresolved/conflicting Script Resolution evidence;
- unreachable/conditional reviewed targets;
- fragile reviewed routes;
- missing current Physical E2E proof;
- identifier/selector conflicts;
- reviewed critical-access findings.

Hard boundaries:

- use the existing factual renderer and compatible real assets only;
- no AI-generated map imagery;
- no visual inference from sprite appearance;
- every overlay cell/marker must retain an exact evidence reference and provenance;
- colours, percentages and heat intensity are presentation only and never override explicit blockers or certification state;
- generated renders/manifests remain external artifacts.

## OWA-003 — TCR-to-QA Drift and Freshness Integration

**Goal:** make exact stable Tibia Client Reference changes invalidate or select only the QA evidence dimensions that actually depend on them.

Intended composition after the owning TCR packages deliver stable formats:

```text
TCR exact reference drift/parity finding
  -> explicit dependency mapping
  -> QA-016 dependency-scoped staleness
  -> QA-008 proven blast-radius paths where declared
  -> QA-002 impacted validation selection
  -> QA-007 continuous-assurance result after selected validation executes
  -> refreshed QA-006 certification state
```

Hard boundaries:

- OWA does not parse `staticdata`, `staticmapdata`, proficiency or minimap files;
- OWA does not guess item/server/object identifier mappings;
- TCR client reference remains evidence, not map authority;
- quest ID/name drift alone does not prove quest-stage or runtime changes;
- matching proficiency IDs do not prove runtime/persistence/protocol parity;
- only stable exact TCR outputs from merged owning packages may enter the integration;
- dependency uncertainty fails closed to stale/review-required or broader selected validation.

## OWA-004 — Runtime Incident to OTBM Evidence Bridge

**Goal:** make OTBM-owned static context cheap to obtain when a runtime owner reports an exact map-related selector.

Candidate explicit inputs:

- `x,y,z` position;
- transition ID;
- interaction ID;
- landmark ID;
- exact route-plan/preflight reference;
- map SHA-256 observed by the runtime artifact when available.

The bridge may return only compatible existing evidence, such as:

- exact tile/item/AID/UID/house-door/teleport context from World Index/Item Audit;
- Script Resolution state and exact correlated handlers;
- reachability/transition evidence;
- semantic landmark and route-interaction references;
- existing route-plan/preflight/failure-triage evidence;
- current QA-001/005/006/016 dimensions;
- exact blockers and provenance mismatch.

It must not:

- become a general log parser or runtime root-cause engine;
- control server, database or OTClient lifecycle;
- generate feature-specific assertions or `NEXT_ACTION` for an E2E owner;
- retry/replay Physical E2E;
- upgrade static correlation into runtime success/failure proof.

## OWA-005 — QA Contract Hardening and Adversarial Fixtures

**Goal:** increase confidence in existing QA invariants without testing by mutating production maps or creating parallel implementations.

Candidate invariant families:

- identical stable input yields byte-identical deterministic output where the contract requires it;
- any dependency byte/hash change invalidates exactly the relevant provenance/freshness state;
- `unresolved`, `conflicting`, ambiguous, stale, truncated or missing evidence never silently upgrades to handled/safe/non-impacting;
- truncated/bounded evidence never authorizes a global absence or safe skip;
- source-map immutability and create-new/no-clobber output rules hold;
- unsafe paths, symlinks and input/output aliasing fail closed where supported by the contract;
- duplicate IDs/selectors remain explicit findings under the owning contract and are not auto-repaired;
- unknown/missing appearance evidence never becomes walkable/compatible by default;
- candidate/current map hash mismatch invalidates candidate/Physical E2E proof;
- ordering changes in semantically unordered reviewed inputs do not create nondeterministic reports when the contract specifies canonical ordering.

Use bounded synthetic fixtures and deterministic generated cases. Third-party fuzz frameworks require a separate justification; default to repository-supported/standard-library test infrastructure.

## OWA-006 — Continuous Assurance Operational Adoption

**Goal:** apply the already-delivered QA-002 and QA-007 orchestration to one real bounded change/release path.

Required sequence:

```text
exact before/current candidate provenance
  -> Semantic Diff
  -> QA-002 selected static + represented Physical E2E plan
  -> owning validators / Universal E2E execute selected work
  -> before/after QA-001 World Health
  -> before/after QA-006 certification
  -> QA-007 exact execution/result-set validation
  -> auditable assurance decision
```

Hard boundaries:

- OWA-006 does not rerun validators inside QA-007;
- selected result sets must match the exact QA-002 plan and pass according to QA-007;
- unrelated non-OTBM CI suites are never suppressed;
- manual/uncertain selection remains fail-closed;
- assurance success does not authorize deployment by itself;
- start with one bounded change class before considering broader adoption.

# Sequencing

Recommended order:

1. **OWA-001** — establish a real reviewed certification campaign and pilot target.
2. **OWA-002** — visualize factual campaign state once real certification artifacts exist.
3. **OWA-005** — harden cross-contract invariants in parallel where path ownership allows.
4. **OWA-004** — expose incident-oriented static context through existing QA-018 evidence.
5. **OWA-003** — begin only after stable owning TCR outputs exist.
6. **OWA-006** — operationalize continuous assurance on one bounded real change path after campaign semantics are proven.

OWA-003 may move earlier or later based only on actual TCR delivery state. OWA-006 remains deliberately late because it can affect merge/release gating and therefore requires proven campaign semantics plus exact CI ownership.

# Completion definition

The programme is complete only when:

1. at least one reviewed real-world campaign is reproducible from exact current evidence;
2. certification/coverage visualization is factual, evidence-linked and renderer-reusing;
3. TCR drift integration, if TCR formats are delivered, invalidates only explicitly dependent QA/certification dimensions and fails closed on uncertainty;
4. runtime incident correlation returns compact OTBM evidence without taking runtime/E2E ownership;
5. high-value fail-closed and determinism invariants have adversarial/property-style regression coverage;
6. one bounded real map/candidate change path uses the existing QA-002/007 assurance contracts without bypassing unrelated CI or deployment governance;
7. no new parser, World Index, pathfinder, renderer, writer, E2E runner or E2E workflow has been introduced;
8. generated certification, evidence and render artifacts remain outside Git.

Completion of this programme still does not imply that every tile, quest or mechanic in the entire world is gameplay-correct. Certification remains target- and evidence-bounded.

# Dependencies and blockers

- OWA-003 is blocked until the required owning TCR outputs are stable and merged.
- Physical proof for OWA-001/006 depends on existing Universal Physical E2E evidence and remains owned by that subsystem.
- No current blocker prevents programme bootstrap or future OWA-001 planning.

# Decisions and invariants

- OTBM-QA-001..018 remains permanently closed as the delivered tooling programme; successor operational work uses `OWA-*` identifiers.
- QA-005/006 explicit evidence dimensions and C0-C7 states remain canonical; operational dashboards may summarize but not replace them.
- World Index, Script Resolution, Reachability/BFS, Semantic Diff, factual renderer, bounded mutation paths and Universal Physical E2E remain single canonical owners.
- Static evidence, Physical E2E proof and candidate-change revalidation remain separate proof levels.
- Source maps are immutable inputs; generated/candidate artifacts remain external unless a separately approved contract explicitly permits a reviewed repository text artifact.
- TCR and OWA remain separate programmes with explicit producer/consumer boundaries.

# Validation strategy

Programme/bootstrap tasks:

- Agent Task Ownership on exact PR head;
- repository CI/Required on exact final head;
- changed-file scope audit;
- review-thread/review audit;
- verify the completed QA roadmap still says OTBM-QA-001..018 complete;
- verify no `OTBM-QA-019` identifier is introduced.

Future implementation tasks must additionally run the focused tests owned by every consumed/changed contract and must not claim runtime proof without retained Universal Physical E2E evidence.

# Handoff

## Start here

Read:

1. `AGENTS.md`;
2. `docs/agents/README.md`;
3. this programme record;
4. `docs/ai-agent/OTBM_WORLD_QUALITY_REPAIR_ROADMAP.md` closure and successor sections;
5. the one selected OWA active task and live PR;
6. only the exact QA/TCR/E2E contracts required by that package.

## Task creation protocol

1. Select exactly one OWA package.
2. Revalidate current `main`, programme queue and relevant producer contracts.
3. Inspect active path ownership and open PRs.
4. Create one active task, branch and draft PR.
5. Declare exact exclusive/shared/read-only paths.
6. Reuse existing QA modules; do not create parallel canonical infrastructure.
7. Validate, merge, archive the task and update this programme queue/handoff.

## Do not repeat

- Do not revive QA-019 naming for operational work.
- Do not build another parser/index/pathfinder/renderer/E2E stack to make campaign execution easier.
- Do not infer coordinates, identifier mappings, semantic criticality or quest topology from names/visual proximity.
- Do not convert missing Physical E2E coverage into invented scenarios.
- Do not treat a green static campaign state as global gameplay proof.

## Open questions

- Exact first OWA-001 target inventory must be selected from current reviewed evidence at task start; `thais.temple -> thais.depot` is only a preferred pilot candidate if its exact current provenance is still valid.
- OWA-003 package scope must be re-derived from the TCR formats that are actually merged at that time.
