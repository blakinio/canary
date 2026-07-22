---
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
name: Oteryn Architecture and Migration
status: active
owner: oteryn-architecture-migration-agent
created: 2026-07-15T15:28:18+02:00
updated: 2026-07-22T11:00:00+02:00
last_verified_commit: "1328fb42b03056a0f2571831a1a1eb7a5416f73a"
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
| OAM-020 | `exaltation-forge → ADAPT` | target `d59207d05ab6dd9450b05d0a6b4d9122fda60489`; feature `2b6ae86539640dfc52323e9d5abbde31d6610c5f`; lifecycle `a3896b67e94990712e00e877666f2bd54dceb22a` |
| OAM-021 | `market → ADAPT` | target `b90e287a40413102c87e8c7fa3d5c01ad401cb6d`; feature `76273c0cb7c2e297c8896a8e7fb6809649fa2870`; lifecycle `2c448205d864f6388b8be932ecbb1a9e6dcaffe0` |
| OAM-022 | `prey → REUSE` | target proof `50dfa248251f245f5519495a4fbd430b6814ffe4`; feature `e3a5cc7321636270db150d289ba2da9ddb99ef0d`; lifecycle `4aa0a054cbd3fcbc45e2bda5b58ab016df6438e6` |
| OAM-023 | `parties → REUSE` | target proof `bcc3e9f7e3e704f3c012bda8693648d52741630f`; feature `e78d927e54d965d742fe762e86c9ea454d068c4a`; lifecycle `060fe0fa018e55725c93daee5dd4cadec0a68162` |
| OAM-024 | `sanctions → ADAPT` | target `65d364b216843db27e84a19a673eee4e6d766c68`; feature `7662d048a75df37f5bfc4238e12fd3b18c935151`; lifecycle `0de75bd2de28c80e9d9587bd3a2520c29c5f267c` |
| OAM-025 | `chat-communication → ADAPT` | target `1c8e3e8b4fc29effb3b0cb882af94f7d26ed2554`; feature `791bca7403da1e93fba96143f42983f09aa10381`; lifecycle `8ed836aae47d6bb882fb646169d2930f951c6c0d` |
| OAM-026 | `guilds → ADAPT` | target `418a9f0bfc72cc58b9806a49e966d9c3ea3c1a6d`; feature `5a2bc2be3b91abdd46c9edf2f825336472515299`; lifecycle `99b9dec84d953d3f200284d0cf193261027650ca` |
| OAM-027 | `houses → ADAPT` | target `c140c4bb9f40067acc36bc446c9e664e6f791c5a`; feature `436b73863b81bfa1ba27f88642f3a816064759fc`; lifecycle `562961ee0dd0c2626ab845dc307ec748e2a6bfb7` |
| OAM-028 | `cyclopedia → REUSE` | target `7e03405aea50d88fdbc27d0d2a7d95c7f1745946`; feature `a28e661c4119857eff36948c4549045f57eae545`; lifecycle `ff694b9e908148fb12cca69a76fc2786d9a0f2c3` |
| OAM-029 | `cyclopedia-character → ADAPT` | target `908834adc7d7e7e4ced7404391c7966b1c961b18`; feature `a5e5565d546a530fc3a3010deb65e9283f6eacab`; lifecycle `2a4b717448e55e1a2c24578df44eb981f8ae4bfd` |
| OAM-030 | `bosstiary → ADAPT` | target `dc483d6e8d659d61482da2af7abda9b46b1766ff`; feature `6c092568e44dcb0b13959a8f22c14a992565aa7b`; lifecycle `994d1ffdfd6828688b1acc6cd7c0c519eab052ba` |
| OAM-031 | `bestiary → ADAPT` | target `86e4b08c28ede2f35c215a7c2327a579f4a61419`; feature `e55e0d548d6013da6676cc7b06cbb8d459ccdd1f`; lifecycle `0fca8ced2d952eab744238f826af81cb9ee135b1` |
| OAM-032 | `titles → REUSE` | target `f5f21347c578a382cf0c52dbb4c69673ab3b05a9`; feature `212d5e5c4ecbb0bd392880019747e2370299c748`; lifecycle `fda6d01b93929ea998965354908062eb6e4e1424` |
| OAM-033 | `charms → ADAPT` | target `c887318a676998da5ef3224a3aa8d1e0df75e607`; feature `5ecc72762feb6bda8f6549ac4238a75247752449`; lifecycle `d83563943e298df33edd084e944812464b8a3ff2` |
| OAM-034 | `creature-definitions → ADAPT` | target `566b3b001987f6f452663b77c380e6405bfc541b`; feature `2a63c4b1efe2a20bf653b419ffd6baea6cb2ee0d`; lifecycle `0ace0e6802501f1752405c4e15d75619171dd4cf` |
| OAM-035 | `creature-ai → REUSE` | target proof `d9359bed541b06c4457d23a352b877caf5e88df7`; feature `dbb832d9f2ac141476b7d0496ceb6149a4101cac`; lifecycle `1328fb42b03056a0f2571831a1a1eb7a5416f73a` |

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

Lifecycle PR #551 final head `823e52fd02798514b5421e27552685a60cfdc5fc` passed Agent Task Ownership #2342 run `29652592820` and CI #3479 run `29652592881` with Required PASS. It had zero comments/reviews/threads, exactly the active-delete/archive-add lifecycle paths, no Canary-main drift, and merged by expected-head squash as `c1925725f05fffb2b57971fa929e4af5dd06d6b0`. The post-governance automation also opened duplicate archive PR #550 for governance PR #549; it was explicitly closed after authoritative lifecycle PR #551 was established.

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

Canary governance PR #555 final head `80650619eb9565398f1b8800ec1d463d90602a3c` passed Agent Task Ownership #2476 run `29679578835` and full final-gate CI #3618 run `29679591913`. It had zero comments/reviews/threads and exactly the two OAM-017 governance paths. Non-overlapping Canary-main drift was audited before merge, and PR #555 merged by expected-head squash as `b868e2855f6194d9fd4f88c5a56ba8e300e3c568`.

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

# OAM-020 durable completion

Final disposition:

```text
exaltation-forge ADAPT
```

Task-start baselines were Canary `c353b89b5a7f783cf4ee22fe1ba91850de837a68`, Otheryn `63547f30fc21e495217b8a92fa44aaad2db188ef`, fresh upstream comparison `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`, previous upstream pin `691614c1a302aee776002ca3851eca399be1a82c`, and maintained OTClient `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`. Canonical `exaltation-forge` depends on completed `player-persistence` and `protocol`; interactions with completed `combat` and separately owned `market` did not broaden the package.

Whole-module `REUSE` was rejected because the task-start target and fresh upstream lacked multiple coherent reviewed legacy Forge repairs, while broad rebuild was rejected because the clean upstream-based Forge core remained usable. The accepted bounded donor chain is merged Canary PRs #89, #110, #177, #250, #257, #259, #262, #267 and #283: normal Transfer rules/cost/history, stable history item identity, Dust killer/party/cap behavior, server-authoritative Fusion/Transfer validation, transactional mutation/rollback, reviewed Dust/Fiendish defaults, exact Premium Dust semantics, Avatar/Momentum effect correctness and history amount/action-type correctness. No whole-file legacy `player.cpp` or `protocolgame.cpp` copy was accepted.

Target-local adaptation preserved Otheryn build contracts by registering the five new helper headers in tracked `vcproj/canary.vcxproj`, guarding PCH-provided standard-library includes for non-PCH builds, and registering the exact Forge tests in the target's current CMake layout rather than copying stale donor CMake files. A target-specific `Oam020ExaltationForgeAdaptTest` proved accepted default, authority, effect-gate and transaction boundaries.

Otheryn PR #44 final head `f05787db7f165d0dae0584b3e06c6526f89a42cd` changed exactly 24 intended paths: 23 bounded Forge runtime/data/test/build paths plus one target-specific OAM-020 proof test, with no temporary materializer paths. It passed autofix.ci #142 run `29701626292`, Repository Audit #19 run `29701626282`, CI #164 run `29701626343`, Required #149 run `29701626255`, Fast Checks, Lua Tests, Linux release/runtime smoke, Linux debug compile/schema/CTest, macOS runtime smoke, both Windows build paths and Docker image validation. Full Linux debug CTest completed `393/393` and `Oam020ExaltationForgeAdaptTest` passed `2/2`. Primary test artifact `8446751016` has digest `sha256:1bc0b22f42693c2eaa4404de0b4e66846d399a1046c1620254a493b9bcba5eef`. Target comments/reviews/threads were empty, target-main drift was none, and PR #44 merged by expected-head squash as `d59207d05ab6dd9450b05d0a6b4d9122fda60489`.

