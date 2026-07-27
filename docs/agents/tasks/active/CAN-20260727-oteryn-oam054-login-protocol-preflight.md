---
task_id: CAN-20260727-oteryn-oam054-login-protocol-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-054
status: blocked
agent: "GPT-5.6 Thinking"
branch: docs/oam-054-compact-handover-20260727
base_branch: main
created: 2026-07-27
updated: 2026-07-27T08:17:00Z
last_verified_commit: "f9bd694db24a0b2d4c519e0427f57d8988094f3a"
risk: high
related_issue: ""
related_pr: "984"
depends_on:
  - OAM-053 durable programme reconciliation merged as 9d395a5563531dfc3d83f4a24361237137715000
blocks:
  - OAM-054 target proof and lifecycle
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
```

`login-protocol` is dependency-valid because `account-authentication` and `network-transport` are durably complete. The target proof preserves Otheryn's secure login-session token, multiprotocol layouts and protocol-session handoff while adapting only the proven account-login response wire gap.

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
updated_at: 2026-07-27T08:17:00Z
head: f9bd694db24a0b2d4c519e0427f57d8988094f3a
branch: docs/oam-054-compact-handover-20260727
pr: 984
status: blocked
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
  - Canary checkpoint head ad0f8507a40af03709c55ecf8cc972d7725cda66 passed Agent Task Ownership run 30247721592 and CI run 30247721991.
  - Otheryn PR 165 is open and mergeable from branch dudantas/oam-054-login-protocol-adapt at restacked head 2b25c874cab063b9d2e428b63fd6ad7b648c1860.
  - Live compare reports Otheryn PR 165 ahead_by 24 and behind_by 0 against current main ec5038a7f132a4c2ed030edda38a56b5b1ec916a.
  - Otheryn PR 165 changes exactly six intended paths: its task record, durable adaptation document, login_protocol_wire.hpp, protocollogin.cpp, focused test registration and oam_054_login_protocol_test.cpp.
  - Otheryn PR 165 has no inline review threads at the current verification.
  - The target-owned serializer writes opcode 0x28 plus deterministic modern and legacy opcode 0x64 responses while ProtocolLogin retains request parsing, profile selection, RSA/XTEA, authentication integration, secure-token issuance, session hints, send and disconnect lifecycle.
  - Modern account-tail serialization is explicit AccountStatus Ok, SubscriptionStatus Free or Premium and premium-expiry u32 in maintained-client field order; legacy serialization retains premium-days u16.
  - One capped snapshot of at most 255 character names feeds token authorization, serialized payload and session hints.
  - Six deterministic tests decode the session key, modern premium/free responses, legacy response and modern/legacy count caps to exact message end.
  - Otheryn implementation head c6fe5d8a2f48e6c8425c3db39ff2372a7cde3c3f passed CI 30245438536, Required 30245438107 and autofix 30245438145, including the full platform matrix and runtime smoke.
  - Otheryn restacked-head autofix run 30248804539 passed.
  - No maintained OTClient implementation change is present or required by the current server-side serializer proof.
derived:
  - The exact Otheryn target file set is resolved and the validated disposition remains bounded ADAPT rather than wholesale ProtocolLogin migration.
  - The maintained-client correspondence gap is closed by the server-side serializer and deterministic decoding tests without an OTClient write.
  - The stale-base blocker is resolved; CI and Required remain the only pending exact-final gates on the restacked head.
unknown:
  - Exact-final CI and Required result for Otheryn restacked head 2b25c874cab063b9d2e428b63fd6ad7b648c1860 and the eventual merge result.
  - Whether physical login/relog evidence is required beyond deterministic target unit, full CI and runtime-smoke proof.
conflicts: []
first_failure:
  marker: otheryn-exact-final-ci-required-pending
  evidence: Restacked Otheryn head 2b25c874cab063b9d2e428b63fd6ad7b648c1860 has behind_by zero and autofix 30248804539 passed, but CI 30248806007 is queued and Required 30248804496 is in progress.
rejected_hypotheses:
  - classify ProtocolLogin as REUSE from profile and token code alone
  - copy Canary multichannel or complete ProtocolLogin wholesale
  - require a maintained-client write before proving server-side field correspondence
  - treat the green pre-restack implementation head as exact-final proof for the new restacked head
changed_paths:
  - docs/agents/tasks/active/CAN-20260727-oteryn-oam054-login-protocol-preflight.md
validation:
  - command: Canary Agent Task Ownership run 30247721592
    result: PASS
    evidence: Exact Canary checkpoint head ad0f8507a40af03709c55ecf8cc972d7725cda66 passed ownership validation.
  - command: Canary CI run 30247721991
    result: PASS
    evidence: Exact Canary checkpoint head ad0f8507a40af03709c55ecf8cc972d7725cda66 passed repository CI.
  - command: Otheryn implementation-head CI 30245438536, Required 30245438107 and autofix 30245438145
    result: PASS
    evidence: Exact implementation head c6fe5d8a2f48e6c8425c3db39ff2372a7cde3c3f passed the complete applicable matrix without a follow-up implementation change.
  - command: live Otheryn PR 165 scope and review-thread audit
    result: PASS
    evidence: Six intended paths and zero inline review threads were found.
  - command: live Otheryn main/head compare
    result: PASS
    evidence: Restacked PR head 2b25c874cab063b9d2e428b63fd6ad7b648c1860 is ahead by 24 and behind current main by zero.
  - command: Otheryn restacked autofix 30248804539
    result: PASS
    evidence: Exact restacked head autofix completed successfully.
  - command: Otheryn restacked CI 30248806007 and Required 30248804496
    result: PENDING
    evidence: CI is queued and Required is in progress for the restacked head.
blockers:
  - Otheryn remains read-only under this request; exact-final CI and Required must pass on restacked head 2b25c874cab063b9d2e428b63fd6ad7b648c1860 before merge.
next_action: Verify exact-final CI 30248806007 and Required 30248804496 on Otheryn restacked head 2b25c874cab063b9d2e428b63fd6ad7b648c1860; if PR 165 merges, finalize this Canary checkpoint and PR 984, otherwise record the first failing gate without mutating Otheryn.
```