# Multi-channel code truth audit — 2026-07-12

## Audit base

- Repository: `blakinio/canary`
- Audited `main` SHA: `e1086633ea36f94495198b6195db2097ed7c3797`
- PR #126 (`docs(multichannel): add implementation handoff`) is merged.
- Open PRs inspected before implementation: #118, #125, #131, #132. None changed `src/game/multichannel`, `schema.sql`, or the login/channel-switch runtime call sites used by this change.
- Local checkout/build was unavailable in the execution sandbox because outbound DNS to GitHub failed. Validation for this branch therefore relies on repository CI plus code-level unit tests added here.

## Documentation versus current code

| Area | Documentation/status claim | Verified code state at audit base | Audit result |
|---|---|---|---|
| Feature default | Multi-channel must remain disabled | `multiChannelEnabled = false` remains the distributed default | Matches |
| Redis session core | Real hiredis acquire/renew/release is wired | `HiredisRedisClient` is configured by `CanaryServer`; login acquire, periodic renew, and logout release call sites exist | Matches, but DB dual-write and durable recovery remain missing |
| Runtime heartbeat | Schema/design only | `channel_runtime_status` exists, but no Redis heartbeat publisher, no DB mirror writer, and no live status cache existed | Critical gap confirmed |
| Login list | Per-channel static list exists | `ChannelRegistry::getLoginListChannels()` filtered only `enabled` and `maintenance`; dead/full channels were still advertised | Critical gap confirmed |
| Channel switch target state | Placeholder | `Game::playerRequestChannelSwitch` supplied `targetChannelOnline=true` and `targetChannelFull=false` | Critical gap confirmed |
| No-live-channel behavior | Fail closed required | Both modern and legacy login paths fell back to the single-world endpoint when the channel list was empty | Critical fail-open gap confirmed |
| Session DB defense | Required before production | `cluster_sessions` schema exists but runtime DB acquire/renew/release is not wired | Critical gap confirmed |
| Save fencing/state version | Required before production | No end-to-end conditional player save guarded by fencing token and optimistic state version | Critical gap confirmed |
| Dirty recovery | Required before production | No complete `SAVING -> COMMIT -> OFFLINE -> compare-release` runtime contract or audited admin recovery workflow | Critical gap confirmed |
| Economy exactly-once | Required before production | Ledger/idempotency scaffolding is not connected to all market/bank/mail/parcel/house mutation paths | Critical gap confirmed |
| Three-process E2E | Required before production | Docker scaffold and scenarios exist; no verified production-gate execution on this audit base | Not proven |

## Scope delivered by this branch

Status: **partially shipped pending CI and review**.

1. Adds a complete channel runtime record (`channel_id`, `instance_id`, `node_id`, startup/heartbeat timestamps, state, population, build/map/data identifiers).
2. Adds atomic Redis heartbeat publication (`HSET` + `PEXPIRE` in one Lua operation).
3. Adds a fail-closed in-process runtime snapshot; Redis errors clear the snapshot immediately.
4. Refreshes all channel runtime keys from the existing cluster heartbeat cycle, including when no players are online.
5. Writes `channel_runtime_status` asynchronously as a diagnostic DB mirror using `INSERT ... ON DUPLICATE KEY UPDATE`.
6. Filters login lists by fresh `ONLINE` heartbeat, maintenance/static eligibility, and `max_players`.
7. Rejects modern and legacy login when no live compatible channel exists; there is no single-world fallback while multi-channel mode is enabled.
8. Makes channel switch evaluate the real cached target online/full state instead of the optimistic placeholders.
9. Adds deterministic unit coverage for fresh heartbeat, capacity, maintenance, crash/TTL expiry, local staleness, and Redis outage cache invalidation.

## Explicit non-goals and remaining blockers

This branch does **not** make multi-channel production-ready. The following remain P0 blockers:

- DB dual-write/recovery contract for `cluster_sessions`;
- fencing-token and optimistic-state-version validation on every persistent player save;
- clean logout ordering and dirty-session recovery/admin tooling;
- full DB-outage fail-closed gameplay/economy policy;
- exactly-once market, bank, mail, parcel, inbox, and house flows;
- verified three-process MariaDB + Redis + gateway + three Canary E2E and race/outage matrix;
- non-blocking refactor for synchronous Redis session renew/heartbeat work currently executed by the existing dispatcher cycle;
- authoritative build/map/data hash generation and startup mismatch refusal (this branch carries configured identifiers and uses `unknown` when not supplied);
- explicit OFFLINE publication on graceful shutdown (crash/offline removal is currently TTL-based).

`multiChannelEnabled` must remain `false` until these gates are completed and the full test matrix is green.
