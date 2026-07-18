---
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
name: Oteryn Architecture and Migration
status: active
owner: oteryn-architecture-migration-agent
created: 2026-07-15T15:28:18+02:00
updated: 2026-07-18T09:10:00+02:00
last_verified_commit: "9627b7524c4da232a47d9c75f2da907cc918b0b6"
primary_paths:
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
  - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
shared_integration_paths:
  - docs/agents/CHANGELOG.md
related_programs:
  - CAN-PROGRAM-TIBIA-SYSTEM-DECOMPOSITION
  - CAN-PROGRAM-REAL-TIBIA-PARITY
  - CAN-PROGRAM-UPSTREAM-INTELLIGENCE
  - CAN-PROGRAM-E2E-PLATFORM
cross_repo_contracts:
  - OTS-001
---

# Mission

Migrate from legacy `blakinio/canary` to clean target `blakinio/Otheryn` one bounded canonical module/package at a time. The canonical registry is the only migration inventory. Target architecture is defined by `docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md`.

# Rules

- Canary is governance/legacy evidence; Otheryn is the separately authorized target.
- OTClient/upstream/donors are read-only unless separately authorized.
- One bounded OAM package/task/branch/PR at a time with exact SHAs.
- Never infer `REUSE` from file presence/blob identity alone.
- Never bulk-copy legacy Player/IOLoginData or the repository.
- Preserve OAM-004 persistence gaps; player SQL and later KV durability are not atomic.
- Reuse the existing Universal Physical-Client E2E; do not create a second generic orchestrator.
- Feature merge must be followed by separate lifecycle/archive and durable program reconciliation before the next OAM starts.
- Final merge requires exact-head gates and clean comments/reviews/threads.

# Completed packages

| Package | Result | Key durable state |
|---|---|---|
| OAM-001..OAM-005 | architecture, target identity, foundations, persistence, account/character lifecycle | complete + lifecycle archived |
| OAM-006 | protocol `ADAPT` | target `c547d8ad70ef1252624c255476e6cb83fa125e14`; physical `29531221365`; lifecycle `b0ea0ba9508cc78d5580f44181115e9b304eb7da` |
| OAM-007 | item-definitions `ADAPT`; item-instances/world-map-runtime `REUSE` | target `68c4f39f7b1b45f880543c258627b4ccf73dbc86`; lifecycle `317c1c4235377c388883aa2fd425d324f8ce4d2e` |
| OAM-008 | `vocations → REUSE` | target `f59a58426b4d3910ba0cdc0d2332c24f31a1db4f`; feature `acdddd924fed170da51a8a54114607842f0cbb68`; lifecycle `e27eeefa4c3b4a6072c8c8ffda73da806fe20b9b` |
| OAM-009 | exact-target physical vocation proof | run `29593102547`; feature `533a1063ab2d25199fb39239e28dace6a064d395`; lifecycle `02403617318049575814c0e24740469829355b0d` |
| OAM-010 | `character-progression → ADAPT` | target `a4d095e3880787233bd194616dc6d19e6b94faaf`; feature `f140a0e62cdcd1eaac39ab9b721d83e528ac3dae`; lifecycle `cb74f8b6c0bda1d5f0e0d6c1327bc198b0ecc740` |
| OAM-011 | `weapon-proficiency → ADAPT` | target `72f7bdc1a5afa9e9982c20bdcf3098c83dca543e`; feature `8df917cf34771e1388533915a6fa4e50aa91e1bb`; lifecycle `9627b7524c4da232a47d9c75f2da907cc918b0b6` |

# OAM-009 durable boundary

OAM-009 proved exact target `f59a58426b4d3910ba0cdc0d2332c24f31a1db4f` can physically login/logout/relog/logout deterministic `Knight 1` with persisted `vocation = 4`. Accepted run `29593102547` executed all three canonical SQL assertions. The generic physical runner was corrected to execute scenario SQL assertions fail-closed; preliminary run `29589941229` was rejected. Maintained OTClient was `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`.

# OAM-010 durable completion

Final disposition:

```text
character-progression ADAPT
```

The clean target/upstream progression core is retained. Whole-module legacy `REUSE` is rejected because legacy Canary has a session-coupled disconnect-death-protection policy absent from the pinned target/upstream. OAM-010 deliberately did not import that policy without separate session/protocol/runtime evidence.

Proof-only Otheryn PR #27 final head `4152ee997e4ab6e1b8ca8c4b18ab86853ebeea58` passed autofix `29619165369`, Required `29619165343`, CI `29619165487`, four focused progression tests and 329/329 full Linux debug tests. Target merge is `a4d095e3880787233bd194616dc6d19e6b94faaf`. Canary feature merge is `f140a0e62cdcd1eaac39ab9b721d83e528ac3dae`; lifecycle is `cb74f8b6c0bda1d5f0e0d6c1327bc198b0ecc740`.

