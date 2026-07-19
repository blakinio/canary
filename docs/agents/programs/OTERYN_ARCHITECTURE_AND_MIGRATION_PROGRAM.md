---
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
name: Oteryn Architecture and Migration
status: active
owner: oteryn-architecture-migration-agent
created: 2026-07-15T15:28:18+02:00
updated: 2026-07-19T15:55:00+02:00
last_verified_commit: "f62481d7ab2e5d13bb74c53e57a5b79bd1d4eb29"
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
| OAM-014 | `combat-conditions → ADAPT` | target `9d797b547c3f85f6d210c6123202c7cae32d5133`; feature `c9ba742731ebea2ccaf73b8b7ae78ee855ad9109`; lifecycle `9d492db84ee50d78c368b818b2ee9a7e297e8748` |
| OAM-015 | `weapons → REUSE` | target proof `1dd21117ce06cc4463e6185f4ff74546031b55e6`; feature `5b9a0a4c23e5114e59e36ad71fb20087473cd9d3`; lifecycle `ef553ef12e1a5b167dff6032b5b44b686dbf4675` |
| OAM-016 | `spells → REUSE` | target proof `46cc7458d644da356371aabf3ff18c0e51d228a8`; feature `a646f0bba6e1a168c9e190abaf483cff817a5e9b`; lifecycle `c1925725f05fffb2b57971fa929e4af5dd06d6b0` |
| OAM-017 | `containers → REUSE` | target proof `952e7550182df739824bddea687ef89bd8997674`; feature `b868e2855f6194d9fd4f88c5a56ba8e300e3c568`; lifecycle `041ca9017fde929429ffb28fb6bfdc615f21b9f6` |
| OAM-018 | `item-decay → REUSE` | target proof `7ba76d2754a060a9a9eec0a23c686aefac725af2`; feature `df97440551ca141b340ff424b1d644430bbb3c28`; lifecycle `5f0656442d6b7856dcc5099e29a78782abaa1170` |
| OAM-019 | `imbuements → ADAPT` | target `63547f30fc21e495217b8a92fa44aaad2db188ef`; feature `f38832dd160910e76d1576bb2c1221374a6ae8b1`; lifecycle `f62481d7ab2e5d13bb74c53e57a5b79bd1d4eb29` |

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

# OAM-014 durable completion

Final disposition:

```text
combat-conditions ADAPT
```

Task-start baselines were Canary `0253b712cd4275e8ad72d5bca7020d1f4a2246b7`, Otheryn `3628effc5f22e7edbdc66dc5f514e4df5c9f0cda`, upstream `e0ac98e399d0f7e483f3668f57b78fcc45b6e53f`, and OTClient `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`. The canonical `combat-conditions` module depends on completed OAM-013 `combat`.

Task-start target and pinned upstream shared `src/creatures/combat/condition.cpp` blob `5b15ed00c7e92eef6d8c719aec423443efae8b7a`. Reviewed Canary PR #297 final head `b7f5de1f04cd3b521ee9621a0f001f0ced5e6c39` supplied the exact accepted bounded donor: runtime blob `26a1cf0c9e01f4ab162438e8284f5cc73d129d11`, focused test blob `ee2f185042cdb359aac1a752dce971ec76c38f8d`, and condition-test CMake blob `b224d4eb1eb15eb92ca4a26f214c0764b82b03c3`. Reviewed-history audit found no second delivered `condition.cpp` fix requiring coupling.

The accepted adaptation normalizes zero `ConditionLight` level to minimum valid level `1` before start-condition fade-interval division and when deserializing persisted state, while preserving valid nonzero behavior. It does not rewrite persisted data automatically and does not broaden condition ownership beyond this reviewed correctness boundary.

