---
task_id: CAN-20260723-owa-002-factual-certification-coverage-map
program_id: CAN-PROGRAM-OTBM-WORLD-ASSURANCE-OPERATIONS
coordination_id: OWA-002
status: completed
agent: "GPT-5.6 Thinking"
branch: feat/owa-002-factual-certification-coverage-map-20260723
base_branch: main
created: 2026-07-23T18:22:48+02:00
updated: 2026-07-23T19:44:52+02:00
last_verified_commit: "077ad5753ac9aedf4a1c3b2380876e0fc2926989"
risk: medium
related_issue: ""
related_pr: "817"
depends_on:
  - "OWA-001 feature PR #801 and lifecycle PR #810"
  - "existing factual OTBM renderer tools/ai-agent/otbm_renderer.py:render_region"
  - "canary-otbm-world-assurance-campaign-v1"
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/archive/CAN-20260723-owa-002-factual-certification-coverage-map.md
  shared:
    - docs/agents/programs/OTBM_WORLD_ASSURANCE_OPERATIONS_PROGRAM.md
  read_only:
    - docs/ai-agent/OTBM_WORLD_ASSURANCE_MAP.md
    - docs/ai-agent/OTBM_WORLD_ASSURANCE_MAP.schema.json
    - tools/ai-agent/otbm_world_assurance_map.py
    - tools/ai-agent/otbm_world_assurance_map_tool.py
cross_repo_tasks: []
---

# Completion summary

`OWA-002 — Factual Certification and Coverage Map` is complete and merged by PR #817.

Feature merge:

- PR: `#817` — `feat(otbm): add factual world assurance coverage map`;
- final feature head: `2db8a8fab9c6c4991a3956e88b6a5aa9f829e977`;
- merge commit: `077ad5753ac9aedf4a1c3b2380876e0fc2926989`;
- merged at: `2026-07-23T17:44:52Z`;
- changed files: 10;
- generated `.otbm`, `.widx`, PNG/SVG render artifacts and proprietary client assets: none committed.

# Delivered public contract

- `canary-otbm-world-assurance-map-v1`;
- schema: `docs/ai-agent/OTBM_WORLD_ASSURANCE_MAP.schema.json`;
- implementation: `tools/ai-agent/otbm_world_assurance_map.py`;
- CLI: `tools/ai-agent/otbm_world_assurance_map_tool.py`;
- durable documentation: `docs/ai-agent/OTBM_WORLD_ASSURANCE_MAP.md`.

The package consumes exact `canary-otbm-world-assurance-campaign-v1` evidence and reuses `tools/ai-agent/otbm_renderer.py:render_region` as the sole map-image renderer.

# Exact proof boundary preserved

For the OWA-001 pilot, the factual visualization keeps these facts independent:

1. QA-006 formal certification remains `C0_NOT_EVALUATED`;
2. all nine QA-005 coverage dimensions remain `not-evaluated` for the pure-movement route;
3. QA-016 static-route and retained route-level Physical E2E freshness remain `current`;
4. retained route-level Physical E2E remains `proven` but is not promoted to QA-005 mechanic coverage or QA-006 C5;
5. the three explicit QA-005/QA-006 blockers remain visible.

No composite health score is produced and colour/presentation state is never proof.

# Delivered behavior

- validates the exact campaign canonical `reportSha256` and records the raw campaign-file SHA-256;
- requires the complete nine-dimension QA-005 shape;
- validates internal QA-016 aggregate/dimension consistency;
- requires current freshness when retained Physical E2E is represented as proven;
- validates exact source-map SHA-256 before invoking the existing renderer;
- validates renderer-reported map hash, asset/appearance hashes, bounds, dimensions and zero padding;
- renders only reviewed routing bounds and exact reviewed origin/destination markers;
- does not reconstruct, infer or pathfind the 59-edge route geometry;
- adds separate evidence-linked panels for QA-006, QA-005, QA-016, retained Physical E2E and blockers;
- every visible annotation/panel carries an exact `campaign:<report-sha256>#/targets/<index>/...` evidence reference;
- confines relative map/assets/output paths under the caller-selected artifact root;
- rejects artifact-root/output symlinks and unsafe collisions;
- uses create-new/no-clobber output by default and explicit atomic overwrite;
- keeps generated base PNG, SVG overlays and visualization manifests outside Git.

# Hard boundaries

OWA-002 does not:

- parse OTBM independently;
- build a World Index;
- resolve scripts;
- run Reachability/BFS or reconstruct route geometry;
- rerun QA-005, QA-006, QA-016 or QA-018;
- execute Physical E2E;
- assign certification independently;
- create a second factual renderer;
- infer semantics from sprites or visual proximity;
- mutate maps, assets or datapacks;
- authorize merge, release or deployment from presentation state.

