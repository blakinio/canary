---
task_id: CAN-20260721-oteryn-oam029-cyclopedia-character-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-029
status: implementing
agent: "GPT-5.6 Thinking"
branch: docs/oam-029-cyclopedia-character-preflight
base_branch: main
created: 2026-07-21
updated: 2026-07-21
last_verified_commit: "ad267a87b3f565daf7e5901d80fbafb5a02b623c"
risk: medium
related_pr: ""
owned_paths:
  - docs/agents/tasks/active/CAN-20260721-oteryn-oam029-cyclopedia-character-preflight.md
  - docs/agents/OTERYN_OAM_029_CYCLOPEDIA_CHARACTER_REVALIDATION.md
depends_on:
  - completed OAM-028 cyclopedia
  - completed OAM player-persistence
blocks:
  - OAM-030
modules_touched:
  - cyclopedia-character
---

# Goal

Revalidate canonical OAM-029 `cyclopedia-character`, adapt only independently reviewed recent-PvP pagination correctness within its narrow component root, close target/governance/lifecycle, then reconcile the durable Oteryn migration program before OAM-030 starts.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T06:28:00Z
head: ad267a87b3f565daf7e5901d80fbafb5a02b623c
branch: docs/oam-029-cyclopedia-character-preflight
pr: none
status: investigating
context_routes:
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
  - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
  - docs/agents/real-tibia/registry/modules/cyclopedia-character.yaml
  - docs/agents/real-tibia/TSD_004_CYCLOPEDIA_FAMILY_REPORT.md
owned_paths:
  - docs/agents/tasks/active/CAN-20260721-oteryn-oam029-cyclopedia-character-preflight.md
  - docs/agents/OTERYN_OAM_029_CYCLOPEDIA_CHARACTER_REVALIDATION.md
proven:
  - OAM-001..OAM-028 are durably complete and OAM-028 target checkpoint is archived.
  - Task-start Canary main is ad267a87b3f565daf7e5901d80fbafb5a02b623c.
  - Task-start Otheryn main is 1521906ffa8bd83ff2b35b0feadab4a44ea6df05.
  - Fresh upstream Canary is 71a0f92b4da3f550b292fa7536a0e35c2769f1ae.
  - Maintained OTClient is a6868920443dc285656bd016acdb2c1ea566e511.
  - Canonical cyclopedia-character depends only on completed cyclopedia and player-persistence.
  - Canonical server root is src/creatures/players/components/player_cyclopedia.*; titles retain independent ownership despite shared client presentation paths.
  - Task-start Otheryn and fresh upstream share player_cyclopedia.cpp blob 91a3235e53e5f7ca4da22649bff6bad34cf44e3a.
  - Current legacy player_cyclopedia.cpp differs with blob b2b6d0f3283380f450b3c79874d5ce38ac2734a.
  - Merged legacy PR 188 contains exactly one cyclopedia-character production hunk: add the existing 70-day window to the recent-PvP count subquery so page count matches the filtered result list.
  - The target/upstream query filters the returned recent-PvP rows to 70 days but its count subquery does not, producing stale excess page counts.
  - Fresh open-PR audit found no active Cyclopedia production writer; current open Canary work is OTBM programme closure, NPC E2E and independent security/audit scopes.
derived:
  - The smallest evidence-backed OAM-029 disposition candidate is cyclopedia-character ADAPT using only the reviewed PR 188 recent-PvP count-window hunk plus focused target proof.
unknown:
  - Exact final target CI evidence until the target PR is gated.
conflicts: []
first_failure:
  marker: none
  evidence: none
rejected_hypotheses:
  - Import PR 188 wholesale; rejected because its Bestiary, Bosstiary and Charms changes belong to independent canonical child packages.
  - Treat shared modules/game_cyclopedia/tab/character client paths as exclusive cyclopedia-character ownership; rejected because titles intentionally shares that presentation directory.
changed_paths: []
validation:
  - command: fresh live-state/open-PR/ownership audit
    result: PASS
    evidence: exact task-start SHAs pinned; no active production writer overlaps player_cyclopedia.*
  - command: canonical dependency and donor-scope audit
    result: PASS
    evidence: dependencies complete; PR 188 cyclopedia-character patch is one isolated SQL count-window correction
blockers: []
next_action: Create dedicated Otheryn branch dudantas/oam-029-cyclopedia-character-adapt from target main 1521906ffa8bd83ff2b35b0feadab4a44ea6df05 and apply only the reviewed PR 188 recent-PvP count-window correction with focused target proof; do not import Bestiary, Bosstiary, Charms or maintained-client changes.
```
