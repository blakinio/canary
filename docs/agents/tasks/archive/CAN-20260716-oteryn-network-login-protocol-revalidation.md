---
task_id: CAN-20260716-oteryn-network-login-protocol-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: "OAM-006"
status: completed
agent: oteryn-architecture-migration-agent
branch: docs/oam-006-network-login-protocol-revalidation
base_branch: main
created: 2026-07-16T20:50:00+02:00
updated: 2026-07-16T21:19:45Z
last_verified_commit: "c40b26ee9481ec99931347ba26897a785a7a38ca"
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
    - blakinio/Otheryn@c547d8ad70ef1252624c255476e6cb83fa125e14
    - blakinio/canary@a1d82a5989fe9e3b7ac6c495804cb1cd83c59090
    - blakinio/canary@02d1b08162a3ad17d6283af16ad481f29c4ec213
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
completed: 2026-07-16T21:19:45Z
---

# Goal

Revalidate the canonical `protocol` module across exact target, legacy, upstream and maintained-client baselines; adapt the target only where the OAM-005 authentication primitive and modern maintained-client contract require it; prove the result with exact cross-repository physical-client E2E; and stop before OAM-007/OAM-008.

# Pinned baselines

- Canary/governance task-start: `a1d82a5989fe9e3b7ac6c495804cb1cd83c59090`
- Otheryn target task-start: `a6d42f6cec024f81a7541084425ec1d43d66d2b8`
- upstream evidence: `opentibiabr/canary@e0ac98e399d0f7e483f3668f57b78fcc45b6e53f`
- maintained client: `blakinio/otclient@2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`
- Universal Agent E2E baseline proof: run #37 (`29412296047`)
- final target: `blakinio/Otheryn@c547d8ad70ef1252624c255476e6cb83fa125e14`
- latest re-fetched Canary main for overlap: `02d1b08162a3ad17d6283af16ad481f29c4ec213`

# Final evidence

- Target and upstream `ProtocolLogin`/`ProtocolGame` blobs matched at task start while legacy PRs #80/#82 supplied bounded modern-login and secure-session integration evidence.
- Maintained OTClient stores the login `sessionKey` opaquely and forwards `G.sessionKey` into `loginWorld` unchanged.
- OTClient PR #11 was closed without merge after packet-evidence correction; no client transport hardening is part of OAM-006.
- Otheryn PR #21 final exact head `5342b374306abb44b6b5e201c85f6a0182c99286` passed ready-triggered CI #80, Required #78 and autofix.ci #71, then squash-merged as `c547d8ad70ef1252624c255476e6cb83fa125e14`.
- Universal Agent E2E was extended in-place with optional exact controlled-server inputs; no second physical-client orchestrator was created.
- Full heavy Universal Agent E2E #118 (`29531221365`) passed against exact controlled server `blakinio/Otheryn@c547d8ad70ef1252624c255476e6cb83fa125e14` and exact maintained client `blakinio/otclient@2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`.
- Run #118 `Required physical E2E` passed; two login/world-entry sessions, two safe logouts, persistence checks, zero client exit code and zero fatal runtime hits were proven.
- Exact run #118 controlled server binary SHA-256: `a69674e53911f4c529fe62d4dee0209633a73a14903c61f8e5fbca1bdbd8097d`.
- Exact run #118 OTClient binary SHA-256: `b562247f8a0499738bf89eb9f8132146a26b2be57d9fb45e9586a0e0659d97ed`.
- Exact run #118 evidence artifact digest: `sha256:0db430d258e6048b826af5c46a453e00647c7b30a2a700d8f0245a43fd6145cc`.
- Earlier run #114 is not used as target proof because incremental reuse skipped heavy jobs.
- The temporary exact-server pin was removed before governance completion.
- Live-main drift through `02d1b08162a3ad17d6283af16ad481f29c4ec213` was rechecked and does not overlap OAM-006 owned paths; the newest drift is confined to bounded Targuna donor-audit files.

# Final disposition

| Module | Disposition | Rationale |
|---|---|---|
| `protocol` | `ADAPT` | task-start target/upstream retained a usable protocol substrate but lacked bounded modern login compatibility and OAM-005 secure session-token wire integration; exact final target + unchanged maintained client passed full physical login/relog proof |

