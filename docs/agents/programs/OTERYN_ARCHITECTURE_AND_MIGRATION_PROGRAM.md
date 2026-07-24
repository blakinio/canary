---
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
name: Oteryn Architecture and Migration
status: active
owner: oteryn-architecture-migration-agent
created: 2026-07-15T15:28:18+02:00
updated: 2026-07-24T08:20:00+02:00
last_verified_commit: "55f9e46ab0804ec2c7b58cfffc772a243234c956"
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
| OAM-036 | `boss-encounters → REUSE` | target proof `c0a84977b574f287db2fb970a25e8041343b99c8`; feature `54abf518a3470c0f1db08f0276164fe5c7e977e0`; lifecycle `637c57d8744204490b452bdd935789ec0c4de23b` |
| OAM-037 | `raids → REUSE` | target proof `d896141d084d381d12cc328d4b920c698eb1d55c`; feature `841053a1800f4e8fdb338c31bac0534ae264dabd`; lifecycle `a3d4ea560f4793380dcb5f73f44eec11279eb44f` |
| OAM-038 | `world-zones → REUSE` | target proof `d1ce61df934843e2f54800f4ea9efce6cf374a09`; feature `f9fc157dad3668b5051761264ebeecf5bdf1f055`; lifecycle `57e26e3a22db90b41a005a467c2f2411e0e1039b` |
| OAM-039 | `instances → ADAPT` | target `a2a52e239d8e8a770ff7376fcbb9b5bfdcc8cc13`; feature `7f5fcfb77c35f83f0841ee1d57a70878b5e544d0`; lifecycle `5f434e9f1e792670545aaf818e34af47c40b2c88` |
| OAM-040 | `otbm-tooling → DO_NOT_MIGRATE` | target proof `e607887533bbbff13ff36d781e3f7f25d2f71675`; feature `74121ca3d968ace7a68bcdb5cd7cd64e6e54d702`; lifecycle `54ce97b3bcaac8c2e1a0d4cc6162a6ff975bbee9` |
| OAM-041 | `spawns → REUSE` | target proof `de061aa6c75114192f1ef6b33f7b4857e502936c`; feature `0dc3fa9d663af47f8808d2457c8108a63294c7c4`; lifecycle `55f9e46ab0804ec2c7b58cfffc772a243234c956` |

# Durable evidence compaction

Detailed per-package narratives for OAM-001..OAM-034 remain authoritative in their archived task records and Git history. The completed-package table above preserves the exact durable merge references needed for sequencing; the most recent package narratives remain inline for bounded continuation.

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

# OAM-036 durable completion

Final disposition:

```text
boss-encounters REUSE
```

Task-start baselines were Canary `27b49fbbdafda9c365bc25b0c2adb790337d42d4`, Otheryn `6275021bbb83dc28d2f5d6cf8db5b16aa7206544`, fresh upstream Canary `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`, and maintained OTClient `a6868920443dc285656bd016acdb2c1ea566e511`. Canonical `boss-encounters` depends only on completed `creature-definitions` and `player-persistence` and owns reward-boss participant state, contribution tracking, target-list reconciliation, boss-death score normalization, reward generation, reward-container insertion and offline persistence handoff.

Task-start Otheryn, fresh upstream and legacy Canary shared exact `data/libs/systems/reward_boss.lua` blob `72476dfcbdd8fd92d6b5bd3ad3015efef87cf2f3` and `data/scripts/systems/reward_chest.lua` blob `4abe17ad2f3103f30f172f23ebdca391197f8646`. Identity alone was not accepted: semantic review and bounded source-contract proof covered participant state, target-list activity, score normalization, reward generation, reward-container insertion, offline-player save handoff and encounter-state cleanup; no stronger delivered legacy donor was identified.

Otheryn PR #74 final head `18153ce36b0d84e2b6b73e68579b2167c91fc03f` changed exactly four intended proof/task paths and no production path. Exact-head autofix `29907996264`, CI `29907997057`, Required `29907996378`, Linux-debug runtime smoke/schema/full `Run Tests`, Linux release, both Windows build paths and macOS succeeded. Comments/reviews/threads were empty, target `main` had no task-start drift, and PR #74 merged by expected-head squash as `c0a84977b574f287db2fb970a25e8041343b99c8`.

Canary governance PR #725 final head `3a12a5c25dfb8443aa8d97d1e1837b152b2b367d` changed exactly the OAM-036 revalidation report and active-task record. Agent Task Ownership run `29941761377` and full final-gate CI run `29941761619` succeeded, including Linux-debug full tests and all platform builds. Comments/reviews/threads were empty and PR #725 merged by expected-head squash as `54abf518a3470c0f1db08f0276164fe5c7e977e0`.

