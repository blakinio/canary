# OAM-025 Chat Communication Revalidation

## Disposition

```text
chat-communication → ADAPT
```

## Immutable task-start baselines

- legacy / governance Canary: `9a7c5ebfa4cb35066293a8b75039fb61b8d8afe5`
- Otheryn target: `86a598426f65e51ff2864ccd1d0a1dbf818b526c`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `87124861eb0faa9134bdda062c881df70f17d495`

## Canonical package

The canonical `chat-communication` record owns configured/scripted chat channels, channel membership callbacks, runtime party/guild channel projections, private-channel ownership/invitation/exclusion and close notifications. Its only fundamental dependency is completed `character-lifecycle`.

OAM-025 does not absorb guild or party membership lifecycle, protocol framing/opcodes, NPC conversation state, generic moderation policy, message privacy/delivery guarantees or unrelated physical-client E2E.

## Fresh source and ownership evidence

Task-start open-PR review found no Canary or Otheryn PR overlapping `src/creatures/interactions/chat.*` or `data/chatchannels/**`.

The following task-start content was identical across legacy Canary, Otheryn and fresh upstream Canary:

- `chat.cpp`: `152a40857f4b184e968eb51601a75634d8d37946`
- `chat.hpp`: `09f8a727fef239b95b1bb5da20356801769732f0`
- `chatchannels.xml`: `e819080856b4460524ca316099c043e8ab3fb4ff`
- all eight configured channel Lua scripts.

That identity is supporting provenance only and was not accepted as `REUSE` evidence.

## Defect found by semantic/history revalidation

Upstream commit `e17d77ac11635c7ddb53c36f6347d88bd3d35223` explicitly migrated chat authorization/message-color logic from account type to player group so an account-level role would not incorrectly determine a character's chat privilege.

In `help.lua`, that historical change converted the acting moderator to `playerGroupType` but left both target-side `!mute` and `!unmute` checks as:

```lua
playerGroupType > target:getAccountType()
```

This compares two different privilege domains. The acting character's group can therefore be incorrectly authorized or denied when the target character's in-game group differs from the target account type. The smallest valid target change is to compare both sides in the player-group domain.

## Target adaptation

Otheryn PR #51 changes exactly the bounded authorization sites to:

```lua
playerGroupType > target:getGroup():getId()
```

It adds a focused C++/Lua execution test that loads the real `help.lua` and deliberately makes group rank conflict with account type. The proof covers:

1. a Senior Tutor group cannot mute a higher-group target merely because the target exposes a lower account type;
2. a Senior Tutor group can unmute a lower-group target even when the target exposes a higher account type.

Current target PR head while validation is running: `27d46028243085aede7736b2202e74ebcedc1dca`.

## Boundary classification

| Boundary | Result |
|---|---|
| ownership/lifecycle | applicable; existing `Chat`/`ChatChannel` ownership unchanged |
| build/toolchain | applicable; focused test registration only |
| configuration | applicable; existing channel XML/core-directory loading unchanged |
| service/API | applicable; existing chat interfaces unchanged |
| scheduling/concurrency | applicable; existing scheduling and in-process maps unchanged |
| persistence | applicable; existing Help mute KV state unchanged, no schema change |
| protocol/session | not applicable to adaptation; no wire/session/client change |
| identifiers/assets | applicable; existing channel IDs/scripts unchanged |
| world/map | not applicable |
| runtime | applicable; synchronous Lua authorization in existing lifecycle |
| tests | applicable; focused real-script Lua execution proof added |
| physical-client E2E | not applicable to adaptation; no wire/client boundary changed |
| operations | not applicable |
| security/privacy | applicable; moderator privilege-domain mismatch corrected |

No applicable boundary remains unresolved for this bounded adaptation.

## Validation state

Target exact-head required CI and review/drift gates are still in progress. This document must be updated with immutable final target head, workflow conclusions and squash merge SHA before Canary governance merge.

## Explicit non-claims

OAM-025 does not claim Real Tibia chat parity, guild/party membership lifecycle, protocol compatibility, maintained-client UI behavior, generic moderation policy, privacy/delivery guarantees, NPC conversations, distributed chat, physical-client chat E2E closure, generic persistence redesign, or map/OTBM/`items.otb`/asset/schema/deployment changes.