Otheryn PR #35 final head `f4044811f2b930318ec6541a51e73a9a1b6fdce0` contained exactly the three accepted donor paths and no temporary materializer helpers. It passed CI `29642976283`, Required `29642976213`, autofix `29642976219`, Linux debug build, Canary runtime smoke, database schema import and actual CTest. The full target suite completed 351/351 with zero failures and `ConditionLightTest` passed 3/3. Primary test artifact `8429300008` has digest `sha256:328f60045be1d42e4fba0c6b80aa64a3b8e767553808d7c47119750922cc2e36`. Target merge is `9d797b547c3f85f6d210c6123202c7cae32d5133`.

Canary governance PR #539 final head `9c806ec8524d59430395173d8187ef90d8b2e64d` passed Ownership `29643562904` and ready-state CI `29643583135` with Required PASS, zero comments/reviews/threads and no main drift, then merged as `c9ba742731ebea2ccaf73b8b7ae78ee855ad9109`. Lifecycle PR #541 final head `8434805bb80d5d9cd2c072e9bb857d6a09cd070f` passed Ownership `29643697230` and CI `29643697256` with Required PASS, zero comments/reviews/threads and no main drift, then merged as `9d492db84ee50d78c368b818b2ee9a7e297e8748`.

OAM-014 preserves OAM-004 SQL/KV non-atomicity and completed OAM-013 generic combat ownership. It changes no spell definitions, protocol, client, map or assets and performs no broad persistence redesign. It does not claim exhaustive condition timing/stacking/persistence correctness or full Real Tibia condition formula/value parity.

# OAM-015 durable completion

Final disposition:

```text
weapons REUSE
```

Task-start baselines were Canary `051f4101cac5250dd41d8aa0914fcc8761b08d64`, Otheryn `9d797b547c3f85f6d210c6123202c7cae32d5133`, upstream `691614c1a302aee776002ca3851eca399be1a82c`, and OTClient `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`. The canonical module depends only on completed OAM-013 `combat`.

OAM-002 whole-tree bootstrap evidence established that the canonical OAM-015 production boundary started from exact pinned upstream content rather than legacy runtime history. Target history from the OAM-002 verified target through the OAM-015 task-start head and upstream history through the OAM-015 pinned upstream head contained no production mutation in that canonical boundary. Representative exact task-start target/upstream blobs were `src/items/weapons/weapons.cpp` `4094a124e42263047b81a459d93b187aeca25c7f` and `src/items/weapons/weapons.hpp` `093c58aef02b4f2ea44b21796ba697ca0a2e7add`. This bounded whole-history provenance, not blob identity alone, supports `REUSE`.

Merged legacy Canary PR #78 was reviewed explicitly. It is a coherent cross-module virtual wand/Cyclopedia display compatibility change spanning item parsing, the canonical runtime file, and protocol serialization. It moves display metadata publication before removing the runtime `const_cast` fragment and explicitly does not alter the actual gameplay damage roll. OAM-015 therefore did not partially import one file fragment or reopen completed OAM-006 protocol and OAM-007 item-definition ownership. Upstream issue #3645 remains a separately recorded unresolved cross-module display compatibility gap. OAM-015 makes no wand/Cyclopedia display-parity or physical-client closure claim.

Proof-only Otheryn PR #37 final head `183800b4a83f86ec0b5eb160501f293d9ae59399` changed exactly `tests/unit/items/CMakeLists.txt` and `tests/unit/items/weapon_reuse_test.cpp`, with no production runtime/data mutation. It passed CI #121 run `29646448123`, Required #111 run `29646448049`, autofix.ci #104 run `29646448054`, Windows, macOS, Linux release, Linux debug build, Canary runtime smoke, database schema import and actual CTest. The full target suite completed 353/353 with zero failures and the focused OAM-015 tests passed 2/2. Primary test artifact `8430298608` has digest `sha256:5e2bca685d11fce37b6e71a80fe82346c8a6b3d9a3bca95bf127122f2cf1e9b8`. Target proof merge is `1dd21117ce06cc4463e6185f4ff74546031b55e6`.

