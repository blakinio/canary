# Canary ↔ OTClient Contract Registry

Last reviewed: 2026-07-23

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
| `OTS-20260721-oteryn-identity-auth` | Canary PR #722 runtime `285dec6a034aa3620ae5ca12549fb9e8e1b35631`; Platform Gateway PR #122 → `8006534108d835474dadd208b0ec934e4a12528b` | OTClient PR #17 → `bb87346f6c516a19d19497d82bb01fb389334ff5` | Gateway HTTP protocol v1 issues a process-local opaque Game Session; existing `GameSessionKey` world-entry field and current game protocol remain unchanged | atomic-required at activation; Canary code is deploy-first-safe while disabled | implemented, production-blocked | Canary exact runtime head `285dec6a034aa3620ae5ca12549fb9e8e1b35631`: CI `29957357479`, Security Validation `29957357463`, Agent Task Ownership `29957357248`, autofix `29957357043` PASS; bounded native-auth behavior E2E `29988893301` and final physical evidence `29992417296` PASS |

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

### OTS-20260721-oteryn-identity-auth contract details

- **Producer:** merged Oteryn Platform Game Gateway PR #122 (`8006534108d835474dadd208b0ec934e4a12528b`).
- **Canary adapter:** PR #722, Candidate B, reusing process-local `LoginSessionManager` rather than replayable DB `account_sessions`.
- **OTClient consumer:** merged PR #17 (`bb87346f6c516a19d19497d82bb01fb389334ff5`).
- **Gateway request:** `POST /internal/v1/game-sessions` with exact protocol-v1 fields `protocol_version`, `canary_account_id`, Platform `world_id`, and 32-hex-character `login_attempt_id`; bearer service authentication is verified against a configured SHA-256 digest.
- **Gateway response:** protocol v1 plus opaque `session.credential` and `session.expires_at`; Canary returns `Cache-Control: no-store` and `Pragma: no-cache` and does not log raw bearer/session credentials.
- **Game wire:** unchanged. OTClient forwards the opaque credential through the existing `GameSessionKey` / world-login handoff; no new game opcode, field order, width or signedness is introduced.
- **Account/character/profile binding:** Canary loads the numeric Canary account without password authentication, binds the token to the current account character-name set and `ProtocolProfileId::Current`, and leaves final `ProtocolGame` → `IOLoginData` ownership/deletion/ban/runtime admission checks authoritative.
- **World/process binding:** the configured Gateway `GAME_SESSION_SERVICE_BASE_URL` selects the exact Canary process. That process requires an explicit positive `CANARY_GAME_SESSION_ISSUER_WORLD_ID` equal to the Platform `game_worlds.id` in the request. Platform `game_worlds.id` is not Canary `ChannelContext::channel_id`.
- **Replay/expiry/restart:** `LoginSessionManager` consumes matching credentials atomically once and expires them after 60 seconds; wrong character/profile burns the credential; process restart invalidates unconsumed process-local credentials.
- **Retry/idempotency:** one successful issuance is permitted per `login_attempt_id` per issuer process/TTL. Duplicate attempts return fail-closed without minting a second credential. Failed issuance releases the reservation. If a success response is lost, the orphan credential expires and the client must start a fresh native login attempt rather than recovering or replaying the same attempt.
- **Capability gate:** initial supported adapter is Gateway protocol v1, one advertised Platform world mapped to one exact Canary process, and Canary `ProtocolProfileId::Current`. Old-profile issuance, multi-world issuer selection and same-world horizontal replicas require a future explicit contract.
- **Activation rollout:** (1) deploy Canary support disabled; (2) provision the private/TLS Gateway→Canary route and matching service credential/hash plus exact Platform world ID; (3) deploy the compatible OTClient PR #17 build; (4) configure Gateway session-service URL/token and enable the Canary issuer together; (5) verify the already-proven native cross-repository E2E assumptions in the production-like deployment boundary; (6) only then consider fencing/removing legacy password paths.
- **One-sided failure:** Canary deployed but disabled is legacy-safe. Gateway configured before a reachable/authorized issuer fails closed. Wrong world/process fails closed. Enabling native auth before compatible Gateway/Canary configuration is unsupported.
- **Production blockers:** current Platform main still lacks the pre-auth throttling, overlapping Gateway credential-hash rotation and full ticket-boundary no-store hardening advertised by closed-unmerged PR #123; Gateway→Canary private-network/TLS behavior is not yet proven; Gateway v1 does not forward Identity `security_generation`, so immediate generation-based Game Session revocation is not claimed.
- **E2E status:** bounded native OTClient→Oteryn Gateway→Canary behavior is proven by run `29988893301`: `Knight 1` entered exactly once and replay of the same Game Session was rejected with `login_error` while `successful_world_entries=1`. Final evidence run `29992417296` passed physical job `89166128089` and Required physical E2E job `89167924405` using Canary `285dec6a034aa3620ae5ca12549fb9e8e1b35631`, OTClient `bb87346f6c516a19d19497d82bb01fb389334ff5`, and Gateway `8006534108d835474dadd208b0ec934e4a12528b`. This does not prove the production private-network/TLS or credential-rotation boundary.

Rollout values: `server-first-safe`, `client-first-safe`, `backward-compatible`, `atomic-required`, `breaking-migration`, `unverified`.
