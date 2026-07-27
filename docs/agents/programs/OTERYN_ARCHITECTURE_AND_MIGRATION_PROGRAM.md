---
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
name: Oteryn Architecture and Migration
status: active
owner: oteryn-architecture-migration-agent
created: 2026-07-15T15:28:18+02:00
updated: 2026-07-27T08:00:00+02:00
last_verified_commit: "66bdb1a9be9c229720a2e667c760bd56f24d40dd"
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

- Canary is governance and legacy evidence; Otheryn is the separately authorized target.
- Upstream, OTClient and donor repositories remain read-only unless separately authorized.
- One bounded OAM package/task/branch/PR at a time with exact SHAs.
- Never infer `REUSE` from file presence, matching blobs or compilation alone.
- Never bulk-copy legacy Player/IOLoginData or the repository.
- Preserve OAM-004 persistence gaps: player SQL state and later KV durability are not atomic.
- Feature/proof merge must be followed by separate lifecycle archive, Canary governance/lifecycle and durable programme reconciliation before the next OAM starts.
- Reuse shared deterministic evidence and Universal Physical-Client E2E; do not create duplicate registries, parsers or orchestrators.
- Final merge requires exact-head gates and clean comments, reviews and review threads.

# Completed packages

| Package | Result | Durable state |
|---|---|---|
| OAM-001..OAM-040 | architecture, foundations and canonical packages through `otbm-tooling → DO_NOT_MIGRATE` | completed; exact references remain authoritative in archived task records and Git history |
| OAM-041 | `spawns → REUSE` | target `de061aa6c75114192f1ef6b33f7b4857e502936c`; feature `0dc3fa9d663af47f8808d2457c8108a63294c7c4`; lifecycle `55f9e46ab0804ec2c7b58cfffc772a243234c956` |
| OAM-042 | `npcs → REUSE` | target `0d01f077f80c2d4cd3d4231d2ffb9416874ba54e`; Otheryn lifecycle `3a37f3d5e4c01ddf4469f1c71461c40ca749142f`; feature `2f42260258f84b323bcd2a74d6107b10d4e01142`; Canary lifecycle `cec180bf0fdcd894d71c8219ffab83f3d07a51b7` |
| OAM-043 | `quests → ADAPT` | target `6512d78004ae2540784b3e67592a92a903554cf6`; Otheryn lifecycle `3f3c15917610e45430aa3902d110806dd25e10a8`; feature `6e55eab72b6f7b164bb38ba2e08fa1a80cf5f8e5`; Canary lifecycle `6e223c142f34285b98ea70d79131c79b1680e2d0` |
| OAM-044 | `protocol-compatibility → REUSE` | target `5c8f48e2a7cb7f841cfb6614e8e804245f17c0ca`; Otheryn lifecycle `e1eed52119ba21a29cb29cbac0793ed2a2b9d0c6`; feature `766aa0198884243c8d9641e5a1e92cd605735500`; Canary lifecycle `87c2204a822ffcdc40f7279f629b35ceec6c2556` |
| OAM-045 | `protocol-session-handoff → ADAPT` | target `597ba62c558ed4e35db38502903ae83e0b2921ec`; Otheryn lifecycle `e8f683e61427e9967cbc180b837220d4b7487d85`; feature `8b24b6603c29250587949a0e1600aa981795f133`; Canary lifecycle `14e3d7b9b21e8fee443d4bc8ebc107dad7c4bdb6` |
| OAM-046 | `configuration → ADAPT` | target `e05109ac6b98fe6761ed7ed7e933b0610b219911`; Otheryn lifecycle `415f559f829c83d79d9c609e7f421d2449e59d74`; governance `a49f3a3d5fc7bcbca823ec7acf9c3e9a822f1e2e`; Canary lifecycle `fd338ccc7864e572f8bed8e38144dc53e096293a` |
| OAM-047 | `lua-runtime → ADAPT` | target `5b3bee0dd6eedf8c2f9578c686ca85c0fde519cf`; Otheryn lifecycle `68e2b233b02356a79a03422ed51d757b85915bc5`; governance `06f3f78724f8f74b704272b9b97837b2ba1819d7`; Canary lifecycle `62c3124fa2331e58ad675e059f8e33f87cb15ad7` |
| OAM-048 | `gameplay-analytics → EXPERIMENTAL_ONLY` | target `a6e2993ed32b1316168045ad0b97ddebb50a2128`; Otheryn lifecycle `fc93848796f05108684dfbb218f7434a8cb88755`; governance `8c8d68b7f0fa523c919a786809ba4a72cbc5369d`; Canary lifecycle `dfe801d1945263984f8cb4e3ee5e1c48627d9501` |
| OAM-049 | `upstream-intelligence → DO_NOT_MIGRATE` | target `9632bf1a0721fb28f3596c57495ba008604587ec`; Otheryn lifecycle `877816a64e31c6d25815ebf6b7543e001648ca52`; governance `b425be2d2b38a51f5f3361ce166d61526a342b4c`; Canary lifecycle `6367652ebcc811913cc4fced9eb2149aafc1fee5` |
| OAM-050 | `physical-client-e2e → DO_NOT_MIGRATE` | target `92cc602332f0ea86dbb669541020112c299ec66c`; Otheryn lifecycle `ff90e93d872b6b47720f711483a9832203d5258d`; governance `e09b9a922729eb0fa800684faacaac61d02aba3f`; Canary lifecycle `ef05fa5a73434df16b9fca912a15389b10450f12` |
| OAM-051 | `wheel-of-destiny → ADAPT` | OAM-051B target `546eac0a00ec620e7293d0548e30662024464084`; Otheryn lifecycle `db10096f0ebb484f05883dbde4dd895744fbe8c6`; Canary preflight `9e865b68b9197b28450002412ca1720683cf1f64`; Canary lifecycle `a3a0c647fd6fdac44fcfb449f570ee75bd95f6df` |
| OAM-052 | `deployment-operations → DO_NOT_MIGRATE` | target `2afcaef4a3d023a7ec987e4380e80905534fdd2b`; Otheryn lifecycle `2c085eee1b1c430d09a87f567aac1a8e701721a4`; governance `b5a45d32b015965fd79aece734857edf4bdc0bac`; Canary lifecycle `adb187edbe948ad2f1801586d5196dd4b0ff8e86` |
| OAM-053 | `network-transport → ADAPT` | Canary preflight `6a9e6cf106b3e0193fb6a9d923a37cee38888f66`; target `c25fff72dd8b89f6ef1565af2d84ab9eef33dce9`; Otheryn lifecycle `9703da845384423ad85883216bf8853642c21bcd`; governance `91d96d8aa72b3851c4db89a71de9ea9722bcc63b`; Canary lifecycle `66bdb1a9be9c229720a2e667c760bd56f24d40dd` |