Authoritative lifecycle PR #726 final head `d8d6d180daa7ce3a20f3d34165917b434a980941` changed exactly the active-delete/archive-add lifecycle paths. Agent Task Ownership run `29946779628` and CI run `29946780348` succeeded with Required PASS; heavy builds were correctly skipped for lifecycle-only scope. Reviews/threads were empty, Canary `main` had no drift from its reconstructed base, and PR #726 merged by expected-head squash as `637c57d8744204490b452bdd935789ec0c4de23b`.

OAM-036 does not claim exact participant eligibility, contribution-score arithmetic, loot factor/roll parity, reward-table correctness, Bosstiary bonus correctness, persistence atomicity, crash recovery, generic boss AI correctness, spawn/raid correctness, quest/cooldown behavior, protocol/client compatibility, physical-client boss E2E closure or full Real Tibia parity.

# OAM-037 durable completion

Final disposition:

```text
raids REUSE
```

OAM-037 selected canonical `raids` after OAM-036 formal closure. Canary preflight PR #733 merged as `8bdeb2747356727df80a3b95073aa29a4dca7818`; immutable Otheryn target task-start main was `3aaf77fe27600b274d2b9c9e6bd30d887e0afd0e`; the reviewed fresh upstream baseline retained exact canonical `raids.cpp` blob `d46a549a341e0872474bd723b10d1208fa22da8c` and `raids.hpp` blob `777558e3e199816bb596636fc7487c38c29224ee`.

Identity alone was not accepted. Semantic review and the bounded target source-contract proof covered registry load/reload, interval/margin/repeat parsing, maintenance-lane periodic selection, scheduling-failure handling, running/non-repeat state, ordered event execution, reset/stop cleanup, and announce/single-spawn/area-spawn/script event dispatch. The older legacy Canary core was rejected as a stronger whole-module donor because target and fresh upstream retained maintenance-lane scheduling and explicit scheduling-failure safeguards absent from the reviewed legacy core.

Otheryn PR #77 final head `133c12f61a1e5e392be9ee7faa9236755cbe0225` changed exactly four intended proof/task paths and no production path. Exact-head autofix `29988627793`, CI `29988627932`, Required `29988627768`, Linux-debug runtime smoke/schema/full `Run Tests`, Linux release, both Windows build paths and macOS succeeded. Comments/reviews/threads were empty, target `main` had no task-start drift, and PR #77 merged by expected-head squash as `d896141d084d381d12cc328d4b920c698eb1d55c`.

Canary governance PR #750 final head `63bd6f684e4d88c5dfe4dfbb79ec86dd01210d5f` changed exactly the OAM-037 revalidation report and active-task checkpoint. Agent Task Ownership `29990517255` and full final-gate CI `29990517385` succeeded on the exact head after an unchanged-head failed-job retry; Linux-debug full tests and all platform builds passed. Comments/reviews/threads were empty, and PR #750 merged by expected-head squash as `841053a1800f4e8fdb338c31bac0534ae264dabd`.

Authoritative lifecycle PR #758 final head `13201f341d8d20851e1ecf652f25ef38c680f27b` changed exactly the active-delete/archive-add lifecycle paths. Agent Task Ownership `29992792757` and CI `29992793019` succeeded with Required PASS; heavy builds were correctly skipped for lifecycle-only scope. Comments/reviews/threads were empty. Concurrent Canary drift was limited to unrelated OTBM task archives with no OAM-037 path overlap, and PR #758 merged by expected-head squash as `a3d4ea560f4793380dcb5f73f44eec11279eb44f`.

OAM-037 does not claim exact official raid probability or timing parity, exact event timing under scheduler load, raid XML/data-definition completeness, restart/crash recovery semantics, distributed or multichannel raid coordination, exact spawn placement parity, webhook delivery guarantees, physical-client E2E closure or full Real Tibia parity.

# OAM-038 durable completion

Final disposition:

```text
world-zones REUSE
```

Task-start baselines were Canary `61163f5d9006351b9eaad799bd9dd0f825529db1`, Otheryn `651ff1c6261eb25bd0992d7530e50e3690c2b5de`, fresh upstream Canary `7323503b3dc61ed86bf1f04a611b2d0aec64b35a`, and maintained OTClient `1e5305395159142634f182d9e888e5f9164228c6`. Canonical `world-zones` depends only on completed `world-map-runtime` and owns the Zone registry by name, id and position, static/dynamic zone lifecycle, area/position indexing, membership caches, remove destinations, bulk removal, refresh, monster-variant metadata and XML zone loading.

