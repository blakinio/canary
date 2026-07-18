---
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
name: Oteryn Architecture and Migration
status: active
owner: oteryn-architecture-migration-agent
created: 2026-07-15T15:28:18+02:00
updated: 2026-07-18T12:24:00+02:00
last_verified_commit: "102ee803308b94faa21b328ff47cd2b06edd2a93"
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
| OAM-012 | `achievements → ADAPT` | target `4a16ca17ebd098cf9763bb3c07755bfd31ac1c43`; feature `92b704415ffb53165647c0623d1ab273fc7b723f`; lifecycle `3dfb606d219006986461d31342260f724a5d84bf` |
| OAM-013 | `combat → REUSE` | target proof `3628effc5f22e7edbdc66dc5f514e4df5c9f0cda`; feature `e4596861d8e8497645815d8eefb6cee3166b91d0`; lifecycle `102ee803308b94faa21b328ff47cd2b06edd2a93` |

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

# OAM-012 durable completion

Final disposition:

```text
achievements ADAPT
```

Task-start baselines were Canary `d9c967d6e9b778da11a206d134d559f38ec1b8c8`, Otheryn `72f7bdc1a5afa9e9982c20bdcf3098c83dca543e`, upstream `e0ac98e399d0f7e483f3668f57b78fcc45b6e53f`, and OTClient `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`.

The accepted coherent donor chain is Canary PR #256 → #264 → #288. OAM-012 couples five corrected point metadata values with deterministic persisted aggregate achievement-point reconciliation, fails closed when a stored achievement name cannot be resolved, preserves one authoritative central catalogue at `data/scripts/lib/register_achievements.lua`, and adds achievement `567` / `The Forbidden Build` with the exact reviewed twelve-weapon Weapon Proficiency attainability condition.

Exact donor verification corrected one stale handover assumption: `tests/unit/players/components/player_achievement_test.cpp` at PR #264 donor commit `d14d5c992d4095c79672a8469050aa9e103e34bb` hashes to `c10d90aa649322520739696507ba8a0ff2d05a06`. Materialization failed closed on the stale expected SHA before the corrected exact provenance was accepted. All seven donor-controlled target files were reverified after CI autofix.

Otheryn PR #31 final head `8ee4bfe3c6b867834447a5b9e206e1dbd44f66d2` passed CI `29638502030`, Required `29638501951`, Repository Audit `29638501958`, and autofix `29638501946`. Linux debug build, Canary runtime smoke, database schema import, and actual CTest all passed. The full target suite completed 346/346 with zero failures; `PlayerAchievementTest` passed 7/7 and `WeaponProficiencyTest` passed 10/10, including the three `The Forbidden Build` cases. Primary test artifact `8427980477` has digest `sha256:170df7911fd928bb6af90c7f703e00554eccb4625a56d9fd54cc20e0854e0d3e`. Target merge is `4a16ca17ebd098cf9763bb3c07755bfd31ac1c43`.

Canary governance PR #524 final head `46e3d4c07146ac8c0eb034ea4b40259d042d6cbe` passed Ownership `29639189342` and CI `29639189415` with Required PASS, zero blocking comments/reviews/threads, and merged as `92b704415ffb53165647c0623d1ab273fc7b723f`. Lifecycle PR #531 final head `da87216a32eadf8ee16dcaffa9560e80f03e883a` passed Ownership `29639318382` and CI `29639318439` with Required PASS, zero blocking comments/reviews/threads, and merged as `3dfb606d219006986461d31342260f724a5d84bf`.

OAM-012 preserves OAM-004 SQL/KV non-atomicity and introduces no generic KV redesign, automatic MySQL reconnect, arbitrary SQL replay, or cross-domain transaction. It does not add unrelated quest/combat/spell achievement hooks, a duplicate or overlay catalogue, client/protocol/map/asset changes, or a claim of full Real Tibia achievement attainability parity. The canonical module registry metadata still does not explicitly name the proven central catalogue path; that is a non-blocking governance metadata cleanup gap, not permission for a second runtime source of truth.

# OAM-013 durable completion

Final disposition:

```text
combat REUSE
```

Task-start baselines were Canary `e3563b447228830a4728790b52766dad56fe86f1`, Otheryn `4a16ca17ebd098cf9763bb3c07755bfd31ac1c43`, upstream `e0ac98e399d0f7e483f3668f57b78fcc45b6e53f`, and OTClient `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`.

The task-start Otheryn generic combat core was exact-identical to pinned upstream for `combat.cpp` blob `8c3a2c87ead3e55c0ae219a0f8b075a44c3dec0a`; `combat.hpp` blob `125390ed1a35cf804f5b31dbec61bcca346275c2` was shared by target, upstream and legacy. Identity alone was not accepted as sufficient: reviewed legacy combat history was audited semantically before selecting `REUSE`.

