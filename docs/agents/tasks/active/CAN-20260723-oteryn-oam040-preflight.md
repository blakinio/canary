---
task_id: CAN-20260723-oteryn-oam040-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
status: ready
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-040-preflight
base_branch: main
created: 2026-07-23
updated: 2026-07-23
last_verified_commit: "f7981992d047b2d718989500ba4a1ef46ec68e3d"
risk: medium
related_issue: ""
related_pr: "790"
depends_on:
  - OAM-039 formally complete
blocks:
  - OAM-040 target disposition proof
  - OAM-041 start
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260723-oteryn-oam040-preflight.md
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/real-tibia/registry/modules/**
    - docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md
modules_touched:
  - oteryn-architecture-migration
  - otbm-tooling
cross_repo_tasks: []
---

# OAM-040 Fresh Preflight

## Selected package

`otbm-tooling` is the selected dependency-valid OAM-040 canonical package.

Preflight disposition: `DO_NOT_MIGRATE candidate`.

Canonical `otbm-tooling` is a dependency-free platform-tooling module whose maintained responsibility is the deterministic OTBM analysis/evidence stack in the Canary legacy laboratory. Its canonical record owns no server, client or data path; its recorded paths are analysis tests and documentation. Clean Otheryn and fresh upstream do not contain the representative World Index tooling root or the OTBM tooling roadmap. The target architecture contract explicitly assigns Canary the roles of legacy laboratory/evidence source/validation environment and requires OTBM/map/content migration to use the existing deterministic analysis stack. Final OAM-040 disposition remains gated on target-side proof that downstream canonical consumers require the Canary evidence contract rather than a target-local copy, and that no unresolved target runtime/product consumer requires the tooling inside Otheryn core.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T14:20:00+02:00
head: 5507fbe61bf9ca200e209701c30a64d9bf1e950e
branch: dudantas/oam-040-preflight
pr: 790
status: ready
context_routes:
  - agent-governance
  - cross-repo
  - otbm
owned_paths:
  - docs/agents/tasks/active/CAN-20260723-oteryn-oam040-preflight.md
proven:
  - OAM-039 is formally complete after Canary durable program reconciliation f7981992d047b2d718989500ba4a1ef46ec68e3d and Otheryn target-task archive 5eea55ca3dd7689d097fadef3ff92eee84f8c163.
  - Fresh Otheryn baseline is 5eea55ca3dd7689d097fadef3ff92eee84f8c163.
  - Fresh upstream Canary baseline is 7323503b3dc61ed86bf1f04a611b2d0aec64b35a.
  - Fresh maintained OTClient baseline is 1e5305395159142634f182d9e888e5f9164228c6.
  - Canonical otbm-tooling has depends_on empty and category platform-tooling.
  - Canonical otbm-tooling owns no server client or data paths; its canonical tests pattern is tools/ai-agent/test_otbm_*.py and its canonical documentation includes docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md.
  - Canonical otbm-tooling registry record blob is 6c2a2e4795ae9698aa276c7b9aa5485dce669679 and records lifecycle active implementation mapped evidence audited and integration tests.
  - The OTBM tooling roadmap blob is 3c3c0a873bbfac81625eeb53779c0bf3c7606887 and states repository blakinio/canary and a mission to maintain one deterministic evidence-based OTBM analysis stack reused for quests teleportation reachability NPCs spawns storage progression semantic diffs geometry audits and safety-gated bounded patching.
  - OTBM tooling roadmap phases 1 through 8 are all recorded merged and archived in Canary including World Index Quest Map Validator reachability spawn/NPC evidence storage graph semantic diff geometry audit and safe bounded patch writer.
  - Legacy representative tools/ai-agent/otbm_world_index.py exists as blob d1e23a9df27a070e2d77fd98210b8574f0c9e0bf.
  - Clean Otheryn and fresh upstream both lack tools/ai-agent/otbm_world_index.py and docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md.
  - The target architecture contract assigns Canary the roles legacy laboratory evidence source validation environment and migration-source candidate while Otheryn is the clean selectively populated target.
  - Target architecture section 4.8 requires OTBM map and content migration to use the existing deterministic analysis stack and forbids donor evidence from authorizing blind map replacement or import.
  - Canonical spawns and npcs each depend on otbm-tooling; canonical quests depends on otbm-tooling and player-persistence.
  - Fresh open-PR and branch searches found no overlapping OAM-040 otbm-tooling owner in Canary or Otheryn.
  - Canonical otbm-tooling has no direct protocol or client path so no maintained OTClient mutation is implied.
derived:
  - otbm-tooling is the smallest dependency-valid unresolved canonical package because it has no hard dependencies and it gates the next world-content candidates spawns npcs and quests.
  - A target-local REUSE or ADAPT copy is not justified by current evidence because the responsibility is an analysis/evidence stack explicitly maintained in Canary rather than Otheryn runtime/product code.
  - DO_NOT_MIGRATE is the leading target disposition if bounded target proof establishes that downstream consumers consume evidence externally and no target-local runtime/product consumer requires the tool suite.
  - EXPERIMENTAL_ONLY remains the fallback disposition if the contract requires preserving an explicit optional target-branch/tooling role rather than a strict target exclusion.
unknown:
  - Whether the final target-side disposition proof satisfies the DO_NOT_MIGRATE no-unresolved-target-consumer criterion or instead requires EXPERIMENTAL_ONLY wording.
  - Exact target proof path set and whether a documentation-only exclusion/dependency contract is sufficient under current Otheryn governance.
  - Whether future spawns npcs or quests target packages require generated evidence artifacts or only pinned Canary tool/report provenance; those packages must decide their own bounded evidence inputs.
conflicts: []
first_failure:
  marker: none
  evidence: No OAM-040 target disposition proof has run; this task is preflight-only.
rejected_hypotheses:
  - Select spawns immediately; its canonical depends_on still includes otbm-tooling and OAM ordering requires dependency resolution first.
  - Select npcs immediately; its canonical depends_on still includes otbm-tooling.
  - Select quests immediately; its canonical depends_on includes otbm-tooling plus player-persistence.
  - Classify otbm-tooling as REUSE merely because the mature legacy stack exists; clean target and upstream lack the tooling roots and target architecture assigns the evidence-laboratory role to Canary.
  - Copy the full tools/ai-agent stack into Otheryn to satisfy dependency ordering; current evidence shows an external migration/evidence responsibility rather than a target runtime/product dependency.
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-oteryn-oam040-preflight.md
validation:
  - command: fresh dependency ownership and overlap preflight
    result: PASS
    evidence: otbm-tooling has no hard dependencies and no overlapping OAM-040 writer was found
  - command: target upstream legacy representative-root comparison
    result: PASS
    evidence: representative OTBM tooling and roadmap exist in Canary but not clean Otheryn or fresh upstream
  - command: target architecture responsibility classification
    result: PASS
    evidence: Canary is the explicit legacy laboratory/evidence/validation repository and world-content migration is required to reuse the existing deterministic analysis stack
blockers: []
next_action: Require exact-current-head Agent Task Ownership and CI success on PR 790, audit the one-file preflight scope and review state, then expected-head squash merge before bounded target-side otbm-tooling disposition proof in Otheryn.
```
