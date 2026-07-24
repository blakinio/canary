---
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
name: Oteryn Architecture and Migration
status: active
owner: oteryn-architecture-migration-agent
created: 2026-07-15T15:28:18+02:00
updated: 2026-07-24T19:51:00+02:00
last_verified_commit: "87c2204a822ffcdc40f7279f629b35ceec6c2556"
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
| OAM-042 | `npcs → REUSE` | target proof `0d01f077f80c2d4cd3d4231d2ffb9416874ba54e`; Otheryn lifecycle `3a37f3d5e4c01ddf4469f1c71461c40ca749142f`; feature `2f42260258f84b323bcd2a74d6107b10d4e01142`; Canary lifecycle `cec180bf0fdcd894d71c8219ffab83f3d07a51b7` |
| OAM-043 | `quests → ADAPT` | target `6512d78004ae2540784b3e67592a92a903554cf6`; Otheryn lifecycle `3f3c15917610e45430aa3902d110806dd25e10a8`; feature `6e55eab72b6f7b164bb38ba2e08fa1a80cf5f8e5`; Canary lifecycle `6e223c142f34285b98ea70d79131c79b1680e2d0` |
| OAM-044 | `protocol-compatibility → REUSE` | target `5c8f48e2a7cb7f841cfb6614e8e804245f17c0ca`; Otheryn lifecycle `e1eed52119ba21a29cb29cbac0793ed2a2b9d0c6`; feature `766aa0198884243c8d9641e5a1e92cd605735500`; Canary lifecycle `87c2204a822ffcdc40f7279f629b35ceec6c2556` |

# Durable evidence compaction

Detailed per-package narratives for OAM-001..OAM-044 remain authoritative in their archived task records, package revalidation reports and Git history. The completed-package table above preserves the exact durable merge references needed for sequencing. This compaction removes duplicated inline histories without weakening the archived evidence or explicit nonclaims.

# OAM-043 durable completion

Final disposition:

```text
quests ADAPT
```

OAM-043 selected canonical `quests` after formal OAM-042 closure. Canary preflight PR #866 merged as `df7abb0cfe4b05ed11da7b3a6a0dcddbefb62375`, and post-preflight handoff PR #872 merged as `13ec3077babba0ac81bb1e30e79f0ea4827ae2fe`. Exact task-start baselines were Otheryn `3a37f3d5e4c01ddf4469f1c71461c40ca749142f`, reviewed current upstream `7323503b3dc61ed86bf1f04a611b2d0aec64b35a`, and legacy Canary `13ec3077babba0ac81bb1e30e79f0ea4827ae2fe`.

The complete inventory recorded target/upstream `978` quest files and legacy `981`: `973` were identical across all three baselines, five retained identical target/upstream variants, and three were legacy-only. Complete source scanning covered all `978` target files and `12,027` evidence entries while preserving `1,045` dynamic expressions unresolved. The configured map SHA-256 `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2` produced World Index `6c22cd26d4414aa094af1d00be7f62190a441e270ee7a478b55449bf92e55e7a` with zero unknown tails; full correlation classified `8,860` findings confirmed, `484` script-only, `2,683` unresolved, zero map-only and zero conflicting.

The bounded target adaptation corrected the Hero of Rathleton achievement lookup, Soulpit `onUse` receiver and Ancient Tomb timed door closure, and restored exactly three map-backed legacy-only `The Beginning` handlers. The final quest inventory is `981` files. Wider donor hypotheses were rejected: Ancient Tomb AID `12108` had zero configured-map placements, Ape City/Wrath account-wide access calls lacked prerequisite target APIs, the Soulpit-local counter duplicated the stronger target-wide implementation, and no bulk legacy quest-tree import was authorized.

