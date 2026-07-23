---
task_id: CAN-20260723-owa-002-factual-certification-coverage-map
program_id: CAN-PROGRAM-OTBM-WORLD-ASSURANCE-OPERATIONS
coordination_id: OWA-002
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/owa-002-factual-certification-coverage-map-20260723
base_branch: main
created: 2026-07-23T18:22:48+02:00
updated: 2026-07-23T18:52:00+02:00
last_verified_commit: "96b394a60e5ae9ba3d71119e28c2d9dc5e488c02"
risk: medium
related_issue: ""
related_pr: "817"
depends_on:
  - "OWA-001 feature PR #801 and lifecycle PR #810"
  - "existing factual OTBM renderer tools/ai-agent/otbm_renderer.py:render_region"
  - "canary-otbm-world-assurance-campaign-v1"
blocks:
  - "OWA-002 lifecycle closure and programme queue advance"
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260723-owa-002-factual-certification-coverage-map.md
    - docs/ai-agent/OTBM_WORLD_ASSURANCE_MAP.md
    - docs/ai-agent/OTBM_WORLD_ASSURANCE_MAP.schema.json
    - tools/ai-agent/otbm_world_assurance_map.py
    - tools/ai-agent/otbm_world_assurance_map_tool.py
    - tools/ai-agent/test_otbm_world_assurance_map.py
    - tools/ai-agent/test_otbm_world_assurance_map_output_safety.py
    - tools/ai-agent/test_otbm_world_assurance_map_schema.py
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - AGENTS.md
    - docs/agents/REPOSITORY_MAP.md
    - docs/agents/CONTEXT_ROUTING.md
    - docs/agents/programs/OTBM_WORLD_ASSURANCE_OPERATIONS_PROGRAM.md
    - docs/ai-agent/OTBM_WORLD_ASSURANCE_OPERATIONS_ROADMAP.md
    - docs/ai-agent/OTBM_WORLD_ASSURANCE_CAMPAIGN.md
    - docs/ai-agent/OTBM_WORLD_ASSURANCE_CAMPAIGN.schema.json
    - docs/ai-agent/OTBM_WORLD_ASSURANCE_CAMPAIGN_TARGETS.json
    - tools/ai-agent/otbm_world_assurance_campaign.py
    - tools/ai-agent/otbm_renderer.py
    - tools/ai-agent/otbm_render_tool.py
    - tools/ai-agent/otbm_semantic_diff_render.py
    - tools/ai-agent/otbm_geometry_audit_render.py
cross_repo_tasks: []
---

# Goal

Implement `OWA-002 — Factual Certification and Coverage Map` as a bounded deterministic visualization layer over the exact OWA-001 campaign report while reusing the existing factual OTBM renderer as the only map-image renderer.

The first supported target is the reviewed OWA-001 landmark route. The visualization must keep four proof dimensions visibly separate:

1. formal QA-006 certification level;
2. QA-005 coverage dimensions;
3. QA-016 freshness;
4. retained route-level Physical E2E state.

Blockers remain explicit and must never be collapsed into a single green/red health score.

# Implementation boundary

The package may:

- consume `canary-otbm-world-assurance-campaign-v1`;
- verify exact campaign report integrity and source-map provenance;
- reuse `tools/ai-agent/otbm_renderer.py:render_region` for the base map image;
- generate deterministic evidence-linked SVG annotations and a machine-readable visualization manifest;
- render reviewed target bounds and exact reviewed endpoint markers only when present in campaign evidence;
- generate all PNG/SVG/manifests under caller-selected external artifact paths.

The package must not:

- parse OTBM independently;
- build a World Index;
- resolve scripts;
- run Reachability/BFS or invent route geometry;
- rerun QA-005/QA-006/QA-016/QA-018;
- run Physical E2E;
- treat route-level Physical E2E as mechanic coverage or C5 certification;
- infer semantics from sprites or visual proximity;
- create a second map renderer;
- mutate maps, assets or datapacks;
- commit generated renders, manifests, `.otbm`, `.widx` or proprietary assets.

