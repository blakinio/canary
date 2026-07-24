---
task_id: CAN-20260724-oteryn-oam044-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-044
status: review
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-044-protocol-compatibility-preflight
base_branch: main
created: 2026-07-24
updated: 2026-07-24
last_verified_commit: "422a97ceea07b91254b66411f7baf2c6896ccc85"
risk: high
related_issue: ""
related_pr: "879"
depends_on:
  - OAM-043 durably completed as 9d99a0665050d244a0ee0beb0362080de0f3d19a
  - canonical protocol completed by OAM-006
blocks:
  - OAM-044 target proof and final disposition
  - OAM-045 start
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260724-oteryn-oam044-preflight.md
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/real-tibia/registry/modules/protocol-compatibility.yaml
    - docs/agents/real-tibia/TSD_010_PROTOCOL_CLIENT_REPORT.md
    - docs/agents/real-tibia/generated/MODULE_INDEX.md
    - docs/agents/real-tibia/generated/MODULE_DEPENDENCIES.md
modules_touched:
  - oteryn-architecture-migration
  - protocol-compatibility
cross_repo_tasks: []
---

# OAM-044 Fresh Preflight

## Selected package

`protocol-compatibility` is the selected dependency-valid OAM-044 canonical package.

Preflight disposition: `REVALIDATE`.

No leading `REUSE`, `ADAPT`, `REWRITE` or `DO_NOT_MIGRATE` hypothesis is accepted before a separately ordered target proof compares the exact server profile registry with the maintained-client feature matrix and establishes bounded paired compatibility fixtures. Target/current-upstream server blob identity is inventory evidence only; it does not prove server/client feature, version, asset, handshake or packet-layout equivalence.

Canonical `protocol-compatibility` owns server protocol-profile and support-state discovery, client version and asset-signature profile resolution, account/game login-layout metadata, transport/challenge selection metadata, server feature masks and the maintained-client version-gated feature matrix. It excludes individual gameplay behavior, broad packet implementation, transport runtime ownership, login authentication and physical-client orchestration.

The package has no hard dependency and directly unblocks canonical `protocol-session-handoff`. `network-transport` is also dependency-valid, but open Canary PR #514 owns authenticated post-login sequence/XTEA validation and creates a live evidence/ownership interaction; OAM-044 therefore selects the narrower collision-free compatibility-profile boundary first.

This preflight performs no target, server runtime, maintained-client, transport, login, packet, protocol, schema, asset or deployment mutation.

## Required target-proof phases

1. **Exact source inventory**
   - pin Otheryn, current-upstream, legacy Canary and maintained-client revisions;
   - compare exact `protocol_profile.*` blobs and the maintained-client `modules/game_features/**` inventory;
   - classify target/upstream/legacy-only and divergent profile, feature, version and asset metadata without importing broad transport/login behavior.

2. **Semantic compatibility matrix**
   - inventory every server profile ID, client version, wire family, RSA family, support state, item-mapper policy, asset signature, transport/challenge profile, login layout and `ProtocolFeature` bit;
   - inventory every maintained-client version gate and enabled `GameFeature` with exact source provenance;
   - classify mappings as confirmed, server-only, client-only, conflicting or unresolved; never infer equivalence from similar names.

3. **Bounded paired fixtures**
   - prove server resolution by version, wire family and asset signatures;
   - prove allowed/blocked support decisions and account/game login-layout selection;
   - prove deterministic maintained-client feature sets for selected current and legacy versions;
   - add explicit fixtures only where both sides expose a bounded reviewed contract.

4. **Ownership boundaries**
   - leave socket/framing/checksum/sequence/XTEA/compression behavior to `network-transport`;
   - leave account-login request/response serialization to `login-protocol`;
   - leave hint registration/lease/consume/expiry to `protocol-session-handoff`;
   - leave broad game packet semantics to completed canonical `protocol`.

5. **Conditional runtime evidence**
   - reuse the exact OAM-006 physical current-profile proof only where the selected server/client roots are byte-identical;
   - use additional packet captures or bounded physical-client login/world-entry proof only where exact source and paired fixtures cannot resolve a selected compatibility claim;
   - retain unsupported versions, unmapped features and unavailable proprietary fixtures as explicit unknowns rather than guessing.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T17:14:00+02:00
head: 422a97ceea07b91254b66411f7baf2c6896ccc85
branch: dudantas/oam-044-protocol-compatibility-preflight
pr: 879
status: validating
context_routes:
  - agent-governance
  - cross-repo
  - protocol-client
owned_paths:
  - docs/agents/tasks/active/CAN-20260724-oteryn-oam044-preflight.md
