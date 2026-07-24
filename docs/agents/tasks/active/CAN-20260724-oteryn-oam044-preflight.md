---
task_id: CAN-20260724-oteryn-oam044-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-044
status: ready
agent: "GPT-5.6 Thinking"
branch: docs/oam-044-compact-handover
base_branch: main
created: 2026-07-24
updated: 2026-07-24
last_verified_commit: "e58c9347aebef1032bf3a1659d543b1cf6a00297"
risk: high
related_issue: ""
related_pr: "883"
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
updated_at: 2026-07-24T17:47:20+02:00
head: e58c9347aebef1032bf3a1659d543b1cf6a00297
branch: docs/oam-044-compact-handover
pr: 883
status: ready
context_routes:
  - agent-governance
  - cross-repo
  - protocol-client
owned_paths:
  - docs/agents/tasks/active/CAN-20260724-oteryn-oam044-preflight.md
proven:
  - OAM-044 preflight PR 879 merged to main as 47611c10be8a2262d66421c9da65de6cc5c7264d, selecting protocol-compatibility with disposition REVALIDATE and no target or runtime mutation.
  - Final PR 879 head bc4728f0c30483e8b3ed5564b183c05b6d86539a passed Agent Task Ownership run 30104167985 and full CI run 30104168121; the PR changed exactly one active task record.
  - protocol-compatibility has no hard dependency and directly unblocks protocol-session-handoff; Canary PR 514 remains the interacting owner for authenticated sequence and XTEA transport validation.
  - Otheryn and reviewed current-upstream share protocol_profile.hpp blob b9f1eec01e1ba348c22315be43ccefe74b210e45 and protocol_profile.cpp blob 5405c343cfa2c2d75a173d6678ecf8afc7690120.
  - Legacy Canary diverges with protocol_profile.hpp blob d045189c02eedfc0c3c4d03c37052cc34390e5ae and protocol_profile.cpp blob d89d951c469547370ef4346b133e7c7e32a257cf.
  - Maintained-client modules/game_features/features.lua blob 8b458b864ad765185fd856414f2c097d565a5a22 contains version-gated GameFeature enablement.
  - OAM-006 physical run 29531221365 proves two current-profile protocol-1525 login/relog cycles, and its tested server/client blobs remain identical to the selected current-profile roots.
  - TSD-010 treats ProtocolFeature and GameFeature as separate inventories and requires explicit mappings plus paired fixtures or captures for compatibility claims.
derived:
  - Target proof may lead with bounded REUSE only for the source-continuous current profile; Tibia 11.00 and 8.60 variants remain REVALIDATE.
  - Target proof must preserve network-transport, login-protocol, protocol-session-handoff and broad protocol ownership boundaries.
unknown:
  - Exact one-to-one or many-to-one correspondence between every ProtocolFeature bit and maintained-client GameFeature gate.
  - Exact compatibility of version, wire-family, RSA-family, asset-signature, challenge and login-layout combinations outside the proven current profile.
  - Which legacy profile metadata belongs to protocol-compatibility versus network-transport or login-protocol.
  - Availability and provenance of representative official or proprietary client fixtures and captures.
  - Physical-client login and world-entry parity for Tibia 11.00, CipSoft 8.60 variants and blocked OTCv8 8.60.
conflicts: []
first_failure:
  marker: none
  evidence: No protocol-compatibility-owned target defect has been isolated; preflight completed without implementation.
rejected_hypotheses:
  - Finalize protocol-compatibility as REUSE from target and upstream protocol_profile blob identity alone.
  - Extend the OAM-006 current-profile physical result to Tibia 11.00 or 8.60 profiles.
  - Treat similar ProtocolFeature and GameFeature names as semantic or byte-layout equivalence.
  - Absorb socket, framing, checksum, sequence, XTEA or compression work owned by network-transport.
  - Absorb login serialization, authentication or session-handoff state into this package.
changed_paths:
  - docs/agents/tasks/active/CAN-20260724-oteryn-oam044-preflight.md
validation:
  - command: PR 879 exact-head Agent Task Ownership
    result: PASS
    evidence: Run 30104167985 succeeded on bc4728f0c30483e8b3ed5564b183c05b6d86539a.
  - command: PR 879 exact-head full CI
    result: PASS
    evidence: Run 30104168121 succeeded on bc4728f0c30483e8b3ed5564b183c05b6d86539a.
  - command: PR 879 merge and scope verification
    result: PASS
    evidence: PR 879 merged as 47611c10be8a2262d66421c9da65de6cc5c7264d and changed one task record.
  - command: python tools/agents/checkpoint.py docs/agents/tasks/active/CAN-20260724-oteryn-oam044-preflight.md --require-checkpoint
    result: PASS
    evidence: Compact checkpoint validated locally before the final handover commit.
blockers: []
next_action: Create a dedicated OAM-044 target-proof branch from main 47611c10be8a2262d66421c9da65de6cc5c7264d, update this task ownership and PR identity, then execute phase 1 exact source inventory without mutating transport, login, handoff or runtime surfaces.
```