Task-start Otheryn and fresh upstream shared exact canonical `zone.cpp` blob `f80af238eb2b4b10193a9b5961652591d9dafeb5` and `zone.hpp` blob `d413dccc690d37dc1a24af6c5d2e630b14b087d1`. Identity alone was not accepted: semantic review and bounded source-contract proof covered registry/index lifecycle, synchronized weak membership caches, dynamic-zone cleanup, bulk removal, monster-variant propagation and XML loading. The divergent legacy Canary roots were rejected as a stronger whole-module donor because the target retains `cacheMutex` protection and safer typed weak-pointer erasure safeguards absent from the reviewed legacy core.

Otheryn PR #79 final head `a2a6eb155a2c2ec4bf74524b94c1df9ebf72f7d1` changed exactly four intended proof/task paths and no production path. Exact-head autofix `29995158391`, CI `29995158283`, Required `29995157990`, Linux-debug runtime smoke/schema/full `Run Tests`, Linux release runtime smokes, both Windows build paths and macOS succeeded. Comments/reviews/threads were empty, target `main` had no task-start drift, and PR #79 merged by expected-head squash as `d1ce61df934843e2f54800f4ea9efce6cf374a09`.

Canary governance PR #766 final head `a71bf3895ef9620cede7ef0f9e52b31ed345edb8` changed exactly the OAM-038 revalidation report and active-task checkpoint. Agent Task Ownership `29996434594` and CI `29996434975` succeeded with Required PASS; heavy builds were skipped by repository scope/reuse policy after the full target matrix passed on PR #79. Comments/reviews/threads were empty. Concurrent Canary drift was limited to unrelated OTBM paths, and PR #766 merged by expected-head squash as `f9fc157dad3668b5051761264ebeecf5bdf1f055`.

Authoritative lifecycle PR #769 final head `5126788e539e475a258afae6a6a1506caba759ff` changed exactly the active-delete/archive-add lifecycle paths. Agent Task Ownership `29997233627` and CI `29997233742` succeeded with Required PASS; heavy builds were correctly skipped for lifecycle-only scope. Comments/reviews/threads were empty, Canary `main` had no drift from lifecycle base, and PR #769 merged by expected-head squash as `57e26e3a22db90b41a005a467c2f2411e0e1039b`.

OAM-038 does not claim exhaustive zone membership or eviction correctness under every movement/reload/concurrency schedule, tile protection/PvP flag correctness, quest/event behavior inside zones, instance isolation, exact monster-variant gameplay semantics, map-content parity, persistence guarantees, protocol/client compatibility, physical-client E2E closure or full Real Tibia parity.

# OAM-039 durable completion

Final disposition:

```text
instances ADAPT
```

OAM-039 selected canonical `instances` after formal OAM-038 closure. Canary preflight PR #771 merged as `5c0613fd853e85421a89f661e9b3774c4dd730ff`; immutable Otheryn target task-start main was `a275f1d788b50164ffc79b6f6143e13b9150c82e`; the reviewed fresh upstream baseline was `7323503b3dc61ed86bf1f04a611b2d0aec64b35a`, and maintained OTClient baseline was `1e5305395159142634f182d9e888e5f9164228c6`. Clean Otheryn and fresh upstream lacked the canonical `InstanceManager` roots, while legacy Canary provided the staged behavioral donor for region allocation, lifecycle, stable creature ownership, fail-closed relations, event liveness and the bounded arena consumer.

The target adaptation remained bounded to canonical `src/game/instance/**`, focused unit tests and CMake registration. It deliberately did not copy `Game`, `Creature`, Lua, talkaction, protocol, client, map-content, asset, schema or persistence wiring. Legacy hard-coded `data-canary` arena coordinates were not imported; clean-target `InstanceArenaService::configuredRegions()` remains empty by default and the consumer operates only against explicitly configured target regions.

Otheryn PR #81 initially reached exact head `58c4d2cf2cb5f26d67974b78e9d8e16885eae702`, where Linux-debug full tests isolated one owned lifecycle defect: `InstanceManagerTest.CleanupRunsExactlyOnceAndDirtyRegionIsQuarantined` showed that an already-`Closing` quarantined instance returned early and could not finalize/release its region after creature ownership was later drained. The bounded repair changed `close()` so a `Closing` retry skips the cleanup callback but retries finalization and region release when ownership is empty, preserving exactly-once cleanup.