Canary governance PR #598 final head `607b8a7af2f9025993964f858498a70e4bc29a38` changed exactly the two OAM-020 governance paths. It passed Agent Task Ownership #2708 run `29702328659` and full `ci:final-gate` CI #3855 run `29702328760`; Fast Checks, Lua Tests, Linux debug tests, Linux release, macOS, both Windows build paths and Docker image validation were green. It had zero comments/reviews/threads. One unrelated OTBM/E2E commit had advanced Canary `main` from the immutable task-start baseline, but its actual changed paths did not overlap OAM-020 governance. PR #598 merged by expected-head squash as `2b6ae86539640dfc52323e9d5abbde31d6610c5f`.

Authoritative lifecycle PR #604 final head `222ee3f7d751c30fd3ea5dfdeab0ffb0b4a1835b` changed exactly the active-delete/archive-add lifecycle paths. It passed Agent Task Ownership #2716 run `29702985616`, draft CI #3862 run `29702985584` and ready-state CI #3863 run `29703010827`; comments/reviews/threads were empty and Canary `main` had no drift from the governance merge before lifecycle merge. PR #604 merged by expected-head squash as `a3896b67e94990712e00e877666f2bd54dceb22a`.

OAM-020 preserves OAM-004 SQL/KV non-atomicity and all previously completed persistence, protocol, combat and item ownership boundaries. It does not claim exhaustive current Real Tibia Forge parity, physical-client Forge E2E closure, unresolved F-014 through F-019 bonus/result/protocol/maintained-client parity, evidence-blocked F-009/F-010 rule parity, or generic market/combat/item/persistence/protocol redesign. It changes no maps, OTBM, `items.otb`, assets, schema or deployment and makes no maintained-OTClient or upstream write.

# OAM-021 durable completion

Final disposition:

```text
market ADAPT
```

Task-start baselines were Canary `183d7224cb5de57585294d72631f37783b93dc89`, Otheryn `d59207d05ab6dd9450b05d0a6b4d9122fda60489`, fresh upstream `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`, and maintained OTClient `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`. Canonical `market` depends on completed `player-persistence` and `protocol`; completed `exaltation-forge` is an interaction boundary. Fresh ownership review found no target/client OAM-021 writer and no overlapping Canary runtime writer.

The task-start Otheryn and fresh upstream Market core were content-identical in the reviewed `src/io/iomarket.cpp` and Market-owned `src/game/game.cpp` paths, but unconditional whole-module `REUSE` was rejected. Legacy Canary's selected Market deltas are coupled to multichannel `EconomicLedgerStore` and leader-election work and do not form a complete generic exactly-once design. Open shared-state/economy security evidence additionally proves a cross-process partial-fill race and a remote-owner stale-save hazard in the multichannel deployment. Those findings are important constraints for future multiwriter Market work, but they do not justify silently importing the separately owned cluster architecture into the clean single-dispatcher target. Generic crash/restart atomicity between offer/history persistence and item/balance effects remains an explicit known gap.

Otheryn PR #45 final head `f13d4d2d0626c99dd2318ef088ce155f67b0b5ae` changed exactly five intended target paths and no materializer path. The bounded server-only adaptation centralizes deterministic 16-bit offer-counter derivation, fails closed on invalid timestamp/duration lookup windows, strictly parses persisted tier values without parse-then-`uint8_t` truncation, and adds focused deterministic proof. The maintained OTClient wire contract remained unchanged, so no client write was required. Autofix.ci #144 run `29704971999`, CI #167 run `29704972077`, and Required #151 run `29704972006` all passed on the exact final target head. Linux debug CTest completed `396/396`, and `Oam021MarketAdaptTest` passed `3/3`. Test-log artifact `8447725005` has digest `sha256:f6f6b67fda044f1d8b88600a87234f4cb6559ae3e3d9270ddd2a98041948debb`. Target comments/reviews/threads were empty, target-main drift was none, and PR #45 merged by expected-head squash as `b90e287a40413102c87e8c7fa3d5c01ad401cb6d`.

Canary governance PR #607 final head `d2290f6072a8fd9e90f43a164a8426076ff6c718` changed exactly the OAM-021 report and active-task record. It passed Agent Task Ownership #2743 run `29705475496` and exact-head `ci:final-gate` CI #3892 run `29705479591`. Fast Checks, Lua Tests and aggregate Required passed; the final-gate build-scope/immediate-parent reuse policy deliberately skipped Linux/macOS/Windows/Docker rebuild jobs for the two-document governance diff, so OAM-021 does not misrepresent that governance run as a second heavy target matrix. Comments, reviews and review threads were empty, Canary `main` had no drift from the task-start Canary base, and PR #607 merged by expected-head squash as `76273c0cb7c2e297c8896a8e7fb6809649fa2870`.

Authoritative lifecycle PR #610 final head `acd76122590584acb4f71db5786ff43e415f596a` changed exactly the active-delete/archive-add lifecycle paths. It passed Agent Task Ownership #2745 run `29705593288`, draft CI #3893 run `29705593339`, and ready-state CI #3894 run `29705635036`. Comments/reviews and review threads were empty and Canary `main` had no drift from the governance merge before lifecycle merge. PR #610 merged by expected-head squash as `2c448205d864f6388b8be932ecbb1a9e6dcaffe0`.

OAM-021 does not import or claim generic multichannel Redis/session ownership, `economic_ledger` recovery, leader election, crash-safe exactly-once Market operations, cross-process/multiwriter Market safety, remote-player mutation routing, generic bank/account/guild economy redesign, exhaustive Real Tibia Market parity, NPC shops, store products, direct player trade, maps, OTBM, `items.otb`, world assets, schema, deployment, maintained-OTClient changes, or physical-client Market E2E closure.

# OAM-022 durable completion

Final disposition:

```text
prey REUSE
```

Task-start baselines were Canary `800142e65c2975e57647bf34128ab468532218f0`, Otheryn `b90e287a40413102c87e8c7fa3d5c01ad401cb6d`, fresh upstream Canary `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`, and maintained OTClient `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`. Canonical `prey` depends on completed `player-persistence` and `protocol`; `wheel-of-destiny` is an interaction boundary and remains separately owned.

The reviewed classic Prey/Task Hunting core has no stronger independent legacy donor. `src/io/ioprey.cpp` blob `b0e335f5a4f7f9d8a3da75196dedf0d49242ef17`, `src/io/ioprey.hpp` blob `52b5ebf36037e2c9eee8b24741075e24b1680410`, and `src/io/functions/iologindata_save_player.cpp` blob `5bb44a2f2e15c33b39a5b24206440057ded4ab5b` are identical across the pinned target, fresh upstream and legacy baselines; the reviewed Prey/Task Hunting load functions are functionally identical. Maintained OTClient already carries the standard `modules/game_prey/prey.lua` contract, so no client write was required.

Legacy Canary's Taskboard difference was deliberately excluded from the independent Prey reuse boundary: merged Wheel PR #230 consumes Hunting Task points while persisting/applying purchased promotion points under the `wheel-of-destiny` KV scope and changes Wheel-owned components/bindings/tests. That is an explicit Prey↔Wheel integration and remains under the separately active Wheel parity program rather than being copied into OAM-022.

Otheryn PR #46 final head `12d79e4532e5784e9530caf433cdad1c869f0142` changed exactly three proof-only paths and no production runtime/data/persistence/protocol/client/schema/map/asset/deployment path. Autofix.ci #145 run `29723046171`, CI #169 run `29723046359`, and Required #152 run `29723046189` succeeded. Linux debug CTest completed `400/400`, including `Oam022PreyReuseTest` `4/4`; test-log artifact `8453371882` has digest `sha256:23e923635138726a33e7900ff84cd481d2182994cb68020c5d03698e4804886c`. Target comments/reviews/threads were empty, target-main drift was none, and PR #46 merged by expected-head squash as `50dfa248251f245f5519495a4fbd430b6814ffe4`.

Canary governance PR #612 final head `52b27ea5efedab9b0112c7e206e3c697e17a0ac3` changed exactly the OAM-022 report and active-task record. It passed Agent Task Ownership #2754 run `29723974759` and exact-head final-gate CI #3904 run `29723982438`; comments/reviews/threads were empty and Canary `main` had no drift from the immutable task-start baseline. PR #612 merged by expected-head squash as `e3a5cc7321636270db150d289ba2da9ddb99ef0d`.

