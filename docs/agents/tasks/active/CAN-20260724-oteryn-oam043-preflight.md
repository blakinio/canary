---
task_id: CAN-20260724-oteryn-oam043-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-043
status: review
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-043-post-preflight-handoff
base_branch: main
created: 2026-07-24
updated: 2026-07-24
last_verified_commit: "c5abe56e568e4ee72814846a32b0c2ae4e4853d9"
risk: high
related_issue: ""
related_pr: "872"
depends_on:
  - OAM-042 formally complete
  - canonical otbm-tooling resolved by OAM-040
  - canonical player-persistence completed by OAM-004
  - canonical spawns completed by OAM-041
  - canonical npcs completed by OAM-042
blocks:
  - OAM-043 target proof and final disposition
  - OAM-044 start
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260724-oteryn-oam043-preflight.md
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/real-tibia/registry/modules/quests.yaml
    - docs/ai-agent/QUEST_MAP_VALIDATION.md
    - docs/ai-agent/OTBM_SCRIPT_RESOLUTION.md
    - tools/ai-agent/quest_map_validation.py
    - tools/ai-agent/quest_map_validation_tool.py
    - tools/ai-agent/otbm_script_resolution.py
    - tools/ai-agent/otbm_script_resolution_tool.py
    - tools/ai-agent/otbm_world_index.py
modules_touched:
  - oteryn-architecture-migration
  - quests
cross_repo_tasks: []
---

# OAM-043 Fresh Preflight

## Selected package

`quests` is the selected dependency-valid OAM-043 canonical package.

Preflight disposition: `REVALIDATE`.

No leading `REUSE`, `ADAPT` or `REWRITE` hypothesis is accepted before the target proof pins the exact target/upstream/legacy quest inventories, storage references and map-mechanic correlations. OAM-042 deliberately queued `quests` behind the narrower NPC boundary; that prerequisite is now formally complete.

Canonical `quests` is a world-content package owning quest scripts and storage transitions, AID/UID/item/position mechanics, rewards, access and NPC/spawn/map dependencies. It excludes whole-world parity claims and forbids treating unresolved dynamic handlers as implemented. Its hard dependencies are canonical `otbm-tooling` and `player-persistence`; both are formally completed. Interacting `npcs`, `spawns`, `houses` and `achievements` packages are also completed, so the package is dependency-valid.

This preflight performs no target, runtime, datapack, map, binary, protocol, client, schema or deployment mutation. Final disposition requires a separately ordered Otheryn target proof on exact pinned baselines.

## Required target-proof phases

1. **Exact source inventory**
   - pin target, current-upstream and legacy quest roots;
   - compare complete file/path inventories and exact blobs;
   - classify target-only, upstream-only, legacy-only and divergent files without bulk-copying.

2. **Source evidence**
   - reuse `canary-quest-map-evidence-v1` for explicit selected quest sets;
   - inventory AID, UID, item, position, teleport and storage evidence with exact source lines and hashes;
   - retain every dynamic expression as unresolved.

3. **Map and handler correlation**
   - reuse the Unified OTBM World Index and OTBM script-resolution report;
   - classify confirmed, map-only, script-only, unresolved and conflicting mechanics;
   - never promote a reviewed unresolved identifier to handled.

4. **Storage and progression review**
   - inventory storage reads/writes and canonical symbolic paths;
   - prove stage ordering, reachable transitions, reward/access gates and scope only where source or runtime evidence supports them;
   - do not infer a transition graph from lexical storage presence alone.

5. **Bounded semantic/runtime proof**
   - choose representative quest families only after the full inventory identifies stable ownership boundaries;
   - prove actions, rewards, access, teleports, NPC/spawn dependencies and persistence handoff;
   - require a bounded physical-client/runtime proof only when source/map evidence cannot prove the selected behavior.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T12:34:00+02:00