Canary governance PR #544 final head `e496185bb2aa384ad60ebb0ee36f4d11ee1fd6ce` passed Agent Task Ownership #2325 run `29647381853` and CI #3466 run `29647381945` with Required PASS. It had zero comments/reviews/threads, exactly two governance paths, no Canary-main drift, and merged by expected-head squash as `5b9a0a4c23e5114e59e36ad71fb20087473cd9d3`. Lifecycle PR #546 final head `b7095b34b5a68a209d03f1cb540371fb15277582` passed Agent Task Ownership #2329 run `29647501401` and CI #3469 run `29647501488` with Required PASS. It had zero comments/reviews/threads, exactly the active-delete/archive-add lifecycle paths, no main drift, and merged by expected-head squash as `ef553ef12e1a5b167dff6032b5b44b686dbf4675`.

The post-merge automation also opened duplicate archive PR #545 for governance PR #544; it was explicitly closed after the authoritative lifecycle PR #546 was established. During OAM-015 housekeeping, stale self-owned automatic archive duplicates #516, #520, #530, #536 and #540 from earlier completed OAM packages were also closed. Unrelated archive PRs were not touched.

OAM-015 preserves OAM-004 SQL/KV non-atomicity and completed OAM-006/OAM-007/OAM-013/OAM-014 ownership. It does not claim exhaustive weapon formula/hit-rate correctness, exhaustive resource consumption, full individual script parity, wand/Cyclopedia display compatibility, upstream #3645 closure, protocol/client/map/asset parity, or persistence redesign.

# OAM-016 durable completion

Final disposition:

```text
spells REUSE
```

Task-start baselines were Canary `93296bbf0c349a6589af51a311d12f7dfaf6c001`, Otheryn `1dd21117ce06cc4463e6185f4ff74546031b55e6`, upstream `691614c1a302aee776002ca3851eca399be1a82c`, and OTClient `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`. The canonical registry record `spells` depends only on completed OAM-013 `combat` and interacts with separately owned `wheel-of-destiny`.

OAM-002 whole-tree bootstrap evidence established that the canonical spell production boundary started from exact pinned upstream content. Target history from the verified bootstrap through the OAM-016 task-start head and upstream history through the OAM-016 pinned upstream head contained no production mutation in `src/creatures/combat/spells/**`, `data/scripts/spells/**`, or `data-otservbr-global/scripts/spells/**`. Representative exact task-start core blobs were `src/creatures/combat/spells.cpp` `4afc2bafdcd3d122097b973931845b0fec7f32fb` and `src/creatures/combat/spells.hpp` `d419f509853b3eb45658c2e8f5d6fbaec1f8d611`. This bounded whole-history provenance, not blob identity alone, supports `REUSE`.

Reviewed legacy history found two real but cross-module difference classes that were deliberately not partially migrated. Canary PR #76/#108 adds and hardens Gameplay Analytics instrumentation in representative spell/rune scripts; Analytics ownership is outside OAM-016. Canary PR #216/#220 changes `flurry_of_blows.lua` and `front_sweep.lua` as part of a coordinated Wheel of Destiny 15.25 package; OAM-016 did not import only the spell-side fragments or reopen unresolved Wheel ownership. These remain separately recorded Analytics and Wheel/spells gaps rather than hidden evidence against the selected core.

Proof-only Otheryn PR #39 final head `62a61725c66a2c394327cb665f08d076c2b7d791` changed exactly `tests/unit/game/CMakeLists.txt` and `tests/unit/game/spell_reuse_test.cpp`, with no production runtime/data mutation. It passed CI #123 run `29651516932`, Required #112 run `29651516827`, autofix.ci #105 run `29651516800`, platform builds, runtime smoke and database schema import. The full target suite completed 355/355 with zero failures and `SpellReuseTest` passed 2/2. Primary test artifact `8431734928` has digest `sha256:e98fc12c4e8c4f661d96ebb39a7b7fe44d58c2e7c7dc53beb27c14773f0db5f8`. Target proof merge is `46cc7458d644da356371aabf3ff18c0e51d228a8`.