Authoritative lifecycle PR #613 final head `13531cdab812d169f21a2e724b71b4e157ca93d6` changed exactly the active-delete/archive-add lifecycle paths. It passed Agent Task Ownership #2756 run `29724219954`, draft CI #3905 run `29724220096`, and ready-state CI #3906 run `29724256954`; comments/reviews/threads were empty and Canary `main` had no drift from the governance merge. PR #613 merged by expected-head squash as `4aa0a054cbd3fcbc45e2bda5b58ab016df6438e6`.

OAM-022 does not claim full modern official Hunting Task/Taskboard parity, Wheel Bonus Promotion Shop migration or Wheel allocation ownership, exhaustive Prey formulas/rarity/reroll-price/monster-pool parity, physical-client Prey or Taskboard E2E closure, generic persistence/protocol redesign, or map/OTBM/`items.otb`/asset/schema/deployment changes.

# OAM-023 durable completion

Final disposition:

```text
parties REUSE
```

Task-start baselines were Canary `0a39a0f76d5f811098dfaa7be9deea40347279d5`, Otheryn `50dfa248251f245f5519495a4fbd430b6814ffe4`, fresh upstream Canary `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`, and maintained OTClient `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`. Canonical `parties` depends only on completed OAM-005 `character-lifecycle`. `wheel-of-destiny` remained under a separate parity program; `cyclopedia` was rejected as materially broader. Fresh task-start ownership and open-PR audits found no overlap with canonical `src/creatures/players/grouping/party.*`.

At the immutable baselines, target, fresh upstream and legacy shared `party.cpp` blob `c3493c962548bffa5e393adc3359137b200b6384` and `party.hpp` blob `52b08e7321dd4e35bfb68415254239245ed236ee`. Blob identity was supporting evidence only. Semantic review covered Party creation and leader binding, member/invitation state, invite/join/leave/revoke/leadership transitions, disband cleanup, shared-experience state and fail-closed no-leader behavior. Relevant legacy-history candidates around multichannel behavior, Gameplay Analytics shared experience and Forge premium Dust were audited and did not modify canonical `party.*`; no stronger independent legacy donor for the canonical Party core was identified.

Otheryn PR #47 final head `c3ff8bb09b736ec835ce1f49ee0d96b8e208ea88` changed exactly three proof-only paths: `docs/oam-023-parties-reuse.md`, `tests/unit/game/CMakeLists.txt`, and `tests/unit/game/oam_023_parties_reuse_test.cpp`. No production `party.*` or maintained OTClient path changed. Autofix.ci #147 run `29728346604`, CI #172 run `29728346757`, and Required #154 run `29728346586` all succeeded on the exact final head. Linux debug CTest completed `403/403`, including `Oam023PartiesReuseTest` `3/3`; test-log artifact `8455540885` has digest `sha256:8c3868b1047057d8419194ce7a555566b8db7dd32024f1ecb1c2cdec1424938b`. Target comments/reviews/threads were empty, target-main drift was none, and PR #47 merged by expected-head squash as `bcc3e9f7e3e704f3c012bda8693648d52741630f`.

Canary governance PR #616 final head `d11f692a23e6b185de9bbe94390c4c76c0b3c47b` changed exactly the OAM-023 report and active-task record. Agent Task Ownership #2780 run `29729424947` and full final-gate CI #3932 run `29729430140` succeeded on the exact final head, including the full Linux/Windows/macOS build matrix. Comments/reviews/threads were empty. Canary `main` drift during governance consisted only of independently owned OTBM/E2E work and its task lifecycle archive; changed-file audits proved no overlap with OAM-023 governance paths or canonical `party.*`. PR #616 merged by expected-head squash as `e78d927e54d965d742fe762e86c9ea454d068c4a`.

Authoritative lifecycle PR #618 final head `6c8355c46102b2aa910cc29d02a76bba6c1f463d` changed exactly the active-delete/archive-add lifecycle paths. It passed Agent Task Ownership #2784 run `29730397086`, draft CI #3934 run `29730397420`, and ready-state CI #3935 run `29730433044`; comments/reviews/threads were empty and Canary `main` had no drift from the governance merge before lifecycle merge. PR #618 merged by expected-head squash as `060fe0fa018e55725c93daee5dd4cadec0a68162`.

OAM-023 does not claim party chat/channel transport, protocol packet compatibility, maintained OTClient behavior, exhaustive shared-experience formula parity, generic combat correctness, vocation/Wheel correctness, guild lifecycle, generic persistence redesign, OAM-004 SQL/KV atomicity, physical-client Party E2E closure, or map/OTBM/`items.otb`/asset/schema/deployment changes.

# OAM-024 durable completion

Final disposition:

```text
sanctions ADAPT
```

Task-start baselines were Canary `3fe0130a408d201d0ca846f86a37b0ab20479932`, Otheryn `bcc3e9f7e3e704f3c012bda8693648d52741630f`, fresh upstream Canary `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`, and maintained OTClient `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`. Canonical `sanctions` depends only on completed OAM-004 `database-connection`. Fresh task-start open-PR and ownership audits found no writer overlapping canonical `src/creatures/players/management/ban.*` or the OAM-024 governance paths.

Task-start legacy, target and fresh upstream shared `ban.cpp` blob `ca4c11ea98d6a8f4b6281f0bb5e84d742ff21ecc` and `ban.hpp` blob `48086b3efef370b2c0e1fab8f85513a95e47dcad`, but blob identity was supporting evidence only. Semantic and history review found no stronger independent legacy donor while identifying one bounded durability defect: expired account-ban archival used an asynchronous history `INSERT` and active-ban `DELETE` as separate writes without one rollback boundary. Completed OAM-004 already provides `DBTransaction`, so the smallest valid disposition was `ADAPT` rather than unconditional `REUSE` or broad rewrite.

Otheryn PR #48 final head `58ba19e0affe75f47c4185c41327880f8403503b` changed exactly four intended paths: `docs/oam-024-sanctions-adapt.md`, `src/creatures/players/management/ban.cpp`, `tests/integration/database/CMakeLists.txt`, and `tests/integration/database/sanctions_it.cpp`. The bounded adaptation moves only expired account-ban history insertion and active-row deletion into one `DBTransaction` under `SELECT ... FOR UPDATE`; active/permanent ban behavior is preserved and IP-ban behavior remains unchanged. Autofix.ci #153 run `29734614481`, CI #179 run `29734614607`, and Required #160 run `29734614503` all passed on the exact final target head. Linux debug CTest completed `406/406`, including `SanctionsRepositoryDBTest` `3/3`; test-log artifact `8458101363` has digest `sha256:97b9aeb5e93bac69461720671ee58bfe5742fd20df2710b139d0aa2298cd30fc`. Target comments/reviews/threads were empty, target-main drift was none, and PR #48 merged by expected-head squash as `65d364b216843db27e84a19a673eee4e6d766c68`.

Canary governance PR #621 final head `894fa6be932937a7b124461dffe6ac2d3a414f84` changed exactly the OAM-024 report and active-task record. The first two Ownership attempts failed only the task checkpoint `first_failure` schema and were corrected without changing target scope or evidence. Final Agent Task Ownership #2805 run `29735949134`, draft CI #3956 run `29735949282`, and ready-state full final-gate CI #3957 run `29735989048` all succeeded on the exact final head. Comments/reviews/threads were empty and Canary `main` had no drift from the immutable task-start baseline before merge. PR #621 merged by expected-head squash as `7662d048a75df37f5bfc4238e12fd3b18c935151`.

Authoritative lifecycle PR #622 final head `5473976a6b1b15bd55c4ed9c10eb6bb95474b3a1` changed exactly the active-delete/archive-add lifecycle paths. It passed Agent Task Ownership #2809 run `29736993817`, draft CI #3960 run `29736994154`, and ready-state CI #3961 run `29737033310`; comments/reviews/threads were empty and Canary `main` had no drift from the governance merge before lifecycle merge. PR #622 merged by expected-head squash as `0de75bd2de28c80e9d9587bd3a2520c29c5f267c`.

OAM-024 preserves the known OAM-004 limitation that player SQL persistence and later KV durability are not atomic. It does not claim exhaustive sanction enforcement at every entry point, generic account-authentication security, protocol compatibility, distributed/multi-database sanctions replication, moderation policy, generic security analytics, AI investigation, PvP skull/frag parity, physical-client sanctions E2E closure, generic persistence redesign, or changes to maintained OTClient, maps, OTBM, `items.otb`, assets, schema or deployment.

# OAM-025 durable completion

Final disposition:

```text
chat-communication ADAPT
```

