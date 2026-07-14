---
task_id: CAN-20260712-the-beginning-otbm-audit
status: completed
agent: "GPT-5.6 Thinking"
branch: docs/the-beginning-otbm-audit
base_branch: main
created: 2026-07-12
updated: 2026-07-14T18:56:00+02:00
last_verified_commit: "dfa535cbfdcb14a6fe4f19880a1281016d35b4c9"
risk: low
related_pr: "#204"
depends_on:
  - "Merged OTBM item/mechanic audit"
  - "Merged OTBM script-resolution audit #104"
  - "Merged factual OTBM renderer / HD pipeline #154 and #161"
blocks: []
owned_paths:
  - docs/ai-agent/THE_BEGINNING_OTBM_AUDIT.md
  - docs/agents/tasks/archive/CAN-20260712-the-beginning-otbm-audit.md
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

Produce an evidence-first audit of The Beginning quest against the supplied real OTBM, real client assets, active Canary Lua/XML/NPC files and companion spawn XML without modifying the map or building replacement tooling.

# Delivered result

PR #204 merged the documentation-only audit as commit `dfa535cbfdcb14a6fe4f19880a1281016d35b4c9`.

The audit recorded:

- map SHA-256 `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2`;
- asset catalogue SHA-256 `93ea5888174ef44b352d7c2b1f8061573a4a260bfaba4b7ec32ea836b9e411ab`;
- appearances SHA-256 `aa44a154f30c7ed59acc25f246286396e4043851ef0b54ef3cf3951e46d1ce50`;
- zero quest-scoped script conflicts in the audited resolver snapshot;
- factual renders from the real OTBM and real assets, with no AI-generated map imagery;
- no `.otbm`, item, asset, Lua/XML/NPC, spawn, engine or production configuration changes.

# Post-merge correction discovered during handoff

The merged report is **stale in one material finding**: it lists Carlos outfit/trade flow as an outstanding confirmed defect, but PR #157 was already merged as commit `813a2ce39daced46802e6801e4abd275709b8672`.

Current `data-otservbr-global/npc/carlos.lua` confirms that:

- `outfit` reuses the normal stage-2 transition;
- trade opening uses the current tutorial trade states;
- successful sale of meat `3577` or ham `3582` advances both Carlos storages from stage 6 to 7;
- the existing shop runtime remains responsible for payment and item removal.

Therefore Carlos must be removed from the report's outstanding-defect list in a corrective documentation PR. The remaining findings must be revalidated against then-current `main` before implementation.

# Findings that still require current-main revalidation

- Santiago `easy` persistence parity;
- rope-success hint state 22;
- four AID `50999` terminal-border placements and their exact crossing contract;
- advertised `skip tutorial` without an active current contract;
- optional cockroach kill/chase/corpse tutorial events;
- static cart branch, extra dead trees and two `0,0,0` teleport attributes.

Do not promote any `map-only`, `script-only` or `unresolved` item to handled without fresh evidence from the existing resolver, OTBM audit and—where movement is involved—real-asset render plus live runtime traces.

# Validation history

The validated report head `12d5860530a7792c04872bc35ace693f407cfc60` passed:

- CI run 1076;
- AI Agent Tools run 494;
- Agent Task Ownership run 45.

A later task-status-only head ran AI Agent Tools 508 and Agent Task Ownership 68 successfully. CI run 1106 was cancelled during Linux build and must not be recorded as passed.

# Completion

- Final status: completed, with post-merge documentation correction required
- PR: #204
- Merge commit: `dfa535cbfdcb14a6fe4f19880a1281016d35b4c9`
- OTBM changed: no
- Runtime gameplay changed: no
- Archived at: 2026-07-14T18:56:00+02:00