Canary governance PR #549 final head `c9f6335f0c3361f47d154af00d123e8cf6ca238c` passed Agent Task Ownership #2338 run `29652474874` and CI #3476 run `29652474962` with Required PASS. It had zero comments/reviews/threads, exactly two governance paths, no Canary-main drift, and merged by expected-head squash as `a646f0bba6e1a168c9e190abaf483cff817a5e9b`. Earlier draft governance PR #548 was closed after final evidence was moved to non-draft PR #549 under a neutral branch label required by the tooling classifier.

Lifecycle PR #551 final head `823e52fd02798514b5421e27552685a60cfdc5fc` passed Agent Task Ownership #2342 run `29652592820` and CI #3479 run `29652592881` with Required PASS. It had zero comments/reviews/threads, exactly the active-delete/archive-add lifecycle paths, no Canary-main drift, and merged by expected-head squash as `c1925725f05fffb2b57971fa929e4af5dd06d6b0`. The post-merge automation also opened duplicate archive PR #550 for governance PR #549; it was explicitly closed after authoritative lifecycle PR #551 was established.

OAM-016 preserves OAM-004 SQL/KV non-atomicity and completed OAM-006/OAM-007/OAM-013/OAM-014/OAM-015 ownership. It does not claim exhaustive spell formula or hit/heal value correctness, exhaustive cooldown enforcement, exhaustive mana/soul/resource/rune consumption, full individual spell-script parity, Gameplay Analytics parity, Wheel spell-augmentation parity, protocol/client/map/asset parity, or persistence redesign.

# OAM-017 durable completion

Final disposition:

```text
containers REUSE
```

Task-start baselines were Canary `6c2ed7fd5d7e0f51bf7bfc75ebcc30b840315e41`, Otheryn `46cc7458d644da356371aabf3ff18c0e51d228a8`, upstream `691614c1a302aee776002ca3851eca399be1a82c`, and OTClient `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`. The canonical `containers` package depends only on completed OAM-007 `item-instances`.

OAM-002 whole-tree provenance plus target/upstream history through task start found no canonical production mutation under `src/items/containers/**` or `src/items/cylinder.*`. Representative task-start blobs were `src/items/containers/container.cpp` `2688a2d59bebac33b801cfdd11d0aa5c26a07016` and `src/items/cylinder.cpp` `82c6cf3fd6dff9d579d35cfbaf1f4b52ec4c46b8`, shared by target, pinned upstream and legacy. Identity alone was not accepted; delivered legacy history was reviewed. Canary PR #60 was rejected as a container-runtime donor because it changes house-transfer orchestration only, and PR #108 was rejected because it changes Gameplay Analytics instrumentation rather than the canonical container/cylinder runtime.

The initial proof head `7dcdcff1dde59a702b00d77f5049bd99a126a6eb` failed only the two new focused `ContainerReuseTest` cases with SEGFAULT. The failure was isolated to the proof harness: unit startup had an empty item-type registry, while synthetic `Item(0)` / `Container(0, ...)` construction reached the item-type lookup fallback before the container behavior under test. The tests-only `ScopedItemTypeRegistry` fix supplied the minimum synthetic registry state and restored it afterward. No production container/cylinder or other runtime/data path changed.

Otheryn PR #41 final head `ee111cb6ef6299a0de7fb19de76934b6369b7cf0` changed exactly `tests/unit/items/containers/container_test.cpp`. It passed autofix.ci #108 run `29679028025`, CI #127 run `29679028059`, Required #115 run `29679028000`, full CTest 357/357 and focused `ContainerReuseTest` 2/2. Artifact `8440064893` has digest `sha256:28d82a5a1d36d89a8892280e73bb671a846743962786922093a907e8b80b79c1`. Target comments/reviews/threads were empty, target-main drift was none, issue #40 was closed completed, and PR #41 merged by expected-head squash as `952e7550182df739824bddea687ef89bd8997674`.

