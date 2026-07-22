---
task_id: CAN-20260722-oteryn-game-session-adapter
coordination_id: OTS-20260721-oteryn-identity-auth
status: investigating
agent: "GPT-5.6 Thinking"
branch: feat/CAN-20260722-oteryn-game-session-adapter
base_branch: main
created: 2026-07-22T16:00:00+02:00
updated: 2026-07-22T16:00:00+02:00
last_verified_commit: UNKNOWN
risk: high
related_issue: ""
related_pr: ""
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
- [ ] Select Candidate A or Candidate B explicitly from evidence and document replay, expiry, revocation, restart and multi-process/world semantics.
- [ ] Preserve final Canary character ownership/deletion/ban/runtime admission checks.
- [ ] Keep legacy authentication unchanged while the adapter is disabled/not configured.
- [ ] Bind any new external issuance capability to exact account, world/process route and protocol profile without password fallback.
- [ ] Use least-privilege service authentication and never log raw Game Session credentials.
- [ ] Add focused unit/integration/runtime coverage for issue/consume, expiry, replay, wrong character/account/profile, restart and routing behavior.
- [ ] Update cross-repository contract/catalogue/changelog documentation with exact rollout order and compatible version pair.
- [ ] Pass exact-final-head required CI and cross-repository E2E before any production-readiness claim.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-22T16:00:00+02:00
head: UNKNOWN
branch: feat/CAN-20260722-oteryn-game-session-adapter
pr: none
status: investigating
context_routes:
  - agent-governance
  - cpp-runtime
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260722-oteryn-game-session-adapter.md
proven:
  - OTClient PR 17 was squash-merged to main as bb87346f6c516a19d19497d82bb01fb389334ff5; the client passes the Gateway-issued Game Session through the existing GameSessionKey world-entry field and clears its global copy after the first handoff.
  - Oteryn Platform GAME_SESSION_CANARY_CONTRACT.md still marks the compatibility adapter as not selected; Candidate A account_sessions is explicitly replayable until expiry or deletion, while Candidate B is the direct Canary integration option.
  - Current Canary LoginSessionManager uses a 60-second default TTL, generates 32 random bytes with mbedTLS CTR-DRBG, stores only SHA-256 token hashes in process memory, and consumes matching tokens atomically exactly once.
  - LoginSessionManager binds issued tokens to accountId, allowed character names and ProtocolProfileId; a wrong character or protocol profile burns the matched token and fails closed.
  - Current ProtocolLogin authType=session path issues LoginSessionManager tokens only after legacy account password authentication and returns the token as the existing session key; this issuer cannot be reused directly by the Oteryn Gateway because the target path must not require the Oteryn password.
  - Oteryn Platform PR 123 is closed unmerged with zero commits; its advertised hardening for pre-auth throttling, rotating Gateway credential hashes and no-store coverage is therefore not present through that PR.
  - Canary PR 514 is open for authenticated game-session transport validation and changes security test tooling/docs only; it does not own LoginSessionManager or ProtocolGame runtime source paths.
derived:
  - Candidate B is the stronger current security direction because Canary already has single-use bounded session semantics; production use still requires a safe way for the Gateway or adapter to issue into the exact Canary process that will consume the token.
  - Candidate A should not be selected merely for compatibility because its replay window is weaker than the existing LoginSessionManager semantics and requires an explicit risk decision plus least-privilege database proof.
unknown:
  - Whether an existing Canary internal service framework can expose a least-privilege authenticated session-issuance endpoint without adding a new general-purpose server.
  - Exact production process/world routing model needed so an externally issued process-local token is consumed by the same Canary process.
  - Restart and horizontal-scaling behavior required for the first production deployment.
  - Whether Platform hardening missing from closed-unmerged PR 123 has been superseded by another live or merged PR.
conflicts:
  - Prior handoff narrative claimed Oteryn Platform PR 123 was squash-merged, but live GitHub state proves PR 123 closed unmerged with zero commits.
first_failure:
  marker: platform-hardening-source-of-truth-conflict
  evidence: live Oteryn Platform PR 123 state is closed, merged=false, commits=0, changed_files=0
rejected_hypotheses:
  - Reuse current ProtocolLogin issuer unchanged for Oteryn native auth: it is reached only after account password authentication, which violates the target no-password flow.
  - Treat DB account_sessions as single-use: the current Platform contract explicitly records them as replayable until expiry or external deletion.
changed_paths:
  - docs/agents/tasks/active/CAN-20260722-oteryn-game-session-adapter.md
validation:
  - command: live source and contract preflight via GitHub connector
    result: PASS
    evidence: OTClient PR 17 merge, Platform contract, Canary LoginSessionManager and ProtocolLogin were revalidated against current repository state.
  - command: local git clone/build/test
    result: BLOCKED
    evidence: sandbox DNS cannot resolve github.com; repository mutation and source inspection remain available through the GitHub connector.
blockers:
  - Platform hardening state must be reconciled before production Phase 6 readiness because PR 123 is not merged as previously claimed.
next_action: Search current Canary service/network modules and open PR ownership for a reusable authenticated internal endpoint or exact-process routing primitive that can issue LoginSessionManager tokens without password authentication; if none exists, document the minimal new bounded issuer design before editing runtime code.
```