Task-start baselines were Canary `9a7c5ebfa4cb35066293a8b75039fb61b8d8afe5`, Otheryn `86a598426f65e51ff2864ccd1d0a1dbf818b526c`, fresh upstream Canary `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`, and maintained OTClient `87124861eb0faa9134bdda062c881df70f17d495`. Canonical `chat-communication` depends only on completed OAM-005 `character-lifecycle`. Fresh task-start open-PR and ownership audits found no writer overlapping canonical `src/creatures/interactions/chat.*`, `data/chatchannels/**`, or the OAM-025 governance paths.

Task-start legacy, target and fresh upstream shared the reviewed chat core and all eight configured channel scripts, but blob/content identity was supporting evidence only. Semantic and history review found a bounded privilege-domain defect in `data/chatchannels/scripts/help.lua`: the acting moderator had already been migrated to player-group authorization while the target-side `!mute` and `!unmute` checks still compared that group rank against `target:getAccountType()`. The smallest valid disposition was `ADAPT`, changing only those two authorization comparisons to target player-group rank.

Otheryn PR #51 final head `5aa0259d2ef34d1803ab1fbae8d931ed5f330486` changed the two Help-channel production comparisons plus focused test registration, a real-script Lua regression test, and target evidence. The focused proof deliberately made group rank conflict with account type and proved both changed authorization sites. The first ready-state autofix attempt `29770250714` failed only while applying generated formatting; after that formatting-only repair, autofix.ci run `29770310537`, Repository Audit run `29770310698`, CI run `29770311110`, and Required run `29770310554` all succeeded on the exact final head. Linux debug `Run Tests` passed. Target comments/reviews/threads were empty, target-main drift was none, and PR #51 merged by expected-head squash as `1c8e3e8b4fc29effb3b0cb882af94f7d26ed2554`.

Canary governance PR #626 final head `ef06264fa64583ab33aa5cc3c8be733fa6fe1b93` changed exactly the OAM-025 report and active-task record. The first final Ownership attempt failed only because the active-task checkpoint omitted the required `derived` field; the final-gate label was removed before that metadata-only repair and reapplied afterward. Final Agent Task Ownership #2842 run `29771810195` and ready-state final-gate CI #3995 run `29771810912` succeeded on the exact final head. Comments/reviews/threads were empty and Canary `main` had no drift from the immutable task-start baseline before merge. PR #626 merged by expected-head squash as `791bca7403da1e93fba96143f42983f09aa10381`.

Authoritative lifecycle PR #630 final head `7f0546a2070470cabb03ebda4cd0b3cca4eb0511` changed exactly the active-delete/archive-add lifecycle paths. It passed Agent Task Ownership #2846 run `29772019038`, draft CI #3998 run `29772019626`, and ready-state CI #3999 run `29772063171`; comments/reviews/threads were empty and Canary `main` had no drift from the governance merge before lifecycle merge. PR #630 merged by expected-head squash as `8ed836aae47d6bb882fb646169d2930f951c6c0d`.

OAM-025 does not claim Real Tibia chat parity, guild/party membership lifecycle, protocol compatibility, maintained-client UI behavior, generic moderation policy, message privacy or delivery guarantees, NPC conversations, distributed chat, physical-client chat E2E closure, generic persistence redesign, or changes to maps, OTBM, `items.otb`, assets, schema or deployment.

# OAM-026 durable completion

Final disposition:

```text
guilds ADAPT
```

Task-start baselines were Canary `052d96014c805aacaa120ce888b7bed038817a72`, Otheryn `1cf38d354b493b4cd9ec8e841ec8f2a6ff322029`, fresh upstream Canary `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`, and maintained OTClient `a6868920443dc285656bd016acdb2c1ea566e511`. Canonical `guilds` depends only on completed `character-lifecycle` and `database-connection`; chat delivery, protocol/wire behavior and broader world persistence remain interaction boundaries rather than package expansion.

Task-start legacy, target and fresh upstream shared exact `guild.cpp` blob `346bfc562275a5835fd81f146eb235048ce9d45b` and `guild.hpp` blob `0e4c53a615d5df90e561cc211da002a89c72a413`; the guild-specific player-load behavior was also semantically aligned. Blob identity was supporting evidence only. Whole-module `REUSE` was rejected because the target intentionally preserves completed OAM-004C persistence architecture: `IOGuild::saveGuild()` returns the underlying database status and `SaveManager` propagates guild-save failure into aggregate server-save status, unlike the legacy/upstream fire-and-forget boundary. OAM-026 therefore retained the upstream-compatible guild core without copying legacy/upstream `IOGuild` over that target-owned contract.

Otheryn PR #53 final head `4709f0c49962dee14e98acb384baab75b21c97a8` changed exactly four proof/test paths and no production guild path. Autofix.ci run `29775483679`, CI run `29775483958`, and Required run `29775483628` succeeded on the exact final head; Linux debug `Run Tests`, both Windows build paths and macOS build passed. Comments/reviews/threads were empty, target `main` had no task-start drift through the merge gate, and PR #53 merged by expected-head squash as `418a9f0bfc72cc58b9806a49e966d9c3ea3c1a6d`.

Canary governance PR #635 was reconstructed onto non-overlapping Canary `main` `191cad8779ec84aaa09c8f62e9b6ff76e958b8fa` after independent OTBM/E2E coverage and lifecycle drift. Final head `a81d637bd63b58a0e4df79e24a1cac64716bd7ae` changed exactly the OAM-026 report and active-task record, passed Agent Task Ownership #2891 run `29777372413` and final-gate CI #4045 run `29777392434`, had zero comments/reviews/threads, no further main drift and was mergeable, then merged by expected-head squash as `5a2bc2be3b91abdd46c9edf2f825336472515299`.

Authoritative lifecycle PR #641 final head `d10008ad1f964ae33883a1d64095fb080307c25f` changed exactly the active-delete/archive-add lifecycle paths. It passed Agent Task Ownership #2893 run `29777615996` and final-gate CI #4047 run `29777622849`; Fast Checks, Lua Tests and Required passed while heavy builds were correctly skipped for lifecycle-only scope. Comments/reviews/threads were empty, Canary `main` had no drift from the governance merge, and PR #641 merged by expected-head squash as `99b9dec84d953d3f200284d0cf193261027650ca`.

OAM-026 does not import the legacy multichannel guild ownership model and does not claim generic distributed guild ownership, atomic multiwriter guild-bank debit safety, Real Tibia guild parity, website guild-management parity, guild-chat delivery parity, protocol/client UI parity, generic transaction atomicity, generic crash/restart durability, physical-client guild E2E closure, or changes to maps, OTBM, `items.otb`, assets, schema or deployment. Legacy `OTS-ECO-GUILD-001` remains a future multiwriter guild-bank stale-balance boundary requiring a separate durable ownership/atomic-debit contract before concurrent guild-bank mutation is enabled.

# OAM-027 durable completion

Final disposition:

```text
houses ADAPT
```

Task-start baselines were Canary `0251b96105720cb67d5ed7a1b3ec8350baa8e312`, Otheryn `5003753e491250732910e9d5857b20293d1bd9ab`, fresh upstream Canary `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`, and maintained OTClient `a6868920443dc285656bd016acdb2c1ea566e511`. Canonical `houses` depends on the active/mapped/audited `otbm-tooling` evidence foundation and completed player-persistence foundation.

Task-start Otheryn and fresh upstream shared `src/map/house/house.cpp` blob `25fa954a55763bc9473234682d143c9761843403`, but blob identity was supporting evidence only. Merged legacy PR #60 final commit `a6977beb06883fb4384476315f3dc17772f99ba4` supplied the bounded accepted donor: snapshot item collections before mutation, skip stale snapshot entries, deduplicate the depot move queue, and fail closed on invalid wrapped results while preserving the original item ID. Whole-file legacy reuse was rejected because current legacy `house.cpp` also contains separately owned multichannel house ownership/mirroring architecture.

Otheryn PR #55 final head `3cfc133a835f7ad14ed8a94cc720c1f0b1a31a65` changed exactly five intended target paths and no temporary materializer path. The first ready-state Linux debug CTest on superseded head `e3c18e52940df481521ae9c8c413c3f5420a383f` passed 411/412; only a new synthetic `House` proof harness segfaulted while the independent transfer-safety source-contract proof passed. The invalid harness was removed without production changes. Final autofix.ci #167 run `29782520081`, CI #202 run `29782520156`, and Required #184 run `29782520075` all succeeded on the exact final head, including Linux debug `Run Tests`. Test-log artifact `8477497565` has digest `sha256:548c9077d94c94c515bff2e33c574bcb67b5b9a31eb09124b152976eb048b349`. Comments/reviews/threads were empty, target-main drift was none, and PR #55 merged by expected-head squash as `c140c4bb9f40067acc36bc446c9e664e6f791c5a`.