Canary PR #297 contains a real zero-level `ConditionLight` correctness fix, but TSD-005 and the canonical registry assign that lifecycle behavior to downstream `combat-conditions`; it was deliberately not migrated in OAM-013. Canary PR #92 was rejected as a runtime donor because its described `combat.cpp` chain-target wiring is absent from both its final head and the task-start legacy main, while its Wheel portion is cross-boundary. No reviewed, delivered, dependency-valid generic-combat runtime adaptation was identified that should replace the pinned target/upstream core.

Proof-only Otheryn PR #33 final head `6d5dfe623fef1a6db9b8447d1978a2a6bb1272eb` changed only `tests/unit/game/CMakeLists.txt` and `tests/unit/game/combat_reuse_test.cpp`. It passed CI `29639923928`, Required `29639923874`, autofix `29639923867`, Linux debug build, Canary runtime smoke, database schema import and actual CTest. The full target suite completed 348/348 with zero failures and `CombatReuseTest` passed 2/2. Primary test artifact `8428406618` has digest `sha256:9165209e09bdef873563b6fef90516d80032e280244af702843cc55f22774635`. Target proof merge is `3628effc5f22e7edbdc66dc5f514e4df5c9f0cda`.

Canary governance PR #533 was clean-synchronized onto non-overlapping OTBM roadmap drift at `main@abbeb51433d33af7398a82f0cd2ab776d01e710f`. Final head `f9ebe10abe28f03326ffab938f472c7c72d991cb` passed Ownership `29640617395` and CI `29640617474` with Required PASS, had zero comments/reviews/threads and no further main drift, then merged as `e4596861d8e8497645815d8eefb6cee3166b91d0`. Lifecycle PR #537 final head `f249c0dd95dc8d592def4f612d7078edc5b1bb20` passed Ownership `29640706327` and CI `29640706382` with Required PASS, zero comments/reviews/threads and no main drift, then merged as `102ee803308b94faa21b328ff47cd2b06edd2a93`.

OAM-013 preserves OAM-004 SQL/KV non-atomicity and changes no generic combat production code, persistence, protocol, client, map or assets. It does not claim exhaustive combat correctness or full Real Tibia combat formula/value parity. The reviewed PR #297 light-condition fix remains downstream evidence for `combat-conditions`, not a residual defect claim against completed generic `combat` ownership.

# Current state

```text
Canary reconciliation base: 102ee803308b94faa21b328ff47cd2b06edd2a93
Otheryn target head after OAM-013: 3628effc5f22e7edbdc66dc5f514e4df5c9f0cda
maintained OTClient: 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
OAM-001..OAM-013: feature/lifecycle complete
OAM-013 task: archived
OAM-014: NOT STARTED
```

No OAM implementation task is active in this reconciliation record.

# Queue

| Package | Status | Next action |
|---|---|---|
| OAM-001..OAM-013 | completed | preserve durable evidence |
| OAM-014+ | planned, not active | only after this reconciliation merges: perform fresh live-state/open-PR/ownership and exact target/upstream/legacy preflight, then select one dependency-valid canonical package |

# Invariants and known gaps

- Canonical registry remains the sole migration inventory; broad path/file differences are discovery evidence only.
- A proof-harness failure is not automatically a target defect; evidence must isolate the selected behavior.
- Child LuaScriptInterface reload semantics, polymorphic Lua userdata safety, concurrent config reload, broader DI cleanup, generic KV eviction failure handling, untouched crash recovery and generic DDL reversibility remain unproven/incomplete.
- OAM-006 does not claim exhaustive old-protocol physical coverage.
- OAM-007 does not claim full item/map/movement parity.
- OAM-008 does not claim broad vocation gameplay parity.
- OAM-009 proves only its deterministic vocation login/relog boundary.
- OAM-010 does not claim Real Tibia progression parity; legacy disconnect-death protection remains deliberately unadopted.
- OAM-011 does not claim Real Tibia proficiency parity; achievement 567 is now owned by completed OAM-012 rather than OAM-011.
- OAM-012 does not claim full Real Tibia achievement attainability parity; unrelated achievement hooks remain outside the accepted bounded package.
- OAM-012 canonical registry data-path metadata should eventually be normalized to explicitly include the proven central catalogue path.
- OAM-013 does not claim exhaustive combat correctness or full Real Tibia combat formula/value parity.
- OAM-013 leaves the reviewed zero-level light-condition fix to downstream `combat-conditions`, preserving canonical ownership separation.

# Exact next task

Merge this program-only OAM-013 completion reconciliation after exact-head Ownership/CI/review gates. Only then may a fresh OAM-014 preflight begin. OAM-014 is NOT STARTED by this record.
