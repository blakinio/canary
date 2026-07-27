---
task_id: CAN-20260727-oteryn-oam054-login-protocol-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-054
status: review
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-054-login-protocol-governance
base_branch: main
created: 2026-07-27
updated: 2026-07-27
last_verified_commit: "66cc5a927686be34a219e9fdb4fdf9ac58f188eb"
risk: high
related_issue: ""
related_pr: "986"
depends_on:
  - OAM-053 durable programme reconciliation merged as 9d395a5563531dfc3d83f4a24361237137715000
  - Otheryn OAM-054 target lifecycle merged as 41bc0562c263781df85c2f6855295fefa201db0a
blocks:
  - OAM-054 Canary lifecycle and final programme reconciliation
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260727-oteryn-oam054-login-protocol-preflight.md
    - docs/agents/OTERYN_OAM_054_LOGIN_PROTOCOL_REVALIDATION.md
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/real-tibia/registry/modules/login-protocol.yaml
    - docs/agents/real-tibia/TSD_010_PROTOCOL_CLIENT_REPORT.md
    - docs/security/SECURITY_VALIDATION_SEC004.md
    - blakinio/Otheryn
    - blakinio/otclient
modules_touched:
  - oteryn-architecture-migration
  - login-protocol
cross_repo_tasks:
  - OTH-20260727-oam054-login-protocol-adapt
---

# OAM-054 Login Protocol governance

Final disposition: `login-protocol → ADAPT`.

Otheryn retained current/11.00/8.60 request layouts, RSA/XTEA, secure opaque session tokens and protocol-session handoff. The target adapted only account-login response serialization into a target-owned maintained-client-correspondent wire contract.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-27T12:45:00+02:00
head: 66cc5a927686be34a219e9fdb4fdf9ac58f188eb
branch: dudantas/oam-054-login-protocol-governance
pr: 986
status: validating
context_routes:
  - agent-governance
  - cross-repo
  - cpp-runtime
  - security
  - testing
owned_paths:
  - docs/agents/tasks/active/CAN-20260727-oteryn-oam054-login-protocol-preflight.md
  - docs/agents/OTERYN_OAM_054_LOGIN_PROTOCOL_REVALIDATION.md
proven:
  - OAM-001 through OAM-053 are durably complete and login-protocol was the final unresolved canonical record.
  - Canary OAM-054 preflight PR 983 merged as d8eb3f5520b2a94e788a31e004bf1aa33b9d7c61.
  - Otheryn feature PR 165 changed exactly six intended paths and preserved credential policy account repository game-world authentication gameplay client schema datapack and production boundaries.
  - Exact atomically synchronized target head f6db2136248b39ccd7aa57178a1c63c788b9bcec was based on target main 4ad8c0f2ed1c6bd60da9b747b8ff180ced60b593 with behind_by zero.
  - Exact target head passed CI 30250360096 Required 30250359982 and autofix 30250359933 without a follow-up commit.
  - Full Linux CTest passed six OAM-054 tests plus OAM-044 and OAM-045 regressions; Linux release Docker macOS and Windows passed applicable build/runtime gates.
  - PR 165 had no comments reviews or review threads and squash-merged with expected-head protection as e077c51fe948652a4849e15f6c518059f4370717.
  - Target lifecycle PR 173 changed exactly three documentation paths, passed Required 30252401732 and merged as 41bc0562c263781df85c2f6855295fefa201db0a.
  - Delivered response serializer matches maintained-client modern status subscription expiry order and preserves legacy premium-days semantics.
  - A single capped u8 snapshot feeds token authorization serialized records and session hints.
  - No maintained-client runtime credential policy account repository game-world gameplay schema datapack endpoint or production write was added.
  - PR 986 changes exactly this checkpoint and the durable OAM-054 report.
derived:
  - ADAPT is proven; pure REUSE and wholesale Canary migration are rejected.
  - After Canary lifecycle and programme reconciliation the canonical OAM inventory is exhausted.
unknown: []
conflicts: []
first_failure:
  marker: maintained-client-account-tail-correspondence
  result: FIXED
  evidence: Target emits explicit AccountStatus Ok SubscriptionStatus and premium expiry in maintained-client order with deterministic decoding tests.
rejected_hypotheses:
  - classify ProtocolLogin as REUSE without direct wire tests
  - copy Canary ProtocolLogin wholesale
  - change the maintained client before proving server-side correspondence
  - expand OAM-054 into credential or game-world ownership
changed_paths:
  - docs/agents/tasks/active/CAN-20260727-oteryn-oam054-login-protocol-preflight.md
  - docs/agents/OTERYN_OAM_054_LOGIN_PROTOCOL_REVALIDATION.md
validation:
  - command: target exact-final gates
    result: PASS
    evidence: CI 30250360096 Required 30250359982 and autofix 30250359933 passed on the atomically synchronized feature head.
  - command: target feature and lifecycle audits
    result: PASS
    evidence: Exact path sets clean discussions behind_by zero and expected-head merges e077c51f and 41bc0562.
  - command: disposition boundary review
    result: PASS
    evidence: Target changed only bounded login-response wire serialization and deterministic correspondence tests while preserving excluded systems.
blockers: []
next_action: Keep this exact governance head unchanged, pass Ownership and CI, merge PR 986, then archive this task and reconcile the programme as OAM-001 through OAM-054 complete with no OAM-055.
```
