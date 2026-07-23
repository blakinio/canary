---
program_id: CAN-PROGRAM-OTBM-WORLD-ASSURANCE-OPERATIONS
name: OTBM World Assurance Operations
status: active
owner: OTBM analysis tooling / world assurance operations
created: 2026-07-23T14:25:00+02:00
updated: 2026-07-23T14:35:00+02:00
last_verified_commit: "a950648d9fe0b04746b65055e045ba144213cc76"
primary_paths:
  - docs/agents/programs/OTBM_WORLD_ASSURANCE_OPERATIONS_PROGRAM.md
  - docs/ai-agent/OTBM_WORLD_ASSURANCE_OPERATIONS_ROADMAP.md
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
  -> existing Physical E2E where runtime proof is required
  -> QA-016 freshness tracking
  -> QA-002/007 impacted validation and assurance for relevant changes
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

| Module/tool/contract | Required reuse rule |
|---|---|
| Unified OTBM World Index | The only canonical full-world OTBM index; never add another parser/scanner/index. |
| OTBM Script Resolution | Preserve unresolved/partial/conflicting states; never guess handled mechanics. |
| OTBM Reachability | The only canonical pathfinder/BFS and predecessor graph. |
| Semantic OTBM Diff | Canonical exact before/after semantic change evidence and finding IDs. |
| QA-001 World Health | Current compatible health dimensions; not global gameplay correctness. |
| QA-002 Regression Guard | Uncertain evidence selects more validation, never less. |
| QA-005 Coverage Dashboard | Independent factual coverage dimensions; percentages remain presentation only. |
| QA-006 Region and Quest Certification | Canonical C0-C7 bounded certification over exact current provenance. |
| QA-007 Continuous Assurance | Existing fail-closed assurance composition; do not rerun validators/E2E inside it. |
| QA-008 Blast-Radius Graph | Only reviewer-declared/proven dependency edges. |
| QA-009..013 | Reuse completeness, quest-state, connectivity, critical-access and identifier evidence. |
| QA-014 Asset Compatibility | Exact map-used appearance/asset compatibility and stale-evidence triggers. |
| QA-016 Release Provenance/Freshness | Exact hashes and dependency-scoped staleness; timestamps are not proof. |
| QA-017 Change Risk | Transparent review aid only; never authorizes skip or merge. |
| QA-018 Compact Evidence Gateway | Compact exact evidence transport; no reinterpretation or runtime ownership. |
| Factual OTBM renderer | Only factual visualization path for certification/coverage overlays; generated imagery stays external. |
| Universal Physical E2E | Owns physical execution and runtime proof; OWA consumes retained results only. |
| Tibia Client Reference Programme | Owns client-reference manifest/index/parity/drift formats; OWA consumes stable merged outputs only. |

# Active tasks

| Task ID | Branch | PR | State | Exact next action |
|---|---|---:|---|---|
| CAN-20260723-otbm-world-assurance-operations-program | `docs/otbm-world-assurance-operations-20260723` | #795 | validating | Validate exact final scope/checks, merge, archive bootstrap task, then start OWA-001 separately. |

# Queue

| ID | Scope | Status | Dependencies | Risk | Exact next action |
|---|---|---|---|---|---|
| OWA-001 | Real-World Certification Campaign | planned | QA-005/006/016/018 + current exact map evidence | medium | Select the first reviewed campaign target set and compose existing certification evidence; prefer an already reviewed semantic target only if current provenance is exact. |
| OWA-002 | Factual Certification and Coverage Map | planned | OWA-001 pilot evidence + factual renderer | medium | Define evidence-linked factual overlays without changing the renderer or treating presentation as proof. |
| OWA-003 | TCR-to-QA Drift and Freshness Integration | blocked on stable TCR outputs | stable owning TCR outputs + QA-008/016/002/007 | medium | After required TCR packages merge, map exact reference drift into dependency-scoped staleness and impacted validation without parsing TCR inputs in OWA. |
| OWA-004 | Runtime Incident to OTBM Evidence Bridge | planned | QA-018 + existing route/failure-triage evidence | medium | Return compact OTBM static context for explicit incident selectors while keeping runtime diagnosis and E2E ownership downstream. |
| OWA-005 | QA Contract Hardening and Adversarial Fixtures | planned | delivered QA contracts | medium | Add deterministic synthetic/property-style invariants for provenance, fail-closed uncertainty, output safety and determinism. |
| OWA-006 | Continuous Assurance Operational Adoption | planned | OWA-001 + QA-002/007 + CI/release governance | high | Integrate existing assurance evidence into one bounded real map/candidate change path without suppressing unrelated suites or authorizing deployment. |

# Sequencing

1. **OWA-001** — establish a real reviewed certification campaign and pilot target.
2. **OWA-002** — visualize factual campaign state once real certification artifacts exist.
3. **OWA-005** — harden cross-contract invariants in parallel where path ownership allows.
4. **OWA-004** — expose incident-oriented static context through existing QA-018 evidence.
5. **OWA-003** — begin only after stable owning TCR outputs exist.
6. **OWA-006** — operationalize Continuous Assurance on one bounded real change path after campaign semantics are proven.

OWA-003 may move based only on actual TCR delivery state. OWA-006 remains deliberately late because it can affect merge/release gating and therefore requires proven campaign semantics plus exact CI ownership.

# Package boundaries

## OWA-001 — Real-World Certification Campaign

