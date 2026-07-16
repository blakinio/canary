---
task_id: CAN-20260716-oteryn-network-login-protocol-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: "OAM-006"
status: implementing
agent: oteryn-architecture-migration-agent
branch: docs/oam-006-network-login-protocol-revalidation
base_branch: main
created: 2026-07-16T20:50:00+02:00
updated: 2026-07-16T21:20:00+02:00
last_verified_commit: "a1d82a5989fe9e3b7ac6c495804cb1cd83c59090"
risk: high
related_issue: ""
related_pr: "436"
depends_on:
  - OAM-005
blocks:
  - OAM-008
  - OAM-009
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260716-oteryn-network-login-protocol-revalidation.md
    - docs/agents/OTERYN_OAM_006_NETWORK_LOGIN_PROTOCOL_REVALIDATION.md
  shared:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/CROSS_REPO_CONTRACTS.md
    - .github/workflows/universal-agent-e2e.yml
  read_only:
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/real-tibia/registry/modules/protocol.yaml
    - docs/agents/real-tibia/registry/modules/physical-client-e2e.yaml
    - docs/agents/real-tibia/registry/modules/platform-compatibility.yaml
    - tests/e2e/scenarios/login/scenario.json
    - blakinio/Otheryn@a6d42f6cec024f81a7541084425ec1d43d66d2b8
    - blakinio/canary@a1d82a5989fe9e3b7ac6c495804cb1cd83c59090
    - opentibiabr/canary@e0ac98e399d0f7e483f3668f57b78fcc45b6e53f
    - blakinio/otclient@2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
modules_touched:
  - protocol
reuses:
  - docs/agents/OTERYN_OAM_005_ACCOUNT_CHARACTER_LIFECYCLE_REVALIDATION.md
  - docs/agents/OTERYN_OAM_004_PERSISTENCE_FOUNDATION_REVALIDATION.md
  - docs/agents/CROSS_REPO_CONTRACTS.md
  - Universal Agent E2E
public_interfaces:
  - account login session-key field
  - game login session-key authentication
  - maintained-client login/game handoff
  - Universal Agent E2E controlled server revision inputs
cross_repo_tasks:
  - blakinio/Otheryn#20
  - blakinio/Otheryn#21
---

# Goal

Revalidate the canonical `protocol` module across exact target, legacy, upstream and maintained-client baselines; adapt the target only where the OAM-005 authentication primitive and modern maintained-client contract require it; prove the result with exact cross-repository physical-client E2E; and stop before OAM-007/OAM-008.

# Pinned baselines

- Canary/governance task-start: `a1d82a5989fe9e3b7ac6c495804cb1cd83c59090`
- Otheryn target task-start: `a6d42f6cec024f81a7541084425ec1d43d66d2b8`
- upstream evidence: `opentibiabr/canary@e0ac98e399d0f7e483f3668f57b78fcc45b6e53f`
- maintained client: `blakinio/otclient@2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`
- Universal Agent E2E baseline proof: run #37 (`29412296047`)

# Current evidence

- Target and upstream `ProtocolLogin` are content-identical at task start; target rejected every non-old protocol before authentication.
- Target and upstream `ProtocolGame` are content-identical at task start; they did not consume the OAM-005 login-session token.
- Legacy Canary PR #80 removed the unconditional modern login rejection without weakening old-protocol gating.
- Legacy Canary PR #82 issues the OAM-005 token in the existing modern session-key field and consumes it during game login, preserving password/DB-session fallbacks and character ownership/deletion checks.
- Maintained OTClient stores the login `sessionKey` opaquely and forwards `G.sessionKey` to `loginWorld` unchanged.
- Universal Agent E2E #37 passed two stable sessions, two safe logouts and persistence using maintained client `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`.
- OTClient PR #11 was closed without merge after packet evidence correction; no client transport hardening is part of the OAM-006 baseline.
- Otheryn PR #21 changes exactly `ProtocolLogin` and `IOLoginData`; `ProtocolGame` and the public `IOLoginData` signature remain unchanged.
- Universal Agent E2E is extended in-place with optional exact `server_repository`/`server_ref` inputs so the existing physical runner can build and execute a controlled Otheryn revision without creating a second orchestrator.

