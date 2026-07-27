---
task_id: CAN-20260727-oteryn-oam054-login-protocol-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-054
status: blocked
agent: "GPT-5.6 Thinking"
branch: docs/oam-054-compact-handover-20260727
base_branch: main
created: 2026-07-27
updated: 2026-07-27T09:50:00+02:00
last_verified_commit: "82a32c70dcdbc0d51f91bcd1048b7107c0e0504d"
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
updated_at: 2026-07-27T09:50:00+02:00
head: 82a32c70dcdbc0d51f91bcd1048b7107c0e0504d
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
  - Otheryn PR 165 is open and mergeable from branch dudantas/oam-054-login-protocol-adapt at live head 1187132c18d15fe745dd3c490630e98481e06ad7.
  - Otheryn PR 165 changes exactly six intended paths: its task record, durable adaptation document, login_protocol_wire.hpp, protocollogin.cpp, focused test registration and oam_054_login_protocol_test.cpp.
  - The target-owned serializer writes opcode 0x28 plus deterministic modern and legacy opcode 0x64 responses while ProtocolLogin retains request parsing, profile selection, RSA/XTEA, authentication integration, secure-token issuance, session hints, send and disconnect lifecycle.
  - Modern account-tail serialization is explicit AccountStatus Ok, SubscriptionStatus Free or Premium and premium-expiry u32 in maintained-client field order; legacy serialization retains premium-days u16.
  - One capped snapshot of at most 255 character names feeds token authorization, serialized payload and session hints.
  - Six deterministic tests decode the session key, modern premium/free responses, legacy response and modern/legacy count caps to exact message end.
  - Otheryn implementation head c6fe5d8a2f48e6c8425c3db39ff2372a7cde3c3f passed CI 30245438536, Required 30245438107 and autofix 30245438145, including the full platform matrix and runtime smoke.
  - No maintained OTClient implementation change is present or required by the current server-side serializer proof.
  - Current Otheryn main advanced from task base 9703da845384423ad85883216bf8853642c21bcd to ec5038a7f132a4c2ed030edda38a56b5b1ec916a through two PRS-002 checkpoint commits that do not overlap any OAM-054 changed path.
  - Otheryn PR 165 is ahead by 21 and behind current main by 2; its own checkpoint requires behind_by zero before merge.
  - Current Otheryn final-head autofix run 30247040780 passed; Required run 30247040789 and CI run 30247040929 were pending at the last live verification.
derived:
  - The exact Otheryn target file set is resolved and the validated disposition remains bounded ADAPT rather than wholesale ProtocolLogin migration.
  - The maintained-client correspondence gap is closed by the server-side serializer and deterministic decoding tests without an OTClient write.
  - The two new main commits are path-disjoint but still invalidate the explicit behind_by-zero and exact-final-head delivery gate until the OAM-054 branch is restacked and revalidated.
unknown:
  - Otheryn PR 165 restack head, exact-final CI/Required result and merge result.
  - Whether physical login/relog evidence is required beyond deterministic target unit, full CI and runtime-smoke proof.
conflicts: []
first_failure:
  marker: otheryn-branch-behind-main
  evidence: Live compare against Otheryn main ec5038a7f132a4c2ed030edda38a56b5b1ec916a reports PR head 1187132c18d15fe745dd3c490630e98481e06ad7 behind_by 2, while the Otheryn task gate requires behind_by zero.
rejected_hypotheses:
  - classify ProtocolLogin as REUSE from profile and token code alone
  - copy Canary multichannel or complete ProtocolLogin wholesale
  - require a maintained-client write before proving server-side field correspondence
  - treat path-disjoint main advancement as satisfying the explicit behind_by-zero final gate
changed_paths:
  - docs/agents/tasks/active/CAN-20260727-oteryn-oam054-login-protocol-preflight.md
validation:
  - command: Canary Agent Task Ownership run 30245274897
    result: PASS
    evidence: Compact-handover head 990f188d75b4b7396b4b34aac7a4ffad4d0968da passed ownership validation before target synchronization.
  - command: Canary CI run 30245275339
    result: PASS
    evidence: Required aggregator passed on compact-handover head 990f188d75b4b7396b4b34aac7a4ffad4d0968da.
  - command: Otheryn implementation-head CI 30245438536, Required 30245438107 and autofix 30245438145
    result: PASS
    evidence: Exact implementation head c6fe5d8a2f48e6c8425c3db39ff2372a7cde3c3f passed the complete applicable matrix without a follow-up implementation change.
  - command: live Otheryn PR 165 scope and overlap audit
    result: PASS
    evidence: Six intended paths, no review threads and no maintained-client implementation PR overlap were found.
  - command: live Otheryn main/head compare
    result: FAIL
    evidence: PR 165 is behind current main by two path-disjoint PRS-002 commits and therefore does not satisfy its explicit behind_by-zero delivery gate.
blockers:
  - Otheryn remains read-only under this request; PR 165 must be restacked onto current main and exact-final gates must pass on the resulting head.
next_action: Verify Otheryn PR 165 is restacked onto current main with behind_by zero and reruns exact-final CI, Required and autofix on the new head; if it merges, finalize this Canary checkpoint and PR 984, otherwise record the first failing gate without mutating Otheryn.
```