Canary governance PR #644 was reconstructed onto non-overlapping Canary `main` `6b1bbadf5c9fdc9c4b5831dcfbdef9c9ed894b3d` after independent OTBM/E2E drift. Final head `a2410f8249b16cfc96991c98931d60d8c2f0e2f1` changed exactly the OAM-027 report and active-task record. The first Ownership attempt failed only because checkpoint `owned_paths` were absent from frontmatter; after the metadata-only repair, Agent Task Ownership #2924 run `29783747823` and final-gate CI #4078 run `29783747923` succeeded. Comments/reviews/threads were empty and no further main drift occurred before expected-head squash merge `436b73863b81bfa1ba27f88642f3a816064759fc`.

Authoritative lifecycle PR #647 final head `75decbd6b05e4f5a008f1db0dab110198439c683` changed exactly the active-delete/archive-add lifecycle paths. Agent Task Ownership #2926 run `29783964089` and final-gate CI #4080 run `29783972947` succeeded; heavy builds were correctly skipped for lifecycle-only scope. Comments/reviews/threads were empty, Canary `main` had no drift from the governance merge, and PR #647 merged by expected-head squash as `562961ee0dd0c2626ab845dc307ec748e2a6bfb7`.

OAM-027 does not claim generic house purchase/auction transaction atomicity, crash-safe transfer recovery, distributed or multiwriter house ownership, cross-channel house safety, Cyclopedia house-tab correctness, protocol/client UI compatibility, exhaustive rent/auction parity, physical-client house E2E closure, full Real Tibia house parity, or map/OTBM correctness. It changes no maintained OTClient, map/OTBM data, schema, assets or deployment.

# OAM-028 durable completion

Final disposition:

```text
cyclopedia REUSE
```

Task-start baselines were Canary `85b26b41510101259f6138f2c864bf0c4a473f2a`, Otheryn `2a008f1c8cfa679c9b70281e4c8c16120a7567fa`, fresh upstream Canary `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`, and maintained OTClient `a6868920443dc285656bd016acdb2c1ea566e511`. Canonical `cyclopedia` depends only on completed `protocol` and `player-persistence`; TSD-004 keeps it as a broad compatibility/discovery umbrella while Bestiary, Bosstiary, Cyclopedia Character, Titles, Charms and Houses retain narrower canonical ownership.

Task-start Otheryn and fresh upstream shared exact `src/server/network/protocol/protocolgame.hpp` blob `082d66596a424fc44143298c41fe01ff4007a439`; task-start Otheryn, fresh upstream and legacy shared exact `src/enums/player_cyclopedia.hpp` blob `45fed9ad2f3b7e35bdc7afd9dbd52d5d1b736311`. Blob identity was supporting evidence only. Semantic review of delivered legacy work showed PR #188 belongs to Bestiary/Bosstiary/Charms/Cyclopedia Character child runtime boundaries, PR #192 belongs to Bestiary/Bosstiary data, and PR #243 is validator/workflow control. None requires replacing the selected umbrella protocol surface or maintained OTClient.

Otheryn PR #57 final head `19c286762fb89ba3ed8d47ebf58538ff070a4d7f` changed exactly four proof-only paths and no production runtime/protocol/data/client path. Autofix.ci #170 run `29785109223`, CI #206 run `29785109355`, and Required #189 run `29785109193` succeeded on the exact final head, including Linux debug `Run Tests`. Test-log artifact `8478394189` has digest `sha256:152b153430d5ccd7953647f37e2d462b16c7aed30a7a027248195e698bdfa9cb`. Comments/reviews/threads were empty, target-main drift was none, and PR #57 merged by expected-head squash as `7e03405aea50d88fdbc27d0d2a7d95c7f1745946`.

Canary governance PR #649 final head `52e765bcaba6dc4b96406e3fa27aa74e1d462e8f` changed exactly the OAM-028 report and active-task record. Initial Agent Task Ownership #2944 failed only because checkpoint `proven` exceeded the compactness limit by one item; after metadata-only compaction, Agent Task Ownership #2945 run `29786086600` and final-gate CI #4099 run `29786086762` succeeded. Comments/reviews/threads were empty, Canary `main` had no task-start drift, and PR #649 merged by expected-head squash as `a28e661c4119857eff36948c4549045f57eae545`.

Authoritative lifecycle PR #650 final head `be8be4f5f3055d44e1f4af6523ec22869a160c83` changed exactly the active-delete/archive-add lifecycle paths. Agent Task Ownership #2947 run `29786292638` and final-gate CI #4101 run `29786301133` succeeded; comments/reviews/threads were empty, Canary `main` had no drift from the governance merge, and PR #650 merged by expected-head squash as `ff694b9e908148fb12cca69a76fc2786d9a0f2c3`.

OAM-028 does not claim Bestiary, Bosstiary, Charm, Cyclopedia Character, Titles or Houses child correctness; exact packet-byte compatibility; maintained-client parsing/rendering correctness; item/map/house presentation correctness; persistence completeness; runtime behavior; physical-client Cyclopedia E2E closure; or full Real Tibia parity. It changes no production runtime, protocol, data, schema, map, asset, deployment or maintained OTClient path.

# OAM-029 durable completion

Final disposition:

```text
cyclopedia-character ADAPT
```

Task-start baselines were Canary `ad267a87b3f565daf7e5901d80fbafb5a02b623c`, Otheryn `1521906ffa8bd83ff2b35b0feadab4a44ea6df05`, fresh upstream Canary `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`, and maintained OTClient `a6868920443dc285656bd016acdb2c1ea566e511`. Canonical `cyclopedia-character` depends only on completed `cyclopedia` and `player-persistence` and owns the narrow server root `src/creatures/players/components/player_cyclopedia.*`.

Task-start Otheryn and fresh upstream shared `player_cyclopedia.cpp` blob `91a3235e53e5f7ca4da22649bff6bad34cf44e3a`; reviewed current legacy differed with blob `b2b6d0f3283380f450b3c79874d5ce38ac2734a0`. Semantic decomposition of merged legacy PR #188 identified exactly one Cyclopedia Character production hunk: the recent-PvP outer row query already uses a 70-day window, while its `count(*)` subquery historically counted all matching deaths. OAM-029 adds the same 70-day predicate to the count subquery so page count and returned rows share one presentation window. Bestiary, Bosstiary, Charms, Titles, protocol and maintained-client changes were excluded.

Otheryn PR #59 final head `5f8f629ca78bcaf8636e2751ef60ae5ce9ab9a85` changed exactly five intended paths. Autofix.ci #173 run `29807291416` succeeded. Linux debug compilation, runtime smoke, schema import and full `Run Tests` succeeded; test-log artifact `8486265013` has digest `sha256:c4eb1f8815e77b3cb7fb243beea00d3e17d2c7a66183ad057b28d1fad59dbb47`. CI #210 run `29807291563` initially concluded failure only because Docker Quickstart Smoke failed after all code/build/test gates had passed; a failed-job retry passed on the unchanged exact head and CI #210 concluded success. Required #194 run `29807291333` was then rerun to evaluate the recovered CI and concluded success. Comments/reviews/threads were empty, target-main drift was none, and PR #59 merged by expected-head squash as `908834adc7d7e7e4ced7404391c7966b1c961b18`.

Canary governance PR #655 final head `1dd84ff459d29a7c734fed8e16f01be20363e73f` changed exactly the OAM-029 report and active-task record. Agent Task Ownership #2969 run `29808583515` and final-gate CI #4123 run `29808618659` succeeded. Comments/reviews/threads were empty, Canary `main` had no task-start drift, and PR #655 merged by expected-head squash as `a5e5565d546a530fc3a3010deb65e9283f6eacab`.

Authoritative lifecycle PR #656 final head `ed14520d265efa00128437e99df1b76b4df7b8ca` changed exactly the active-delete/archive-add lifecycle paths. Agent Task Ownership #2972 run `29808898548` and final-gate CI #4126 run `29808909750` succeeded. Comments/reviews/threads were empty, Canary `main` had no drift from the governance merge, and PR #656 merged by expected-head squash as `2a4b717448e55e1a2c24578df44eb981f8ae4bfd`.

OAM-029 does not claim full Cyclopedia Character parity, exact packet-byte compatibility, death-history correctness, KV/store-summary parity, database query performance, retained-history policy, maintained-client rendering correctness, physical-client Cyclopedia Character E2E closure, or full Real Tibia parity.

