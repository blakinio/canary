---
task_id: CAN-20260727-oteryn-oam054-login-protocol-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-054
status: ready
agent: "GPT-5.6 Thinking"
branch: docs/oam-054-compact-handover-20260727
base_branch: main
created: 2026-07-27
updated: 2026-07-27T11:04:00+02:00
last_verified_commit: "157c010204f4843c75ec4f5f3970b6253628506c"
risk: high
related_issue: ""
related_pr: "984"
depends_on:
  - OAM-053 durable programme reconciliation merged as 9d395a5563531dfc3d83f4a24361237137715000
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260727-oteryn-oam054-login-protocol-preflight.md
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/real-tibia/registry/modules/login-protocol.yaml
    - docs/agents/real-tibia/TSD_010_PROTOCOL_CLIENT_REPORT.md
    - docs/security/SECURITY_VALIDATION_SEC004.md
    - src/server/network/protocol/protocollogin.*
    - src/server/network/protocol/protocol_profile.*
    - src/server/network/protocol/protocol_session_hint.*
    - security/login_session_manager.*
    - tests/unit/server/network/protocol/**
    - blakinio/Otheryn
    - blakinio/otclient
modules_touched:
  - oteryn-architecture-migration
  - login-protocol
cross_repo_tasks:
  - OTH-20260727-oam054-login-protocol-adapt
---

# OAM-054 Login Protocol preflight

## Result

```text
OAM-054 → login-protocol
preflight → REVALIDATE
target disposition → ADAPT
target delivery → MERGED
```

`login-protocol` is dependency-valid because `account-authentication` and `network-transport` are durably complete. Otheryn PR 165 delivered the bounded ADAPT target while preserving secure login-session token issuance, multiprotocol request layouts and protocol-session handoff.

## Selected target-proof boundary

Included:

- current, 11.00 and 8.60 account-login request layout selection;
- bounded pre-RSA metadata validation and RSA/XTEA handoff;
- session-key opcode and fail-closed secure-token issuance;
- current world/character list and legacy character-list serialization;
- maintained-client parser correspondence, including the modern account-status/subscription/expiry tail;
- disconnect-after-response and deterministic target serialization/parser regressions.

Excluded:

- password hashing, credential policy or account repository ownership;
- game-world authentication, player attach/detach and gameplay opcode routing;
- multichannel expansion beyond existing target architecture;
- client UI/launcher flows, public endpoints, production credentials or deployment;
- proof of complete account/session security or universal server-client compatibility.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-27T11:04:00+02:00
head: 157c010204f4843c75ec4f5f3970b6253628506c
branch: docs/oam-054-compact-handover-20260727
pr: 984
status: ready
context_routes:
  - agent-governance
  - cross-repo
  - cpp-runtime
  - security
  - testing
owned_paths:
  - docs/agents/tasks/active/CAN-20260727-oteryn-oam054-login-protocol-preflight.md
proven:
  - PR 983 merged the OAM-054 preflight as d8eb3f5520b2a94e788a31e004bf1aa33b9d7c61 from exact head 7b0ba76e81ff958f9714bc12c8295357ec759faa; ownership run 30242303120 and CI run 30242303240 passed.
  - OAM-054 selected login-protocol as REVALIDATE with a bounded ADAPT target boundary.
  - Otheryn PR 165 merged at 2026-07-27T09:01:07Z from exact head f6db2136248b39ccd7aa57178a1c63c788b9bcec as merge commit e077c51fe948652a4849e15f6c518059f4370717.
  - Before merge, exact Otheryn head f6db2136248b39ccd7aa57178a1c63c788b9bcec was ahead_by 25 and behind_by 0 against main 4ad8c0f2ed1c6bd60da9b747b8ff180ced60b593.
  - Otheryn PR 165 changed exactly six intended paths and had zero inline review threads.
  - Exact-final Otheryn autofix 30250359933, CI 30250360096 and Required 30250359982 passed on head f6db2136248b39ccd7aa57178a1c63c788b9bcec.
  - The target-owned serializer writes opcode 0x28 plus deterministic modern and legacy opcode 0x64 responses while ProtocolLogin retains request parsing, profile selection, RSA/XTEA, authentication integration, secure-token issuance, session hints, send and disconnect lifecycle.
  - Modern account-tail serialization is explicit AccountStatus Ok, SubscriptionStatus Free or Premium and premium-expiry u32 in maintained-client field order; legacy serialization retains premium-days u16.
  - One capped snapshot of at most 255 character names feeds token authorization, serialized payload and session hints.
  - Six deterministic tests decode the session key, modern premium/free responses, legacy response and modern/legacy count caps to exact message end.
  - No maintained OTClient implementation change was required by the server-side serializer proof.
  - Canary checkpoint head 157c010204f4843c75ec4f5f3970b6253628506c passed Agent Task Ownership 30251819947 and CI 30251820124.
derived:
  - The exact Otheryn target file set is resolved and the validated disposition remains bounded ADAPT rather than wholesale ProtocolLogin migration.
  - The maintained-client correspondence gap is closed by the merged server-side serializer and deterministic decoding tests without an OTClient write.
  - All target delivery, stale-base and exact-final validation blockers are resolved.
unknown:
  - Whether physical login/relog evidence is required beyond deterministic target unit, full CI and runtime-smoke proof.
conflicts: []
first_failure:
  marker: none
  evidence: No failing target or Canary gate remains at this checkpoint.
rejected_hypotheses:
  - classify ProtocolLogin as REUSE from profile and token code alone
  - copy Canary multichannel or complete ProtocolLogin wholesale
  - require a maintained-client write before proving server-side field correspondence
  - treat green checks from a previous Otheryn head as exact-final proof for the merge head
  - treat the corrected checkpoint enum defect as an ownership or runtime-scope conflict
changed_paths:
  - docs/agents/tasks/active/CAN-20260727-oteryn-oam054-login-protocol-preflight.md
validation:
  - command: Otheryn exact-final autofix 30250359933
    result: PASS
    evidence: Exact merge head f6db2136248b39ccd7aa57178a1c63c788b9bcec passed autofix.
  - command: Otheryn exact-final CI 30250360096
    result: PASS
    evidence: Exact merge head f6db2136248b39ccd7aa57178a1c63c788b9bcec passed the applicable CI matrix.
  - command: Otheryn exact-final Required 30250359982
    result: PASS
    evidence: Exact merge head f6db2136248b39ccd7aa57178a1c63c788b9bcec passed the required aggregator.
  - command: Otheryn PR 165 scope and review-thread audit
    result: PASS
    evidence: Six intended paths and zero inline review threads were present at merge.
  - command: Otheryn main/head compare before merge
    result: PASS
    evidence: Exact merge head was ahead by 25 and behind current main by zero.
  - command: Canary Agent Task Ownership 30251819947
    result: PASS
    evidence: Exact Canary head 157c010204f4843c75ec4f5f3970b6253628506c passed ownership validation after correcting the unsupported enum.
  - command: Canary CI 30251820124
    result: PASS
    evidence: Exact Canary head 157c010204f4843c75ec4f5f3970b6253628506c passed repository CI.
blockers: []
next_action: Mark Canary PR 984 ready, verify Agent Task Ownership and CI on the resulting exact final checkpoint head, then squash-merge PR 984 with expected-head protection.
```