proven:
  - OAM-043 quests ADAPT is durably complete after Otheryn feature 6512d78004ae2540784b3e67592a92a903554cf6, Otheryn lifecycle 3f3c15917610e45430aa3902d110806dd25e10a8, Canary governance 6e55eab72b6f7b164bb38ba2e08fa1a80cf5f8e5, Canary lifecycle 6e223c142f34285b98ea70d79131c79b1680e2d0 and durable reconciliation 9d99a0665050d244a0ee0beb0362080de0f3d19a.
  - Fresh Canary task-start main is a5cafe1b7ce148af59c64d1382963ac6ac633334; its only initial post-OAM-043 drift was independent E2E packet-record path redaction.
  - Fresh Otheryn target main is 3f3c15917610e45430aa3902d110806dd25e10a8, reviewed current-upstream Canary is 7323503b3dc61ed86bf1f04a611b2d0aec64b35a and maintained OTClient is b3bcea2a95959bb4e92cc0b80cd49f36b63699b2.
  - The canonical registry contains 62 modules; after OAM-003 through OAM-043 coverage, nine records remain outside durable OAM completion.
  - Canonical protocol-compatibility registry blob 5fba5a2712aa17db68c5edba2a913ed09fa51a09 declares category client-protocol and no hard dependency.
  - protocol-compatibility directly interacts with and unblocks protocol-session-handoff, whose hard dependency is protocol-compatibility.
  - Otheryn and reviewed current-upstream share exact protocol_profile.hpp blob b9f1eec01e1ba348c22315be43ccefe74b210e45 and protocol_profile.cpp blob 5405c343cfa2c2d75a173d6678ecf8afc7690120.
  - Legacy Canary diverges on protocol_profile.hpp blob d045189c02eedfc0c3c4d03c37052cc34390e5ae and protocol_profile.cpp blob d89d951c469547370ef4346b133e7c7e32a257cf, including a more granular current transport-profile split that must not be imported into this package without ownership review.
  - Maintained-client modules/game_features/features.lua blob is 8b458b864ad765185fd856414f2c097d565a5a22 and contains version-gated GameFeature enablement.
  - OAM-006 physical run 29531221365 passed two current-profile protocol-1525 login/relog cycles against Otheryn c547d8ad70ef1252624c255476e6cb83fa125e14 and maintained client 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f.
  - The OAM-006 tested protocol_profile.hpp, protocol_profile.cpp and maintained-client features.lua blobs are still exactly b9f1eec01e1ba348c22315be43ccefe74b210e45, 5405c343cfa2c2d75a173d6678ecf8afc7690120 and 8b458b864ad765185fd856414f2c097d565a5a22; bounded current-profile source/runtime continuity is therefore proven without claiming 1100/860 parity.
  - TSD-010 explicitly treats server ProtocolFeature and client GameFeature records as inventories, not one-to-one semantic or byte-contract proof, and requires paired fixtures or captures for compatibility claims.
  - Fresh exact branch searches found no prior OAM-044 or protocol-compatibility owner in Canary or Otheryn; Otheryn has no open PRs.
  - Open Canary PR #514 owns authenticated game-session sequence/XTEA validation, so network-transport was rejected as the collision-free first OAM-044 choice.
  - Canary PR 879 changes exactly this active task record and carries the ci:final-gate label before its synchronization commits.
  - Ready head 422a97ceea07b91254b66411f7baf2c6896ccc85 passed Agent Task Ownership 30102398900 and full CI 30102410130 across Fast Checks, Lua, Linux release/debug with tests and runtime smokes, Windows CMake/Solution and Docker.
derived:
  - protocol-compatibility is the narrowest dependency-valid remaining canonical boundary with no live owner and advances the dependency graph by unblocking protocol-session-handoff.
  - Exact target/upstream server identity and unchanged OAM-006 tested current-profile roots support bounded REUSE as the target-proof leading hypothesis only; legacy divergence and independent 1100/860 evidence still require REVALIDATE.
  - A safe final disposition requires explicit server/client mapping and bounded fixtures while preserving transport, login and handoff ownership boundaries.
unknown:
  - Exact one-to-one or many-to-one correspondence between every ProtocolFeature bit and maintained-client GameFeature gate.
  - Exact compatibility of version, wire-family, RSA-family, asset-signature, challenge and login-layout combinations outside the proven current-profile boundary.
  - Which legacy profile metadata is stronger evidence versus network-transport or login-protocol scope.
  - Exact current and legacy packet layouts for every registered profile.
  - Availability and provenance of representative official/proprietary client fixtures or captures.
  - Physical-client login/world-entry parity for Tibia 11.00, CipSoft 8.60 variants and blocked OTCv8 8.60.
conflicts: []
first_failure:
  marker: none
  evidence: No protocol-compatibility-owned target defect has been isolated during preflight.
rejected_hypotheses:
  - Finalize protocol-compatibility as REUSE from target/upstream protocol_profile blob identity alone.
  - Extend the OAM-006 current-profile physical result to Tibia 11.00 or 8.60 profiles.
  - Treat similar ProtocolFeature and GameFeature names as semantic or byte-layout equivalence.
  - Absorb socket/framing/checksum/sequence/XTEA/compression work owned by network-transport.
  - Absorb login serialization/authentication or session-handoff state into this package.
  - Select network-transport while open PR 514 owns interacting authenticated transport validation.
changed_paths:
  - docs/agents/tasks/active/CAN-20260724-oteryn-oam044-preflight.md
validation:
  - command: live canonical registry and dependency review
    result: PASS
    evidence: Generated module and dependency indexes preserve 62 canonical records; protocol-compatibility has no hard dependency and protocol-session-handoff depends on it.
  - command: exact target/upstream/legacy/client source preflight
    result: PASS
    evidence: Exact Git blobs establish target/upstream identity, legacy divergence, maintained-client feature inventory and bounded OAM-006 current-profile continuity without asserting broad compatibility.
  - command: live branch, PR and ownership preflight
    result: PASS
    evidence: No prior OAM-044/protocol-compatibility branch or PR owner existed; open PR 514 is retained as an interacting network-transport constraint.
  - command: PR 879 ready-head Agent Task Ownership and final-gate CI
    result: PASS
    evidence: Head 422a97ceea07b91254b66411f7baf2c6896ccc85 passed Agent Task Ownership 30102398900 and CI 30102410130.
  - command: PR 879 synchronization-head exact gates
    result: NOT_RUN
    evidence: This validation-only synchronization commit must pass exact-head ownership and CI before merge.
blockers: []
next_action: Require exact-head Agent Task Ownership and final-gate CI on this validation-only synchronization commit, audit comments, reviews, threads and Canary-main drift, then squash-merge PR 879 with the expected head.
```
