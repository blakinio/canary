---
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
name: Oteryn Architecture and Migration
status: active
owner: oteryn-architecture-migration-agent
created: 2026-07-15T15:28:18+02:00
updated: 2026-07-26T17:15:00+02:00
last_verified_commit: "a3a0c647fd6fdac44fcfb449f570ee75bd95f6df"
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
- Upstream, OTClient and donor repositories remain read-only unless separately authorized.
- One bounded OAM package/task/branch/PR at a time with exact SHAs.
- Never infer `REUSE` from file presence, matching blobs or compilation alone.
- Never bulk-copy legacy Player/IOLoginData or the repository.
- Preserve OAM-004 persistence gaps: player SQL state and later KV durability are not atomic.
- Feature/proof merge must be followed by separate lifecycle archive, Canary governance/lifecycle and durable program reconciliation before the next OAM starts.
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

Detailed package narratives, exact task-start baselines, gate runs, rejected hypotheses and nonclaims remain authoritative in archived task records and package revalidation reports.

# OAM-051 durable completion

Final disposition:

```text
wheel-of-destiny ADAPT
```

OAM-051 completed in two bounded phases. OAM-051A integrated server-side Wheel allocation, point-accounting, gem/state and malformed-current-protocol safety without importing current balance, combat effects, spells, stances, geometry, Task Shop or client work. OAM-051B integrated only one Hunting Task Shop Bonus Promotion offer using SQL-backed PlayerStorage key `1000006`, exact maintained-client packet widths/statuses and same-player-SQL-transaction persistence with Hunting Task Points; Wheel KV remained a separate post-commit domain.

OAM-051A Otheryn feature PR #115 merged as `47863ce250bce73c1b9af3077f82e9bf6e99e3d1`, lifecycle PR #118 merged as `bd0b58a362d89e449a6863ba299d1c50ad4e6685`, and Canary phase-A governance merged as `d8416553be77d4999d81afcce2399a37a25337a6`. OAM-051B Canary preflight head `f7ba253dc078b9ed65801d1df36599e181ecdb81` passed Ownership `30200151129` and CI `30200151201` and merged as `9e865b68b9197b28450002412ca1720683cf1f64`. Otheryn final feature head `a507abc5d6b9aa3158f9b009a715d5aee0b4c43c` passed Repository Audit `30206237389`, autofix `30206237391`, full CI `30206237518` and Required `30206237406`; feature PR #128 merged as `546eac0a00ec620e7293d0548e30662024464084`. Otheryn lifecycle PR #134 passed Required `30207104087` and merged as `db10096f0ebb484f05883dbde4dd895744fbe8c6`. Canary final governance head `d277ab5b0fa09876c91135db4ec72e193dfe9e96` passed Ownership `30207339099` and CI `30207339168` and merged as `a3a0c647fd6fdac44fcfb449f570ee75bd95f6df`.

OAM-051 does not claim physical maintained-client Taskboard interaction, a complete Taskboard UI, other Taskboard offers, complete Wheel parity, current balance/effect/spell/stance/geometry behavior, schema migration, deployment or production readiness.

# Current state

```text
Canary reconciliation base: a3a0c647fd6fdac44fcfb449f570ee75bd95f6df
Otheryn target head after OAM-051: db10096f0ebb484f05883dbde4dd895744fbe8c6
OAM-001..OAM-051: feature/proof, governance and lifecycle complete
OAM-051 tasks: archived in Canary and Otheryn
OAM-052: NOT STARTED pending a fresh dependency-valid preflight
```

No OAM implementation task is active in this reconciliation record.

# Queue

| Package | Status | Next action |
|---|---|---|
| OAM-001..OAM-051 | completed | preserve durable evidence and nonclaims |
| OAM-052+ | planned, not active | perform fresh live-state, open-PR, ownership, dependency and exact target/upstream/legacy preflight; select exactly one dependency-valid canonical package |

# Retained boundaries

- Canonical registry records remain the sole logical migration inventory; paths and PR history are discovery evidence only.
- `network-transport` remains blocked by overlapping authenticated transport work in Canary PR #514; `login-protocol` remains dependency-blocked behind `network-transport`.
- `physical-client-e2e` remains active under the Canary Universal E2E programme and is consumed through exact target-SHA validation, not migration.
- PR #925's original incomplete baseline remains historical evidence; the merged retention repair enables fresh future attempts but does not rewrite history or prove general stability.
- OAM-051 completed only its selected Wheel safety and Bonus Promotion boundary; broader Wheel parity remains separately governed and must not be silently reopened by OAM-052.
- Upstream Intelligence remains active under its own Canary programme; OAM-049 only excludes duplicating it in Otheryn.
- `deployment-operations` requires completed build-system and explicit target-ownership proof.
- Completed package nonclaims remain in force; compaction does not upgrade static, unit, runtime or physical-client evidence.