Canary governance PR #555 final head `80650619eb9565398f1b8800ec1d463d90602a3c` passed Agent Task Ownership #2476 run `29679578835` and full final-gate CI #3618 run `29679591913`. It had zero comments/reviews/threads, exactly the two OAM-017 governance paths, and the 11-commit Canary-main drift from the immutable task-start base did not overlap those paths. It merged by expected-head squash as `b868e2855f6194d9fd4f88c5a56ba8e300e3c568`.

Authoritative lifecycle PR #576 final head `63d2f8067b8e53a5ae9c42dd6161fbf81d2a7aa2` passed Agent Task Ownership #2494 run `29680259710` and CI #3635 run `29680259780` with Required PASS. It had zero comments/reviews/threads, exactly the active-delete/archive-add lifecycle paths, and no Canary-main drift before merge, then merged by expected-head squash as `041ca9017fde929429ffb28fb6bfdc615f21b9f6`. The post-governance automation also opened duplicate archive PR #575; it was explicitly closed unmerged only after authoritative lifecycle PR #576 was established.

OAM-017 preserves OAM-004 SQL/KV non-atomicity and completed OAM-007 item-instance ownership. It does not claim transactional move atomicity, absence of duplication or item loss across generic move orchestration, exhaustive cycle safety, full serialization/persistence completeness, restart/crash recovery, depot/inbox/mailbox/reward parity, protocol/client UI parity, market/boss-reward/item-decay parity, or full Real Tibia container formula/value semantics.

# OAM-018 durable completion

Final disposition:

```text
item-decay REUSE
```

Task-start baselines were Canary `3c4d2789ffa3d0c1e9453d20a8c5faeba35eb366`, Otheryn `952e7550182df739824bddea687ef89bd8997674`, upstream `691614c1a302aee776002ca3851eca399be1a82c`, and OTClient `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`. Canonical `item-decay` depends on completed OAM-003 `engine-scheduler` and OAM-007 `item-instances`; OAM-017 `containers` is an interaction, not a fundamental dependency.

Target history from verified OAM bootstrap through task start and pinned-upstream history through `691614c1a302aee776002ca3851eca399be1a82c` contained no production mutation under `src/items/decay/**`. Target and upstream shared `src/items/decay/decay.cpp` blob `a337b872755217d87ac2261de6c3c1a593d805a6`, while all reviewed sources shared `decay.hpp` blob `0d540e10dc73b65f2ce1aa00bfb9dd72994dcc5f`. The narrow legacy Canary `decay.cpp` difference omits `DispatcherLane::Maintenance` from the three decay scheduling calls; OAM-003 had already established the target/upstream lane/WDRR scheduler as canonical, so that legacy delta was rejected as a stronger donor.

Proof-only Otheryn PR #42 final head `13e245f3c49477fa75c20171f0c845dec91d0824` changed exactly `tests/unit/items/CMakeLists.txt` and `tests/unit/items/decay/decay_test.cpp`, with no production `src/items/decay/**` or other runtime/data/client mutation. It passed autofix.ci #110 run `29682419114`, CI #130 run `29682419178`, Required #117 run `29682419125`, full Linux debug CTest 359/359 and focused `ItemDecayReuseTest` 2/2. Artifact `8441163603` has digest `sha256:de3f541b41aa9d4f39a4d8d629de52a51e09b8eaff461c8706bb7a296cfd9631`. The first ready-cycle macOS smoke wrapper failure was classified as transient because compilation succeeded, its runtime artifact showed a clean online startup and shutdown with empty stderr, and one same-head failed-job rerun passed without code changes. Target comments/reviews/threads were empty, target-main drift was none, and PR #42 merged by expected-head squash as `7ba76d2754a060a9a9eec0a23c686aefac725af2`.

