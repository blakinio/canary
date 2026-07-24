---
task_id: CAN-20260724-oteryn-oam044-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-044
status: review
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-044-protocol-compatibility-governance
base_branch: main
created: 2026-07-24
updated: 2026-07-24
last_verified_commit: "e1eed52119ba21a29cb29cbac0793ed2a2b9d0c6"
risk: high
related_issue: ""
related_pr: "888"
depends_on:
  - OAM-043 durably completed as 9d99a0665050d244a0ee0beb0362080de0f3d19a
  - canonical protocol completed by OAM-006
blocks:
  - OAM-044 Canary lifecycle archive
  - OAM-044 durable program reconciliation
  - OAM-045 start
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260724-oteryn-oam044-preflight.md
    - docs/agents/OTERYN_OAM_044_PROTOCOL_COMPATIBILITY_REVALIDATION.md
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/real-tibia/registry/modules/protocol-compatibility.yaml
    - docs/agents/real-tibia/TSD_010_PROTOCOL_CLIENT_REPORT.md
modules_touched:
  - oteryn-architecture-migration
  - protocol-compatibility
cross_repo_tasks:
  - Otheryn PR 100 feature merge 5c8f48e2a7cb7f841cfb6614e8e804245f17c0ca
  - Otheryn PR 101 lifecycle merge e1eed52119ba21a29cb29cbac0793ed2a2b9d0c6
---

# OAM-044 protocol compatibility revalidation

## Final disposition

`protocol-compatibility → REUSE`

The separately ordered Otheryn proof retained the exact target/current-upstream protocol-profile registry without production mutation. Bounded current-profile source continuity, inherited OAM-006 physical evidence and focused profile fixtures support REUSE. Tibia 11.00/8.60 physical parity, exhaustive feature mapping and transport/login/session-handoff behavior remain explicit nonclaims.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T19:25:00+02:00
head: 1bd7ef9724f498b3399809f1381bc69786f3eb57
branch: dudantas/oam-044-protocol-compatibility-governance
pr: 888
status: validating
context_routes:
  - agent-governance
  - cross-repo
  - protocol-client
owned_paths:
  - docs/agents/tasks/active/CAN-20260724-oteryn-oam044-preflight.md
  - docs/agents/OTERYN_OAM_044_PROTOCOL_COMPATIBILITY_REVALIDATION.md
proven:
  - OAM-043 quests ADAPT is durably complete through program reconciliation 9d99a0665050d244a0ee0beb0362080de0f3d19a.
  - Canary OAM-044 preflight selected canonical protocol-compatibility with REVALIDATE and merged as 47611c10be8a2262d66421c9da65de6cc5c7264d.
  - Otheryn target task-start was 3f3c15917610e45430aa3902d110806dd25e10a8; reviewed upstream was 7323503b3dc61ed86bf1f04a611b2d0aec64b35a; legacy Canary was a5cafe1b7ce148af59c64d1382963ac6ac633334; maintained client was b3bcea2a95959bb4e92cc0b80cd49f36b63699b2.
  - Target and reviewed current-upstream share protocol_profile.hpp blob b9f1eec01e1ba348c22315be43ccefe74b210e45 and protocol_profile.cpp blob 5405c343cfa2c2d75a173d6678ecf8afc7690120.
  - Maintained-client modules/game_features/features.lua blob is 8b458b864ad765185fd856414f2c097d565a5a22.
  - OAM-006 physical run 29531221365 passed two protocol-1525 login/relog cycles on server/client roots byte-identical to the current OAM-044 roots.
  - Legacy Canary diverges at the server registry roots and contains transport-owned hardening rejected from this package.
  - The target registry exposes six profiles and the focused test covers profile manifest, version/wire-family/asset resolution, support states, item-mapper policies, selected current feature pairs and bounded current/1100/860 login metadata.
  - Otheryn feature ready head 29d196e1b7d084813e24d368bd9e70329e16d0b3 passed Autofix 30106675779, CI 30106676001 and Required 30106675816.
  - Otheryn feature final-sync head 62a42372e2225b71aaa0066cc934f684e830913c passed Autofix 30111297337, CI 30111297597 and Required 30111297475.
  - Otheryn PR 100 had no comments, reviews or review threads, no target-main drift and squash-merged as 5c8f48e2a7cb7f841cfb6614e8e804245f17c0ca.
  - Otheryn lifecycle PR 101 changed one logical active/archive path, passed Required 30112638532, had a clean audit and merged as e1eed52119ba21a29cb29cbac0793ed2a2b9d0c6.
  - Canary governance task-start main is ad8b978236e6dfa8c40b06170f19f281b84b395d; intervening OTS/native-auth/content-reference merges do not overlap the OAM-044 governance paths.
  - Canary PR 888 changes exactly the governance report and active checkpoint and carries ci:final-gate before this synchronization commit.
  - docs/agents/OTERYN_OAM_044_PROTOCOL_COMPATIBILITY_REVALIDATION.md records the exact evidence and nonclaim boundaries.
