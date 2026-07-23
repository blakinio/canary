---
task_id: CAN-20260723-oteryn-native-auth-production-cutover
program_id: none
coordination_id: OTS-20260721-oteryn-identity-auth
status: blocked
agent: "GPT-5.6 Thinking"
branch: docs/CAN-20260723-native-auth-hardened-e2e-evidence
base_branch: main
created: 2026-07-23T15:00:00+02:00
updated: 2026-07-23T18:15:00+02:00
last_verified_commit: 981c82f5ebb6bc22c867312c2b274a71f6aeeb3e
risk: high
related_issue: ""
related_pr: "807"
depends_on:
  - "Canary Game Session adapter PR #722 merged as b8a88f073b2609b444fa15370aae30ac9f80b908"
  - "Oteryn Platform hardening PR #124 merged as 53158217a6c6017230301cf4daa783b04fcc13d5"
  - "Canary credential-rotation PR #807 merged as 981c82f5ebb6bc22c867312c2b274a71f6aeeb3e"
blocks:
  - "production native-auth activation"
  - "legacy password-auth cutover"
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260723-oteryn-native-auth-production-cutover.md
  shared:
    - docs/agents/CROSS_REPO_CONTRACTS.md
    - docs/agents/MODULE_CATALOG.md
modules_touched:
  - Oteryn Game Session HTTP issuer service authentication
  - Oteryn native-auth production rollout
reuses:
  - Oteryn Game Session HTTP issuer
  - LoginSessionManager
  - OTS-20260721-oteryn-identity-auth cross-repository contract
public_interfaces:
  - CANARY_GAME_SESSION_SERVICE_TOKEN_SHA256
  - CANARY_GAME_SESSION_PREVIOUS_SERVICE_TOKEN_SHA256
  - POST /internal/v1/game-sessions
cross_repo_tasks:
  - OTERYN-20260723-native-auth-production-cutover
---

# Goal

Complete the production-boundary prerequisites for safe Oteryn native-auth activation while keeping the Canary Game Session issuer disabled by default until the real deployed network, TLS, secret-manager and revision gates are directly proven.

# Acceptance criteria

- [x] Current Gateway -> Canary service credential SHA-256 hash remains required when the issuer is enabled.
- [x] One optional previous service credential SHA-256 hash is accepted during a bounded rotation overlap window.
- [x] Invalid previous-hash configuration fails closed and duplicate current/previous hashes collapse to one effective credential.
- [x] Focused unit coverage proves current and previous credential acceptance and wrong-credential rejection.
- [x] Exact final-head Canary CI, ownership and formatting checks are green; Security Validation is not path-triggered by the PR #807 delta.
- [x] Cross-repository contract records merged Platform hardening and the finalized rotation/transport sequence.
- [x] Hardened OTClient -> Gateway -> Canary native-auth E2E is re-proven on exact merged runtime revisions.
- [ ] Exact production Gateway -> Canary private-network/TLS boundary, deployed revisions and secret-manager rotation state are directly verified before issuer activation.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T18:15:00+02:00
head: 981c82f5ebb6bc22c867312c2b274a71f6aeeb3e
branch: docs/CAN-20260723-native-auth-hardened-e2e-evidence
implementation_pr: 807
status: blocked
context_routes:
  - agent-governance
  - cpp-runtime
  - cross-repo
proven:
  - Canary Game Session adapter PR #722 merged as b8a88f073b2609b444fa15370aae30ac9f80b908 and the issuer remains disabled unless explicitly enabled.
  - Oteryn Platform hardening PR #124 merged as 53158217a6c6017230301cf4daa783b04fcc13d5 after final-head CI, Gateway CI, governance, concurrency, DB outage, Phase 7 production-like and Acceptance E2E passed.
  - Canary PR #807 merged as 981c82f5ebb6bc22c867312c2b274a71f6aeeb3e and provides bounded current/previous SHA-256 service-credential overlap without enabling the issuer by default.
  - PR #807 exact head b51b2a7e7ccd03aecee4f00165d5b7fe61894e4e passed CI run 30019582097, Agent Task Ownership run 30019581804 and autofix run 30019581790; Security Validation is not triggered by the PR delta path filter.
  - Hardened Universal Agent E2E run 30021347231 completed successfully using Canary server source 981c82f5ebb6bc22c867312c2b274a71f6aeeb3e, Oteryn Platform Gateway source 53158217a6c6017230301cf4daa783b04fcc13d5 and OTClient source bb87346f6c516a19d19497d82bb01fb389334ff5.
  - Hardened physical job 89260751971 and Required physical E2E job 89263233211 both completed successfully.
  - Retained artifact universal-agent-e2e-login-oteryn-native-auth id 8570399702 has digest sha256:109f92eaf54044c1b073e9c6c21918d99d68e9318f970f7e67c65f487f509bbc.
  - Retained result.json reports status=success, server_login_count=1, successful_world_entries=1, client_exit_code=0, lastlogin/lastlogout persistence PASS and zero matching players_online rows after logout.
  - Retained client events prove gateway_session=received, login_1=success, online_stable_1=confirmed, logout_request_1=safe, logout_1=complete, replay_attempt=started, replay_rejected=login_error and e2e=success.
  - A bounded scan of retained text evidence found no Authorization/Bearer header and no raw Game Session/service-token value in retained text logs; scenario.env records only the password environment-variable name rather than a password value.
  - Evidence-only PR #755 is closed without merge after the hardened rerun succeeded.
