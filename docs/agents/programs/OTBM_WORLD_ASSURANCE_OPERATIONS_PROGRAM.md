---
program_id: CAN-PROGRAM-OTBM-WORLD-ASSURANCE-OPERATIONS
name: OTBM World Assurance Operations
status: active
owner: OTBM analysis tooling / world assurance operations
created: 2026-07-23T14:25:00+02:00
updated: 2026-07-23T17:10:00+02:00
last_verified_commit: "3115185e4eaf95f0ff6319ec9949274e7573065d"
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
| CAN-20260723-otbm-owa-005-qa-contract-hardening | `test/owa-005-qa-contract-hardening-20260723` | #802 | implementation merged; lifecycle record still active | Owning OWA-005 agent must lifecycle-close its own task; do not edit its exclusive paths from OWA-002. |

OWA-001 is merged and archived. No OWA-002 task has been claimed yet.

# Queue

| ID | Scope | Status | Dependencies | Risk | Exact next action |
|---|---|---|---|---|---|
| OWA-001 | Real-World Certification Campaign | completed via #801 | QA-005/006/016/018 + exact reviewed Thais route evidence | medium | Preserve the exact delivered state: QA-005 not-evaluated, QA-006 C0, QA-016 current, route-level Physical E2E proven, three explicit QA-005/006 blockers. |
| OWA-002 | Factual Certification and Coverage Map | ready for next bounded task | OWA-001 reviewed manifest/campaign semantics + factual renderer | medium | Render evidence-linked factual overlays that keep C0, freshness, Physical E2E and blockers separate; do not turn route proof into mechanic coverage or one health score. |
| OWA-003 | TCR-to-QA Drift and Freshness Integration | blocked on stable TCR outputs | stable owning TCR outputs + QA-008/016/002/007 | medium | Re-derive scope from the stable merged TCR producer contract before implementation; OWA consumes it but does not parse client reference inputs. |
| OWA-004 | Runtime Incident to OTBM Evidence Bridge | planned | QA-018 + existing route/failure-triage evidence | medium | Return compact OTBM static context for explicit incident selectors while keeping runtime diagnosis and E2E ownership downstream. |
| OWA-005 | QA Contract Hardening and Adversarial Fixtures | implementation merged in #802; lifecycle closure pending with owning task | delivered QA contracts | medium | Do not duplicate the merged adversarial-contract work; let its owning task close lifecycle independently. |
| OWA-006 | Continuous Assurance Operational Adoption | planned | OWA-001 + QA-002/007 + CI/release governance | high | Integrate existing assurance evidence into one bounded real map/candidate change path without suppressing unrelated suites or authorizing deployment. |

# Sequencing

1. **OWA-001** — completed: the first reviewed campaign target and fail-closed proof boundary are established.
2. **OWA-002** — next bounded package: factual visualization of the exact OWA-001 campaign state.
3. **OWA-005** — implementation merged independently; lifecycle closure remains owned by its existing task.
4. **OWA-004** — expose incident-oriented static context through existing QA-018 evidence.
5. **OWA-003** — begin only from stable owning TCR outputs and explicit producer/consumer contracts.
6. **OWA-006** — operationalize Continuous Assurance on one bounded real change path after campaign semantics are proven.

OWA-003 may move based only on actual TCR delivery state. OWA-006 remains deliberately late because it can affect merge/release gating and therefore requires proven campaign semantics plus exact CI ownership.

# Package boundaries

## OWA-001 — Real-World Certification Campaign

Delivered by PR #801.

The durable campaign layer composes existing QA-005/006/016/018 evidence and retained Physical E2E over reviewed targets. It does not rerun canonical validators or execution systems and never promotes missing proof.

First reviewed target:

- target ID: `owa-001.thais-temple-to-depot`;
- class: `landmark-route`;
- semantic route: `thais.temple -> thais.depot`;
- exact source-map SHA-256: `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2`;
- exact World Index SHA-256: `6c22cd26d4414aa094af1d00be7f62190a441e270ee7a478b55449bf92e55e7a`;
- QA-005: all dimensions `not-evaluated` because no reviewed mechanic binding exists for this pure-movement route;
- QA-006: `C0_NOT_EVALUATED`;
- QA-016 static-route freshness: `current`;
- QA-016 retained route-level Physical E2E freshness: `current`;
- retained route-level Physical E2E: `proven` from workflow run `29704821423`, artifact `8447816376`;
- target state: `blocked`.

Exact blockers:

- `QA005_LANDMARK_ROUTE_REQUIRES_REVIEWED_MECHANIC_IDS`;
- `QA005_NO_REVIEWED_MECHANIC_BINDING_FOR_PURE_MOVEMENT_ROUTE`;
- `QA006_REQUIRES_CANONICAL_QA005_TARGET`.

Completion signal satisfied: a reproducible reviewed target inventory exists with exact current-compatible proof boundaries and blockers. This is not a claim that the target is formally C5 or that the whole world is healthy.

## OWA-002 — Factual Certification and Coverage Map

Consume exact OWA-001 campaign output semantics plus QA-005/006/016 evidence and supported QA findings to render evidence-linked overlays through the existing factual renderer.

The first visualization must preserve four separate facts instead of collapsing them into a score:

1. formal QA-006 certification is C0;
2. QA-005 dimensions are not evaluated for the pilot;
3. exact static-route and retained route-level Physical E2E evidence are current;
4. route-level Physical E2E is proven but cannot manufacture mechanic coverage or formal certification.

No AI-generated imagery, visual inference or presentation-only gate is allowed. Generated renders/manifests remain external.

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

- OWA-001 is complete but formal certification for its first pilot remains blocked at C0 until a legitimate canonical QA-005 target binds exact reviewed mechanic evidence.
- OWA-002 is not blocked by the C0 state; that C0 state and its blockers are factual content that must be visualized explicitly.
- OWA-003 remains dependency-gated by stable owning TCR outputs and must be re-derived from the actual merged producer contract at task start.
- Physical proof for OWA-001/006 depends on existing Universal Physical E2E evidence and remains owned by that subsystem.

# Decisions and invariants

- OTBM-QA-001..018 remains permanently closed as the delivered tooling programme; successor operational work uses `OWA-*` identifiers.
- `docs/ai-agent/OTBM_WORLD_QUALITY_REPAIR_ROADMAP.md` remains the closed QA roadmap and is not rewritten by this programme.
- `docs/ai-agent/OTBM_WORLD_ASSURANCE_OPERATIONS_ROADMAP.md` is the successor operational roadmap.
- QA-005/006 explicit evidence dimensions and C0-C7 states remain canonical; operational dashboards may summarize but not replace them.
- World Index, Script Resolution, Reachability/BFS, Semantic Diff, factual renderer, bounded mutation paths and Universal Physical E2E remain single canonical owners.
- Static evidence, Physical E2E proof and candidate-change revalidation remain separate proof levels.
- TCR and OWA remain separate programmes with explicit producer/consumer boundaries.
- A successful pure-movement Physical E2E route does not by itself establish QA-005 mechanic coverage.

# Validation strategy

Programme/lifecycle tasks:

- Agent Task Ownership on exact PR head;
- repository CI/Required on exact final head;
- changed-file scope audit;
- review-thread/review audit;
- verify the closed QA roadmap remains unchanged and still marks OTBM-QA-001..018 complete;
- verify no `OTBM-QA-019` identifier is introduced.

Future implementation tasks must additionally run the focused tests owned by every consumed/changed contract and must not claim runtime proof without retained Universal Physical E2E evidence.

# Handoff

## OWA-001 delivered state

Start from the archived task:

`docs/agents/tasks/archive/CAN-20260723-owa-001-real-world-certification-campaign.md`

and the durable campaign documentation:

`docs/ai-agent/OTBM_WORLD_ASSURANCE_CAMPAIGN.md`.

The first target is intentionally **not formally certified above C0**. Its exact reviewed map/World Index provenance and route/preflight evidence are current, and exact retained route-level Physical E2E is proven, but no reviewed QA-005 mechanic binding exists for the pure-movement route.

Do not repeat the OWA-001 investigation and do not invent a mechanic ID to make the route certifiable.

## Next bounded task: OWA-002

The next agent should:

1. revalidate current `main`, this programme queue and active ownership;
2. create exactly one OWA-002 active task, branch and draft PR;
3. read only the OWA-001 campaign contract/manifest plus factual renderer and QA-005/006/016 evidence required for visualization;
4. reuse the existing factual renderer;
5. keep formal certification, freshness, Physical E2E and blockers as independent evidence-linked overlays;
6. show the pilot as C0 with current route evidence and separate Physical E2E proof, not as a green/certified mechanic;
7. keep generated renders and campaign outputs outside Git.

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
- Do not promote the OWA-001 retained successful walk into QA-005 mechanic coverage or QA-006 C5.

## Open questions

- Which existing factual renderer overlay surfaces best preserve the four independent OWA-001 facts for OWA-002 without introducing a composite health score?
- OWA-003 package scope must be re-derived from the TCR formats that are actually stable and merged at that time.