PR #81 final head `e216c3bb732bc6dc97374833bbfcb13a4f4ebc50` changed exactly 19 intended bounded paths and passed autofix `30002236999`, CI `30002237279`, Required `30002237057`, Linux release/debug including full `Run Tests`, both Windows build paths, macOS and Docker. Comments/reviews/threads were empty, target `main` had no task-start drift, and PR #81 merged by expected-head squash as `a2a52e239d8e8a770ff7376fcbb9b5bfdcc8cc13`.

Canary governance PR #779 final head `f07951fbb7475779347e2721931cb8f0adf1a612` changed exactly the OAM-039 revalidation report and active-task checkpoint. Exact-head Agent Task Ownership `30003789254` and full `ci:final-gate` CI `30003789351` succeeded, including Linux release/debug, both Windows paths, macOS and Docker. Comments/reviews/threads were empty; concurrent Canary drift was limited to unrelated documentation/task paths, and PR #779 merged by expected-head squash as `7f5fcfb77c35f83f0841ee1d57a70878b5e544d0`.

Authoritative lifecycle PR #786 final head `5159a8b28b3b920175285299a2bae4251c5a570b` changed exactly the active-delete/archive-add lifecycle paths. Agent Task Ownership `30005076380` and CI `30005076505` succeeded with Required PASS; heavy builds were correctly skipped for lifecycle-only scope. Comments/reviews/threads were empty, Canary `main` had no drift from lifecycle base, and PR #786 merged by expected-head squash as `5f434e9f1e792670545aaf818e34af47c40b2c88`.

OAM-039 does not claim complete production instance activation through `Game`, ordinary spawn/NPC ownership, full spectator/target/combat isolation, logout/death/reconnect semantics, generic scheduler task cancellation, production arena coordinates, persistence semantics, admin Lua/talkaction reachability, two-parallel-instance physical E2E, multiworld support or full Real Tibia instance parity.

# OAM-040 durable completion

Final disposition:

```text
otbm-tooling DO_NOT_MIGRATE
```

OAM-040 selected canonical `otbm-tooling` after formal OAM-039 closure. Canary preflight PR #790 merged as `90b5054ebc8b2a19d52cc1bc2731e9dc6f3080f3`. The canonical module is dependency-free `platform-tooling`, owns no server/client/data paths, and represents the deterministic OTBM analysis/evidence stack maintained in the Canary laboratory and validation repository.

The target architecture contract assigns Canary the legacy laboratory/evidence/validation responsibility and Otheryn the clean selectively populated target role. Canonical `spawns` and `npcs` depend on `otbm-tooling`; `quests` depends on it plus `player-persistence`. OAM-040 resolved those relationships as cross-repository evidence dependencies: downstream packages must pin exact Canary tooling/report provenance and prove their own target behavior, while no identified Otheryn runtime, service, protocol, client, map-loader, production build or data path requires a target-local copy.

Otheryn PR #83 final head `06d1a692e2e6ed0eaaf98d7acb54281a1cd5d4c3` changed exactly two documentation/task paths and introduced zero target production mutation. Required run `30007035180` succeeded. Comments/reviews/threads were empty, target `main` had no task-start drift, and PR #83 merged by expected-head squash as `e607887533bbbff13ff36d781e3f7f25d2f71675`.

Canary governance PR #792 final head `cdfa8edd72ecf80610fab28115538d689161191e` changed exactly the OAM-040 revalidation report and active-task checkpoint. Agent Task Ownership `30007303629` and CI `30007303732` succeeded with Required PASS; heavy builds were correctly skipped for the two-document scope. Comments/reviews/threads were empty, Canary `main` had no drift from governance base, and PR #792 merged by expected-head squash as `74121ca3d968ace7a68bcdb5cd7cd64e6e54d702`.

Authoritative lifecycle PR #793 final head `2c26f722f454e9db85291f0af75f7b29b26bde87` changed exactly the active-delete/archive-add lifecycle paths. Agent Task Ownership `30007601961` and CI `30007601786` succeeded with Required PASS; heavy builds were correctly skipped for lifecycle-only scope. Comments/reviews/threads were empty, Canary `main` had no drift from lifecycle base, and PR #793 merged by expected-head squash as `54ce97b3bcaac8c2e1a0d4cc6162a6ff975bbee9`.

OAM-040 does not claim that static OTBM evidence proves live gameplay, that the Canary toolchain is permanently feature-complete, that generated reports or map assets belong in Otheryn, or that downstream `spawns`, `npcs` or `quests` are already migrated or correct.

# OAM-041 durable completion

Final disposition:

```text
spawns REUSE
```