Canary governance PR #578 final head `80681dd0bbaa6bed0d212bc90b7a0c728e73b836` passed Agent Task Ownership #2531 run `29683370000` and full final-gate CI #3675 run `29683558587` with the Linux debug/release, macOS, both Windows, Docker, Fast Checks, Lua and Required chain green. It had zero comments/reviews/threads and exactly the two OAM-018 governance paths. Non-overlapping Canary-main drift was audited before merge, and PR #578 merged by expected-head squash as `df97440551ca141b340ff424b1d644430bbb3c28`.

Authoritative lifecycle PR #584 final head `f8c8442f00fe829c78903116cde32733ae817dd1` passed Agent Task Ownership #2555 run `29684823002` and CI #3697 run `29684823101` with Required PASS. It changed exactly the active-delete/archive-add lifecycle paths; heavy build jobs were correctly skipped for lifecycle-only scope. Main drift before merge consisted only of unrelated task archival commits and did not overlap OAM-018 lifecycle paths. It merged by expected-head squash as `5f0656442d6b7856dcc5099e29a78782abaa1170`. No automation-created duplicate archive PR for governance #578 was found, so no duplicate closure was required.

OAM-018 preserves OAM-004 SQL/KV non-atomicity and completed OAM-003 scheduler/OAM-007 item ownership. It does not claim scheduler fairness or starvation freedom, exact wall-clock decay timing, restart/crash decay recovery, persistence completeness, item move/container transaction atomicity, duplication/loss freedom, static decay metadata parity, exhaustive transform correctness, protocol/client UI parity, or full Real Tibia decay semantics.

# OAM-019 durable completion

Final disposition:

```text
imbuements ADAPT
```

Task-start baselines were Canary `e551f3fd33c9642399bb1e70d1f2f6383464b936`, Otheryn `7ba76d2754a060a9a9eec0a23c686aefac725af2`, upstream `691614c1a302aee776002ca3851eca399be1a82c`, and OTClient `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`. Canonical `imbuements` depends on completed `combat` and `player-persistence`; `protocol` is an interaction boundary. Fresh task-start ownership review found no overlapping live Imbuement runtime/data writer.

Whole-module `REUSE` was rejected because task-start Otheryn lacked a coherent chain of delivered legacy correctness and data repairs. The accepted bounded donor chain is merged Canary PR #86 for configured-storage filtering, #206 for Powerful Forgotten Knowledge storage reconciliation, #239 for Vibrancy scroll mappings, #251 for the selected confirmed fee/Strike/Punch/Featherweight/Vibrancy data contract, and #282 for direct numeric-ID premium/storage authorization before relevant resource mutation. OAM-019 did not bulk-copy legacy `player.cpp`; only reviewed Imbuement-specific hunks, two isolated policy helpers, exact registry data and focused tests were adapted into the target.

Otheryn PR #43 final head `4e993c4ee160fe03d8575c1b830ef71dde450562` changed exactly ten intended Imbuement runtime/data/test paths and no temporary materializer paths. It passed autofix.ci #121 run `29687711140`, Repository Audit #12 run `29687711133`, CI #142 run `29687711219`, Required #128 run `29687711131`, Linux debug build/runtime smoke/schema import and full CTest `367/367`. The eight new focused OAM-019 tests passed `8/8`. Primary test artifact `8442743109` has digest `sha256:a0ef33bd15be8d004dce89ce5014782990961cb239c50e9f48f19d906694c6e0`. The first macOS smoke wrapper attempt was transient: its artifact showed successful online startup and clean shutdown with empty stderr, and one permitted same-head rerun passed without code changes. Target comments/reviews/threads were empty, target-main drift was none, and PR #43 merged by expected-head squash as `63547f30fc21e495217b8a92fa44aaad2db188ef`.