# OAM-030 durable completion

Final disposition:

```text
bosstiary ADAPT
```

Task-start baselines were Canary `419d0848448c641561e7bc06392a4b17b95213b2`, Otheryn `68d48deea999990b1eab30858f3a85fc9fef7067`, fresh upstream Canary `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`, and maintained OTClient `a6868920443dc285656bd016acdb2c1ea566e511`. Canonical `bosstiary` depends on completed `cyclopedia` and `player-persistence` and owns the narrow server root `src/io/io_bosstiary.*`.

Semantic donor review selected exactly the Bosstiary hunk from merged legacy PR #188: `IOBosstiary::loadBoostedBoss()` no longer returns before a missing `boosted_boss` singleton row can be initialized, after which the existing reroll path continues. Later legacy multichannel leader-election behavior, Bestiary, Charms, monster data, protocol and maintained OTClient changes were deliberately excluded. Task-start target and fresh upstream shared the pre-fix `io_bosstiary.cpp` state; current legacy retained the reviewed recovery fix plus separately owned later multichannel logic, so whole-file legacy reuse was rejected.

Otheryn PR #61 final head `4b6dd3fdca907d2f521cb366322dd5b007aca668` changed exactly five intended OAM-030 paths and no temporary helper/workflow path. Exact-head autofix.ci #185, CI #223 and Required #208 succeeded; Linux debug full `Run Tests` succeeded and test-log artifact `8488418806` has digest `sha256:1bf24e4a4d61bb8f0aab3769b2b19cfe7abd9c98507b691d9d034de07b476e29`. Comments/reviews/threads were empty, target `main` had no drift from the immutable base, and PR #61 merged by expected-head squash as `dc483d6e8d659d61482da2af7abda9b46b1766ff`.

Canary governance PR #659 was reconstructed on non-overlapping Canary `main` `af27845b130a87d92f2794c2817d77cfe6d84825` after independent OTBM lifecycle drift. Final head `5cd38afab83e47aa7cdaa19691e5f0f28c4eef58` changed exactly the OAM-030 report and active-task record. Agent Task Ownership #2991 and final-gate CI #4147 succeeded; comments/reviews/threads were empty and no further drift occurred before expected-head squash merge `6c092568e44dcb0b13959a8f22c14a992565aa7b`.

Authoritative lifecycle PR #662 was twice reconstructed onto newer non-overlapping Canary `main` states because independent OTBM/E2E work landed before merge. Final head `8570fd23da85b2f014bd17c8e8b38526a1c8f49f` still changed exactly the active-delete/archive-add lifecycle paths. Agent Task Ownership #2999 and CI #4153 succeeded on that exact head; comments/reviews/threads were empty, and PR #662 merged by expected-head squash as `994d1ffdfd6828688b1acc6cd7c0c519eab052ba`.

OAM-030 does not claim full Bosstiary parity, exhaustive boosted-boss selection correctness, distributed or multiwriter leader election, cross-channel Bosstiary safety, Bestiary or Charms child correctness, exact protocol/client compatibility, maintained-client rendering correctness, monster-data parity, database availability or crash-recovery guarantees, physical-client Bosstiary E2E closure, or full Real Tibia parity.

# OAM-031 durable completion

Final disposition:

```text
bestiary ADAPT
```

Task-start baselines were Canary `9aa582eb6b8ab9444294e08798f628cd053d2428`, Otheryn `6a7e54ee3c9597e3ab265a14c2b783631ef3776f`, fresh upstream Canary `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`, and maintained OTClient `a6868920443dc285656bd016acdb2c1ea566e511`. Canonical `bestiary` depends on completed `cyclopedia` and `player-persistence`, owns the narrow server root `src/io/iobestiary.*`, and keeps Charm policy plus monster-definition data outside this package boundary.

Task-start Otheryn and fresh upstream shared exact `src/io/iobestiary.cpp` blob `c0497c4d1814e7950ad8fc27b9a4ec1f86d4a5cd`. Semantic decomposition of merged legacy PR #188 selected exactly two Bestiary-owned corrections: `IOBestiary::addBestiaryKill` validates `player` and `mtype` before dereferencing `mtype->info.raceid`, and `IOBestiary::calculateDifficult` converts `chance` to `double` before division by `1000.0` so fractional thresholds are not truncated. The PR #188 all-Charm reset-price correction and PR #192 monster-definition data were deliberately excluded; whole-file legacy reuse was rejected because the file also hosts separately owned Charm helpers and behavior.

Otheryn PR #63 final head `c49796d696448aa168c34629dc9ebcd9fd7a9465` changed exactly five intended OAM-031 paths, with production diff limited to `src/io/iobestiary.cpp`. Exact-head autofix.ci #187 run `29825053904`, CI #226 run `29825054221`, and Required #211 run `29825053840` succeeded; Linux debug full `Run Tests` succeeded. Test-log artifact `8493329878` has digest `sha256:e99f341683bc432512ddd0dc235204f8b13510cd48eaf9f06c9cdf53d7dbc432`. Comments/reviews/threads were empty, target `main` had no task-start drift, and PR #63 merged by expected-head squash as `86e4b08c28ede2f35c215a7c2327a579f4a61419`.

Canary governance PR #675 final head `1ce09da615e703ff72062c60093ae8b5173cf80b` was reconstructed on non-overlapping Canary `main` `87c4f71b0deb880da7ba4228bc29e769db2c5818`. It changed exactly the OAM-031 revalidation report and active-task record. Agent Task Ownership #3069 run `29826443473` and final-gate CI #4222 run `29826443642` succeeded; comments/reviews/threads were empty, and PR #675 merged by expected-head squash as `e55e0d548d6013da6676cc7b06cbb8d459ccdd1f`.

Authoritative lifecycle PR #676 final head `7e722d1872db8e4e7beeb31feae28b1060ea4cde` changed exactly the active-delete/archive-add lifecycle paths. Agent Task Ownership #3073 run `29826706123` and CI #4225 run `29826706339` succeeded; comments/reviews/threads were empty, and PR #676 merged by expected-head squash as `0fca8ced2d952eab744238f826af81cb9ee135b1`.

OAM-031 does not claim full Bestiary parity, exhaustive kill-stage/reward correctness, Charm correctness, monster-definition parity, exact protocol/client rendering compatibility, persistence completeness, tracker refresh correctness under every runtime state, database durability, physical-client Bestiary E2E closure, or full Real Tibia parity.

# OAM-032 durable completion

Final disposition:

```text
titles REUSE
```

Task-start baselines were Canary `db7cf6af480285ad4a87c3be2981a873f175eab6`, Otheryn `ad2bd2f187df057c47d05c121351159ce30cc457`, fresh upstream Canary `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`, and maintained OTClient `a6868920443dc285656bd016acdb2c1ea566e511`. Canonical `titles` depends only on completed `cyclopedia-character` and `player-persistence`; TSD-004 owns the narrow server root `src/creatures/players/components/player_title.*` while Bestiary, Bosstiary, character progression, houses and protocol remain interactions rather than ownership transfers.

Task-start target, current legacy and fresh upstream shared exact `player_title.cpp` blob `c885d5ee55970d8ce93a80bb477bc317fb9faa98` and `player_title.hpp` blob `118806fee9ca6d939d73067af14c63c59d291f25`. Blob identity was supporting evidence only. Semantic donor-history review found no accepted Titles-root delta: merged Cyclopedia runtime PR #188 contains no `player_title` path, PR #192 is monster-data remediation, and PR #243 is validator/workflow control. The final Cyclopedia zero-finding scan was not promoted into a claim about title definitions, thresholds, persistence, protocol, runtime behavior or maintained-client correctness.

Otheryn PR #65 final head `3244c8b0993047d9fe72ed56125a6f9e218defbb` changed exactly four proof/task paths and no production path. Autofix.ci #188 run `29863062941`, CI #228 run `29863063433`, and Required #213 run `29863063406` succeeded; Linux debug full `Run Tests` succeeded. Test-log artifact `8508497986` has digest `sha256:2c2b98f96fe73bd8b2e9123f662779534a70ec7b0a5b7ebe895f1769b05ae9b3`. Comments/reviews/threads were empty, target `main` had no task-start drift, and PR #65 merged by expected-head squash as `f5f21347c578a382cf0c52dbb4c69673ab3b05a9`.

