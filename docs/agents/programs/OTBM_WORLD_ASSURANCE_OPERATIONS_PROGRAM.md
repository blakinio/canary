---
program_id: CAN-PROGRAM-OTBM-WORLD-ASSURANCE-OPERATIONS
name: OTBM World Assurance Operations
status: active
owner: OTBM analysis tooling / world assurance operations
created: 2026-07-23T14:25:00+02:00
updated: 2026-07-23T19:44:52+02:00
last_verified_commit: "077ad5753ac9aedf4a1c3b2380876e0fc2926989"
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

No active OWA task is claimed after OWA-002 lifecycle closure.

OWA-001, OWA-002 and OWA-005 are merged and archived. A future agent must perform a fresh `main`, ownership and open-PR preflight before claiming the next bounded package.

# Queue

| ID | Scope | Status | Dependencies | Risk | Exact next action |
|---|---|---|---|---|---|
| OWA-001 | Real-World Certification Campaign | completed via #801 | QA-005/006/016/018 + exact reviewed Thais route evidence | medium | Preserve the exact delivered state: QA-005 not-evaluated, QA-006 C0, QA-016 current, route-level Physical E2E proven, three explicit QA-005/006 blockers. |
| OWA-002 | Factual Certification and Coverage Map | completed via #817 | OWA-001 reviewed manifest/campaign semantics + factual renderer | medium | Preserve `canary-otbm-world-assurance-map-v1`: factual renderer reuse, reviewed bounds/endpoints only, separate QA-006/QA-005/QA-016/Physical-E2E/blocker surfaces, no inferred route geometry or composite health score. |
| OWA-003 | TCR-to-QA Drift and Freshness Integration | blocked on stable TCR parity/drift outputs | stable owning TCR outputs + QA-008/016/002/007 | medium | Re-derive scope from the stable merged TCR producer contracts only after the required parity/drift outputs exist; OWA consumes them but never parses client reference inputs. |
| OWA-004 | Runtime Incident to OTBM Evidence Bridge | ready for next bounded task | QA-018 + existing route/failure-triage evidence | medium | Revalidate current QA-018 and failure-triage contracts, then return compact OTBM static context for explicit incident selectors while keeping runtime diagnosis and E2E ownership downstream. |
| OWA-005 | QA Contract Hardening and Adversarial Fixtures | completed via #802; lifecycle closed via #816 | delivered QA contracts | medium | Preserve the merged deterministic adversarial/fail-closed contract coverage; do not duplicate canonical validators. |
| OWA-006 | Continuous Assurance Operational Adoption | planned | OWA-001 + QA-002/007 + CI/release governance | high | Integrate existing assurance evidence into one bounded real map/candidate change path without suppressing unrelated suites or authorizing deployment. |

# Sequencing

1. **OWA-001** — completed: the first reviewed campaign target and fail-closed proof boundary are established.
2. **OWA-002** — completed: factual evidence-linked visualization is delivered through the existing renderer.
3. **OWA-005** — completed independently: adversarial/fail-closed QA contract hardening is merged and lifecycle-closed.
4. **OWA-004** — next bounded package: expose incident-oriented static context through existing QA-018 evidence without taking runtime/E2E ownership.
5. **OWA-003** — begin only after stable owning TCR parity/drift outputs and explicit producer/consumer contracts exist.
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

Delivered by PR #817.

The package adds `canary-otbm-world-assurance-map-v1` as a deterministic evidence-linked visualization over exact `canary-otbm-world-assurance-campaign-v1` evidence while reusing `tools/ai-agent/otbm_renderer.py:render_region` as the sole map-image renderer.

The delivered visualization preserves these facts as independent surfaces:

1. formal QA-006 certification;
2. all nine QA-005 coverage dimensions;
3. QA-016 freshness and its dimensions;
4. retained route-level Physical E2E state and proof boundary;
5. explicit blockers.

For the OWA-001 pilot this means C0, QA-005 `not-evaluated`, current static/Physical-E2E freshness, proven route-level Physical E2E and the three explicit blockers remain visibly separate. The successful walk is not promoted to mechanic coverage or C5.

Visible spatial overlays are limited to exact reviewed routing bounds and exact reviewed origin/destination markers. The package does not reconstruct or infer the route path, rerun Reachability/BFS, create a second renderer, rerun QA validators/E2E, mutate maps/assets or produce a composite health score. Every visible annotation/panel carries an exact campaign JSON-pointer evidence reference. Generated PNG/SVG/manifests remain external.

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

Current gate: a stable package/reference manifest alone is insufficient. OWA-003 remains blocked until the owning TCR programme delivers the required stable parity/drift producer outputs.

## OWA-004 — Runtime Incident to OTBM Evidence Bridge

Accept explicit selectors such as `x,y,z`, transition ID, interaction ID, landmark ID or route/preflight reference and return only compatible existing OTBM evidence. It must not become a general log parser, runtime root-cause engine, E2E executor or `NEXT_ACTION` generator.

OWA-004 should reuse QA-018 as the compact evidence transport boundary and existing route/failure-triage evidence as downstream-owned runtime context. Its exact selector and composition contract must be revalidated from current `main` at task start rather than inferred from this programme record.

## OWA-005 — QA Contract Hardening and Adversarial Fixtures

Delivered by implementation PR #802; lifecycle closed by PR #816.

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
- OWA-002 is complete and must continue to represent that C0 state, independent QA-005 dimensions, freshness, retained Physical E2E and blockers without promotion or collapse into a score.
- OWA-003 remains dependency-gated by stable owning TCR parity/drift outputs and must be re-derived from the actual merged producer contracts at task start.
- OWA-004 is ready for a fresh bounded-task preflight; its runtime diagnosis and Physical E2E inputs remain owned downstream.
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
- Evidence-linked factual visualization does not convert presentation state into certification, runtime proof or release authority.

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

## OWA-002 delivered state

Start from the archived task:

`docs/agents/tasks/archive/CAN-20260723-owa-002-factual-certification-coverage-map.md`

and the durable visualization documentation:

`docs/ai-agent/OTBM_WORLD_ASSURANCE_MAP.md`.

PR #817 delivered the deterministic `canary-otbm-world-assurance-map-v1` contract. Preserve the existing factual renderer as the only map-image renderer, do not infer route geometry, and keep certification, coverage, freshness, retained Physical E2E and blockers as independent evidence-linked facts.

## Next bounded task: OWA-004

The next agent should:

1. revalidate current `main`, this programme queue, active ownership and open PRs;
2. confirm OWA-003 is still blocked by the actual current TCR producer state rather than by this handoff alone;
3. create exactly one OWA-004 active task, branch and draft PR if no ownership conflict exists;
4. read only the current QA-018 Evidence Gateway contract plus exact route/preflight/failure-triage contracts required for the selected incident bridge;
5. accept explicit reviewed selectors and return compact compatible existing OTBM evidence;
6. keep runtime diagnosis, failure classification and Physical E2E execution owned by their existing downstream systems;
7. do not become a log parser, root-cause engine, pathfinder, E2E runner or `NEXT_ACTION` generator;
8. keep generated evidence bundles outside Git.

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
- Do not reconstruct OWA-002 route geometry that was intentionally left unrepresented by exact campaign evidence.

## Open questions

- OWA-003 package scope must be re-derived from the TCR formats that are actually stable and merged at that time.
- OWA-004 must select its exact supported incident selector set from current QA-018 and downstream failure-triage contracts at task start; this programme record does not authorize a generic log/root-cause interface.
