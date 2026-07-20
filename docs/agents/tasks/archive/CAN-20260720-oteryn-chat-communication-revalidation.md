---
task_id: CAN-20260720-oteryn-chat-communication-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-025
status: completed
agent: "GPT-5.5 Thinking"
branch: docs/oam-025-chat-communication-lifecycle
base_branch: main
created: 2026-07-20
updated: 2026-07-20
completed: 2026-07-20
last_verified_commit: "791bca7403da1e93fba96143f42983f09aa10381"
risk: medium
related_pr: "626"
depends_on:
  - OAM-005 character-lifecycle
blocks:
  - OAM-026
modules_touched:
  - chat-communication
---

# Goal

Revalidate canonical OAM-025 `chat-communication`, classify the smallest dependency-valid clean-target disposition from current evidence, deliver only the bounded target change required by that disposition, and close target plus governance before the separate lifecycle and durable program stages.

# Final disposition

```text
chat-communication → ADAPT
```

# Immutable task-start baselines

- Canary: `9a7c5ebfa4cb35066293a8b75039fb61b8d8afe5`
- Otheryn: `86a598426f65e51ff2864ccd1d0a1dbf818b526c`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `87124861eb0faa9134bdda062c881df70f17d495`

# Accepted adaptation boundary

Canonical `chat-communication` is bounded to `src/creatures/interactions/chat.*` and `data/chatchannels/**` and depends only on completed OAM-005 `character-lifecycle`. Exact legacy/target/upstream content identity was supporting evidence only and did not establish `REUSE`.

Semantic/history review found a bounded privilege-domain defect in `data/chatchannels/scripts/help.lua`: the acting moderator had already been migrated to player-group authorization while `!mute` and `!unmute` still compared that group rank against the target account type. The accepted target adaptation changes only those two checks to compare actor group against target group.

No chat C++ API, channel ID, protocol/opcode, maintained-client, guild/party membership lifecycle, schema, map, asset or deployment behavior changed.

# Exact target proof

```text
Otheryn PR #51 final head: 5aa0259d2ef34d1803ab1fbae8d931ed5f330486
target squash merge: 1c8e3e8b4fc29effb3b0cb882af94f7d26ed2554
autofix.ci run 29770310537: SUCCESS
Repository Audit run 29770310698: SUCCESS
CI run 29770311110: SUCCESS
Required run 29770310554: SUCCESS
Linux debug Run Tests: SUCCESS
```

The focused real-script Lua regression proof used deliberately conflicting group/account privilege values to prove both changed authorization sites. Target comments, reviews and review threads were empty; Otheryn `main` had no task-start drift before expected-head squash merge.

# Canary governance proof

```text
governance PR #626 final head: ef06264fa64583ab33aa5cc3c8be733fa6fe1b93
Agent Task Ownership #2842 / 29771810195: SUCCESS
ready-state final-gate CI #3995 / 29771810912: SUCCESS
governance changed paths: exactly 2
comments: 0
reviews: 0
review threads: 0
governance squash merge: 791bca7403da1e93fba96143f42983f09aa10381
```

The first final ownership attempt failed only because the active task checkpoint omitted the required `derived` field. The final-gate label was removed before that metadata-only repair, then reapplied; exact-final-head Ownership and CI both passed. Canary `main` had no drift from the immutable task-start baseline before governance merge.

# Reviewed exclusions

OAM-025 does not claim Real Tibia chat parity, guild/party membership lifecycle, protocol compatibility, maintained-client UI behavior, generic moderation policy, message privacy or delivery guarantees, NPC conversations, distributed chat, physical-client chat E2E closure, generic persistence redesign, or changes to maps, OTBM, `items.otb`, assets, schema or deployment.

# Lifecycle state

The target and governance stages are merged. This authoritative lifecycle PR owns only the active-task deletion and archive addition. Durable one-file program reconciliation remains pending after this lifecycle merge. OAM-026 must remain NOT STARTED until that reconciliation is merged.
