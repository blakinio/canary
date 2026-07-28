# Canary Cross-Repository Contract Registry

Last reviewed: 2026-07-28

Copy durable contract changes to both repositories when both sides change. Task-specific details belong in task records. An unchanged consumer may remain pinned by exact commit when evidence proves that no consumer-side mutation is required.

## Required fields

- shared coordination ID and linked repository tasks;
- producer and consumer;
- opcode/message/protobuf/feature/config/identifier/path or file-schema boundary;
- old/new behavior;
- field order, widths, signedness, optional values or schema constraints;
- capability/version gate;
- supported/unsupported combinations;
- rollout order and one-sided failure behavior;
- tests on both sides;
- linked PRs and last verified commit pair.

## Durable areas

| Area | Canary source | Consumer source | Rule |
|---|---|---|---|
| Protocol/opcodes | server protocol handlers and related definitions | affected client/server consumer | Never reuse an opcode without checking both sides/versions. |
| Protobuf | `src/protobuf` and serialization | matching generated schema/deserialization | Schemas and generated expectations stay synchronized. |
| Feature flags | server capability/version behavior | consumer feature checks | Gate new behavior while older combinations remain supported. |
| Assets/IDs/paths | datapack/distribution definitions | assets/loaders/catalogue consumer | Definitions and references differ; IDs/paths cannot be silently repurposed. |
| Login/auth | login service/config/protocol | enter-game/server-list/login consumer | Defaults, TLS, fallback, and failure behavior are explicit. |
| Feature payloads | game logic/emission | matching consumer | Field order, optionals, and gates match exactly. |
| File/schema exports | deterministic producer and schema | importer, persistence and visibility logic | Schema version, hash, bounds, rollout and failure semantics remain synchronized. |
| Coupled defaults | server config/schema/migrations | consumer config/setup/module defaults | Defaults do not silently diverge. |

## Compatibility matrix

| Coordination ID | Canary PR/commit | Consumer PR/commit | Boundary | Rollout | Status | Last verified |
|---|---|---|---|---|---|---|
| `OTS-001` / `OAM-006` | Otheryn PR #21 → `c547d8ad70ef1252624c255476e6cb83fa125e14`; Canary governance PR #436 | OTClient unchanged baseline `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f` | `1525` current-profile login: server-issued opaque single-use session key is forwarded unchanged into game login; server preserves DB-session/password and old-protocol fallbacks | server-first-safe | verified | Universal Agent E2E #118 (`29531221365`): exact Otheryn `c547d8ad70ef1252624c255476e6cb83fa125e14` + OTClient `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`, `login/relog` PASS, Required physical E2E PASS |
| `OTS-20260721-oteryn-identity-auth` | Canary adapter PR #722 → `b8a88f073b2609b444fa15370aae30ac9f80b908`; Canary rotation PR #807; Platform hardening PR #124 → `53158217a6c6017230301cf4daa783b04fcc13d5` | OTClient PR #17 → `bb87346f6c516a19d19497d82bb01fb389334ff5` | Gateway HTTP protocol v1 issues a process-local opaque Game Session; existing `GameSessionKey` world-entry field and current game protocol remain unchanged | atomic-required at activation; Platform/Canary code is deploy-first-safe while native auth remains disabled | hardened, activation-gated | pre-hardening bounded native-auth E2E `29988893301` and final physical evidence `29992417296` PASS; hardened exact-revision E2E pending Canary #807 merge |
| `OTS-20260728-game-catalog-v1` | task `CAN-20260728-game-catalog-export-architecture`; PR #989 | task `OTERYN-20260728-versioned-game-catalog-architecture`; Platform PR #271 | Offline file contract `oteryn.game-catalog` schema `1.0.0`; byte-identical schema expected at SHA-256 `099a8373ff2b0017cc2b321991662dc4e4783b626391aa7a110a6db0559d146b` | additive producer-first-safe after inactive consumer importer; unsupported schema fails closed | proposed | draft PRs #989/#271 opened; both schema paths resolve to Git blob `a3c239a6d61385edde0b06f72cdf781f4ce58df3` |

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