OAM-004D persistence and OAM-005 character lifecycle remain authoritative. OAM-010 does not claim Real Tibia progression formula/value parity, exhaustive death-loss/blessing behavior, protocol/UI compatibility, or a new physical-client E2E result.

# OAM-011 durable completion

Final disposition:

```text
weapon-proficiency ADAPT
```

Task-start baselines were Canary `9586530202eb3e40569bf4f97d21c63c9d99b6cb`, Otheryn `a4d095e3880787233bd194616dc6d19e6b94faaf`, upstream `e0ac98e399d0f7e483f3668f57b78fcc45b6e53f`, and OTClient `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`.

Function-level revalidation found a concrete task-start target defect: the first proficiency experience gain could cap the newly created entry at maximum without setting `mastered=true`. Canary PR #212 provided the bounded mastery-state correctness fix and `getMasteredWeaponCount()`. Canary PR #272 provided idempotent proficiency-side reconciliation for existing achievement IDs 564/565/566 on live mastery and silent load backfill.

The exact selected production boundary is the Canary state after PR #272 and before PR #288. Later achievement `567` / `The Forbidden Build` and its twelve-weapon condition remain deliberately excluded because the target achievement catalogue still treats `567` as unknown/non-existent and achievement-catalogue ownership is outside OAM-011.

Otheryn PR #29 final head `c9f060a2020c3612f65f8e31c6e745a03aa3fe5f` passed autofix `29634273531`, CI `29634273615`, Required `29634273523`, Linux debug compile/runtime smoke/database import and `Run Tests`. Seven focused `WeaponProficiencyTest` cases passed and the full Linux debug suite completed 336/336 with zero failures. Artifact `8426692510` digest is `sha256:f7602a97b67686e25f53e06974b08ee0c7646c4cba873999397437830f95c5cf`. Target merge is `72f7bdc1a5afa9e9982c20bdcf3098c83dca543e`.

Canary PR #519 final head `35a0320c63fefe06789a928edef5bdcd4cc0fe33` passed Ownership `29634880703`, pre-ready CI `29634880757` and ready-state CI `29634906649` with Required PASS, then merged as `8df917cf34771e1388533915a6fa4e50aa91e1bb`. Lifecycle PR #521 was repeatedly reconstructed onto current non-overlapping `main` drift, final head `efde6a289d6966a3d54202393e187ec0f0960acb` passed Ownership `29635187127` and CI `29635187179`, then merged as `9627b7524c4da232a47d9c75f2da907cc918b0b6`.

OAM-011 preserves OAM-004 SQL/KV non-atomicity, OAM-010 character-progression ownership, existing proficiency JSON, generic combat/perk architecture and all protocol/client/map/asset boundaries. It does not claim Real Tibia proficiency formula/perk parity or migrate achievement 567.

# Current state

```text
Canary reconciliation base: 9627b7524c4da232a47d9c75f2da907cc918b0b6
Otheryn target head after OAM-011: 72f7bdc1a5afa9e9982c20bdcf3098c83dca543e
maintained OTClient: 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
OAM-001..OAM-011: feature/lifecycle complete
OAM-011 task: archived
OAM-012: not created and not started
```

No OAM implementation task is active in this reconciliation record.

# Queue

| Package | Status | Next action |
|---|---|---|
| OAM-001..OAM-011 | completed | preserve durable evidence |
| OAM-012+ | planned, not active | only after this reconciliation merges: perform fresh live-state/open-PR/ownership and exact target/upstream/legacy preflight, then select one dependency-valid canonical package |

# Invariants and known gaps

- Canonical registry remains the sole migration inventory; broad path/file differences are discovery evidence only.
- A proof-harness failure is not automatically a target defect; evidence must isolate the selected behavior.
- Child LuaScriptInterface reload semantics, polymorphic Lua userdata safety, concurrent config reload, broader DI cleanup, generic KV eviction failure handling, untouched crash recovery and generic DDL reversibility remain unproven/incomplete.
- OAM-006 does not claim exhaustive old-protocol physical coverage.
- OAM-007 does not claim full item/map/movement parity.
- OAM-008 does not claim broad vocation gameplay parity.
- OAM-009 proves only its deterministic vocation login/relog boundary.
- OAM-010 does not claim Real Tibia progression parity; legacy disconnect-death protection remains deliberately unadopted.
- OAM-011 does not claim Real Tibia proficiency parity and deliberately excludes achievement 567.

# Exact next task

Merge this program-only OAM-011 completion reconciliation after exact-head Ownership/CI/review gates. Only then may a fresh OAM-012 preflight begin. OAM-012 is not created or started by this record.