# Planned public contract

- `canary-otbm-world-assurance-map-v1` — deterministic manifest describing the existing-renderer base image, spatial annotations, evidence references, proof-dimension panels and generated external artifacts.

Every visible annotation/panel must carry at least one exact evidence reference of the form `campaign:<report-sha256>#<json-pointer>`.

# Acceptance criteria

- [x] exact OWA-001 campaign report hash is validated fail-closed;
- [x] exact source map SHA-256 is validated before base render execution;
- [x] existing `render_region()` is the only map-image renderer used;
- [x] reviewed routing bounds and endpoints are visualized without inferring the actual path;
- [x] C0, QA-005 not-evaluated, QA-016 current, Physical E2E proven and blockers remain separate visible facts;
- [x] every visible overlay element has exact evidence references;
- [x] stale/blocked/malformed or provenance-mismatched evidence fails closed rather than being upgraded;
- [x] output paths use create-new semantics by default, support explicit atomic overwrite, reject symlinks and input/output collisions;
- [x] deterministic manifest/SVG output for identical inputs;
- [x] focused tests and schema validation pass locally (20 tests);
- [x] generated render/SVG/manifest artifacts remain outside Git;
- [ ] `MODULE_CATALOG.md` and `CHANGELOG.md` are updated only for the delivered reusable/public interface;
- [ ] final PR diff contains no `.otbm`, `.widx`, binary assets, generated renders or unrelated changes;
- [ ] exact final head passes required GitHub checks before merge.

# Preflight evidence

- current `main` observed at task start: `930d7553e87c66e9e00a68c640c86f3d22d16e88`;
- OWA-001 feature PR #801: merged;
- OWA-001 lifecycle PR #810: merged;
- programme queue marks OWA-002 `ready for next bounded task`;
- no existing OWA-002 PR/task found;
- OWA-005 lifecycle PR #816 is lifecycle-only, has since merged, and did not own the OWA-002 exclusive implementation paths;
- existing factual renderer is `tools/ai-agent/otbm_renderer.py:render_region`;
- existing Semantic Diff/Geometry render helpers already model renderer reuse without creating a second OTBM parser/renderer.

# Reuse decision

`PROVEN`: reuse the existing factual renderer for the base map image.

`REJECTED`: extending OWA-002 with a second OTBM parser, pathfinder, route reconstruction or independent sprite/map rendering is unnecessary and forbidden by programme policy.

`DERIVED`: a deterministic SVG annotation layer over the renderer-produced base PNG is a presentation/annotation surface, not a second map renderer, provided it never draws or reconstructs map terrain and every shape is sourced from exact reviewed campaign coordinates/bounds.

## Context checkpoint

### Proven

- OWA-001 exact pilot state is C0 / QA-005 not-evaluated / QA-016 current / route-level Physical E2E proven / blocked by explicit QA-005 and QA-006 blockers.
- The OWA-001 campaign report contains reviewed definition bounds/endpoints and exact source-map provenance.
- Existing factual map rendering is owned by `otbm_renderer.py:render_region`.
- OWA-002 implementation is published on PR #817 with deterministic plan/materialization, CLI, schema, documentation and 20 focused local tests.
- Exact evidence validation now requires the complete nine-dimension QA-005 shape, internally consistent QA-016 freshness, current freshness for `physicalE2e.state=proven`, exact renderer output bounds/dimensions/padding and valid renderer asset/appearance SHA-256 metadata.
- Relative `--map` and `--assets` inputs are confined under `--artifact-root`; exact artifact-root and output symlinks fail closed.

### Rejected hypotheses

- Do not draw a reconstructed 59-edge route: the campaign report does not contain the full route path and OWA-002 must not rerun BFS or infer path geometry.
- Do not encode a composite health score or use colour as certification proof.

### Next action

Update narrow discovery records, inspect exact PR diff and current-main overlap, then validate GitHub Actions and fix any exact-head failures before the final gate.
