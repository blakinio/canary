---
task_id: CAN-20260716-oteryn-account-character-lifecycle-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: "OAM-005"
status: implementing
agent: oteryn-architecture-migration-agent
branch: docs/oam-005-account-character-lifecycle-revalidation
base_branch: main
created: 2026-07-16T19:58:30+02:00
updated: 2026-07-16T20:07:00+02:00
last_verified_commit: "0f25e7fd4d41e90f17fc95d13dba84b7e81d1681"
risk: high
related_issue: ""
related_pr: "432"
depends_on:
  - OAM-004
blocks:
  - OAM-006
  - OAM-008
  - OAM-009
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260716-oteryn-account-character-lifecycle-revalidation.md
    - docs/agents/OTERYN_OAM_005_ACCOUNT_CHARACTER_LIFECYCLE_REVALIDATION.md
  shared:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
  read_only:
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/real-tibia/registry/modules/account-lifecycle.yaml
    - docs/agents/real-tibia/registry/modules/account-authentication.yaml
    - docs/agents/real-tibia/registry/modules/character-lifecycle.yaml
    - docs/agents/real-tibia/TSD_003_ACCOUNT_CHARACTER_PROGRESSION_REPORT.md
    - blakinio/Otheryn@67212530b03c10175da2c0d9eabcee8991a05924
    - blakinio/canary@c2ffe09dc8753734be00c3433fab6f2ebe25d2e8
    - opentibiabr/canary@e0ac98e399d0f7e483f3668f57b78fcc45b6e53f
modules_touched:
  - account-lifecycle
  - account-authentication
  - character-lifecycle
reuses:
  - docs/agents/real-tibia/TSD_003_ACCOUNT_CHARACTER_PROGRESSION_REPORT.md
  - docs/agents/OTERYN_OAM_004_PERSISTENCE_FOUNDATION_REVALIDATION.md
public_interfaces:
  - OAM-005 account and character lifecycle migration dispositions
cross_repo_tasks:
  - blakinio/Otheryn#15
  - blakinio/Otheryn#17
  - blakinio/Otheryn#19
---

# Goal

Revalidate the canonical account and character lifecycle foundation against exact target, legacy and upstream baselines; assign evidence-backed dispositions; deliver only bounded target adaptations required before OAM-006; and keep wire-level protocol/client integration out of OAM-005.

# Canonical modules

- `account-lifecycle`
- `account-authentication`
- `character-lifecycle`

# Pinned baselines

- Canary/governance task-start: `c2ffe09dc8753734be00c3433fab6f2ebe25d2e8`
- Canary/governance integration base after CI #415: `0f25e7fd4d41e90f17fc95d13dba84b7e81d1681`
- Otheryn target task-start: `67212530b03c10175da2c0d9eabcee8991a05924`
- Upstream evidence: `opentibiabr/canary@e0ac98e399d0f7e483f3668f57b78fcc45b6e53f`

# Current evidence

- `account.cpp`, `account_repository.cpp` and `account_repository_db.cpp` are content-identical across the pinned legacy, target and upstream revisions.
- `LoginSessionManager` exists in legacy Canary but is absent from both target and upstream.
- Legacy PR #77 isolated the secure login-session primitive from live protocol wiring and merged as `3c5268fe86fd9785e3feea192d70c8bd3d51ef87`.
- Legacy PR #82 later wired the primitive through `ProtocolLogin`, `ProtocolGame` and an optional `IOLoginData` pre-authenticated-account handoff. That wire/session integration is reserved for OAM-006.
- Target PR #19 ports only the bounded primitive and focused tests.
- OAM-004D persistence semantics must remain intact; OAM-005 must not rewrite player save boundaries.

# Working dispositions

| Module | Disposition | Rationale |
|---|---|---|
| `account-lifecycle` | `REUSE` | core account implementation checked so far is content-identical across target, legacy and upstream |
| `account-authentication` | `ADAPT` | legacy has a bounded secure-session primitive absent from target/upstream; target PR #19 ports the primitive without wire integration |
| `character-lifecycle` | `ADAPT` | target already carries OAM-004 persistence adaptations; authenticated handoff integration remains a cross-boundary concern for OAM-006 and must preserve ownership/deletion checks |

# Safety boundary

- Do not touch production credentials or databases.
- Do not weaken password authentication or DB-backed `account_sessions` fallback behavior.
- Do not modify login/game packet layouts in OAM-005.
- Do not wire `ProtocolLogin` or `ProtocolGame` in OAM-005.
- Do not undo OAM-004A/B/C/D persistence behavior.
- Do not start OAM-006 before OAM-005 feature and lifecycle completion.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T20:07:00+02:00
head: 8756fead8917e1341628c8b75a474315c95dc2d1
branch: docs/oam-005-account-character-lifecycle-revalidation
pr: 432
status: implementing
context_routes:
  - agent-governance
  - account-authentication
  - character-lifecycle
owned_paths:
  - docs/agents/tasks/active/CAN-20260716-oteryn-account-character-lifecycle-revalidation.md
  - docs/agents/OTERYN_OAM_005_ACCOUNT_CHARACTER_LIFECYCLE_REVALIDATION.md
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
proven:
  - OAM-004 feature and lifecycle are complete
  - Canary task-start main is c2ffe09dc8753734be00c3433fab6f2ebe25d2e8
  - Canary integration base includes CI 415 at 0f25e7fd4d41e90f17fc95d13dba84b7e81d1681
  - Otheryn task-start main is 67212530b03c10175da2c0d9eabcee8991a05924
  - upstream evidence head is e0ac98e399d0f7e483f3668f57b78fcc45b6e53f
  - account cpp and account repository core files checked are content-identical across legacy target and upstream
  - legacy LoginSessionManager is absent from target and upstream
  - legacy secure-session primitive PR 77 merged as 3c5268fe86fd9785e3feea192d70c8bd3d51ef87
  - Otheryn PR 19 is the bounded primitive-only target adaptation
  - wire-level auth integration remains excluded until OAM-006
derived:
  - account-lifecycle is a REUSE candidate
  - account-authentication requires ADAPT
  - character-lifecycle must preserve OAM-004 persistence semantics and defer protocol wiring
unknown:
  - final Otheryn PR 19 exact-head ready CI and merge SHA
  - final OAM-005 Canary governance merge SHA
  - final OAM-005 lifecycle merge SHA
conflicts: []
first_failure:
  marker: none active
  evidence: earlier checkpoint status and stale pre-CI-415 branch-base failures were corrected; active task now uses repository-valid implementing status
rejected_hypotheses:
  - all TSD-003 progression modules belong to OAM-005
  - protocol packet wiring can be merged into OAM-005
  - account authentication can be marked REUSE despite missing target primitive
  - OAM-004 persistence boundaries can be reverted for lifecycle convenience
changed_paths:
  - docs/agents/tasks/active/CAN-20260716-oteryn-account-character-lifecycle-revalidation.md
  - docs/agents/OTERYN_OAM_005_ACCOUNT_CHARACTER_LIFECYCLE_REVALIDATION.md
validation:
  - command: cross-repository blob comparison for account lifecycle core files
    result: PASS
    evidence: checked account.cpp account_repository.cpp and account_repository_db.cpp are identical across pinned revisions
blockers: []
next_action: Complete exact-head validation and merge of Otheryn PR 19, then finalize OAM-005 dispositions and Canary governance while keeping OAM-006 inactive until separate lifecycle completion.
```