# Working disposition

| Module | Disposition | Rationale |
|---|---|---|
| `protocol` | `ADAPT` | target/upstream lacked bounded modern login compatibility and secure session-token wire integration already evidenced in legacy; maintained client can carry the opaque token without source mutation |

# Safety boundary

- Do not relax sequence/checksum/XTEA/protocol validation.
- Do not remove old-protocol compatibility or existing password/DB-backed session fallbacks.
- Do not bypass character ownership or deletion-state checks.
- Do not wholesale replace `IOLoginData`; preserve OAM-004D save semantics.
- Do not mutate maintained-client source unless exact E2E proves it necessary.
- Reuse the existing Universal Agent E2E rather than create a second physical-client orchestrator.
- Require exact-head target CI and exact cross-repository physical E2E before feature governance completion.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T21:20:00+02:00
head: 912754ee61aadf4813b1be03c547457aa003f933
branch: docs/oam-006-network-login-protocol-revalidation
pr: 436
status: implementing
context_routes:
  - agent-governance
  - protocol
  - physical-client-e2e
owned_paths:
  - docs/agents/tasks/active/CAN-20260716-oteryn-network-login-protocol-revalidation.md
  - docs/agents/OTERYN_OAM_006_NETWORK_LOGIN_PROTOCOL_REVALIDATION.md
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
  - docs/agents/CROSS_REPO_CONTRACTS.md
  - .github/workflows/universal-agent-e2e.yml
proven:
  - OAM-005 feature and lifecycle are complete
  - Canary task-start main is a1d82a5989fe9e3b7ac6c495804cb1cd83c59090
  - Otheryn task-start main is a6d42f6cec024f81a7541084425ec1d43d66d2b8
  - upstream evidence head is e0ac98e399d0f7e483f3668f57b78fcc45b6e53f
  - maintained client main is 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
  - Universal Agent E2E 37 passed on the maintained client baseline
  - target and upstream ProtocolLogin and ProtocolGame blobs matched at task start while legacy differed
  - OTClient PR 11 is closed without merge after evidence correction
  - Otheryn PR 21 exact initial head is 4fa4001d4e59aeba952fcae28b9df204c8d997be and changes only ProtocolLogin plus IOLoginData
  - Universal Agent E2E retains one orchestrator and now accepts an optional controlled server repository and exact ref
derived:
  - protocol requires ADAPT
  - maintained client source mutation is not currently justified
  - target adaptation must preserve all existing fallback and ownership checks
  - final physical proof must run the exact merged Otheryn SHA through the existing physical-client scenario
unknown:
  - final target PR 21 merge SHA
  - exact physical E2E result on final Otheryn target
  - final Canary governance and lifecycle merge SHAs
conflicts: []
first_failure:
  marker: none active
  evidence: target PR 21 ready-triggered CI and controlled-target physical E2E remain
rejected_hypotheses:
  - LoginSessionManager presence alone completes live authentication
  - client PR 11 is required for baseline login/relog correctness
  - modern login support requires disabling strict protocol validation
  - whole legacy IOLoginData can replace the OAM-004D target file
  - target physical proof can be substituted by a Canary-only binary run
changed_paths:
  - .github/workflows/universal-agent-e2e.yml
  - docs/agents/tasks/active/CAN-20260716-oteryn-network-login-protocol-revalidation.md
  - docs/agents/OTERYN_OAM_006_NETWORK_LOGIN_PROTOCOL_REVALIDATION.md
validation:
  - command: exact cross-repository protocol blob comparison
    result: PASS
    evidence: target and upstream matched at task start; legacy contains later bounded integration
  - command: Universal Agent E2E run 37
    result: PASS
    evidence: maintained client 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f completed two stable sessions and safe logouts
  - command: Otheryn PR 21 draft CI 78 and Required 76
    result: PASS
    evidence: completed success on head 4fa4001d4e59aeba952fcae28b9df204c8d997be
blockers: []
next_action: Complete Otheryn PR 21 ready-triggered exact-head gate and merge, then dispatch Universal Agent E2E login/relog with server_repository blakinio/Otheryn and server_ref pinned to the final target SHA.
```