Compose existing QA-005/006/016/018 evidence over reviewed target classes such as cities/regions, landmark routes, selected quest chains, teleport networks, dungeons, critical infrastructure sets and mechanic sets. C5/C6/C7 claims require the exact physical/candidate proof required by QA-006. Campaign result artifacts remain outside Git.

Completion signal: a reproducible reviewed target inventory with exact current certification states and blockers, not a claim that the whole world is healthy.

## OWA-002 — Factual Certification and Coverage Map

Consume exact QA-005/006/016 evidence and supported QA findings to render evidence-linked overlays through the existing factual renderer. No AI-generated imagery, visual inference or presentation-only gate is allowed. Generated renders/manifests remain external.

## OWA-003 — TCR-to-QA Drift and Freshness Integration

After stable owning TCR formats exist:

```text
TCR exact parity/drift finding
  -> explicit dependency mapping
  -> QA-016 staleness
  -> QA-008 proven blast radius where declared
  -> QA-002 impacted validation
  -> owning validators / Physical E2E
  -> QA-007 assurance
  -> refreshed QA-006 certification
```

OWA never parses `staticdata`, `staticmapdata`, proficiency or minimap files and never guesses identifier mappings.

## OWA-004 — Runtime Incident to OTBM Evidence Bridge

Accept explicit selectors such as `x,y,z`, transition ID, interaction ID, landmark ID or route/preflight reference and return only compatible existing OTBM evidence. It must not become a general log parser, runtime root-cause engine, E2E executor or `NEXT_ACTION` generator.

## OWA-005 — QA Contract Hardening and Adversarial Fixtures

Use bounded deterministic synthetic fixtures to test invariants including deterministic output, dependency-scoped invalidation, fail-closed unresolved/conflicting/stale/truncated evidence, source immutability, no-clobber/path confinement, duplicate/unknown evidence handling and candidate/current hash mismatches. Do not mutate production maps or duplicate canonical implementations.

## OWA-006 — Continuous Assurance Operational Adoption

Apply the existing chain to one bounded real change path:

```text
exact before/current/candidate provenance
  -> Semantic Diff
  -> QA-002 selected validation plan
  -> owning validators / Universal Physical E2E
  -> before/after World Health and certification
  -> QA-007 exact result-set validation
  -> auditable assurance decision
```

Unrelated suites are never suppressed; assurance success never authorizes deployment by itself.

# Completion definition

The programme is complete only when:

1. at least one reviewed real-world campaign is reproducible from exact current evidence;
2. certification/coverage visualization is factual, evidence-linked and renderer-reusing;
3. TCR drift integration, if owning TCR formats are delivered, invalidates only explicitly dependent QA/certification dimensions and fails closed on uncertainty;
4. runtime incident correlation returns compact OTBM evidence without taking runtime/E2E ownership;
5. high-value fail-closed and determinism invariants have adversarial/property-style regression coverage;
6. one bounded real map/candidate change path uses the existing QA-002/007 assurance contracts without bypassing unrelated CI or deployment governance;
7. no new parser, World Index, pathfinder, renderer, writer, E2E runner or E2E workflow has been introduced;
8. generated certification, evidence and render artifacts remain outside Git.

Completion still does not imply that every tile, quest or mechanic in the entire world is gameplay-correct. Certification remains reviewed-target- and evidence-bounded.

# Dependencies and blockers

- OWA-003 is blocked until the required owning TCR outputs are stable and merged.
- Physical proof for OWA-001/006 depends on existing Universal Physical E2E evidence and remains owned by that subsystem.
- No current blocker prevents programme bootstrap or future OWA-001 planning.

# Decisions and invariants

- OTBM-QA-001..018 remains permanently closed as the delivered tooling programme; successor operational work uses `OWA-*` identifiers.
- `docs/ai-agent/OTBM_WORLD_QUALITY_REPAIR_ROADMAP.md` remains the closed QA roadmap and is not rewritten by this programme.
- `docs/ai-agent/OTBM_WORLD_ASSURANCE_OPERATIONS_ROADMAP.md` is the successor operational roadmap.
- QA-005/006 explicit evidence dimensions and C0-C7 states remain canonical; operational dashboards may summarize but not replace them.
- World Index, Script Resolution, Reachability/BFS, Semantic Diff, factual renderer, bounded mutation paths and Universal Physical E2E remain single canonical owners.
- Static evidence, Physical E2E proof and candidate-change revalidation remain separate proof levels.
- TCR and OWA remain separate programmes with explicit producer/consumer boundaries.

# Validation strategy

Programme/bootstrap tasks:

- Agent Task Ownership on exact PR head;
- repository CI/Required on exact final head;
- changed-file scope audit;
- review-thread/review audit;
- verify the closed QA roadmap remains unchanged and still marks OTBM-QA-001..018 complete;
- verify no `OTBM-QA-019` identifier is introduced.

Future implementation tasks must additionally run the focused tests owned by every consumed/changed contract and must not claim runtime proof without retained Universal Physical E2E evidence.

# Handoff

## Start here

Read:

1. `AGENTS.md`;
2. `docs/agents/README.md`;
3. this programme record;
4. `docs/ai-agent/OTBM_WORLD_ASSURANCE_OPERATIONS_ROADMAP.md`;
5. the closed `docs/ai-agent/OTBM_WORLD_QUALITY_REPAIR_ROADMAP.md` only for delivered QA contract boundaries;
6. the one selected OWA active task and live PR;
7. only the exact QA/TCR/E2E contracts required by that package.

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