head: c5abe56e568e4ee72814846a32b0c2ae4e4853d9
branch: dudantas/oam-043-post-preflight-handoff
pr: 872
status: validating
context_routes:
  - agent-governance
  - otbm
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260724-oteryn-oam043-preflight.md
proven:
  - Canary OAM-043 preflight PR 866 selected quests with disposition REVALIDATE and merged as df7abb0cfe4b05ed11da7b3a6a0dcddbefb62375.
  - PR 866 final head 8ea49613bc37b152726d0afaf291ecaa450ee853 passed CI and Agent Task Ownership checks with no review comments or unresolved threads.
  - Current Canary main is b1d24ec362ec52652886f6be6129234ff44e7d4d, contains the merged quests preflight, and duplicate draft PR 867 was closed as superseded without merge.
  - Current pinned baselines are Otheryn 3a37f3d5e4c01ddf4469f1c71461c40ca749142f, upstream Canary 7323503b3dc61ed86bf1f04a611b2d0aec64b35a, and maintained OTClient b3bcea2a95959bb4e92cc0b80cd49f36b63699b2.
  - Canonical quests registry blob is 61f3f8249a1b7b2efef956cbcec2b78da9dafc08 and declares category world-content.
  - Canonical quests owns quest source, storage transitions, AID/UID/item/position mechanics, rewards, access and NPC/spawn/map dependencies.
  - Canonical quests depends on otbm-tooling and player-persistence; OAM-040 and OAM-004 formally completed those dependencies.
  - Interacting npcs, spawns, houses and achievements packages are completed by OAM-042, OAM-041, OAM-027 and OAM-012.
  - The existing quest map validator reuses otbm_script_resolution and the Unified OTBM World Index rather than implementing another registration or OTBM parser.
  - The validator records source file SHA-256, exact source lines, AID/UID/item/position/teleport/storage evidence and unresolved dynamic expressions.
  - The validator requires explicit include globs and never assumes every Lua file belongs to one quest.
  - The optional script-resolution input preserves reviewed unresolved identifiers as unresolved and detects competing handlers.
  - The existing resolver scans only active data and data-otservbr-global roots by default and does not mix data-canary unless explicitly requested.
  - Canary PR 789 is documentation/design-only and does not mutate quest runtime, datapack, map, client or this task path.
  - Canonical quests declares no direct maintained-client path; OTClient mutation is not implied by this preflight.
derived:
  - quests is the dependency-valid package explicitly queued after completion of the narrower npcs boundary.
  - Existing external Canary evidence infrastructure is sufficient for the map, identifier and static-handler phases and must be reused rather than copied into Otheryn.
  - The breadth of quest storages, rewards and access semantics makes a final disposition unsafe before complete inventory and bounded semantic proof.
unknown:
  - Exact current Otheryn, current-upstream and legacy quest file inventories and blob relationships.
  - Exact number and classification of quest-owned AID, UID, item, position, teleport, storage and dynamic-expression findings.
  - Whether target-local source-contract tests are sufficient for every selected quest family or bounded runtime/physical-client proof is required.
  - Whether any target-local quest defect requires ADAPT or whether the complete package supports REUSE.
  - Whether a canonical storage-transition graph implementation already exists outside the reviewed quest validator; no such module was proven during preflight.
conflicts: []
first_failure:
  marker: active task frontmatter status
  evidence: PR 872 Agent Task Ownership runs rejected active and validating as frontmatter statuses; this final checkpoint restores accepted status review while retaining checkpoint status validating.
rejected_hypotheses:
  - Finalize quests as REUSE from target/upstream path presence or blob identity alone.
  - Build a second OTBM parser, map scanner, registration resolver or quest-map validator.
  - Treat lexical storage reads/writes as a proven progression graph.
  - Resolve dynamic registrations, computed storages, generated rewards or runtime-loaded tables by guessing.
  - Treat PR 789 design direction as current runtime evidence.
  - Start target mutation before exact inventory and evidence classification.
  - Continue duplicate PR 867 after canonical PR 866 merged the selected package preflight.
changed_paths:
  - docs/agents/tasks/active/CAN-20260724-oteryn-oam043-preflight.md
validation:
  - command: live OAM-043 preflight merge and final-head verification
    result: PASS
    evidence: PR 866 merged as df7abb0cfe4b05ed11da7b3a6a0dcddbefb62375 after successful CI and Agent Task Ownership on head 8ea49613bc37b152726d0afaf291ecaa450ee853.
  - command: duplicate ownership reconciliation
    result: PASS
    evidence: overlapping draft PR 867 was commented and closed without merge; canonical main retains PR 866 content.
  - command: existing quest/OTBM evidence-contract review
    result: PASS
    evidence: quest map validation reuses canonical script resolution and world index, requires explicit source selection and preserves unresolved evidence fail-closed.
  - command: PR 872 final-head ownership and CI
    result: FAIL
    evidence: CI passed on c5abe56e568e4ee72814846a32b0c2ae4e4853d9; Agent Task Ownership rejected only the frontmatter status and must rerun on this corrected final head.
blockers: []
next_action: Require exact-head Agent Task Ownership and CI on PR 872, audit comments, reviews, threads and Canary-main drift, then squash-merge with the expected head.
```