Detailed package narratives, exact task-start baselines, gate runs, rejected hypotheses and nonclaims remain authoritative in archived task records and package revalidation reports.

# OAM-053 durable completion

Final disposition:

```text
network-transport ADAPT
```

OAM-053 preserved Otheryn's existing connection, multiprotocol and session-handoff architecture while adapting explicit current transport profiles, complete profile authority for framing/checksum/compression/encrypted layout, typed fail-closed inbound outcomes, checksum-free block-count symmetry and accepted-sequence commit only after complete checksum/XTEA acceptance.

Canary preflight PR #979 merged as `6a9e6cf106b3e0193fb6a9d923a37cee38888f66`. Otheryn feature head `7376eff79e166595a91f4581d8eef6e6c228e754` passed CI `30225971903`, Required `30225971757` and autofix `30225971771`; PR #163 merged as `c25fff72dd8b89f6ef1565af2d84ab9eef33dce9`. Otheryn lifecycle head `34036aa6db8e6f8942a970a214f09493d1fbcd51` passed Required `30226763484` and PR #164 merged as `9703da845384423ad85883216bf8853642c21bcd`. Canary governance head `bacd3b880487c8c35d0e1230b956520cd201ad7c` passed Ownership `30226993622` and CI `30226993717` and merged as `91d96d8aa72b3851c4db89a71de9ea9722bcc63b`. Canary lifecycle head `2fef1da44c757911a00366fcb9c3c16e716e4192` passed Ownership `30241248116` and CI `30241248233` and merged as `66bdb1a9be9c229720a2e667c760bd56f24d40dd`.

The target feature changed exactly eleven intended paths and passed full Linux CTest plus Linux, macOS, Windows and Docker gates. Governance and lifecycle were documentation-only with clean path sets, `behind_by=0`, no comments, reviews or review threads, and expected-head merges.

OAM-053 does not claim complete wire compatibility for every client, account authorization, login or character-list correctness, gameplay packet correctness, session-race safety, economy or transaction safety, Redis/multichannel correctness, hostile-server client resilience, sustained capacity, denial-of-service resistance or production deployment safety.

# Current state

```text
Canary reconciliation base: 66bdb1a9be9c229720a2e667c760bd56f24d40dd
Otheryn target head after OAM-053: 9703da845384423ad85883216bf8853642c21bcd
OAM-001..OAM-053: feature/proof, governance and lifecycle complete
OAM-053 tasks: archived in Canary and Otheryn
OAM-054: NOT STARTED pending a fresh dependency-valid preflight
```

No OAM implementation task is active in this reconciliation record.

# Queue

| Package | Status | Next action |
|---|---|---|
| OAM-001..OAM-053 | completed | preserve durable evidence and nonclaims |
| OAM-054 | dependency-valid, not active | perform fresh live-state, open-PR, ownership and four-repository preflight for canonical `login-protocol`; select a bounded target-proof disposition |
| OAM-055+ | no unresolved canonical package currently identified | do not fabricate work; refresh the canonical registry after OAM-054 completion |

# Retained boundaries

- Canonical registry records remain the sole logical migration inventory; paths and PR history are discovery evidence only.
- `login-protocol` is now dependency-valid because `network-transport` is durably complete; it remains unselected until a fresh OAM-054 ownership and target-gap preflight merges.
- `physical-client-e2e` remains active under the Canary Universal E2E programme and is consumed through exact target-SHA validation, not migration.
- SEC-005 remains bounded evidence for its registered disposable authenticated-session assertions; it is not complete transport or login equivalence proof.
- OAM-051 completed only its selected Wheel safety and Bonus Promotion boundary; broader Wheel parity remains separately governed.
- Upstream Intelligence remains active under its own Canary programme; OAM-049 only excludes duplicating it in Otheryn.
- Canary `deployment-operations` remains laboratory/content-validation tooling; future Otheryn production deployment is separately PRS-owned.
- Completed package nonclaims remain in force; compaction does not upgrade static, unit, runtime or physical-client evidence.