Canary governance PR #691 final head `62af0071f777fd029c7c0718914375928ecf2389` changed exactly the OAM-032 report and active-task record. Three earlier Ownership attempts exposed only checkpoint metadata-contract issues and caused no scope or evidence change. Final Agent Task Ownership #3186 run `29864789104` and final-gate CI #4343 run `29864789391` succeeded; comments/reviews/threads were empty, Canary `main` had no task-start drift, and PR #691 merged by expected-head squash as `212d5e5c4ecbb0bd392880019747e2370299c748`.

Authoritative lifecycle PR #692 final head `18751315a53c5f0af82581b447b14f90f9c9c742` changed exactly the active-delete/archive-add lifecycle paths. Agent Task Ownership #3188 run `29865034951` and final-gate CI #4344 run `29865035270` succeeded; comments/reviews/threads were empty, Canary `main` had no drift from the governance merge, and PR #692 merged by expected-head squash as `fda6d01b93929ea998965354908062eb6e4e1424`.

OAM-032 does not claim title-definition or unlock-threshold parity, completeness of every cross-domain eligibility check, map/Drome/Goshnar or other TODO-backed title conditions, persistence atomicity or crash recovery, exact protocol compatibility, maintained-client parsing/rendering correctness, physical-client Titles E2E closure, or full Real Tibia parity.

# OAM-033 durable completion

Final disposition:

```text
charms ADAPT
```

Task-start baselines were Canary `f05ea5e916af00ab1469a2332aaec2d3c9df7478`, Otheryn `1a4bbceda2c805bc69c68c1592e04e63d7e9a269`, fresh upstream Canary `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`, and maintained OTClient `a6868920443dc285656bd016acdb2c1ea566e511`. Canonical `charms` depends on completed `combat`, `cyclopedia`, `player-persistence` and `protocol`; TSD-004 preserves independent Charm ownership for definitions, costs, unlock state, assignment and combat effects even where `IOBestiary` hosts helper methods.

Merged legacy PR #188 supplied exactly two selected Charm-owned corrections: `registerCharm.category` gates on `mask.category` before applying the category, and all-Charm reset pricing charges the `11,000` surcharge only for levels above 100 via `(playerLevel - 100) * 11000`. PR #188 Bestiary, Bosstiary and Cyclopedia Character hunks, PR #192 monster-data remediation and PR #243 validator/workflow control were excluded. No maintained OTClient change was selected.

Otheryn PR #67 final head `e1fca0b372173db335118735f501f315d442888f` changed exactly seven intended paths. The first target Linux-debug full suite completed `421/422`; its sole failure was the superseded OAM-031 Charm reset-price exclusion assertion, while both OAM-033 focused tests passed. That obsolete proof-boundary assertion was removed without any further production change. Final autofix.ci #192 run `29867543037`, Repository Audit #27 run `29867542987`, CI #233 run `29867543182`, Required #218 run `29867542998`, and Linux-debug full `Run Tests` succeeded. Test-log artifact `8510218346` has digest `sha256:1bc7425f036bb5f39c19539590da0704f026718e4bbd54ad2ede79c023300cbc`. Comments/reviews/threads were empty, target `main` had no task-start drift, and PR #67 merged by expected-head squash as `c887318a676998da5ef3224a3aa8d1e0df75e607`.

Canary governance PR #696 final head `34ca59c5ca53e7082d4e1ced1428b745bb8e91e1` changed exactly the OAM-033 revalidation report and active-task record. The initial Ownership failure was compactness-only (`proven` contained 17 items with a limit of 16) and was repaired without scope or evidence change. Final Agent Task Ownership #3213 run `29868982754` and final-gate CI #4369 run `29868983212` succeeded; comments/reviews/threads were empty, Canary `main` had no task-start drift, and PR #696 merged by expected-head squash as `5ecc72762feb6bda8f6549ac4238a75247752449`.

Authoritative lifecycle PR #697 final head `0130b6c9944020c1185ded02dd67c2ca82e6d60f` changed exactly the active-delete/archive-add lifecycle paths. Agent Task Ownership #3216 run `29869194552` and final-gate CI #4372 run `29869195095` succeeded; comments/reviews/threads were empty, Canary `main` had no drift from the governance merge, and PR #697 merged by expected-head squash as `d83563943e298df33edd084e944812464b8a3ff2`.

OAM-033 does not claim exhaustive Charm definition/value parity, all unlock costs, assignment-slot rules, combat proc formulas, element/resistance behavior, Bestiary progress correctness, protocol/client compatibility, maintained-client rendering, persistence atomicity, economy transaction atomicity, physical-client Charm E2E closure, or full Real Tibia parity.

# OAM-034 durable completion

Final disposition:

```text
creature-definitions ADAPT
```

Task-start baselines were Canary `ab2fb5548260544f42f786d11d4dd1b600c39a06`, Otheryn `2fe646dfff3d4fc0672c3fbeca85708dabc4ce87`, fresh upstream Canary `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`, and maintained OTClient `465b7a2192b176cf8cb9d58e000c38863e4a6e4c`. Canonical `creature-definitions` has no fundamental dependencies and owns monster definition data; Creature AI, spawns, raids and boss encounter orchestration remain separately owned.

Merged legacy PR #192 supplied the exact bounded donor. OAM-034 adapted six production corrections that remained absent from task-start Otheryn and fresh upstream while current legacy preserved the reviewed fixes: Agrestic Chicken gained `BESTY_RACE_BIRD`; Terrified Elephant gained `BESTY_RACE_MAMMAL`; alternate Eradicator changed `bossRaceId` from `1225` to `1226`; Monk's Apparition changed Bestiary `raceId` from `1946` to `2636`; Haunted Dragon gained `BESTY_RACE_DRAGON`; and Crypt Warrior gained Bestiary `raceId = 1995` plus `BESTY_RACE_UNDEAD`. PR #192 validator infrastructure, Cyclopedia logs and unrelated governance paths were excluded.

Otheryn PR #69 final head `dabc868c5ff9ca8009f20f1eb90645937ff18e22` changed exactly ten intended paths: six production definitions, focused proof, test registration, target evidence and active task checkpoint. Autofix.ci #193 run `29871761403`, Repository Audit #29 run `29871761411`, CI #235 run `29871761846`, and Required #220 run `29871761506` succeeded. Linux-debug build, Canary datapack runtime smoke, schema import and full `Run Tests` succeeded; the suite completed `423/423`, including both focused `Oam034CreatureDefinitionsAdaptTest` cases. Test-log artifact `8511786128` has digest `sha256:a53b92d60e34069d5fd0f52cd1ad94957edf757c2e8dd29c13ca5f2ec9ae30be`. Comments/reviews/threads were empty, target `main` had no task-start drift, and PR #69 merged by expected-head squash as `566b3b001987f6f452663b77c380e6405bfc541b`.

Canary governance PR #701 final head `37a58be7df77e7875d8faaffa9b5c0939fec6794` changed exactly the OAM-034 revalidation report and active-task record. The initial Ownership failure was limited to a missing checkpoint `pr` field and was repaired without scope or evidence change. Final Agent Task Ownership #3243 run `29872921471` and final-gate CI #4398 run `29872921548` succeeded; comments/reviews/threads were empty, non-overlapping E2E drift was audited, and PR #701 merged by expected-head squash as `2a63c4b1efe2a20bf653b419ffd6baea6cb2ee0d`.

Authoritative lifecycle PR #703 final head `35a9274ba157fc61fb82aed47e8d339499a7a9a6` changed exactly the active-delete/archive-add lifecycle paths. Agent Task Ownership #3245 run `29873136331` and final-gate CI #4399 run `29873136415` succeeded; comments/reviews/threads were empty, Canary `main` had no drift from the governance merge, and PR #703 merged by expected-head squash as `0ace0e6802501f1752405c4e15d75619171dd4cf`.

OAM-034 does not claim full monster catalogue parity, exhaustive creature stats, loot, spells, resistances or immunities, Creature AI, spawn placement, raid behavior, boss encounter mechanics, Bestiary or Bosstiary runtime correctness, protocol/client compatibility, persistence correctness, map/asset/schema/deployment parity, physical-client creature E2E closure, or full Real Tibia parity.

# OAM-035 durable completion

Final disposition:

```text
creature-ai REUSE
```

Task-start baselines were Canary `6a87373e84073a84ccdbdb64f7d61b2747f40764`, Otheryn `4771350b44665c5a37b0c058b3d413c0c0de542d`, fresh upstream Canary `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`, and maintained OTClient `a6868920443dc285656bd016acdb2c1ea566e511`. Canonical `creature-ai` depends only on completed `creature-definitions` and owns Monster runtime think, target/friend maintenance, target selection, follow/flee/movement decisions, attack/defense execution, callbacks, spawn/despawn and summon-ownership interactions.

