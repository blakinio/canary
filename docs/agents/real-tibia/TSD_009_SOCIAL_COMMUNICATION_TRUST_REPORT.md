# TSD-009 — Social, Communication and Trust Decomposition

> Task-start main: `c68855a0c9ee33d454bb0d6bbab697693578bb0a`.
> Live main later advanced through merged protocol PR #360; TSD-009 remains inventory only and does not claim communication, party, guild, sanction, runtime or parity correctness.

## Result

Registry grows from **52** to **56** records. Existing records remain unchanged.

Added only:

- `chat-communication`;
- `parties`;
- `guilds`;
- `sanctions`.

Preserved unchanged:

- `account-authentication`;
- `account-lifecycle`;
- `character-lifecycle`;
- `npcs`;
- `protocol`;
- `player-persistence`;
- `world-persistence`;
- all existing gameplay records.

## Evidence inventory

### Chat communication

`Chat`, `ChatChannel` and `PrivateChatChannel` own configured public/scripted channels, user membership, join/leave/speak callbacks, runtime party/guild channels and premium private-channel ownership/invitations. This is a communication lifecycle distinct from protocol framing and from the membership lifecycles of parties and guilds.

Direct-message and channel packets remain protocol capabilities. Scripted channel moderation remains behavior inside the communication boundary and is not evidence for a separate safety or moderation platform.

### Parties

`Party::create`, invitation/member lists, join/leave, leadership transfer and disband form an independent ephemeral social-group state machine. Shared-experience eligibility, analyzer data and status propagation are capabilities within that lifecycle; their gameplay formulas and runtime correctness are not established here.

### Guilds

`Guild` owns runtime identity/ranks/online-member state while `IOGuild` and player guild loading expose a distinct persistence handoff for guild metadata, balance, membership/ranks and war lists. Database access proves only an implementation surface, not durable correctness or transactionality.

### Sanctions

`Ban` owns short-term connection-attempt throttling. `IOBan` performs persisted account/IP ban lookup, expiry, account-ban history handoff and player namelock lookup. These form a bounded sanction/access-control surface, but do not prove enforcement at every login/game entry point or complete audit integrity.

## Candidate decisions

| Candidate | Decision | Reason |
|---|---|---|
| `chat-communication` | `ADD_NOW` | independent channel registry, membership and private-channel lifecycle |
| `parties` | `ADD_NOW` | explicit create/invite/join/leadership/leave/disband state machine |
| `guilds` | `ADD_NOW` | independent guild/rank/member cache plus IOGuild persistence handoff |
| `sanctions` | `ADD_NOW` | bounded connection throttle and account/IP/namelock sanction lookup/expiry lifecycle |
| `public-chat` | `MERGE_WITH_ANOTHER_MODULE` | configured channel instance inside `chat-communication` |
| `private-chat` | `MERGE_WITH_ANOTHER_MODULE` | owned/invited runtime channel inside `chat-communication` |
| `party-chat` | `MERGE_WITH_ANOTHER_MODULE` | communication projection interacting with `parties` |
| `guild-chat` | `MERGE_WITH_ANOTHER_MODULE` | communication projection interacting with `guilds` |
| `shared-experience` | `MERGE_WITH_ANOTHER_MODULE` | party capability, not an independent lifecycle root |
| `guild-wars` | `MERGE_WITH_ANOTHER_MODULE` | loaded guild relationship state inside the guild boundary |
| `direct-messaging` | `MERGE_WITH_ANOTHER_MODULE` | communication/protocol capability without an independent current lifecycle root |
| `moderation-audit-platform` | `DEFER` | no independent general audit lifecycle beyond bounded sanction history evidence |
| `player-groups-permissions` | `DEFER` | configuration/permission registry exists, but this package lacks evidence for a distinct durable trust lifecycle |
| `account-authentication` | `ALREADY_COVERED` | preserve TSD-003 authentication boundary |
| `account-lifecycle` | `ALREADY_COVERED` | preserve TSD-003 account boundary |
| `npcs` | `ALREADY_COVERED` | NPC conversation/world interaction remains existing world-content boundary |
| `protocol` | `ALREADY_COVERED` | packet transport and client compatibility remain protocol/client scope |
| `player-persistence` | `ALREADY_COVERED` | preserve existing player persistence umbrella |
| `world-persistence` | `ALREADY_COVERED` | preserve existing world persistence umbrella and overlapping IOGuild discovery |
| `chat-safety-intelligence` | `DEFER` | planned system explicitly forbidden in this program |
| `security-analytics` | `DEFER` | planned system explicitly forbidden in this program |
| `ai-investigation` | `DEFER` | planned system explicitly forbidden in this program |
| individual channels, guild ranks or party instances | `REJECT_AS_TOO_GRANULAR` | runtime/configuration entries, not durable modules |

## Dependencies

- `chat-communication` depends on `character-lifecycle`.
- `parties` depends on `character-lifecycle`.
- `guilds` depends on `character-lifecycle` and `database-connection`.
- `sanctions` depends on `database-connection`.

All records begin at lifecycle/implementation/evidence `inventory`; persistence, protocol, automated tests, runtime validation and gameplay E2E remain `not-assessed`.

## Discovery expectations

```text
src/creatures/interactions/chat.cpp
  → chat-communication
src/creatures/players/grouping/party.cpp
  → parties
src/creatures/players/grouping/guild.cpp
  → guilds
src/io/ioguild.cpp
  → guilds (and pre-existing persistence umbrellas may also match)
src/creatures/players/management/ban.cpp
  → sanctions
```

Server source mapping must not consume the broad client `protocol` bucket. Client `src/**` paths remain governed by the explicit client source policy and must not inherit server-only social modules. Mapping stays deterministic and discovery-only.

## Evidence limits

TSD-009 does not prove message delivery, privacy, ordering, moderation, party shared-experience formulas, analyzer correctness, guild persistence/transactionality, guild-war behavior, sanction enforcement completeness, audit integrity, protocol compatibility, physical-client E2E, Real Tibia parity or Oteryn readiness.

No planned `chat-safety-intelligence`, `security-analytics` or `ai-investigation` system is implemented or registered here.

## Next package

After feature merge and lifecycle archive:

```text
task: CAN-20260714-tibia-system-decomposition-protocol-client
package: TSD-010
branch: docs/tibia-system-decomposition-protocol-client
```
