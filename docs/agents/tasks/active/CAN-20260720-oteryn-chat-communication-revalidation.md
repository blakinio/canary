---
task_id: CAN-20260720-oteryn-chat-communication-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-025
status: implementing
agent: "GPT-5.5 Thinking"
branch: docs/oam-025-chat-communication-revalidation
base_branch: main
created: 2026-07-20
updated: 2026-07-20
last_verified_commit: "ee34db88041120c3e64af3e62300372f04394e78"
risk: medium
related_issue: ""
related_pr: "626"
depends_on:
  - OAM-005 character-lifecycle
blocks:
  - OAM-026
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260720-oteryn-chat-communication-revalidation.md
    - docs/agents/OTERYN_OAM_025_CHAT_COMMUNICATION_REVALIDATION.md
  shared: []
  read_only:
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/real-tibia/registry/modules/chat-communication.yaml
    - src/creatures/interactions/chat.cpp
    - src/creatures/interactions/chat.hpp
    - data/chatchannels/**
modules_touched:
  - chat-communication
reuses:
  - OAM-005 character-lifecycle
  - OAM-006 protocol boundary where chat uses already-owned transport helpers
public_interfaces:
  - Chat
  - ChatChannel
  - PrivateChatChannel
cross_repo_tasks:
  - blakinio/Otheryn:dudantas/oam-025-chat-communication-adapt
---

# Goal

Revalidate canonical OAM-025 `chat-communication`, classify the smallest dependency-valid clean-target disposition from current evidence, deliver only the bounded target implementation or proof required by that disposition, and complete the migration-governance lifecycle without absorbing guild membership lifecycle, party membership lifecycle, wire packet framing, generic moderation, NPC conversation state or unrelated physical-client E2E work.

# Acceptance criteria

- [x] Merge the OAM-024 durable reconciliation before starting OAM-025.
- [x] Pin exact task-start Canary, Otheryn, upstream Canary and maintained OTClient heads.
- [x] Confirm canonical dependencies and open-PR ownership overlap for the selected package.
- [x] Complete semantic/history/source revalidation beyond blob identity.
- [x] Classify every target-relevant boundary as applicable, not-applicable or unresolved.
- [x] Select exactly one disposition: `ADAPT`.
- [x] Deliver the smallest target adaptation on a `dudantas/` branch with exact-head CI.
- [ ] Record governance evidence and pass exact-head Ownership/CI/review gates.
- [ ] Merge target, governance, separate lifecycle archive and separate durable program reconciliation before OAM-026 starts.

# Immutable task-start baselines

- Canary: `9a7c5ebfa4cb35066293a8b75039fb61b8d8afe5`
- Otheryn: `86a598426f65e51ff2864ccd1d0a1dbf818b526c`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `87124861eb0faa9134bdda062c881df70f17d495`

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-20T21:20:00+02:00
head: ee34db88041120c3e64af3e62300372f04394e78
branch: docs/oam-025-chat-communication-revalidation
pr: 626
status: validating
context_routes:
  - agent-governance
  - cpp-runtime
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260720-oteryn-chat-communication-revalidation.md
  - docs/agents/OTERYN_OAM_025_CHAT_COMMUNICATION_REVALIDATION.md
proven:
  - OAM-024 durable reconciliation merged as 9a7c5ebfa4cb35066293a8b75039fb61b8d8afe5 before OAM-025 started
  - canonical chat-communication depends only on completed character-lifecycle and is smaller than the broader persistence-bearing guilds package
  - no task-start Canary or Otheryn open PR overlapped canonical chat paths
  - legacy target and fresh upstream chat core XML and all eight configured channel scripts were content-identical at task start
  - upstream commit e17d77ac11635c7ddb53c36f6347d88bd3d35223 migrated chat privilege decisions from account type to player group but left two mixed-domain target checks in help.lua
  - disposition is ADAPT because playerGroupType was compared against target getAccountType for both mute and unmute authorization
  - Otheryn PR 51 changed only two production Lua comparisons plus focused test registration test code and target evidence
  - final Otheryn PR 51 head 5aa0259d2ef34d1803ab1fbae8d931ed5f330486 passed autofix 29770310537 Repository Audit 29770310698 CI 29770311110 and Required 29770310554
  - focused Linux debug Run Tests passed on the exact final target head
  - target review submissions inline review threads and discussion comments were empty and Otheryn main had zero drift from 86a598426f65e51ff2864ccd1d0a1dbf818b526c at merge gate
  - Otheryn PR 51 was expected-head squash-merged as 1c8e3e8b4fc29effb3b0cb882af94f7d26ed2554
unknown:
  - exact-final-head Canary governance Ownership and CI conclusions
  - governance squash merge SHA
conflicts: []
first_failure:
  marker: Otheryn PR 51 first ready-state autofix application
  evidence: run 29770250714 failed while applying generated formatting; its artifact formatted only the new CMake and C++ test files and produced follow-up head 5aa0259d2ef34d1803ab1fbae8d931ed5f330486
rejected_hypotheses:
  - select guilds before chat-communication: guilds is broader and persistence-bearing
  - declare REUSE from blob identity: semantic history review found the mixed group/account privilege-domain defect
changed_paths:
  - docs/agents/tasks/active/CAN-20260720-oteryn-chat-communication-revalidation.md
  - docs/agents/OTERYN_OAM_025_CHAT_COMMUNICATION_REVALIDATION.md
validation:
  - command: live GitHub open-PR overlap audit
    result: PASS
    evidence: no task-start PR matched canonical chat scope
  - command: upstream history plus current help.lua semantic review
    result: PASS
    evidence: historical group migration left two target getAccountType comparisons
  - command: Otheryn PR 51 exact-final-head gates
    result: PASS
    evidence: head 5aa0259d2ef34d1803ab1fbae8d931ed5f330486; runs 29770310537 29770310698 29770311110 and 29770310554 succeeded; no reviews comments threads or main drift
  - command: Otheryn PR 51 expected-head squash merge
    result: PASS
    evidence: merge 1c8e3e8b4fc29effb3b0cb882af94f7d26ed2554
blockers:
  - none
next_action: Run exact-final-head Canary PR 626 Ownership CI review comment thread and main-drift gates; if green, squash-merge governance before creating the separate lifecycle archive PR.
```
