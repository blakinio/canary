---
task_id: CAN-20260727-oteryn-oam054-login-protocol-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-054
status: blocked
agent: "GPT-5.6 Thinking"
branch: docs/oam-054-compact-handover-20260727
base_branch: main
created: 2026-07-27
updated: 2026-07-27T09:06:13+02:00
last_verified_commit: "d8eb3f5520b2a94e788a31e004bf1aa33b9d7c61"
risk: high
related_issue: ""
related_pr: "983"
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
cross_repo_tasks: []
---

# OAM-054 Login Protocol preflight

## Result

```text
OAM-054 → login-protocol
preflight → REVALIDATE
leading target hypothesis → ADAPT
```

`login-protocol` is dependency-valid because `account-authentication` and `network-transport` are durably complete. The target proof must preserve Otheryn's secure login-session token, multiprotocol layouts and protocol-session handoff while adapting only proven account-login wire and maintained-client parsing gaps.

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
updated_at: 2026-07-27T09:06:13+02:00
head: d8eb3f5520b2a94e788a31e004bf1aa33b9d7c61
branch: docs/oam-054-compact-handover-20260727
pr: 983
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
  - PR 983 merged the OAM-054 login-protocol preflight as d8eb3f5520b2a94e788a31e004bf1aa33b9d7c61 from exact head 7b0ba76e81ff958f9714bc12c8295357ec759faa and changed only this task record.
  - Exact preflight head passed Agent Task Ownership run 30242303120 and CI run 30242303240.
  - OAM-054 selected login-protocol as REVALIDATE with a leading bounded ADAPT hypothesis and preserved the declared target-proof boundary.
  - Current Canary main is d8eb3f5520b2a94e788a31e004bf1aa33b9d7c61 and current Otheryn main is 9703da845384423ad85883216bf8853642c21bcd.
  - Maintained OTClient advanced from code baseline 99ad5de5a19179f21e2e21e961c1ef121a30d08e to 0ce30abc4e582eb05dce1471153d85b1152d4d5e only through task lifecycle documentation paths.
  - No open PR matching login protocol, ProtocolLogin, session key or account tail was found in Canary, Otheryn or maintained OTClient.
  - Otheryn already has secure-token failure handling, multiprotocol account layouts and protocol-session handoff that must not be replaced wholesale.
  - The maintained-client account-tail correspondence gap remains unresolved and no Otheryn target implementation task or PR exists.
derived:
  - The preflight is durably complete, but target implementation cannot begin from this Canary-only authorization.
  - The next implementation should remain a bounded ADAPT proof rather than wholesale ProtocolLogin migration.
unknown:
  - Exact Otheryn target file set and whether the maintained client needs any implementation write after server-side serializer correction.
  - Whether physical login/relog evidence is required beyond deterministic target unit and CI proof.
conflicts: []
first_failure:
  marker: otheryn-write-authorization-absent
  evidence: Root AGENTS.md permits writes only to blakinio/canary; the current request authorizes only the Canary checkpoint and compact handover.
rejected_hypotheses:
  - classify ProtocolLogin as REUSE from profile and token code alone
  - copy Canary multichannel or complete ProtocolLogin wholesale
  - start Otheryn implementation without separate explicit repository authorization
changed_paths:
  - docs/agents/tasks/active/CAN-20260727-oteryn-oam054-login-protocol-preflight.md
validation:
  - command: Agent Task Ownership run 30242303120
    result: PASS
    evidence: Exact preflight head 7b0ba76e81ff958f9714bc12c8295357ec759faa passed ownership validation.
  - command: CI run 30242303240
    result: PASS
    evidence: Exact preflight head 7b0ba76e81ff958f9714bc12c8295357ec759faa passed repository CI.
  - command: live repository and overlap audit
    result: PASS
    evidence: Canary/Otheryn/OTClient heads were refreshed and no matching open login-protocol PR was found.
  - command: python tools/agents/checkpoint.py docs/agents/tasks/active/CAN-20260727-oteryn-oam054-login-protocol-preflight.md --require-checkpoint
    result: PASS
    evidence: Compact checkpoint validated before handover publication.
blockers:
  - Explicit authorization to write in blakinio/Otheryn is not present in the current request.
next_action: Obtain explicit authorization for blakinio/Otheryn, then create one bounded OAM-054 target task, branch and draft PR for the ADAPT proof without modifying Canary or OTClient runtime paths.
```
