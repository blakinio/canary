---
task_id: CAN-20260723-oteryn-native-auth-production-cutover
program_id: none
coordination_id: OTS-20260721-oteryn-identity-auth
status: blocked
agent: "GPT-5.6 Thinking"
branch: feat/CAN-20260722-oteryn-game-session-adapter
base_branch: main
created: 2026-07-23T15:00:00+02:00
updated: 2026-07-23T15:20:00+02:00
last_verified_commit: 27a2c0954caa785a3abb9994eb83cd92f50e3227
risk: high
related_issue: ""
related_pr: "722"
depends_on:
  - "merged Canary Game Session adapter PR #722"
  - "Oteryn Platform production hardening superseding closed-unmerged PR #123"
  - "proven private/TLS Gateway -> Canary deployment boundary"
  - "proven Gateway service-credential rotation"
blocks:
  - "production native-auth activation"
  - "legacy password-auth cutover"
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260723-oteryn-native-auth-production-cutover.md
  shared:
    - docs/agents/CROSS_REPO_CONTRACTS.md
  read_only:
    - docs/agents/tasks/active/CAN-20260722-oteryn-game-session-adapter.md
modules_touched:
  - Oteryn native-auth production rollout
reuses:
  - Oteryn Game Session HTTP issuer
  - OTS-20260721-oteryn-identity-auth cross-repository contract
public_interfaces:
  - POST /internal/v1/game-sessions
cross_repo_tasks:
  - OTS-20260721-oteryn-identity-auth
---

# Goal

Track the production activation boundary for Oteryn native authentication separately from the completed, disabled-by-default Canary adapter implementation.

# Acceptance criteria

- [ ] Oteryn Platform production hardening replacing the closed-unmerged PR #123 is delivered and proven.
- [ ] Production Gateway -> Canary private-network/TLS routing is defined and proven.
- [ ] Gateway service-credential rotation is defined and proven.
- [ ] Production-like deployment verification confirms the already-proven bounded native-auth E2E assumptions before activation.
- [ ] Native-auth activation and any legacy-password cutover occur only after the above gates are satisfied.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-23T15:20:00+02:00
head: 27a2c0954caa785a3abb9994eb83cd92f50e3227
branch: feat/CAN-20260722-oteryn-game-session-adapter
pr: 722
status: blocked
context_routes:
  - agent-governance
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260723-oteryn-native-auth-production-cutover.md
proven:
  - Canary PR #722 implements the disabled-by-default Game Session issuer and its bounded native-auth E2E is proven.
  - Cross-repository contract OTS-20260721-oteryn-identity-auth classifies activation as atomic-required while Canary deployment is deploy-first-safe when the issuer remains disabled.
  - Oteryn Platform PR #123 is closed unmerged and its advertised production hardening is absent from the proven Platform main state.
derived:
  - Production activation gates are rollout concerns separate from merging the disabled-by-default Canary adapter implementation.
unknown:
  - Exact production private-network/TLS Gateway -> Canary boundary remains unproven.
  - Exact service-credential rotation mechanism remains unproven.
  - Immediate security-generation revocation, multi-world routing and same-world horizontal replicas remain outside Gateway protocol v1.
conflicts:
  - Prior handoff claimed Oteryn Platform PR #123 was merged; verified live state showed it closed unmerged.
first_failure:
  marker: platform-production-hardening-unproven
  evidence: Closed-unmerged Oteryn Platform PR #123 did not deliver the advertised production hardening, and no proven successor is recorded.
rejected_hypotheses:
  - Treat bounded E2E as production-boundary proof: existing evidence does not prove private/TLS transport or credential rotation.
changed_paths:
  - docs/agents/tasks/active/CAN-20260723-oteryn-native-auth-production-cutover.md
validation:
  - command: bounded native-auth cross-repository E2E runs 29988893301 and 29992417296
    result: PASS
    evidence: One successful world entry and fail-closed replay are proven on pinned Canary, OTClient and Gateway revisions.
blockers:
  - Oteryn Platform production hardening is not yet proven.
  - Production Gateway -> Canary private-network/TLS and service-credential rotation are not yet proven.
next_action: Deliver and prove the missing Oteryn Platform production hardening and deployment-boundary controls before enabling the Canary issuer in production.
```