OAM-041 selected canonical `spawns` after formal OAM-040 closure. Canary preflight PR #813 merged as `82da6f6c5284b13446c5e71d075e7b06c9252b67`; target-proof-plan PR #819 merged as `5c2ec1df1b5be9494fbf97ba389bea8fd9070f58`; immutable Otheryn target task-start main was `9369b0719ff94997a9cf5a2d62853939744e6338`. Canonical `spawns` depends only on externally resolved `otbm-tooling`, while raid lifecycle remains owned by completed OAM-037 and monster combat AI remains outside this package.

Task-start Otheryn and fresh upstream shared exact canonical `spawn_monster.cpp` blob `4c82217631ddf479faa5443025d43f99a0c927d1` and `spawn_npc.cpp` blob `21718ad80827a16e9a1b29bc9d649ad603bcf216`. Identity alone was not accepted: semantic source-contract proof covered XML center-plus-offset placement, interval/default/rate scaling, player blocking, removed-creature cleanup, maintenance-lane scheduling, monster boss exclusivity and weighted selection. The divergent legacy Canary runtime was rejected as a stronger whole-module donor because target/upstream retain stronger maintenance-lane scheduling safeguards.

Deterministic target proof run `30049543113` pinned Canary evidence revision `d1ad83056ec7930f067986909f66b8f20f1a1f44`, exact Phase 4 tool blobs, target map SHA-256 `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2` and external World Index SHA-256 `6c22cd26d4414aa094af1d00be7f62190a441e270ee7a478b55449bf92e55e7a`. The full active-datapack scan found `52,903` groups and `84,294` static placements with `318` complete findings. Duplicate `Harlow` NPC-definition ambiguity and `310` nonliteral dynamic creation calls remain explicit unresolved evidence boundaries. The final bounded region confirmed `34/34` groups and `39/39` placements with complete reachability diagnostics and zero correlation findings.

Otheryn PR #92 final head `2168ff23a7415b9aea8f66b7051995e7fd148691` changed exactly four proof/task/test-registration paths and no production path. Autofix `30068408311`, CI `30068408471` and Required `30068408289` succeeded across Linux release/debug, runtime smokes, full tests, macOS and both Windows paths. Comments/reviews/threads were empty, target `main` had no drift, and PR #92 merged by expected-head squash as `de061aa6c75114192f1ef6b33f7b4857e502936c`.

Canary governance PR #853 final head `b45d0f9ce5c7dc7d359364db013db509eeb4d035` changed exactly the revalidation report and active-task checkpoint. Agent Task Ownership `30069689973` and full final-gate CI `30069698603` succeeded. Comments/reviews/threads were empty, Canary `main` had no governance-base drift, and PR #853 merged by expected-head squash as `0dc3fa9d663af47f8808d2457c8108a63294c7c4`.

Authoritative lifecycle PR #854 final head `72ba86574322927218d4d5b1a99062a5fa749961` changed exactly the active-delete/archive-add task paths. Agent Task Ownership `30070624817` and full final-gate CI `30070630936` succeeded. Comments/reviews/threads were empty; concurrent Canary drift was limited to unrelated TCR-003 OTBM paths with no OAM-041 overlap, and PR #854 merged by expected-head squash as `55f9e46ab0804ec2c7b58cfffc772a243234c956`.

Canary PR #856 is the one-file durable reconciliation gate for this record and the final Canary-side prerequisite before the Otheryn OAM-041 target-task archive.

OAM-041 does not claim execution or correctness of unresolved dynamic Lua creation calls, exhaustive live validation of all `84,294` static placements, exact Real Tibia spawn population/timing/placement parity, scheduler fairness under production load, raid lifecycle beyond the separated OAM-037 boundary, protocol/client compatibility, physical-client spawn/NPC gameplay E2E closure or full world-content parity.

# Current state

```text
Canary reconciliation base: 55f9e46ab0804ec2c7b58cfffc772a243234c956
Otheryn target head after OAM-041: de061aa6c75114192f1ef6b33f7b4857e502936c
maintained OTClient: 1e5305395159142634f182d9e888e5f9164228c6
OAM-001..OAM-041: feature/lifecycle complete
OAM-041 task: archived in Canary
OAM-042: NOT STARTED pending Otheryn OAM-041 target checkpoint archive
```

No OAM implementation task is active in this reconciliation record.

# Queue

| Package | Status | Next action |
|---|---|---|
| OAM-001..OAM-041 | completed | preserve durable evidence |
| OAM-042+ | planned, not active | only after this reconciliation merges and the Otheryn OAM-041 target checkpoint is archived: perform fresh live-state/open-PR/ownership and exact target/upstream/legacy preflight, then select one dependency-valid canonical package |

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
- OAM-041 does not promote static evidence into live gameplay proof and does not close the explicit Harlow or dynamic-Lua evidence boundaries.