# Safety boundary

- Do not relax sequence/checksum/XTEA/protocol validation.
- Do not remove old-protocol compatibility or existing password/DB-backed session fallbacks.
- Do not bypass character ownership or deletion-state checks.
- Do not wholesale replace `IOLoginData`; preserve OAM-004D save semantics.
- Do not mutate maintained-client source without separate evidence and authorization.
- Reuse the existing Universal Agent E2E rather than create a second physical-client orchestrator.
- Do not claim exhaustive old-profile or hostile replay coverage from the maintained-current-profile physical scenario.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T22:52:00+02:00
head: d97cf2e1e919f8dad4710f8cda631ee7ec5d7f30
branch: docs/oam-006-network-login-protocol-revalidation
pr: 436
status: ready
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
  - maintained client is 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
  - OTClient PR 11 is closed without merge after evidence correction
  - Otheryn PR 21 merged as c547d8ad70ef1252624c255476e6cb83fa125e14 after exact-head CI 80 and Required 78 passed
  - Universal Agent E2E retains one orchestrator and accepts an optional controlled server repository and exact SHA
  - full heavy Universal Agent E2E 118 passed with Required physical E2E success
  - run 118 recorded controlled server c547d8ad70ef1252624c255476e6cb83fa125e14 and maintained client 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
  - temporary controlled-server pin is absent from final governance scope
  - live main 02d1b08162a3ad17d6283af16ad481f29c4ec213 has no OAM-006 owned-path overlap
derived:
  - protocol disposition is ADAPT
  - maintained client source mutation is not justified for this contract
  - target adaptation preserves existing fallback and ownership checks
  - OAM-006 feature governance is ready for exact-head final gates
unknown:
  - final Canary feature-governance merge SHA
  - final Canary lifecycle merge SHA
conflicts: []
first_failure:
  marker: none active
  evidence: target and exact cross-repository physical proof are complete
rejected_hypotheses:
  - LoginSessionManager presence alone completes live authentication
  - client PR 11 is required for baseline login/relog correctness
  - modern login support requires disabling strict protocol validation
  - whole legacy IOLoginData can replace the OAM-004D target file
  - target physical proof can be substituted by a Canary-only binary run
  - Universal Agent E2E run 114 is sufficient exact-target proof
changed_paths:
  - .github/workflows/universal-agent-e2e.yml
  - docs/agents/tasks/active/CAN-20260716-oteryn-network-login-protocol-revalidation.md
  - docs/agents/OTERYN_OAM_006_NETWORK_LOGIN_PROTOCOL_REVALIDATION.md
  - docs/agents/CROSS_REPO_CONTRACTS.md
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
validation:
  - command: exact cross-repository protocol blob comparison
    result: PASS
    evidence: target and upstream matched at task start; legacy contained later bounded integration evidence
  - command: Otheryn PR 21 exact-head CI 80 and Required 78
    result: PASS
    evidence: head 5342b374306abb44b6b5e201c85f6a0182c99286; squash merge c547d8ad70ef1252624c255476e6cb83fa125e14
  - command: Universal Agent E2E run 118 / Required physical E2E
    result: PASS
    evidence: exact Otheryn c547d8ad70ef1252624c255476e6cb83fa125e14 plus OTClient 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f completed login/relog and persistence checks
  - command: live-main overlap recheck through 02d1b08162a3ad17d6283af16ad481f29c4ec213
    result: PASS
    evidence: no OAM-006 owned path changed by intervening main commits
blockers: []
next_action: Update the shared program record, validate exact final PR 436 scope/ownership/CI/review state, mark ready, require ready-triggered final-head gates, then squash-merge and archive through a separate lifecycle-only PR.
```

## Automated lifecycle completion

- Feature PR: #436.
- Feature head: `85309726f8db2619c611421ea0f2598396f1fa2c`.
- Merge commit: `c40b26ee9481ec99931347ba26897a785a7a38ca`.
- Merged at: `2026-07-16T21:19:45Z`.
- This record was moved from `tasks/active` by the post-merge lifecycle automation.