Task-start Otheryn and fresh upstream shared exact canonical `monster.cpp` blob `30cdadf4076d29116eb96fb8bb5f7f46bebddcd5` and `monster.hpp` blob `a5426fdd22533179a9d54834dbe7b340a5d45012`. Identity alone was not accepted: semantic review confirmed the target already contained the newer modular targeting, pathfinding, combat-intention, compute-service and relevance boundaries, while legacy Canary diverged on both core blobs and was rejected as a stronger whole-module donor.

Proof-only Otheryn PR #72 final head `c623dc3b60f359bd821cab112e7204aac1696494` changed exactly four intended proof/task paths and no production path. Autofix run `29902975001`, CI run `29902975132`, Required run `29902974955`, Linux-debug runtime smoke/schema/full `Run Tests`, Linux release, both Windows build paths and macOS succeeded. Comments/reviews/threads were empty, target `main` had no task-start drift, and PR #72 merged by expected-head squash as `d9359bed541b06c4457d23a352b877caf5e88df7`.

Canary governance PR #711 final head `f138577bff8bb9fac8bb017d69be11ad165f771b` changed exactly the OAM-035 revalidation report and active-task record. Initial Ownership failures were limited to active-task lifecycle metadata (`related_pr`/checkpoint `pr`, unsupported active frontmatter status, and one noncanonical validation result) and were repaired without changing target scope or evidence. Final Agent Task Ownership run `29904707668` and CI run `29904707898` succeeded; reviews/threads were empty, and PR #711 merged by expected-head squash as `dbb832d9f2ac141476b7d0496ceb6149a4101cac`.

Authoritative lifecycle PR #712 final head `33035d96ad9d54c6d3e06b37230d91c62caa9117` changed exactly the active-delete/archive-add lifecycle paths. Agent Task Ownership run `29904968580` and CI run `29904969315` succeeded with Required PASS; heavy builds were correctly skipped for lifecycle-only scope. Reviews/threads were empty, and PR #712 merged by expected-head squash as `1328fb42b03056a0f2571831a1a1eb7a5416f73a`.

OAM-035 does not claim Real Tibia AI parity, exact target-choice weights, pathfinding parity, thread-safety proof, scheduler fairness, combat formula parity, spawn timing parity, summon ownership completeness, boss AI/reward correctness, raid behavior, protocol/client compatibility, physical-client gameplay E2E closure, or full Oteryn readiness.

# Current state

```text
Canary reconciliation base: 1328fb42b03056a0f2571831a1a1eb7a5416f73a
Otheryn target head after OAM-035: d9359bed541b06c4457d23a352b877caf5e88df7
maintained OTClient: a6868920443dc285656bd016acdb2c1ea566e511
OAM-001..OAM-035: feature/lifecycle complete
OAM-035 task: archived in Canary
OAM-036: NOT STARTED
```

No OAM implementation task is active in this reconciliation record.

# Queue

| Package | Status | Next action |
|---|---|---|
| OAM-001..OAM-035 | completed | preserve durable evidence |
| OAM-036+ | planned, not active | only after this reconciliation merges and the Otheryn OAM-035 target checkpoint is archived: perform fresh live-state/open-PR/ownership and exact target/upstream/legacy preflight, then select one dependency-valid canonical package |

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
- OAM-020 does not claim exhaustive Forge parity, physical-client Forge E2E closure, unresolved F-014 through F-019 server/client result parity, evidence-blocked F-009/F-010 rule parity, or generic cross-domain transaction/persistence redesign.
- OAM-021 does not claim crash-safe exactly-once Market create/cancel/accept/expiry, cross-process or multiwriter Market safety, remote-player mutation routing, generic multichannel/economic-ledger/leader-election redesign, exhaustive Real Tibia Market parity, maintained-client changes, or physical-client Market E2E closure.
- OAM-022 does not claim full modern Hunting Task/Taskboard parity, Wheel Bonus Promotion Shop or Wheel allocation ownership, exhaustive Prey formulas/rarity/reroll-price/monster-pool parity, physical-client Prey/Taskboard E2E closure, generic persistence/protocol redesign, or map/asset/schema/deployment migration.
- OAM-023 does not claim party chat/channel transport, protocol packet compatibility, maintained-client behavior, exhaustive shared-experience formula parity, generic combat correctness, vocation/Wheel correctness, guild lifecycle, physical-client Party E2E closure, or map/asset/schema/deployment migration.
- OAM-024 does not claim exhaustive sanction enforcement at every entry point, generic account-authentication security, protocol compatibility, distributed/multi-database sanctions replication, moderation policy, generic security analytics, AI investigation, PvP skull/frag parity, physical-client sanctions E2E closure, generic persistence redesign, or map/asset/schema/deployment migration.
- OAM-025 does not claim Real Tibia chat parity, guild/party membership lifecycle, protocol compatibility, maintained-client UI behavior, generic moderation policy, message privacy or delivery guarantees, NPC conversations, distributed chat, physical-client chat E2E closure, generic persistence redesign, or map/asset/schema/deployment migration.
- OAM-026 does not claim distributed guild ownership, multiwriter guild-bank safety, Real Tibia guild parity, website guild-management parity, guild-chat delivery parity, protocol/client UI parity, generic transaction atomicity, generic crash/restart durability, physical-client guild E2E closure, or map/asset/schema/deployment migration.
- OAM-027 does not claim generic house purchase/auction transaction atomicity, crash-safe transfer recovery, distributed or multiwriter house ownership, cross-channel house safety, Cyclopedia house-tab correctness, protocol/client UI compatibility, exhaustive rent/auction parity, physical-client house E2E closure, full Real Tibia house parity, or map/OTBM correctness.
- OAM-028 does not claim Bestiary, Bosstiary, Charm, Cyclopedia Character, Titles or Houses child correctness, exact packet-byte compatibility, maintained-client parsing/rendering correctness, item/map/house presentation correctness, persistence completeness, runtime behavior, physical-client Cyclopedia E2E closure, or full Real Tibia parity.
- OAM-029 does not claim full Cyclopedia Character parity, exact packet-byte compatibility, death-history correctness, KV/store-summary parity, database query performance, retained-history policy, maintained-client rendering correctness, physical-client Cyclopedia Character E2E closure, or full Real Tibia parity.
- OAM-030 does not claim full Bosstiary parity, exhaustive boosted-boss selection correctness, distributed or multiwriter leader election, cross-channel Bosstiary safety, Bestiary or Charms child correctness, exact protocol/client compatibility, maintained-client rendering correctness, monster-data parity, database availability or crash-recovery guarantees, physical-client Bosstiary E2E closure, or full Real Tibia parity.
- OAM-031 does not claim full Bestiary parity, exhaustive kill-stage/reward correctness, Charm correctness, monster-definition parity, exact protocol/client rendering compatibility, persistence completeness, tracker refresh correctness under every runtime state, database durability, physical-client Bestiary E2E closure, or full Real Tibia parity.
- OAM-032 does not claim title-definition or unlock-threshold parity, completeness of every cross-domain eligibility check, map/Drome/Goshnar or other TODO-backed title conditions, persistence atomicity or crash recovery, exact protocol compatibility, maintained-client parsing/rendering correctness, physical-client Titles E2E closure, or full Real Tibia parity.
- OAM-033 does not claim exhaustive Charm definition/value parity, all unlock costs, assignment-slot rules, combat proc formulas, element/resistance behavior, Bestiary progress correctness, protocol/client compatibility, maintained-client rendering, persistence atomicity, economy transaction atomicity, physical-client Charm E2E closure, or full Real Tibia parity.
- OAM-034 does not claim full monster catalogue parity, exhaustive creature stats, loot, spells, resistances or immunities, Creature AI, spawn placement, raid behavior, boss encounter mechanics, Bestiary or Bosstiary runtime correctness, protocol/client compatibility, persistence correctness, map/asset/schema/deployment parity, physical-client creature E2E closure, or full Real Tibia parity.
- OAM-035 does not claim Real Tibia AI parity, exact target-choice weights, pathfinding parity, thread-safety proof, scheduler fairness, combat formula parity, spawn timing parity, summon ownership completeness, boss AI/reward correctness, raid behavior, protocol/client compatibility, physical-client gameplay E2E closure, or full Oteryn readiness.

# Exact next task

Merge this program-only OAM-035 completion reconciliation after exact-head Ownership/CI/review gates. Only then may the Otheryn OAM-035 target checkpoint be archived; only after that archive merges may a fresh OAM-036 preflight begin. OAM-036 is NOT STARTED by this record.
