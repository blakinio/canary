---
task_id: CAN-20260727-oteryn-oam054-login-protocol-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-054
status: blocked
agent: "GPT-5.6 Thinking"
branch: docs/oam-054-compact-handover-20260727
base_branch: main
created: 2026-07-27
updated: 2026-07-27T10:36:00+02:00
last_verified_commit: "6304eeee21ad8a3f8bacf3acf3680316da1dd920"
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
updated_at: 2026-07-27T10:36:00+02:00
head: 6304eeee21ad8a3f8bacf3acf3680316da1dd920
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
  - Canary checkpoint head 6304eeee21ad8a3f8bacf3acf3680316da1dd920 passed CI run 30249361080.
  - Canary Ownership run 30249359719 failed only because validation item 7 used unsupported result value PENDING; focused tests and all prior ownership steps passed.
  - Otheryn PR 165 is open and mergeable from branch dudantas/oam-054-login-protocol-adapt at current head f6db2136248b39ccd7aa57178a1c63c788b9bcec.
  - Live compare reports Otheryn PR 165 ahead_by 25 and behind_by 0 against current main 4ad8c0f2ed1c6bd60da9b747b8ff180ced60b593.
  - Otheryn PR 165 changes exactly six intended paths: its task record, durable adaptation document, login_protocol_wire.hpp, protocollogin.cpp, focused test registration and oam_054_login_protocol_test.cpp.
  - Otheryn PR 165 has zero inline review threads at the current verification.
  - The target-owned serializer writes opcode 0x28 plus deterministic modern and legacy opcode 0x64 responses while ProtocolLogin retains request parsing, profile selection, RSA/XTEA, authentication integration, secure-token issuance, session hints, send and disconnect lifecycle.
  - Modern account-tail serialization is explicit AccountStatus Ok, SubscriptionStatus Free or Premium and premium-expiry u32 in maintained-client field order; legacy serialization retains premium-days u16.
  - One capped snapshot of at most 255 character names feeds token authorization, serialized payload and session hints.
  - Six deterministic tests decode the session key, modern premium/free responses, legacy response and modern/legacy count caps to exact message end.
  - Otheryn implementation head c6fe5d8a2f48e6c8425c3db39ff2372a7cde3c3f passed CI 30245438536, Required 30245438107 and autofix 30245438145, including the full platform matrix and runtime smoke.
  - Otheryn current-head autofix run 30250359933 passed.
  - No maintained OTClient implementation change is present or required by the current server-side serializer proof.
derived:
  - The exact Otheryn target file set is resolved and the validated disposition remains bounded ADAPT rather than wholesale ProtocolLogin migration.
  - The maintained-client correspondence gap is closed by the server-side serializer and deterministic decoding tests without an OTClient write.
  - The stale-base blocker remains resolved; current-head CI and Required are the remaining Otheryn exact-final gates.
  - The Canary Ownership failure is a checkpoint-enum defect rather than a scope, ownership or runtime failure and is corrected by this update.
unknown:
  - Exact-final CI and Required result for Otheryn current head f6db2136248b39ccd7aa57178a1c63c788b9bcec and the eventual merge result.
  - Exact-current-head Canary Ownership and CI result after correcting the unsupported validation enum.
  - Whether physical login/relog evidence is required beyond deterministic target unit, full CI and runtime-smoke proof.
conflicts: []
first_failure:
  marker: exact-final-gates-incomplete
  evidence: Otheryn head f6db2136248b39ccd7aa57178a1c63c788b9bcec has behind_by zero and autofix 30250359933 passed, but CI 30250360096 is queued and Required 30250359982 is in progress; the corrected Canary head also requires fresh Ownership and CI.
rejected_hypotheses:
  - classify ProtocolLogin as REUSE from profile and token code alone
  - copy Canary multichannel or complete ProtocolLogin wholesale
  - require a maintained-client write before proving server-side field correspondence
  - treat green checks from a previous Otheryn head as exact-final proof for the current head
  - treat the unsupported PENDING enum as an ownership or runtime-scope conflict
changed_paths:
  - docs/agents/tasks/active/CAN-20260727-oteryn-oam054-login-protocol-preflight.md
validation:
  - command: Canary CI run 30249361080
    result: PASS
    evidence: Exact Canary head 6304eeee21ad8a3f8bacf3acf3680316da1dd920 passed repository CI.
  - command: Canary Agent Task Ownership run 30249359719
    result: FAIL
    evidence: Changed-task validation rejected unsupported result value PENDING in validation item 7; focused tests and prior steps passed.
  - command: Otheryn implementation-head CI 30245438536, Required 30245438107 and autofix 30245438145
    result: PASS
    evidence: Exact implementation head c6fe5d8a2f48e6c8425c3db39ff2372a7cde3c3f passed the complete applicable matrix without a follow-up implementation change.
  - command: live Otheryn PR 165 scope and review-thread audit
    result: PASS
    evidence: Six intended paths and zero inline review threads were found.
  - command: live Otheryn main/head compare
    result: PASS
    evidence: Current PR head f6db2136248b39ccd7aa57178a1c63c788b9bcec is ahead by 25 and behind current main by zero.
  - command: Otheryn current-head autofix 30250359933
    result: PASS
    evidence: Exact current-head autofix completed successfully.
  - command: Otheryn current-head CI 30250360096 and Required 30250359982 completion gate
    result: FAIL
    evidence: CI remains queued and Required remains in progress, so the exact-final completion gate is not yet satisfied.
blockers:
  - Otheryn remains read-only under this request; current-head CI and Required must pass before PR 165 can merge.
  - The corrected Canary checkpoint must pass exact-current-head Ownership and CI before PR 984 can advance.
next_action: Verify Otheryn CI 30250360096 and Required 30250359982 plus exact-current-head Canary Ownership and CI; if PR 165 merges and all Canary gates pass, finalize and squash-merge PR 984 with expected-head protection, otherwise record the first failing gate without mutating Otheryn.
```