---
task_id: CAN-20260712-the-beginning-otbm-audit
status: active
agent: "GPT-5.6 Thinking"
branch: docs/the-beginning-otbm-audit
base_branch: main
created: 2026-07-12
updated: 2026-07-12
risk: low
related_pr: ""
depends_on:
  - "Merged OTBM item/mechanic audit"
  - "Merged OTBM script-resolution audit #104"
  - "Merged factual OTBM renderer / HD pipeline #154 and #161"
blocks:
  - "The Beginning repair plan"
  - "Further The Beginning gameplay fixes"
owned_paths:
  - docs/ai-agent/THE_BEGINNING_OTBM_AUDIT.md
  - docs/agents/tasks/active/CAN-20260712-the-beginning-otbm-audit.md
modules_touched:
  - World Semantic Review
  - Existing OTBM audit and rendering outputs (read-only use only)
reuses:
  - tools/ai-agent/otbm_item_audit_tool.py
  - tools/ai-agent/otbm_script_resolution_tool.py
  - tools/ai-agent/otbm_map_tool.py
  - tools/ai-agent/otbm_render_tool.py
cross_repo_tasks: []
---

# Goal

Produce a complete evidence-first audit of The Beginning quest against the supplied real OTBM, matching real client assets, active Canary Lua/XML/NPC files and companion spawn XML. The audit must precede any new repair work.

# Hard boundaries

- Do not create another OTBM parser, resolver or renderer.
- Do not use generated AI imagery.
- Do not edit the OTBM, `items.otb`, appearances, sprites, active datapack, NPC, XML, engine or production configuration.
- Generated JSON and PNG artifacts remain under local `artifacts/**` and are not committed.
- Do not classify unresolved identifiers as handled without explicit resolver evidence.
- Use only: `confirmed`, `map-only`, `script-only`, `unresolved`, `conflicting`.

# Inputs

- map SHA-256: `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2`;
- asset catalogue SHA-256: `93ea5888174ef44b352d7c2b1f8061573a4a260bfaba4b7ec32ea836b9e411ab`;
- appearances SHA-256: `aa44a154f30c7ed59acc25f246286396e4043851ef0b54ef3cf3951e46d1ce50`;
- Canary baseline: `32c12436894d3c6c836be238eb6d8733dcc2459f`, with relevant current-main quest files fetched and overlaid exactly for resolver execution.

# Acceptance criteria

- [x] read the mandatory agent/tooling documentation;
- [x] inspect open PRs and avoid overlap with OTBM world-index PR #190;
- [x] verify map and assets hashes;
- [x] export the bounded quest region with the existing map tool;
- [x] rerun the existing script resolver after current-main PR #186 merged;
- [x] generate factual renders of key locations using real assets, with zero missing appearances/sprites;
- [x] verify NPC and monster spawn placements through the existing companion-XML reader;
- [x] verify current Rookgaard town ID from the OTBM town table;
- [ ] publish the complete quest/mission report and classification matrix;
- [ ] publish priorities, regression risk, likely files and required pre-merge tests;
- [ ] create a separate repair-plan task/document only after this report is complete.

# Validation notes

The shell environment cannot resolve GitHub, so it could not clone the latest repository. The audit uses the existing PR #104 tooling source snapshot and overlays the exact current-main files relevant to The Beginning fetched through the GitHub connector. This limitation is recorded explicitly and does not authorize guessing. The map and renderer inputs are the supplied binaries with recorded hashes.
