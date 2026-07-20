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
last_verified_commit: "9a7c5ebfa4cb35066293a8b75039fb61b8d8afe5"
risk: medium
related_issue: ""
related_pr: ""
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
  - blakinio/Otheryn:dudantas/oam-025-chat-communication-revalidation
---

# Goal

Revalidate canonical OAM-025 `chat-communication`, classify the smallest dependency-valid clean-target disposition from current evidence, deliver only the bounded target implementation or proof required by that disposition, and complete the migration-governance lifecycle without absorbing guild membership lifecycle, party membership lifecycle, wire packet framing, generic moderation, NPC conversation state or unrelated physical-client E2E work.

# Acceptance criteria

- [x] Merge the OAM-024 durable reconciliation before starting OAM-025.
- [x] Pin exact task-start Canary, Otheryn, upstream Canary and maintained OTClient heads.
- [x] Confirm canonical dependencies and open-PR ownership overlap for the selected package.
- [ ] Complete semantic/history/source revalidation beyond blob identity.
- [ ] Classify every target-relevant boundary as applicable, not-applicable or unresolved.
- [ ] Select exactly one disposition: `REUSE`, `ADAPT`, `REWRITE` or `DO_NOT_MIGRATE`.
- [ ] Deliver the smallest target proof or implementation on a `dudantas/` branch with exact-head CI.
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
updated_at: 2026-07-20T20:00:00+02:00
head: 9a7c5ebfa4cb35066293a8b75039fb61b8d8afe5
branch: docs/oam-025-chat-communication-revalidation
pr: null
status: implementing
context_routes:
  - agent-governance
  - cpp-runtime
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260720-oteryn-chat-communication-revalidation.md
  - docs/agents/OTERYN_OAM_025_CHAT_COMMUNICATION_REVALIDATION.md
proven:
  - OAM-024 durable reconciliation PR 624 merged as 9a7c5ebfa4cb35066293a8b75039fb61b8d8afe5 before OAM-025 started
  - canonical chat-communication depends only on completed character-lifecycle and interacts with guilds parties and protocol without owning those lifecycles
  - chat-communication is a smaller dependency-valid next package than guilds because guilds additionally owns persistence-facing paths and database-connection dependency
  - no open Canary or Otheryn PR was found for chat-communication chatchannels or src/creatures/interactions/chat scope at task start
  - legacy target and fresh upstream chat.cpp share blob 152a40857f4b184e968eb51601a75634d8d37946
  - legacy target and fresh upstream chat.hpp share blob 09f8a727fef239b95b1bb5da20356801769732f0
  - legacy target and fresh upstream chatchannels.xml share blob e819080856b4460524ca316099c043e8ab3fb4ff
  - blob identity is supporting evidence only and does not establish REUSE
unknown:
  - whether semantic and history review identifies a bounded target defect requiring ADAPT
  - whether any data/chatchannels script differs across legacy target and fresh upstream
  - exact target proof required for the final disposition
conflicts: []
first_failure:
  marker: none
  evidence: no validation failure observed yet
rejected_hypotheses:
  - select guilds before chat-communication: both are dependency-valid but guilds is broader and persistence-bearing
changed_paths:
  - docs/agents/tasks/active/CAN-20260720-oteryn-chat-communication-revalidation.md
validation:
  - command: live GitHub open-PR overlap audit
    result: PASS
    evidence: no open PR matched chat communication chatchannels or src/creatures/interactions/chat scope
  - command: canonical dependency review
    result: PASS
    evidence: chat-communication depends_on contains only character-lifecycle
blockers:
  - none
next_action: Finish semantic history and data-script revalidation, classify the OAM-025 boundary, then open the smallest target proof or adaptation PR on a dudantas/ branch.
```