derived:
  - protocol-compatibility supports bounded REUSE because no package-owned target defect was isolated and the current profile retains exact source/runtime continuity.
  - Tibia 11.00 and 8.60 remain source-fixture boundaries rather than physical parity claims.
  - Legacy transport-profile differences remain assigned to network-transport and login-protocol.
unknown:
  - Exhaustive one-to-one or many-to-one correspondence between every ProtocolFeature and GameFeature.
  - Byte-level compatibility for every packet and registered profile.
  - Provenance and factual correctness of every proprietary asset signature.
  - Physical-client login/world-entry parity for Tibia 11.00 and CipSoft 8.60 variants.
  - OTCv8 8.60 readiness.
  - Production gameplay parity and full protocol-stack readiness.
conflicts: []
first_failure:
  marker: none
  evidence: No protocol-compatibility-owned target defect was isolated.
rejected_hypotheses:
  - Finalize REUSE from server blob identity alone without paired fixtures and physical continuity review.
  - Import legacy transport-profile splitting into protocol-compatibility.
  - Infer semantic compatibility from similar server/client feature names.
  - Extend OAM-006 current-profile physical evidence to legacy profiles.
  - Absorb network transport, login authentication or session-handoff behavior.
  - Treat blocked OTCv8 8.60 as ready.
changed_paths:
  - docs/agents/tasks/active/CAN-20260724-oteryn-oam044-preflight.md
  - docs/agents/OTERYN_OAM_044_PROTOCOL_COMPATIBILITY_REVALIDATION.md
validation:
  - command: exact target/upstream/legacy/client source and ownership review
    result: PASS
    evidence: Exact roots, divergence and bounded ownership are recorded in the governance report.
  - command: Otheryn focused protocol compatibility contract
    result: PASS
    evidence: CI runs 30106676001 and 30111297597 compiled and executed the registered unit-test matrix.
  - command: Otheryn feature exact-head gates and audit
    result: PASS
    evidence: Ready and final-sync heads passed Autofix, CI and Required; discussions were empty and no main drift occurred before merge 5c8f48e2a7cb7f841cfb6614e8e804245f17c0ca.
  - command: Otheryn lifecycle gate and audit
    result: PASS
    evidence: PR 101 passed Required 30112638532 and merged as e1eed52119ba21a29cb29cbac0793ed2a2b9d0c6 after clean audit.
  - command: Canary governance exact-head gates and audit
    result: NOT_RUN
    evidence: Final PR 888 head must pass Agent Task Ownership and final-gate CI before merge.
blockers:
  - Canary governance PR 888 merge
  - Canary lifecycle archive merge
  - durable OAM-044 program reconciliation
next_action: Require exact-head Agent Task Ownership and final-gate CI on PR 888, audit comments, reviews, threads and Canary-main drift, then squash-merge with the expected head.
```
