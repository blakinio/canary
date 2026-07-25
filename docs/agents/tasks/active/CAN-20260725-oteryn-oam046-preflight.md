---
task_id: CAN-20260725-oteryn-oam046-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-046
status: review
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-046-configuration-preflight
base_branch: main
created: 2026-07-25
updated: 2026-07-25
last_verified_commit: "b733b0e42dbd0087c957b4fa8e5bcff2cba94708"
risk: high
related_issue: ""
related_pr: "911"
depends_on:
  - OAM-045 durably completed as d103add3c3a0f9cb026f3ec5b0aad73f13a71e18
blocks:
  - OAM-046 Otheryn target proof
  - OAM-046 Canary governance and lifecycle
  - OAM-046 durable program reconciliation
  - OAM-047 start
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260725-oteryn-oam046-preflight.md
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/real-tibia/registry/modules/configuration.yaml
    - docs/agents/real-tibia/generated/MODULE_DEPENDENCIES.md
modules_touched:
  - oteryn-architecture-migration
  - configuration
cross_repo_tasks: []
---

# OAM-046 configuration preflight

## Selection

`configuration → REVALIDATE`

Canonical scope is limited to typed configuration keys/access, `config.lua` loading/reload boundaries, default-distribution discovery and server/client feature-flag configuration under `src/config/**` and `config.lua.dist`. It excludes feature behavior controlled by those values, production configuration changes, secret management, protocol correctness and runtime feature validation.

## Fresh live preflight

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T10:00:00+02:00
head: b733b0e42dbd0087c957b4fa8e5bcff2cba94708
branch: dudantas/oam-046-configuration-preflight
pr: 911
status: validating
context_routes:
  - agent-governance
  - cross-repo
  - engine-foundation
owned_paths:
  - docs/agents/tasks/active/CAN-20260725-oteryn-oam046-preflight.md
proven:
  - OAM-045 durable reconciliation merged as d103add3c3a0f9cb026f3ec5b0aad73f13a71e18 before this task started.
  - Canary task-start main is 930e0a15767b7e5348bb36c679fa5e458a76f184.
  - Otheryn task-start main is e8f683e61427e9967cbc180b837220d4b7487d85 and has no open pull requests.
  - Reviewed current upstream is opentibiabr/canary@7323503b3dc61ed86bf1f04a611b2d0aec64b35a.
  - Open Canary PR 514 owns authenticated post-login sequence/XTEA transport validation and collides with network-transport.
  - login-protocol depends on network-transport and is therefore blocked.
  - physical-client-e2e, upstream-intelligence and wheel-of-destiny remain active under separate programs; deployment-operations and gameplay-analytics are broader platform surfaces.
  - configuration has no canonical depends_on edge and no active owner or open-PR path collision.
  - Target/upstream/legacy CMake root is blob 7a5a5058a22447091dd20e6190911e7f95937a98.
  - Target/upstream configmanager.hpp is blob c3027c491cbc326a3f66d2ed39a19ad7856ca6cf; live legacy is 8c1e90a7f0f1f894879b54a2de9971ffaeb48e1f.
  - Target/upstream config_enums.hpp is blob 1676d0ac445e4cd83e91fc57ca405b4a0dccfb55; live legacy is 4753549d77a2e97a774c90b3d2aed371f06f4e0d.
  - Target configmanager.cpp is blob 48c0637ba870cb25d119c16fc21d4134d6bdac15, upstream is b8d433b6a7f178864f4bd07c131fd78d5bccc832 and live legacy is 74c8a6f558257aa8bddf57f56116838390dcb25c.
  - Target retains package-external Forge defaults blob f5fab42df536304baa8fe034d2a7e8ac245204fd; upstream has no such file and live legacy has blob 7ebf71e9b6c47f3213aff229002aab9d5d116d60.
  - Target config.lua.dist is blob add3df239fb22592b7c63d166f880d0c31098ba2, upstream is 08ffe407ac4dadcfe787a13cc54df9c705565226 and live legacy is 021dc3e49aadbecead4d5b6d7d3b7ca6243b776e.
  - In all reviewed implementations, loadLuaOTCFeatures appends directly to enabledFeaturesOTC and disabledFeaturesOTC; repeated successful loads do not replace the previous feature snapshot.
  - Canary preflight PR 911 opened from b733b0e42dbd0087c957b4fa8e5bcff2cba94708.
derived:
  - Source identity alone cannot justify REUSE because target contains accepted earlier composition/Forge deltas and the reload state machine requires behavioral proof.
  - Repeated successful configuration loads can duplicate retained OTCR feature IDs and can preserve feature IDs removed from a later configuration.
  - The suspected defect is package-owned because it is entirely inside configuration snapshot loading and does not require changing controlled feature behavior.
unknown:
  - Whether focused target execution reproduces duplicate and stale OTCR feature snapshots deterministically.
  - Exhaustive key/default correspondence across target, upstream and legacy.
  - Concurrent reload safety and complete cache/read synchronization.
  - Production configuration, secret handling and environment-specific behavior.
  - Maintained-client interpretation and physical-client effects of every feature ID.
conflicts: []
first_failure:
  marker: non-idempotent-otcr-feature-load
  evidence: loadLuaOTCFeatures uses push_back for each parsed/default feature while neither load nor reload clears or atomically replaces enabledFeaturesOTC/disabledFeaturesOTC.
rejected_hypotheses:
  - Select network-transport while PR 514 owns an overlapping authenticated transport surface.
  - Select login-protocol before network-transport is dependency-valid.
  - Finalize REUSE from shared CMake/header blobs or successful compilation alone.
  - Treat Forge defaults or legacy multichannel keys as configuration-owned migration defects without package-specific evidence.
  - Expand this task into feature behavior, secrets, deployment policy, protocol correctness or generic concurrent configuration redesign.
changed_paths:
  - docs/agents/tasks/active/CAN-20260725-oteryn-oam046-preflight.md
validation:
  - command: fresh live-state, open-PR, ownership and dependency review
    result: PASS
    evidence: configuration is dependency-valid and unowned; network/login candidates remain blocked by PR 514 and dependency order.
  - command: exact target/upstream/live-legacy root review
    result: PASS
    evidence: Exact repository SHAs and canonical file blobs are pinned above.
blockers:
  - Canary preflight exact-head validation and merge
  - Otheryn focused target proof
  - Canary governance/lifecycle and durable reconciliation
next_action: Mark PR 911 ready, require exact-head Agent Task Ownership and CI, audit discussions and Canary-main drift, then squash-merge with the expected head before starting the Otheryn target proof.
```
