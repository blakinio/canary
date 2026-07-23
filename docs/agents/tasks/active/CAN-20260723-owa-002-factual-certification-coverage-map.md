---
task_id: CAN-20260723-owa-002-factual-certification-coverage-map
program_id: CAN-PROGRAM-OTBM-WORLD-ASSURANCE-OPERATIONS
coordination_id: OWA-002
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/owa-002-factual-certification-coverage-map-20260723
base_branch: main
created: 2026-07-23T18:22:48+02:00
updated: 2026-07-23T18:54:00+02:00
last_verified_commit: "097a517384a1c5a2a833ebd7e182953e7e184e96"
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

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T16:54:00Z
head: 097a517384a1c5a2a833ebd7e182953e7e184e96
branch: feat/owa-002-factual-certification-coverage-map-20260723
pr: 817
status: implementing
context_routes:
  - agent-governance
  - otbm
owned_paths:
  - docs/agents/tasks/active/CAN-20260723-owa-002-factual-certification-coverage-map.md
  - docs/ai-agent/OTBM_WORLD_ASSURANCE_MAP.md
  - docs/ai-agent/OTBM_WORLD_ASSURANCE_MAP.schema.json
  - tools/ai-agent/otbm_world_assurance_map.py
  - tools/ai-agent/otbm_world_assurance_map_tool.py
  - tools/ai-agent/test_otbm_world_assurance_map.py
  - tools/ai-agent/test_otbm_world_assurance_map_output_safety.py
  - tools/ai-agent/test_otbm_world_assurance_map_schema.py
proven:
  - OWA-001 pilot state is QA-006 C0, QA-005 not-evaluated, QA-016 current, route-level Physical E2E proven, with three explicit QA-005/QA-006 blockers.
  - Existing factual map rendering is owned by tools/ai-agent/otbm_renderer.py:render_region and OWA-002 reuses it as the sole map-image renderer.
  - PR 817 contains deterministic plan/materialization, CLI, schema, documentation and 20 passing focused local tests.
  - Exact evidence validation requires all nine QA-005 dimensions, consistent QA-016 freshness, current freshness for proven Physical E2E and validated renderer bounds/dimensions/padding/hash metadata.
  - Relative map/assets inputs are confined under artifact-root and exact artifact-root/output symlinks fail closed.
derived:
  - A deterministic SVG layer containing only reviewed bounds/endpoints and evidence panels is presentation over the canonical base render, not a second terrain/map renderer.
unknown:
  - Exact final-head CI outcome after checkpoint-schema repair.
  - Final discovery-record diff until MODULE_CATALOG.md and CHANGELOG.md are updated.
conflicts:
  - none
first_failure:
  marker: Agent Task Ownership changed-task checkpoint validation
  evidence: run 30026881377 artifact active-task-ownership reported that Context checkpoint lacked the required fenced YAML block.
rejected_hypotheses:
  - Reconstruct the 59-edge route for visualization: OWA-001 campaign evidence does not contain ordered route geometry and OWA-002 must not rerun BFS.
  - Collapse certification/freshness/coverage/Physical-E2E into one score: programme contract requires them to remain independent.
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-owa-002-factual-certification-coverage-map.md
  - docs/ai-agent/OTBM_WORLD_ASSURANCE_MAP.md
  - docs/ai-agent/OTBM_WORLD_ASSURANCE_MAP.schema.json
  - tools/ai-agent/otbm_world_assurance_map.py
  - tools/ai-agent/otbm_world_assurance_map_tool.py
  - tools/ai-agent/test_otbm_world_assurance_map.py
  - tools/ai-agent/test_otbm_world_assurance_map_output_safety.py
  - tools/ai-agent/test_otbm_world_assurance_map_schema.py
validation:
  - command: PYTHONPATH=tools/ai-agent python -m unittest -v tools/ai-agent/test_otbm_world_assurance_map.py tools/ai-agent/test_otbm_world_assurance_map_output_safety.py tools/ai-agent/test_otbm_world_assurance_map_schema.py
    result: PASS
    evidence: 20 tests passed locally after hardening.
  - command: GitHub Actions CI run 30026881615
    result: PASS
    evidence: CI run 5090 completed successfully on head 097a517384a1c5a2a833ebd7e182953e7e184e96.
  - command: GitHub Actions Agent Task Ownership run 30026881377
    result: FAIL
    evidence: checkpoint section was not a fenced YAML block; this checkpoint commit repairs that contract.
blockers:
  - MODULE_CATALOG.md and CHANGELOG.md discovery updates remain before final gate.
  - Exact final-head required workflows must pass after the checkpoint repair and discovery updates.
next_action: Update the narrow MODULE_CATALOG.md and CHANGELOG.md discovery entries, then run exact-head ownership/OTBM/AI/CI validation and proceed to final gate only if all pass.
```