- **Platform producer/hardening:** Game Gateway PR #122 merged as `8006534108d835474dadd208b0ec934e4a12528b`; production-boundary hardening PR #124 merged as `53158217a6c6017230301cf4daa783b04fcc13d5`.
- **Canary adapter:** Candidate B PR #722 merged as `b8a88f073b2609b444fa15370aae30ac9f80b908`, reusing process-local `LoginSessionManager` rather than replayable DB `account_sessions`.
- **Canary credential rotation:** PR #807 adds one optional previous SHA-256 service-credential hash alongside the required current hash for bounded overlap rotation; malformed previous hashes fail closed and the issuer remains disabled by default.
- **OTClient consumer:** merged PR #17 (`bb87346f6c516a19d19497d82bb01fb389334ff5`).
- **Gateway request:** `POST /internal/v1/game-sessions` with exact protocol-v1 fields `protocol_version`, `canary_account_id`, Platform `world_id`, and 32-hex-character `login_attempt_id`; bearer service authentication is verified against configured SHA-256 digest(s).
- **Gateway response:** protocol v1 plus opaque `session.credential` and `session.expires_at`; Canary returns `Cache-Control: no-store` and `Pragma: no-cache` and does not log raw bearer/session credentials.
- **Game wire:** unchanged. OTClient forwards the opaque credential through the existing `GameSessionKey` / world-login handoff; no new game opcode, field order, width or signedness is introduced.
- **Account/character/profile binding:** Canary loads the numeric Canary account without password authentication, binds the token to the current account character-name set and `ProtocolProfileId::Current`, and leaves final `ProtocolGame` → `IOLoginData` ownership/deletion/ban/runtime admission checks authoritative.
- **World/process binding:** the configured Gateway `GAME_SESSION_SERVICE_BASE_URL` selects the exact Canary process. That process requires an explicit positive `CANARY_GAME_SESSION_ISSUER_WORLD_ID` equal to Platform `game_worlds.id` in the request. Platform `game_worlds.id` is not Canary `ChannelContext::channel_id`.
- **Replay/expiry/restart:** `LoginSessionManager` consumes matching credentials atomically once and expires them after 60 seconds; wrong character/profile burns the credential; process restart invalidates unconsumed process-local credentials.
- **Retry/idempotency:** one successful issuance is permitted per `login_attempt_id` per issuer process/TTL. Duplicate attempts return fail-closed without minting a second credential. Failed issuance releases the reservation. If a success response is lost, the orphan credential expires and the client must start a fresh native login attempt rather than recovering or replaying the same attempt.
- **Capability gate:** protocol v1 supports one advertised Platform world mapped to one exact Canary process and Canary `ProtocolProfileId::Current`. Old-profile issuance, multi-world issuer selection and same-world horizontal replicas require a future explicit contract.
- **Platform hardening:** PR #124 adds pre-auth source throttling for private ticket redeem, current/previous Gateway credential-hash overlap, no-store/no-cache sensitive HTTP boundaries, and fail-closed HTTPS requirement for non-loopback Gateway dependencies.
- **Credential rotation:** Gateway→Platform and Gateway→Canary use separate secrets. Each boundary deploys new=current plus old=previous, rolls Gateway to the new plaintext runtime secret, verifies, then removes previous. Plaintext secrets stay outside Git.
- **Transport boundary:** Gateway rejects non-loopback `http://` Platform or Game Session dependencies and retains standard Go TLS certificate/hostname verification. Exact production ingress/firewall, deployed certificate/hostname and secret-manager state still require direct environment evidence.
- **Activation rollout:** (1) merge/deploy Platform hardening with activation unchanged; (2) merge/deploy Canary rotation support with issuer disabled; (3) provision private/TLS routes and separate service credentials; (4) deploy compatible OTClient; (5) rerun hardened exact-revision native-auth E2E; (6) directly verify deployed network/TLS/secrets/revisions; (7) only then enable native auth in a controlled rollout; (8) only after successful production validation consider fencing/removing legacy password paths.
- **One-sided failure:** Canary deployed but disabled is legacy-safe. Gateway configured before a reachable/authorized issuer fails closed. Wrong world/process fails closed. Enabling native auth before compatible Gateway/Canary configuration is unsupported.
- **Production activation blockers:** hardened exact-revision native-auth E2E remains pending; exact production private-network ingress/firewall, TLS certificate/hostname, secret-manager injection/rotation and deployed revision state remain unproven. Gateway v1 also does not forward Identity `security_generation`, so immediate generation-based Game Session revocation is not claimed.
- **E2E status:** pre-hardening bounded native OTClient→Oteryn Gateway→Canary behavior is proven by run `29988893301`: `Knight 1` entered exactly once and replay of the same Game Session was rejected with `login_error` while `successful_world_entries=1`. Final evidence run `29992417296` passed physical job `89166128089` and Required physical E2E job `89167924405` using Canary `285dec6a034aa3620ae5ca12549fb9e8e1b35631`, OTClient `bb87346f6c516a19d19497d82bb01fb389334ff5`, and Gateway `8006534108d835474dadd208b0ec934e4a12528b`. The same scenario must be rerun after Canary #807 merges, pinned to exact merged hardened Platform and Canary revisions.

### OTS-20260728-game-catalog-v1 contract details

- **Producer:** `blakinio/canary`, offline deterministic CLI export.
- **Consumer:** `blakinio/Oteryn-Platform`, transactional inactive snapshot importer and profile visibility owner.
- **Paths:** Canary `schemas/game-catalog/v1/game-catalog-snapshot.schema.json`; Platform `resources/schemas/game-catalog/v1/game-catalog-snapshot.schema.json`.
- **Transport:** local operator/deployment `game-catalog.json` plus optional `.sha256` sidecar; no network push or browser upload in v1.
- **Initial entities:** items and creatures. Initial relation: creature loot. NPCs, quests, spawns and historical profiles are reserved later slices.
- **Version gate:** releases use explicit integer `release_order`; versions are never floats; entity and relation ranges are independent and `removed_in` is exclusive.
- **Completeness/availability:** missing evidence stays unknown; public projection is complete-only and fail-closed by default; registration alone does not prove obtainability or encounterability.
- **Rollout:** architecture/contracts first; inactive Platform importer second; optional Canary exporter third; reviewed staging snapshot/import/rollback fourth; public activation later. Producer-only deployment has no runtime effect. Consumer rejects unsupported schema versions.
- **Tests:** both repositories must validate the same sanitized fixture and prove byte-identical schema hash. Canary additionally proves deterministic offline generation; Platform proves transactional import, visibility and rollback.
- **One-sided failure:** missing producer output leaves the prior active Platform snapshot unchanged; unsupported/malformed output is rejected; exporter failure leaves no partial final file.
- **Production:** no production deployment, import or activation is authorized by the architecture tasks.

Rollout values: `server-first-safe`, `client-first-safe`, `backward-compatible`, `atomic-required`, `breaking-migration`, `unverified`, `additive-producer-first-safe`.
