---
task_id: CAN-20260727-oteryn-oam054-login-protocol-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-054
status: completed
agent: "GPT-5.6 Thinking"
branch: docs/oam-054-login-protocol-lifecycle
base_branch: main
created: 2026-07-27
updated: 2026-07-27T19:32:00+02:00
completed: 2026-07-27T19:29:00+02:00
last_verified_commit: "2029cd7000545cb0ab60920b797af8519dd4dd0a"
risk: high
related_issue: ""
related_pr: "986"
lifecycle_pr: "987"
depends_on:
  - OAM-053 durable programme reconciliation merged as 9d395a5563531dfc3d83f4a24361237137715000
  - Canary OAM-054 delivery checkpoint merged as 577d04c1d3a723af3ee8933600eff15938deac9f
  - Otheryn OAM-054 feature merged as e077c51fe948652a4849e15f6c518059f4370717
  - Otheryn OAM-054 lifecycle merged as 41bc0562c263781df85c2f6855295fefa201db0a
  - Canary OAM-054 governance merged as 2029cd7000545cb0ab60920b797af8519dd4dd0a
blocks:
  - final OAM programme reconciliation
owned_paths:
  exclusive:
    - docs/agents/tasks/archive/CAN-20260727-oteryn-oam054-login-protocol-preflight.md
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

# OAM-054 Login Protocol governance — archived

Final disposition: `login-protocol → ADAPT`.

The active Canary task is complete. Otheryn retained current/11.00/8.60 request layouts, RSA/XTEA, secure opaque session tokens and protocol-session handoff while adapting only the account-login response serializer into a target-owned maintained-client-correspondent wire contract.

## Completion evidence

```yaml
checkpoint_version: 1
updated_at: 2026-07-27T19:32:00+02:00
head: 60f52bd12f584308ced79b5c48dec7586c909f98
branch: docs/oam-054-login-protocol-lifecycle
pr: 987
status: completed
context_routes:
  - agent-governance
  - cross-repo
  - cpp-runtime
  - security
  - testing
owned_paths:
  - docs/agents/tasks/archive/CAN-20260727-oteryn-oam054-login-protocol-preflight.md
  - docs/agents/OTERYN_OAM_054_LOGIN_PROTOCOL_REVALIDATION.md
proven:
  - Canary preflight PR 983 merged as d8eb3f5520b2a94e788a31e004bf1aa33b9d7c61.
  - Canary delivery checkpoint PR 984 passed Ownership 30252630890 and CI 30252641709, then merged as 577d04c1d3a723af3ee8933600eff15938deac9f.
  - Otheryn exact feature head f6db2136248b39ccd7aa57178a1c63c788b9bcec passed CI 30250360096, Required 30250359982 and autofix 30250359933.
  - Otheryn feature PR 165 merged with expected-head protection as e077c51fe948652a4849e15f6c518059f4370717.
  - Otheryn lifecycle PR 173 merged as 41bc0562c263781df85c2f6855295fefa201db0a.
  - Canary governance head c6e9f90e5d59684a5a28b698b0d8a03f8e6a0462 passed Ownership 30288119453 and full final-gate CI 30288119744.
  - Canary governance PR 986 changed exactly two documentation paths and squash-merged with expected-head protection as 2029cd7000545cb0ab60920b797af8519dd4dd0a.
  - Canary lifecycle PR 987 changes exactly the active/archive task pair and durable OAM-054 report.
  - Modern status, subscription and premium-expiry serialization corresponds to the maintained client; legacy premium-days semantics remain intact.
  - One capped u8 character snapshot feeds token authorization, serialized response records and session hints.
  - Credential policy, account repository ownership, game-world authentication, gameplay, maintained-client runtime, schema, datapack, endpoint and production behavior remained unchanged.
derived:
  - The final canonical login-protocol package is complete as bounded ADAPT.
  - After this lifecycle merge, OAM-001 through OAM-054 can be reconciled as complete and no OAM-055 should be invented without new registry evidence.
unknown:
  - Whether physical login/relog evidence is required beyond deterministic target unit, full CI and runtime-smoke proof.
conflicts: []
first_failure:
  marker: maintained-client-account-tail-correspondence
  result: FIXED
  evidence: The target now serializes explicit account status, subscription status and premium expiry in maintained-client order with deterministic decoding tests.
rejected_hypotheses:
  - classify ProtocolLogin as REUSE without direct wire tests
  - copy Canary ProtocolLogin wholesale
  - require a maintained-client mutation before proving server-side correspondence
  - expand OAM-054 into credential or game-world ownership
changed_paths:
  - docs/agents/tasks/active/CAN-20260727-oteryn-oam054-login-protocol-preflight.md
  - docs/agents/tasks/archive/CAN-20260727-oteryn-oam054-login-protocol-preflight.md
  - docs/agents/OTERYN_OAM_054_LOGIN_PROTOCOL_REVALIDATION.md
validation:
  - command: Canary governance exact-final gates
    result: PASS
    evidence: Ownership 30288119453 and full CI 30288119744 passed on head c6e9f90e5d59684a5a28b698b0d8a03f8e6a0462 before merge 2029cd70.
  - command: lifecycle path audit
    result: PASS
    evidence: PR 987 moves the task from active to archive and updates only the durable OAM-054 report.
blockers: []
next_action: Verify exact-final Ownership and CI on PR 987, squash-merge it with expected-head protection, then reconcile the programme as OAM-001 through OAM-054 complete with no OAM-055.
```

## Preserved nonclaims

OAM-054 does not prove password security, arbitrary-account authorization, every historical protocol version, game-world authentication, reconnect/session races, client UI correctness, sustained capacity, denial-of-service resistance or production deployment safety.
