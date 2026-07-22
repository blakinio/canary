---
task_id: CAN-20260722-oteryn-game-session-adapter
program_id: none
coordination_id: OTS-20260721-oteryn-identity-auth
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/CAN-20260722-oteryn-game-session-adapter
base_branch: main
created: 2026-07-22T16:00:00+02:00
updated: 2026-07-22T18:19:31+02:00
last_verified_commit: 991b7091405dbc2a53094641bfeff945910f382e
risk: high
related_issue: ""
related_pr: "722"
depends_on:
  - "Oteryn Platform architecture/OAuth/ticket/Gateway phases"
  - "OTClient PR #17 merged as bb87346f6c516a19d19497d82bb01fb389334ff5"
  - "Oteryn Platform docs/contracts/GAME_SESSION_CANARY_CONTRACT.md"
blocks:
  - "production Oteryn native-auth cross-repository E2E"
  - "legacy password-auth cutover"
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260722-oteryn-game-session-adapter.md
  shared:
    - docs/agents/CROSS_REPO_CONTRACTS.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - src/security/login_session_manager.hpp
    - src/security/login_session_manager.cpp
    - src/server/network/protocol/protocollogin.cpp
    - src/server/network/protocol/protocolgame.cpp
    - src/server/server.hpp
    - src/server/server.cpp
    - src/game/game.cpp
    - src/game/multichannel/channel_context.hpp
modules_touched:
  - Canary login session authentication
reuses:
  - LoginSessionManager
  - existing GameSessionKey world-entry field consumed by ProtocolGame
public_interfaces: []
cross_repo_tasks:
  - OTS-20260721-oteryn-identity-auth
---

# Goal

Select and implement the production Game Session -> Canary compatibility adapter for the Oteryn native-auth flow without transmitting or validating the user's Oteryn password in the supported path.

# Acceptance criteria

- [x] Revalidate the current OTClient Phase 5 merge and the current Platform Game Session contract before Canary implementation.
- [x] Revalidate current Canary `LoginSessionManager` issuance/consume semantics on `main`.
- [x] Select Candidate A or Candidate B explicitly from evidence and document replay, expiry, revocation, restart and multi-process/world semantics.
- [ ] Preserve final Canary character ownership/deletion/ban/runtime admission checks.
- [ ] Keep legacy authentication unchanged while the adapter is disabled/not configured.
- [ ] Bind any new external issuance capability to exact account, world/process route and protocol profile without password fallback.
- [ ] Use least-privilege service authentication and never log raw Game Session credentials.
- [ ] Add focused unit/integration/runtime coverage for issue/consume, expiry, replay, wrong character/account/profile, restart and routing behavior.
- [ ] Update cross-repository contract/catalogue/changelog documentation with exact rollout order and compatible version pair.
- [ ] Pass exact-final-head required CI and cross-repository E2E before any production-readiness claim.

## Candidate selection

**Selected: Candidate B — direct Canary integration reusing `LoginSessionManager`.**

Candidate A (`account_sessions`) remains rejected for this phase because the current Platform contract records it as replayable until expiry or deletion, while Canary already has process-local SHA-256-only token storage with atomic single-use consume semantics.

The selected first deployment scope is deliberately narrower than future multi-world support:

- Gateway protocol v1 only;
- Canary `ProtocolProfileId::Current` only;
- exactly one Platform-advertised world mapped to exactly one Canary process;
- existing game wire protocol and `GameSessionKey` field unchanged;
- legacy password/session authentication unchanged when the adapter is disabled.

## Minimal bounded issuer design

### Process and world routing

The issuer must execute inside the same Canary OS process that owns the `LoginSessionManager` instance which will later consume the credential. The endpoint therefore validates `world_id == g_channelContext().getChannelId()` and fails closed on mismatch before issuing anything.

This is compatible with the current merged Gateway MVP because it accepts exactly one world and has one `GAME_SESSION_SERVICE_BASE_URL`. For that bounded deployment the URL points to the issuer in the sole world process. Multi-world routing or multiple live processes for the same world are explicitly unsupported until the Gateway/World Registry contract gains per-world issuer routing or another exact-process affinity mechanism.

### Internal HTTP boundary

Do not reuse `ServiceManager` unchanged for this boundary. Its current abstraction is a Tibia protocol TCP factory, has no least-privilege service-authentication layer, and binds listeners through the shared server address policy.

Add one narrowly scoped, disabled-by-default internal HTTP issuer owned by the Canary process with only:

- `GET /health`;
- `POST /internal/v1/game-sessions`.