Otheryn PR #98 ready head `7a783c65e83a9fead651e38f336b10cbffe7a19b` and synchronization head `333b7047f8ecc660a84b215e9a4149b10d083c35` passed autofix, CI, Required and Repository Audit matrices across Fast Checks, Lua, Linux release/debug with full tests and runtime smokes, macOS and both Windows paths. Comments, reviews and threads were empty, target `main` had no drift before expected-head squash merge `6512d78004ae2540784b3e67592a92a903554cf6`. Otheryn lifecycle PR #99 changed only its task lifecycle path, passed Required `30093061770`, and merged as `3f3c15917610e45430aa3902d110806dd25e10a8`.

Canary governance PR #873 final head `c4a61cdbb51caa8450c2a03797307594e22acfb5` changed exactly the OAM-043 revalidation report and active-task record. Agent Task Ownership `30093436131` and full final-gate CI `30093456616` succeeded. Comments, reviews and threads were empty; concurrent Canary drift from E2E-QRI-006 did not overlap OAM-043 paths, and PR #873 merged as `6e55eab72b6f7b164bb38ba2e08fa1a80cf5f8e5`.

Authoritative Canary lifecycle PR #876 final head `32ef073efeb51b0f65c7cefec0353b1060a10f8b` changed only the active-to-archive task lifecycle path. Agent Task Ownership `30100163834` and CI/Required `30100164081` succeeded; heavy builds were correctly skipped. Comments, reviews and threads were empty, Canary `main` had no lifecycle-base drift, and PR #876 merged as `6e223c142f34285b98ea70d79131c79b1680e2d0`.

OAM-043 does not claim ownership or gameplay impact for all `484` shared script-only findings, runtime execution/correctness of the `1,045` dynamic expressions, exhaustive stage ordering and reachability for all `2,016` storage references, factual correctness of every quest family/reward/access/NPC/spawn dependency, physical-client quest closure, production gameplay parity or full world-content parity.

# OAM-044 durable completion

Final disposition:

```text
protocol-compatibility REUSE
```

OAM-044 selected canonical `protocol-compatibility` through fresh Canary preflight PR #879, merged as `47611c10be8a2262d66421c9da65de6cc5c7264d`. Exact reviewed baselines were Otheryn `3f3c15917610e45430aa3902d110806dd25e10a8`, current upstream `7323503b3dc61ed86bf1f04a611b2d0aec64b35a`, legacy Canary `a5cafe1b7ce148af59c64d1382963ac6ac633334` and maintained client `b3bcea2a95959bb4e92cc0b80cd49f36b63699b2`.

Target and current upstream retained identical protocol-profile roots: header blob `b9f1eec01e1ba348c22315be43ccefe74b210e45` and implementation blob `5405c343cfa2c2d75a173d6678ecf8afc7690120`; the maintained-client feature root was blob `8b458b864ad765185fd856414f2c097d565a5a22`. These roots are byte-identical to those exercised by OAM-006 physical run `29531221365`, which passed two current-profile protocol-1525 login/relog cycles. That continuity is bounded to the current profile and was not extended to Tibia 11.00, CipSoft 8.60 variants or OTCv8.

The target proof retained production code unchanged and added a focused contract for all six registered profiles, deterministic version/wire-family/asset resolution, support states, item-mapper policies, selected current server/client feature pairs and bounded current/1100/860 login metadata. Legacy transport-profile splitting was rejected from this package because it belongs to `network-transport` or `login-protocol`; similar feature names were not treated as semantic or byte-layout proof.

Otheryn feature PR #100 ready head `29d196e1b7d084813e24d368bd9e70329e16d0b3` passed Autofix `30106675779`, CI `30106676001` and Required `30106675816`. Final synchronization head `62a42372e2225b71aaa0066cc934f684e830913c` passed Autofix `30111297337`, CI `30111297597` and Required `30111297475`. Discussions were empty, target `main` had no drift and expected-head squash merge produced `5c8f48e2a7cb7f841cfb6614e8e804245f17c0ca`. Otheryn lifecycle PR #101 passed Required `30112638532` and merged as `e1eed52119ba21a29cb29cbac0793ed2a2b9d0c6` after a clean audit.

