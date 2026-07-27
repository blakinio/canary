---
task_id: CAN-20260727-oteryn-oam054-login-protocol-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-054
status: implementing
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-054-login-protocol-preflight
base_branch: main
created: 2026-07-27
updated: 2026-07-27
last_verified_commit: "9d395a5563531dfc3d83f4a24361237137715000"
risk: high
related_issue: ""
related_pr: "pending"
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
updated_at: 2026-07-27T08:20:00+02:00
head: 9d395a5563531dfc3d83f4a24361237137715000
branch: dudantas/oam-054-login-protocol-preflight
pr: pending
status: implementing
context_routes:
  - agent-governance
  - cross-repo
  - cpp-runtime
  - security
  - testing
owned_paths:
  - docs/agents/tasks/active/CAN-20260727-oteryn-oam054-login-protocol-preflight.md
proven:
  - OAM-001 through OAM-053 are durably complete and login-protocol is the only remaining identified canonical package.
  - Canary is 9d395a5563531dfc3d83f4a24361237137715000; Otheryn is 9703da845384423ad85883216bf8853642c21bcd; upstream Canary is 7644bcbcbbad4a09e52a5707ed531e4dd21d8a79; maintained OTClient is 99ad5de5a19179f21e2e21e961c1ef121a30d08e.
  - Canonical login-protocol includes account-login request/response, version/profile selection, RSA/XTEA handoff, session-key field, character/world serialization, maintained-client parsing and disconnect after response.
  - No open Otheryn PR owns ProtocolLogin or login wire paths; Canary PR 975 is measurement-only E2E, OTClient PR 23 is UI-only and PR 48 forbids login/world connection.
  - Otheryn ProtocolLogin blob 97f6549c928baa9409aea67ee521f10cc63083fa differs from Canary 8efc7b986dbaf127860a6183a756f65d1f742c32 and upstream 3c7d751b020b89a104a6669d5c07e52b4b7eef82.
  - Otheryn already resolves explicit current/11.00/8.60 account layouts, selects the response transport, issues fail-closed secure tokens and registers profile/session/character handoff hints.
  - Maintained-client parser blob a1ab34e72ee19cccec116cc4fa470dd3289b24fa sends version/signature/preview/RSA/XTEA/account/password fields and parses opcodes 0x28 and 0x64.
  - The maintained client names the modern account tail as status, subscription substatus and u32 premium expiry, while target serialization currently writes premium remaining days, a premium boolean and premium last day.
  - Existing OAM-044 tests prove profile metadata and login-layout selection; OAM-045 tests prove hint matching, but no target test serializes ProtocolLogin output and decodes it with the maintained-client contract.
  - Canary PR 80 merged as d2e02a3d533bfdfdedc3a81a8f4e4801bc828f22 and removed unconditional rejection of every current-protocol login.
  - Canary PR 82 merged as 9cafe7e945391a6f170f5b96bf68713d91d758be and wired LoginSessionManager into the opaque 0x28 session-key handoff.
  - SEC-004 proves only bounded pre-auth login parser resilience; it does not prove successful account authentication, character-list serialization or client parsing.
derived:
  - Pure REUSE is rejected because direct server-client wire evidence is absent and the modern account tail is semantically mismatched.
  - Wholesale Canary migration is rejected because target secure-token failure handling and profile/session-handoff architecture are newer and stronger.
  - Expected target disposition is bounded ADAPT through testable serialization helpers, exact field semantics and deterministic cross-surface regressions.
unknown:
  - Exact target file set and whether the maintained client needs any write after server-side serializer correction.
  - Whether physical login/relog evidence is required beyond exact target unit/CI and the existing Universal E2E programme.
conflicts: []
first_failure:
  marker: maintained-client-account-tail-correspondence
  result: BLOCKED
  evidence: Target emits premiumRemainingDays/bool/lastDay where the maintained parser consumes status/subStatus/expiry; no direct target regression resolves the contract.
rejected_hypotheses:
  - classify ProtocolLogin as REUSE from existing profile and token code alone
  - copy Canary multichannel or complete ProtocolLogin wholesale
  - move credential verification or game-world authentication into OAM-054
changed_paths:
  - docs/agents/tasks/active/CAN-20260727-oteryn-oam054-login-protocol-preflight.md
validation:
  - command: dependency and ownership audit
    result: PASS
    evidence: login-protocol dependencies are complete and no active target PR owns its wire paths.
  - command: four-repository server/client inventory
    result: PASS
    evidence: Exact heads and server/client blobs are pinned; target, legacy and upstream differ.
  - command: target gap and donor review
    result: PASS
    evidence: Existing token/profile/handoff strengths are preserved while direct serialization and account-tail gaps require adaptation.
blockers: []
next_action: Merge this one-file preflight, then create a separately authorized Otheryn target task and implementation PR for the bounded ADAPT proof.
```