derived:
  - Repository implementation and hardened exact-revision native-auth behavior are complete for the proven single-world/single-process/current-profile deployment model.
  - Platform hardening and Canary credential overlap are no longer production activation blockers at the code-contract layer.
  - The remaining gate is operational deployment evidence: actual private ingress/firewall, TLS certificate/hostname, secret-manager current/previous credential state and deployed revision identity.
  - Prior bounded E2E evidence is superseded for hardening purposes by run 30021347231, while still remaining valid historical behavior evidence.
unknown:
  - exact production private-network ingress/firewall topology for Gateway -> Canary
  - exact production TLS certificate, hostname and trust termination point for Gateway -> Canary
  - exact production secret-manager injection and current/previous credential rotation state
  - exact deployed production revisions of Gateway and Canary at the intended activation target
conflicts:
  - docs/agents/MODULE_CATALOG.md may still describe Platform hardening as a production blocker; the large concurrently changed catalogue should be synchronized with a safe patch-capable workflow rather than reconstructed from incomplete connector output.
first_failure:
  marker: production-deployment-boundary-unproven
  evidence: Git and CI prove hardened code and exact-revision physical behavior, but do not prove the actual production private network, TLS certificate/hostname, secret-manager state or deployed revision identity.
rejected_hypotheses:
  - Treat successful hardened CI/E2E as proof of the real production network boundary: CI uses a controlled local environment and cannot attest external production ingress/firewall/TLS state.
  - Enable the issuer solely because code and E2E are green: activation remains a deployment action and must fail closed until production deployment evidence is verified.
  - Merge evidence PR #755: it is a reusable evidence harness only; its successful rerun is retained in Actions artifacts and it is intentionally closed without merge.
validation:
  - command: PR #807 exact-head CI 30019582097 on b51b2a7e7ccd03aecee4f00165d5b7fe61894e4e
    result: PASS
    evidence: full final-gate CI completed successfully.
  - command: PR #807 Agent Task Ownership 30019581804
    result: PASS
    evidence: active-task lifecycle and ownership validation passed.
  - command: PR #807 autofix 30019581790
    result: PASS
    evidence: formatting completed successfully without a mutating follow-up commit.
  - command: Canary PR #807 squash merge
    result: PASS
    evidence: merged as 981c82f5ebb6bc22c867312c2b274a71f6aeeb3e.
  - command: Universal Agent E2E 30021347231
    result: PASS
    evidence: Physical client job 89260751971 and Required physical E2E job 89263233211 completed successfully on exact merged Canary/Platform/OTClient revisions.
  - command: retained artifact review for artifact 8570399702
    result: PASS
    evidence: exact source commits match the intended merged revisions; one successful Knight 1 world entry, safe logout, fail-closed replay and persistence assertions are recorded.
blockers:
  - exact production Gateway -> Canary private-network ingress/firewall evidence is not available from repository state
  - exact production TLS certificate/hostname/trust-boundary evidence is not available from repository state
  - exact production secret-manager current/previous credential deployment state is not available from repository state
  - exact production deployed Gateway and Canary revision identity is not available from repository state
next_action: Directly verify the intended production Gateway and Canary deployed revisions, private-network/firewall path, TLS certificate/hostname/trust boundary and secret-manager current/previous credential state; only after all four match the proven contract, enable the Canary issuer and native-auth route while retaining rollback to disabled/legacy auth.
```