Canary governance PR #888 final head `3a996c687106ea3d3c0f70257ebef650d3de80d3` passed Agent Task Ownership `30112911749` and full final-gate CI `30112919837`, including Fast Checks, Lua, Docker, Linux debug/release with tests and runtime smokes, and Windows CMake/Solution. Discussions were empty, Canary `main` had no drift and expected-head squash merge produced `766aa0198884243c8d9641e5a1e92cd605735500`. Canary lifecycle PR #890 final head `c543a2d7b861a8b7ff56cdb4a107b05560fdae99` passed Ownership `30114361152` and CI/Required `30114362140`; heavy builds were correctly skipped, discussions were empty and merge produced `87c2204a822ffcdc40f7279f629b35ceec6c2556`.

OAM-044 does not claim exhaustive one-to-one or many-to-one correspondence between every server `ProtocolFeature` and client `GameFeature`, byte-level compatibility for every packet/profile, factual provenance of all proprietary asset signatures, physical-client login/world-entry parity for Tibia 11.00 or CipSoft 8.60, OTCv8 readiness, transport/login/session-handoff closure, production gameplay parity or full protocol-stack readiness.

# Current state

```text
Canary reconciliation base: 87c2204a822ffcdc40f7279f629b35ceec6c2556
Otheryn target head after OAM-044: e1eed52119ba21a29cb29cbac0793ed2a2b9d0c6
maintained OTClient: b3bcea2a95959bb4e92cc0b80cd49f36b63699b2
OAM-001..OAM-044: feature/lifecycle complete
OAM-044 task: archived in Canary and Otheryn
OAM-045: NOT STARTED pending a fresh dependency-valid preflight
```

No OAM implementation task is active in this reconciliation record.

# Queue

| Package | Status | Next action |
|---|---|---|
| OAM-001..OAM-044 | completed | preserve durable evidence |
| OAM-045+ | planned, not active | only after this reconciliation merges: perform fresh live-state/open-PR/ownership and exact target/upstream/legacy preflight, then select one dependency-valid canonical package |

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
- OAM-036 does not claim exact participant eligibility, contribution-score arithmetic, loot factor/roll parity, reward-table correctness, Bosstiary bonus correctness, persistence atomicity, crash recovery, generic boss AI correctness, spawn/raid correctness, quest/cooldown behavior, protocol/client compatibility, physical-client boss E2E closure or full Real Tibia parity.
- OAM-037 does not claim exact official raid probability or timing parity, event timing under every scheduler load, raid XML completeness, restart/crash recovery, exact spawn placement parity or physical-client raid closure.
- OAM-038 does not claim exhaustive zone membership/eviction correctness, tile PvP/protection semantics, quest/event behavior inside zones, persistence guarantees, protocol/client compatibility or physical-client zone closure.
- OAM-039 does not claim complete production instance activation, full isolation, logout/death/reconnect semantics, production arena coordinates, persistence, two-instance physical E2E or Real Tibia instance parity.
- OAM-040 does not promote static OTBM evidence into live gameplay proof and does not authorize copying generated reports, map assets or the Canary toolchain into Otheryn.
- OAM-041 does not promote static evidence into live gameplay proof and does not close the explicit Harlow or dynamic-Lua evidence boundaries.
- OAM-042 does not promote bounded source-contract evidence into exhaustive individual-conversation, dynamic-call, production or physical-client parity and does not close the duplicate Harlow boundary.
- OAM-043 does not promote static source/map evidence into exhaustive quest progression or gameplay proof and retains all shared script-only, dynamic-expression, storage-graph and physical-client/production boundaries.
- OAM-044 does not promote current-profile source continuity and bounded fixtures into exhaustive legacy-profile, packet-byte, transport/login/session-handoff, physical-client or production protocol-stack parity.