The POST contract matches the merged Gateway MVP request: `protocol_version = 1`, `canary_account_id`, `world_id`, and bounded `login_attempt_id`. It returns `protocol_version = 1` plus `session.credential` and `session.expires_at`. Requests use dedicated bearer service authentication; raw service credentials and raw Game Session credentials must never be logged. The listener requires an independently configured private bind address/port, bounded request body and timeouts, fail-closed parsing, and `Cache-Control: no-store` responses. Production transport remains gated on an explicitly proven private-network/TLS boundary.

### Account, character and profile binding

The issuer does not authenticate a password. It loads the Canary account by `canary_account_id`, resolves the account's current player names using Canary account data, and passes those names plus the account id to `LoginSessionManager`.

Gateway protocol v1 does not carry a Canary protocol-profile identifier, so the bounded initial adapter binds every issued credential to `ProtocolProfileId::Current`. Any future old-profile support requires an explicit versioned cross-repository contract rather than silently weakening the binding.

The existing `ProtocolGame` consume path remains authoritative for the selected character and profile, and the pre-authenticated account id must continue through the existing `IOLoginData::gameWorldAuthentication` path so character ownership, deletion state and later game-admission checks are not bypassed.

### Replay, expiry, revocation, restart and scaling semantics

- Replay: a matching `LoginSessionManager` credential is consumed atomically exactly once; wrong character or wrong protocol profile burns the matched credential and fails closed.
- Expiry: keep the current 60-second bounded lifetime; the HTTP response expiry must derive from the same issuance lifetime rather than an independently drifting constant.
- Revocation: the current manager has no explicit remote revoke API. Before consumption, credentials are revoked only by expiry or process loss/restart. Immediate Identity-generation revocation after issuance is not represented in the current Gateway -> session issuer request and is therefore not claimed.
- Restart: all process-local unconsumed credentials are lost and become invalid; the client must restart the native login/ticket flow.
- Multi-process/world: first deployment requires exactly one Canary process for the sole advertised world. Multi-world or horizontal replicas for one world are unsupported because a credential issued into one process cannot be consumed from another process-local manager.

### Cross-repository gaps that remain production blockers

The merged Gateway MVP has one global session-service base URL and its session request does not carry Canary protocol profile or Identity `security_generation`. The bounded single-world/current-profile adapter can therefore be implemented without changing the game wire protocol, but immediate generation-based revocation, old-profile support, multi-world issuer selection and same-world horizontal scaling require explicit future contract work.

Oteryn Platform PR #123 remains closed unmerged. Its advertised pre-auth throttling, rotating Gateway credential hashes and no-store coverage must not be treated as shipped through that PR; production readiness remains blocked until the live replacement state is proven or equivalent hardening is delivered.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T18:19:31+02:00
head: 991b7091405dbc2a53094641bfeff945910f382e
branch: feat/CAN-20260722-oteryn-game-session-adapter
pr: 722
status: implementing
context_routes:
  - agent-governance
  - cpp-runtime
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260722-oteryn-game-session-adapter.md
proven:
  - OTClient PR 17 was squash-merged to main as bb87346f6c516a19d19497d82bb01fb389334ff5; the client passes the Gateway-issued Game Session through the existing GameSessionKey world-entry field and clears its global copy after the first handoff.
  - Current Canary LoginSessionManager uses a 60-second default TTL, stores only SHA-256 token hashes in process memory, and consumes matching tokens atomically exactly once while binding account id, allowed character names and ProtocolProfileId.
  - Current ProtocolLogin issues LoginSessionManager tokens only after legacy account password authentication, so that issuer path cannot be reused unchanged by the Oteryn Gateway.
  - Canary ServiceManager currently registers protocol factories and has no service-authentication primitive; ServicePort listener binding follows the shared server bind policy.
  - Game::start currently registers only ProtocolGame, ProtocolLogin and ProtocolStatus services; no authenticated internal game-session issuer exists.
  - Canary multi-channel architecture uses one OS process per channel and ChannelContext resolves the per-process channel id from CLI or CANARY_CHANNEL_ID with single-channel fallback.
  - Oteryn Platform PR 122 is merged as 8006534108d835474dadd208b0ec934e4a12528b and its Gateway SessionIssuer HTTP client calls POST /internal/v1/game-sessions with bearer authentication.
  - The merged Gateway MVP has one GAME_SESSION_SERVICE_BASE_URL, accepts exactly one login-context world, and sends canary_account_id, world_id and login_attempt_id without Canary protocol profile or Identity security_generation.
  - Oteryn Platform PR 123 is closed unmerged; its advertised hardening is not present through that PR.
  - Open Canary PR 514 changes security validation tooling/tests/docs only, PR 526 changes security-audit docs only, and no discovered open PR owns LoginSessionManager, ProtocolGame or ProtocolLogin runtime paths.
