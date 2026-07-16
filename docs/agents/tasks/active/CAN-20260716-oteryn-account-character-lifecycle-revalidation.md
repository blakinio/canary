---
task_id: CAN-20260716-oteryn-account-character-lifecycle-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: "OAM-005"
status: ready
agent: oteryn-architecture-migration-agent
branch: docs/oam-005-account-character-lifecycle-revalidation
base_branch: main
created: 2026-07-16T19:58:30+02:00
updated: 2026-07-16T20:20:00+02:00
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
    - blakinio/Otheryn@a6d42f6cec024f81a7541084425ec1d43d66d2b8
    - blakinio/canary@c2ffe09dc8753734be00c3433fab6f2ebe25d2e8
    - blakinio/canary@0f25e7fd4d41e90f17fc95d13dba84b7e81d1681
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

# Final dispositions

| Module | Disposition | Result |
|---|---|---|
| `account-lifecycle` | `REUSE` | checked account implementation/repository blobs are identical across legacy, target task-start and upstream |
| `account-authentication` | `ADAPT` | bounded secure login-session primitive delivered by Otheryn PR #19; wire integration remains OAM-006 work |
| `character-lifecycle` | `ADAPT` | preserve OAM-004D player persistence boundaries; authenticated account handoff remains a protocol-coupled OAM-006 seam |

# Proven target delivery

- Otheryn task-start: `67212530b03c10175da2c0d9eabcee8991a05924`.
- Otheryn PR #19 exact head: `2a2e1e5e22df697435e705d8a19d69dcbc46bbfd`.
- Ready-triggered CI #76: PASS.
- Required #75: PASS.
- autofix.ci #68: PASS.
- Linux release, Linux debug tests, macOS and Windows gates passed.
- Final comments, submitted reviews and unresolved review threads were empty.
- PR #19 squash-merged with exact-head guard as `a6d42f6cec024f81a7541084425ec1d43d66d2b8`.
- `Otheryn:main` verified identical to `a6d42f6cec024f81a7541084425ec1d43d66d2b8`.
- Otheryn issue #17 closed as completed.
- Parent Otheryn issue #15 remains open until OAM-005 feature governance and lifecycle completion.

# Safety boundary

- Do not touch production credentials or databases.
- Do not weaken password authentication or DB-backed `account_sessions` fallback behavior.
- Do not modify login/game packet layouts in OAM-005.
- Do not wire `ProtocolLogin` or `ProtocolGame` in OAM-005.
- Do not undo OAM-004A/B/C/D persistence behavior.
- Do not claim the login-session primitive is live on the wire before OAM-006 integration.
- Do not start OAM-006 before OAM-005 feature and lifecycle completion.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T20:20:00+02:00
head: 06069382e5894a04c2f935923c79fafcf3d19980
branch: docs/oam-005-account-character-lifecycle-revalidation
pr: 432
status: ready
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
  - account lifecycle core blobs checked are identical across task-start target legacy and upstream
  - account-lifecycle disposition is REUSE
  - account-authentication disposition is ADAPT
  - character-lifecycle disposition is ADAPT
  - Otheryn PR 19 exact head 2a2e1e5e22df697435e705d8a19d69dcbc46bbfd passed CI 76 Required 75 and autofix 68
  - Otheryn PR 19 had no comments submitted reviews or unresolved review threads at final gate
  - Otheryn PR 19 merged as a6d42f6cec024f81a7541084425ec1d43d66d2b8
  - Otheryn main is identical to a6d42f6cec024f81a7541084425ec1d43d66d2b8
  - Otheryn issue 17 is closed as completed
  - wire-level authentication integration remains excluded until OAM-006
derived:
  - OAM-005 target delivery is complete
  - remaining work is Canary feature governance followed by separate lifecycle archive
  - OAM-006 remains inactive until both remaining OAM-005 merges complete
unknown:
  - final OAM-005 Canary governance merge SHA
  - final OAM-005 lifecycle merge SHA
conflicts: []
first_failure:
  marker: none active
  evidence: target delivery and draft governance validation are green; final governance exact-head ready gate remains
rejected_hypotheses:
  - all TSD-003 progression modules belong to OAM-005
  - protocol packet wiring can be merged into OAM-005
  - account authentication can be marked REUSE despite missing target primitive
  - OAM-004 persistence boundaries can be reverted for lifecycle convenience
  - LoginSessionManager presence alone proves live authentication hardening
changed_paths:
  - docs/agents/OTERYN_OAM_005_ACCOUNT_CHARACTER_LIFECYCLE_REVALIDATION.md
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
  - docs/agents/tasks/active/CAN-20260716-oteryn-account-character-lifecycle-revalidation.md
validation:
  - command: cross-repository blob comparison for account lifecycle core files
    result: PASS
    evidence: checked account.cpp account_repository.cpp and account_repository_db.cpp are identical across pinned task-start revisions
  - command: Otheryn PR 19 ready-triggered CI 76
    result: PASS
    evidence: completed success on head 2a2e1e5e22df697435e705d8a19d69dcbc46bbfd
  - command: Otheryn PR 19 Required 75
    result: PASS
    evidence: completed success on head 2a2e1e5e22df697435e705d8a19d69dcbc46bbfd
  - command: Otheryn PR 19 autofix.ci 68
    result: PASS
    evidence: completed success on head 2a2e1e5e22df697435e705d8a19d69dcbc46bbfd
  - command: Canary PR 432 draft Agent Task Ownership 1692 and CI 2831
    result: PASS
    evidence: completed success before final target-delivery documentation refresh
blockers: []
next_action: Update the authoritative program record, verify PR 432 exact scope and ownership, mark it ready, use the latest ready-triggered exact-head final gate, then squash-merge with exact-head guard and complete a separate lifecycle archive before starting OAM-006.
```
