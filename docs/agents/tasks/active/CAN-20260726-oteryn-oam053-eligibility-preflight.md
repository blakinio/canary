---
task_id: CAN-20260726-oteryn-oam053-eligibility-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-053
status: implementing
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-053-network-transport-preflight
base_branch: main
created: 2026-07-26
updated: 2026-07-27
last_verified_commit: "f14b2e26536b191504ae5b0428ef5f8814ffdbcd"
risk: high
related_issue: ""
related_pr: "979"
depends_on:
  - OAM-052 durable program reconciliation merged as 4dac672b7d7cd67e467411c3c27c85b47f736833
  - SEC-005 lifecycle merged as ba08e346540f017773b9268832d304c7f5664ac2
blocks:
  - OAM-053 target proof and lifecycle
  - OAM-054 login-protocol start
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260726-oteryn-oam053-eligibility-preflight.md
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/real-tibia/registry/modules/network-transport.yaml
    - docs/agents/real-tibia/registry/modules/login-protocol.yaml
    - docs/agents/programs/SECURITY_VALIDATION_PROGRAM.md
    - docs/security/SECURITY_VALIDATION_SEC005.md
    - docs/security/SECURITY_VALIDATION_SEC005_HANDOVER.md
    - src/server/network/connection/**
    - src/server/network/protocol/**
    - src/server/network/message/outputmessage.hpp
    - tests/unit/server/network/protocol/**
    - blakinio/Otheryn
    - blakinio/otclient
modules_touched:
  - oteryn-architecture-migration
cross_repo_tasks: []
---

# OAM-053 network transport preflight

## Result

```text
OAM-053 → network-transport
preflight → REVALIDATE
leading target hypothesis → ADAPT
```

The prior ownership blocker is resolved. PR #514 was closed unmerged as superseded after SEC-005 recovery PR #974 merged and lifecycle PR #977 made the evidence durable.

The target proof must not replace Otheryn's entire connection or protocol layer. It must preserve current Otheryn profile/session-handoff work and adapt only evidence-backed transport authority, framing and rejection/recovery invariants from the pinned donors.

## Selected target-proof boundary

Included:

- complete `TransportProfile` authority for framing, checksum, sequence and compression;
- distinct current login, sequenced-game and checksum-free-game transport profiles;
- exact checksum-free modern block-count encode/decode symmetry;
- complete first modern game-frame sizing;
- typed inbound rejection outcomes;
- sequence state mutation only after complete checksum/decrypt acceptance;
- bounded guards for truncated checksum/header, invalid block size, missing inner length/padding and oversized padding;
- deterministic target tests plus applicable exact-head runtime validation.

Excluded:

- wholesale `Connection` or `ProtocolGame` replacement;
- account authentication, character-list or login response semantics;
- game opcode layouts and gameplay dispatch;
- legacy-client parity beyond existing target profiles;
- session lifecycle races, economy, Redis/multichannel, hostile-server client testing, sustained load or production claims;
- arbitrary packet, credential, target or command surfaces.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-27T00:25:00+02:00
head: f14b2e26536b191504ae5b0428ef5f8814ffdbcd
branch: dudantas/oam-053-network-transport-preflight
pr: 979
status: implementing
context_routes:
  - agent-governance
  - cross-repo
  - cpp-runtime
  - security
owned_paths:
  - docs/agents/tasks/active/CAN-20260726-oteryn-oam053-eligibility-preflight.md
proven:
  - OAM-001 through OAM-052 are durably complete and network-transport is the only dependency-free unresolved canonical record.
  - Canary main is ba08e346540f017773b9268832d304c7f5664ac2; Otheryn is 64ad965eee40f62ff996980fd8a0d329245c519f; upstream Canary is 7644bcbcbbad4a09e52a5707ed531e4dd21d8a79; maintained OTClient is 5568cb6f5e2fd6162c78cde304deea5d32461e05.
  - PR 514 is closed unmerged as superseded; PR 974 merged SEC-005 as 1408aaa886240034a90fc33873e9b9e0fa47cab6 and lifecycle PR 977 merged as ba08e346540f017773b9268832d304c7f5664ac2.
  - SEC-005 exact-head Security Validation 30220958474 passed with five case probes five fresh controls and no fatal findings.
  - The canonical network-transport record has no dependencies and login-protocol depends on it.
  - No open Otheryn PR owns connection protocol transport codec or XTEA paths; open PR 162 is bounded module-composition work and excludes protocol wire changes.
  - Otheryn transport_codec.cpp blob 23804d0b267773246547882fc612756983170e69 matches upstream and differs from legacy blob 787a3370b734dc84b66442c5d62fb0977f6544a2.
  - Otheryn connection.cpp blob 2633410ab4408f4eb6aa8503460fd4a48d43434a matches upstream and differs from legacy blob f9953a07e46b73c1507f457557fd272a82911c8d.
  - Otheryn currently increments the accepted client sequence before complete frame validation and returns only bool; legacy records typed outcomes and commits sequence state only after decrypt acceptance.
  - Legacy PR 71 merged as bbff04524bbb99ab54c9571c24382399b904cbd8 and made transport profiles authoritative with focused regressions.
  - Legacy PR 155 merged as 4535836d4df0fc669033ed73f525754a1a2d1b40 and fixed checksum-free block-count symmetry.
  - Legacy PR 375 merged as 5c750e13fb95f46225807b8907a95ce3091283c8 and fixed the captured modern first game frame size without relaxing sequence validation.
derived:
  - Pure REUSE is rejected because current Otheryn lacks the proven rejection/recovery and framing fixes.
  - Wholesale legacy migration is rejected because target protocol profiles and session handoff have later OAM and MGE evolution.
  - The bounded target disposition is expected to be ADAPT by semantic integration of transport-only invariants and tests.
unknown:
  - Exact target file set after reconciling current GameProfile and session-handoff changes.
  - Whether full physical maintained-client validation is required beyond target unit/CI and reusable SEC-005 adapter evidence.
conflicts: []
first_failure:
  marker: stale-security-ownership
  result: FIXED
  evidence: SEC-005 recovered on current main, fully validated, merged, archived and PR 514 closed as superseded.
rejected_hypotheses:
  - keep OAM-053 blocked after ownership release
  - select login-protocol before its transport dependency
  - classify current target transport as REUSE without testing legacy-proven invariants
  - replace all connection/session lifecycle code from legacy
changed_paths:
  - docs/agents/tasks/active/CAN-20260726-oteryn-oam053-eligibility-preflight.md
validation:
  - command: dependency and ownership audit
    result: PASS
    evidence: network-transport is dependency-valid and no active PR owns its target paths.
  - command: four-repository baseline and donor audit
    result: PASS
    evidence: exact heads and donor merges pinned; target/upstream equality and legacy divergence confirmed.
  - command: target-gap review
    result: PASS
    evidence: sequence mutation timing and unchecked/truncated transport boundaries require bounded adaptation.
blockers: []
next_action: Merge this one-file preflight, then create a separately authorized Otheryn target task and implementation PR for the bounded ADAPT proof.
```