Canary governance PR #588 final head `42d46421df0f0c5191eaf857f19aa4fa3fe42df9` passed Agent Task Ownership #2607 run `29688560927`, Imbuement Validation #326 run `29688560945`, and full `ci:final-gate` CI #3750 run `29688564115`. Every platform build/test job passed. The first workflow attempt failed only in the Docker Quickstart/Required tail; one permitted same-head failed-jobs rerun passed Docker Quickstart and the overall CI completed successfully without a head change. The PR had exactly two governance paths, zero comments/reviews/threads and no Canary-main drift before merge, then merged by expected-head squash as `f38832dd160910e76d1576bb2c1221374a6ae8b1`.

Authoritative lifecycle PR #590 final head `9b26a10519fbeb3e5bff8587bf48e0b780129bc9` passed Agent Task Ownership #2610 run `29689465413`, Imbuement Validation #328 run `29689465406` and CI #3752 run `29689465487` with Required PASS; heavy build jobs were correctly skipped for lifecycle-only scope. The only Canary-main drift before merge was unrelated E2E work with no overlap in the active/archive OAM-019 paths. The PR had zero comments/reviews/threads and merged by expected-head squash as `f62481d7ab2e5d13bb74c53e57a5b79bd1d4eb29`. No automation-created duplicate archive PR for governance #588 was found, so no duplicate closure was required.

OAM-019 preserves OAM-004 SQL/KV non-atomicity and all previously completed combat, persistence, item and protocol ownership boundaries. It does not claim exhaustive current Real Tibia Imbuement parity, exhaustive equipment eligibility, full live quest-unlock visibility, exact protocol/UI presentation across all clients, physical-client E2E closure, exhaustive combat-math parity, production crash/restart persistence completeness, generic resource transaction atomicity, or changes to generic items, Exaltation Forge, maps, assets, `items.otb`, schema or client code.

# Current state

```text
Canary reconciliation base: f62481d7ab2e5d13bb74c53e57a5b79bd1d4eb29
Otheryn target head after OAM-019: 63547f30fc21e495217b8a92fa44aaad2db188ef
maintained OTClient: 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
OAM-001..OAM-019: feature/lifecycle complete
OAM-019 task: archived
OAM-020: NOT STARTED
```

No OAM implementation task is active in this reconciliation record.

# Queue

| Package | Status | Next action |
|---|---|---|
| OAM-001..OAM-019 | completed | preserve durable evidence |
| OAM-020+ | planned, not active | only after this reconciliation merges: perform fresh live-state/open-PR/ownership and exact target/upstream/legacy preflight, then select one dependency-valid canonical package |

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
- OAM-014 does not claim exhaustive condition timing, stacking or persistence correctness, nor full Real Tibia condition formula/value parity.
- OAM-014 normalizes invalid zero light state in memory but does not claim automatic persisted-data repair or broader persistence completeness.
- OAM-015 does not claim exhaustive weapon correctness, full Real Tibia weapon formula/value parity, exhaustive resource/script parity, or closure of the separate upstream #3645 cross-module display compatibility gap.
- OAM-016 does not claim exhaustive spell correctness, full Real Tibia spell formula/value parity, exhaustive cooldown/resource/script parity, Gameplay Analytics parity, or closure of the separate Wheel/spells cross-module gap.
- OAM-017 does not claim transactional move atomicity, duplication/loss freedom across generic move orchestration, exhaustive cycle safety, full persistence/recovery, container UI/protocol parity, or full Real Tibia container semantics.
- OAM-018 does not claim scheduler fairness/starvation freedom, exact wall-clock decay timing, restart/crash recovery, persistence completeness, movement/container atomicity, duplication/loss freedom, static metadata parity, exhaustive transform correctness, protocol/client UI parity, or full Real Tibia decay semantics.
- OAM-019 does not claim exhaustive Imbuement parity, exhaustive equipment eligibility, full live quest-unlock visibility, client/UI parity, physical-client E2E closure, exhaustive combat math, crash/restart persistence completeness, or generic resource transaction atomicity.

# Exact next task

Merge this program-only OAM-019 completion reconciliation after exact-head Ownership/CI/review gates. Only then may a fresh OAM-020 preflight begin. OAM-020 is NOT STARTED by this record.
