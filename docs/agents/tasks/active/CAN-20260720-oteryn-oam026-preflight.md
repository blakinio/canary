---
task_id: CAN-20260720-oteryn-oam026-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-026
status: ready
agent: "GPT-5.5 Thinking"
branch: docs/oam-026-preflight
base_branch: main
created: 2026-07-20
updated: 2026-07-20
last_verified_commit: "191cad8779ec84aaa09c8f62e9b6ff76e958b8fa"
risk: medium
related_issue: ""
related_pr: "635"
depends_on:
  - OAM-004 database-connection and world-persistence foundation
  - OAM-005 character-lifecycle
blocks:
  - OAM-027
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260720-oteryn-oam026-preflight.md
    - docs/agents/OTERYN_OAM_026_GUILDS_REVALIDATION.md
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/real-tibia/registry/modules/guilds.yaml
    - src/creatures/players/grouping/guild.*
    - src/io/ioguild.*
    - src/io/functions/iologindata_load_player.cpp
modules_touched:
  - guilds
reuses:
  - completed OAM-004 persistence adaptation
  - completed OAM-005 character-lifecycle
public_interfaces:
  - Guild
  - IOGuild
cross_repo_tasks:
  - blakinio/Otheryn:dudantas/oam-026-guilds-revalidation
---

# Goal

Revalidate exactly one canonical package, `guilds`, preserve completed target persistence contracts, deliver the smallest evidence-backed target proof, then close governance before separate lifecycle archive and durable program reconciliation.

# Acceptance criteria

- [x] OAM-025 durable reconciliation merged before OAM-026 started.
- [x] Pin exact Canary, Otheryn, upstream Canary and maintained OTClient task-start baselines.
- [x] Audit open PR ownership and non-overlapping live drift.
- [x] Select one dependency-valid canonical package only: `guilds`.
- [x] Complete semantic/history/persistence revalidation beyond blob identity.
- [x] Select disposition `ADAPT` while preserving OAM-004C save-failure propagation.
- [x] Deliver bounded target proof and merge exact-head Otheryn PR #53.
- [x] Record immutable target evidence and reviewed exclusions.
- [ ] Pass Canary governance exact-head ownership/CI/review gates and merge PR #635.
- [ ] Merge separate authoritative lifecycle archive.
- [ ] Merge separate one-file durable program reconciliation before OAM-027 starts.

# Immutable task-start baselines

- Canary: `052d96014c805aacaa120ce888b7bed038817a72`
- Otheryn: `1cf38d354b493b4cd9ec8e841ec8f2a6ff322029`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `a6868920443dc285656bd016acdb2c1ea566e511`

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-20T22:52:00+02:00
head: 39f5e13f6fee1e83ef0352c397816a9957ca09c2
branch: docs/oam-026-preflight
pr: 635
status: ready
context_routes:
  - agent-governance
  - cpp-runtime
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260720-oteryn-oam026-preflight.md
  - docs/agents/OTERYN_OAM_026_GUILDS_REVALIDATION.md
proven:
  - OAM-025 durable reconciliation merged before OAM-026 start.
  - Immutable baselines are Canary 052d96014c805aacaa120ce888b7bed038817a72, Otheryn 1cf38d354b493b4cd9ec8e841ec8f2a6ff322029, upstream 71a0f92b4da3f550b292fa7536a0e35c2769f1ae and OTClient a6868920443dc285656bd016acdb2c1ea566e511.
  - Canonical guilds depends only on completed character-lifecycle and database-connection contracts.
  - guild.cpp and guild.hpp are blob-identical across pinned legacy target and upstream baselines; blob identity alone was not accepted as REUSE.
  - The guild-specific player-load behavior is semantically aligned; shared iologindata_load_player.cpp was not bulk-copied.
  - Target IOGuild intentionally preserves completed OAM-004C bool save-result propagation through SaveManager, so whole-module REUSE or wholesale legacy/upstream copy is invalid.
  - OAM-026 disposition is ADAPT with no new production guild mutation required.
  - Otheryn PR 53 exact final head 4709f0c49962dee14e98acb384baab75b21c97a8 changed exactly four proof/test paths and no production guild path.
  - Target exact-head autofix 29775483679, CI 29775483958 and Required 29775483628 succeeded; Linux debug Run Tests succeeded; comments reviews and review threads were empty.
  - Otheryn PR 53 was expected-head squash-merged as 418a9f0bfc72cc58b9806a49e966d9c3ea3c1a6d.
  - Canary main drift from task-start 052d96014c805aacaa120ce888b7bed038817a72 to 191cad8779ec84aaa09c8f62e9b6ff76e958b8fa is limited to independent OTBM/E2E coverage lifecycle and MODULE_CATALOG paths with no OAM-026 canonical or governance overlap.
  - Governance branch was reconstructed onto current non-overlapping Canary main 191cad8779ec84aaa09c8f62e9b6ff76e958b8fa.
derived:
  - Governance can now close independently on immutable target evidence before separate authoritative lifecycle and durable program reconciliation stages.
  - Legacy OTS-ECO-GUILD-001 is a future multiwriter guild-bank boundary and is not evidence that current Otheryn imports the legacy multichannel ownership model.
unknown:
  - Exact-final-head Canary governance ownership and CI conclusions.
  - Governance squash merge SHA.
conflicts: []
first_failure:
  marker: none
  evidence: bounded target proof and current governance drift audit found no OAM-026 blocker
rejected_hypotheses:
  - declare guilds REUSE from guild core blob identity: target IOGuild contains intentional completed OAM-004C architecture.
  - copy legacy or upstream IOGuild wholesale: this would regress save-failure propagation.
  - import legacy multichannel guild ownership: canonical guild files provide no stronger donor and multiwriter guild-bank stale-balance risk is proven.
changed_paths:
  - docs/agents/tasks/active/CAN-20260720-oteryn-oam026-preflight.md
  - docs/agents/OTERYN_OAM_026_GUILDS_REVALIDATION.md
validation:
  - command: exact task-start source dependency and history revalidation
    result: PASS
    evidence: bounded guild core and loader reviewed; intentional target IOGuild persistence divergence preserved
  - command: Otheryn PR 53 exact-final-head gate
    result: PASS
    evidence: head 4709f0c49962dee14e98acb384baab75b21c97a8; autofix 29775483679; CI 29775483958; Required 29775483628; Linux debug Run Tests success
  - command: Otheryn PR 53 expected-head squash merge
    result: PASS
    evidence: target merge 418a9f0bfc72cc58b9806a49e966d9c3ea3c1a6d
  - command: Canary task-start-to-current-main drift audit
    result: PASS
    evidence: 052d9601..191cad87 changes only independent OTBM/E2E coverage lifecycle and MODULE_CATALOG paths
blockers: []
next_action: Mark PR 635 ready for review and verify exact-final-head changed-file ownership CI mergeability comments reviews threads and Canary-main drift gates; if all required gates pass, expected-head squash-merge governance before creating the separate authoritative lifecycle archive PR.
```