derived:
  - Candidate B is selected because it preserves Canary's stronger existing single-use token semantics without introducing the replayable account_sessions compatibility path.
  - Existing ServiceManager cannot provide the required least-privilege internal HTTP issuer unchanged; a dedicated bounded per-process issuer boundary is required.
  - The current single-world Gateway can route to the exact consuming Canary process by pointing its single session-service URL at that process and requiring world_id to equal ChannelContext.
  - Current Gateway protocol v1 can safely support only ProtocolProfileId::Current unless the cross-repository request contract is expanded.
  - Immediate Identity-generation revocation after Game Session issuance is not enforceable from the current Gateway session request because security_generation is not forwarded.
unknown:
  - Whether Platform hardening missing from closed-unmerged PR 123 has been superseded by differently named live or merged work.
  - The exact production private-network/TLS boundary and credential-rotation mechanism for Gateway -> Canary issuer traffic.
  - Whether future production requirements mandate multi-world routing or same-world horizontal replicas in the first expansion after the single-world deployment.
conflicts:
  - Prior handoff narrative claimed Oteryn Platform PR 123 was squash-merged, but live GitHub state proves PR 123 closed unmerged with zero commits.
first_failure:
  marker: local-cpp-execution-capability
  evidence: Discovery, checkpoint validation, repository-wide ownership validation and CI pass on 991b7091405dbc2a53094641bfeff945910f382e; the first unmet implementation criterion now requires a bounded local C++ edit/build/test loop unavailable in the current connector-only CHAT execution path.
rejected_hypotheses:
  - Reuse current ProtocolLogin issuer unchanged for Oteryn native auth: it is reached only after account password authentication.
  - Treat DB account_sessions as single-use: the current Platform contract explicitly records them as replayable until expiry or external deletion.
  - Reuse ServiceManager unchanged as the authenticated issuer boundary: it has no service-auth primitive and its listener binding is governed by shared server address configuration.
  - Route all Game Session issuance through the Canary login-gateway process: LoginSessionManager storage is process-local, so a token minted there is unavailable to a different world process.
changed_paths:
  - docs/agents/tasks/active/CAN-20260722-oteryn-game-session-adapter.md
validation:
  - command: live PR/head/CI preflight via GitHub connector
    result: PASS
    evidence: PR 722 head 991b7091405dbc2a53094641bfeff945910f382e; CI run 29937417007 and Agent Task Ownership run 29937416797 both completed successfully.
  - command: targeted service/network/routing reuse discovery via GitHub connector
    result: PASS
    evidence: ServiceManager/ServicePort, Game::start, ChannelContext, ChannelRegistry and multi-channel process model inspected; no existing authenticated internal issuer was found.
  - command: open PR path-ownership overlap check via GitHub connector
    result: PASS
    evidence: PR 514 owns security runtime-validation tooling/docs, PR 526 owns audit docs, and PR 722 remains task-record-only before runtime implementation.
  - command: Oteryn Platform merged Gateway contract inspection via GitHub connector
    result: PASS
    evidence: PR 122 merge plus current Gateway session client/config/service/types establish one HTTP session base URL, bearer auth, single-world fail-closed behavior and protocol-v1 request/response shape.
  - command: local C++ edit/build/test loop
    result: BLOCKED
    evidence: no usable local Canary checkout/runtime is available in this CHAT environment; critical C++ implementation requires the bounded local build/test loop before runtime code is claimed.
blockers:
  - Production readiness remains blocked until the Platform hardening state represented by closed-unmerged PR 123 is reconciled.
  - Production transport security for Gateway -> Canary issuer is not proven yet.
  - Immediate generation-based revocation, multi-world routing and same-world horizontal scaling are outside the current Gateway protocol-v1 session issuer contract.
next_action: Claim the exact affected runtime/config/test paths, then implement the disabled-by-default per-process Candidate B HTTP issuer in a bounded local C++ edit/build/test loop, validating world_id against ChannelContext, resolving allowed characters from Canary account data, binding ProtocolProfileId::Current, preserving downstream ProtocolGame/IOLoginData admission checks, and adding focused issue/consume/expiry/replay/wrong-account/wrong-character/wrong-profile/restart/routing coverage.
```