# Validation evidence

Focused local validation:

- `20` focused OWA-002 tests passed after evidence and path-confinement hardening;
- Python module compilation passed through `py_compile` during implementation validation.

Prefinal exact-head validation on `acaa2a53ba2f7eba1a11a89ab873e559a81126cb`:

- Agent Task Ownership run `30027918958`: success;
- CI run `30027919267`: success;
- OTBM Map Tools run `30027918881`: success;
- AI Agent Tools run `30027918998`: success.

Final exact-head validation on `2db8a8fab9c6c4991a3956e88b6a5aa9f829e977` after applying `ci:final-gate` before the final checkpoint commit:

- Agent Task Ownership run `30028140542`: success;
- OTBM Map Tools run `30028140468`: success;
- AI Agent Tools run `30028140419`: success;
- full final-gate CI rerun `30029162426` / CI `#5141`: success.

The first full-CI attempt on the same final SHA stalled in environment setup at `Setup Lua` before checkout/tests. The PR was safely toggled draft -> ready to retrigger CI without changing the branch or SHA. CI `#5141` then completed the required full matrix successfully. No commit was made after the final checkpoint.

# Scope audit

The merged feature diff contains exactly ten declared text paths:

- `docs/agents/CHANGELOG.md`;
- `docs/agents/MODULE_CATALOG.md`;
- `docs/agents/tasks/active/CAN-20260723-owa-002-factual-certification-coverage-map.md`;
- `docs/ai-agent/OTBM_WORLD_ASSURANCE_MAP.md`;
- `docs/ai-agent/OTBM_WORLD_ASSURANCE_MAP.schema.json`;
- `tools/ai-agent/otbm_world_assurance_map.py`;
- `tools/ai-agent/otbm_world_assurance_map_tool.py`;
- `tools/ai-agent/test_otbm_world_assurance_map.py`;
- `tools/ai-agent/test_otbm_world_assurance_map_output_safety.py`;
- `tools/ai-agent/test_otbm_world_assurance_map_schema.py`.

`MODULE_CATALOG.md` and `CHANGELOG.md` each received one narrow public-interface/discovery entry. No feature-owned map, World Index, binary asset, generated render or proprietary asset entered Git.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T17:44:52Z
head: 077ad5753ac9aedf4a1c3b2380876e0fc2926989
branch: main
pr: 817
status: completed
context_routes:
  - agent-governance
  - otbm
owned_paths:
  - docs/agents/tasks/archive/CAN-20260723-owa-002-factual-certification-coverage-map.md
  - docs/agents/programs/OTBM_WORLD_ASSURANCE_OPERATIONS_PROGRAM.md
proven:
  - OWA-002 feature PR 817 merged with merge commit 077ad5753ac9aedf4a1c3b2380876e0fc2926989.
  - Final feature head 2db8a8fab9c6c4991a3956e88b6a5aa9f829e977 passed Agent Task Ownership, OTBM Map Tools, AI Agent Tools and full ci:final-gate CI 5141.
  - canary-otbm-world-assurance-map-v1 preserves QA-006, QA-005, QA-016, retained Physical E2E and blockers as independent evidence-linked surfaces.
  - The canonical factual renderer remains the only map-image renderer and no route geometry is inferred.
derived:
  - OWA-004 is the next executable bounded package only after a fresh main/ownership preflight because OWA-003 still depends on stable TCR parity/drift producers.
unknown:
  - Exact OWA-004 implementation shape until its own task revalidates current QA-018 and failure-triage contracts.
conflicts:
  - none
first_failure:
  marker: Agent Task Ownership checkpoint format during feature implementation
  evidence: run 30026881377 failed because the task checkpoint was not a fenced YAML block; the contract was repaired and later ownership runs passed.
rejected_hypotheses:
  - Reconstruct the 59-edge route for visualization.
  - Collapse certification, coverage, freshness and Physical E2E into one score.
changed_paths:
  - docs/agents/tasks/archive/CAN-20260723-owa-002-factual-certification-coverage-map.md
  - docs/agents/tasks/active/CAN-20260723-owa-002-factual-certification-coverage-map.md
  - docs/agents/programs/OTBM_WORLD_ASSURANCE_OPERATIONS_PROGRAM.md
validation:
  - command: GitHub Actions CI run 30029162426
    result: PASS
    evidence: Full ci:final-gate matrix passed on exact final feature head 2db8a8fab9c6c4991a3956e88b6a5aa9f829e977.
blockers: []
next_action: Lifecycle-close this task, advance the authoritative OWA programme queue, then revalidate current main and ownership before claiming the next bounded package.
```
