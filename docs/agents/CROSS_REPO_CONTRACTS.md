# Canary ↔ OTClient Contract Registry

Last reviewed: 2026-07-16

Copy durable contract changes to both repositories when both sides change. Task-specific details belong in task records. An unchanged consumer may remain pinned by exact commit when evidence proves that no consumer-side mutation is required.

## Required fields

- shared `OTS-*` ID and linked `CAN-*`/`OTC-*` tasks;
- producer and consumer;
- opcode/message/protobuf/feature/config/identifier/path;
- old/new behavior;
- field order, widths, signedness, optional values;
- capability/version gate;
- supported/unsupported combinations;
- rollout order and one-sided failure behavior;
- tests on both sides;
- linked PRs and last verified commit pair.

## Durable areas

| Area | Canary source | OTClient source | Rule |
|---|---|---|---|
| Protocol/opcodes | server protocol handlers and related definitions | `src/client` and affected modules | Never reuse an opcode without checking both sides/versions. |
| Protobuf | `src/protobuf` and serialization | `src/protobuf` and deserialization | Schemas and generated expectations stay synchronized. |
| Feature flags | server capability/version behavior | `modules/game_features` and C++ checks | Gate new behavior while older combinations remain supported. |
| Assets/IDs/paths | datapack/distribution definitions | things/sounds/assets/loaders | Definitions and references differ; IDs/paths cannot be silently repurposed. |
| Login/auth | login service/config/protocol | enter-game/server-list/login modules | Defaults, TLS, fallback, and failure behavior are explicit. |
| Feature payloads | game logic/emission | matching `modules/game_*` consumer | Field order, optionals, and gates match exactly. |
| Coupled defaults | server config/schema/migrations | client config/setup/module defaults | Defaults do not silently diverge. |

## Compatibility matrix

| Coordination ID | Canary PR/commit | OTClient PR/commit | Protocol | Rollout | Status | Last verified |
|---|---|---|---:|---|---|---|
| `OTS-001` / `OAM-006` | Otheryn PR #21 → `c547d8ad70ef1252624c255476e6cb83fa125e14`; Canary governance PR #436 | unchanged baseline `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f` | `1525` current-profile login: server-issued opaque single-use session key is forwarded unchanged into game login; server preserves DB-session/password and old-protocol fallbacks | server-first-safe | verified | Universal Agent E2E #118 (`29531221365`): exact Otheryn `c547d8ad70ef1252624c255476e6cb83fa125e14` + OTClient `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`, `login/relog` PASS, Required physical E2E PASS |

### OTS-001 contract details

- **Producer:** `blakinio/Otheryn` login/game authentication flow.
- **Consumer:** `blakinio/otclient` maintained baseline above.
- **Field/path:** existing login response `sessionKey` / `G.sessionKey` / `g_game.loginWorld` handoff; no new opcode or field width/order change.
- **Old behavior:** modern session-key payload used the historical descriptor/password representation and the OAM-005 token was not live on the wire.
- **New behavior:** for supported modern session authentication, the server emits an opaque OAM-005 login-session token and consumes it first for the matching current protocol profile.
- **Capability/version gate:** exact physical proof covers profile `current`, protocol `1525`; old-protocol compatibility and existing DB-session/password fallbacks remain in server code.
- **One-sided rollout:** server-first-safe for the pinned maintained client because the client treats `sessionKey` as opaque and forwards it unchanged. This does not authorize unverified clients/profiles.
- **Consumer mutation:** none. OTClient PR #11 was closed without merge after packet-evidence correction and is not part of this contract.
- **Exact proof:** Universal Agent E2E #118 artifact `universal-agent-e2e-login-relog`, digest `sha256:0db430d258e6048b826af5c46a453e00647c7b30a2a700d8f0245a43fd6145cc`; controlled server binary SHA-256 `a69674e53911f4c529fe62d4dee0209633a73a14903c61f8e5fbca1bdbd8097d`; OTClient binary SHA-256 `b562247f8a0499738bf89eb9f8132146a26b2be57d9fb45e9586a0e0659d97ed`.

Rollout values: `server-first-safe`, `client-first-safe`, `backward-compatible`, `atomic-required`, `breaking-migration`, `unverified`.
