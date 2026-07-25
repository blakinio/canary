---
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
name: Oteryn Architecture and Migration
status: active
owner: oteryn-architecture-migration-agent
created: 2026-07-15T15:28:18+02:00
updated: 2026-07-25T15:18:00+02:00
last_verified_commit: "fd338ccc7864e572f8bed8e38144dc53e096293a"
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
| OAM-001..OAM-040 | architecture, foundations and canonical packages through `otbm-tooling → DO_NOT_MIGRATE` | completed; exact feature/lifecycle references remain authoritative in archived task records and Git history |
| OAM-041 | `spawns → REUSE` | target `de061aa6c75114192f1ef6b33f7b4857e502936c`; feature `0dc3fa9d663af47f8808d2457c8108a63294c7c4`; lifecycle `55f9e46ab0804ec2c7b58cfffc772a243234c956` |
| OAM-042 | `npcs → REUSE` | target `0d01f077f80c2d4cd3d4231d2ffb9416874ba54e`; Otheryn lifecycle `3a37f3d5e4c01ddf4469f1c71461c40ca749142f`; feature `2f42260258f84b323bcd2a74d6107b10d4e01142`; Canary lifecycle `cec180bf0fdcd894d71c8219ffab83f3d07a51b7` |
| OAM-043 | `quests → ADAPT` | target `6512d78004ae2540784b3e67592a92a903554cf6`; Otheryn lifecycle `3f3c15917610e45430aa3902d110806dd25e10a8`; feature `6e55eab72b6f7b164bb38ba2e08fa1a80cf5f8e5`; Canary lifecycle `6e223c142f34285b98ea70d79131c79b1680e2d0` |
| OAM-044 | `protocol-compatibility → REUSE` | target `5c8f48e2a7cb7f841cfb6614e8e804245f17c0ca`; Otheryn lifecycle `e1eed52119ba21a29cb29cbac0793ed2a2b9d0c6`; feature `766aa0198884243c8d9641e5a1e92cd605735500`; Canary lifecycle `87c2204a822ffcdc40f7279f629b35ceec6c2556` |
| OAM-045 | `protocol-session-handoff → ADAPT` | target `597ba62c558ed4e35db38502903ae83e0b2921ec`; Otheryn lifecycle `e8f683e61427e9967cbc180b837220d4b7487d85`; feature `8b24b6603c29250587949a0e1600aa981795f133`; Canary lifecycle `14e3d7b9b21e8fee443d4bc8ebc107dad7c4bdb6` |
| OAM-046 | `configuration → ADAPT` | target `e05109ac6b98fe6761ed7ed7e933b0610b219911`; Otheryn lifecycle `415f559f829c83d79d9c609e7f421d2449e59d74`; governance `a49f3a3d5fc7bcbca823ec7acf9c3e9a822f1e2e`; Canary lifecycle `fd338ccc7864e572f8bed8e38144dc53e096293a` |

Detailed package narratives, exact task-start baselines, gate runs, rejected hypotheses and nonclaims remain authoritative in archived Canary/Otheryn task records and package revalidation reports. This document preserves sequencing and the exact recent merge chain without duplicating those records.

# OAM-046 durable completion

Final disposition:

```text
configuration ADAPT
```

OAM-046 retained the typed configuration architecture and corrected one package-owned state defect: every successful `OTCRFeatures` load appended into retained enabled/disabled vectors instead of replacing the current snapshot. Otheryn now parses local vectors, applies fallback enabled IDs `101`, `102`, `103`, `118` with no disabled IDs when the table is omitted, and replaces both retained vectors after each successful load. Failed Lua-file execution still preserves the prior snapshot.

Focused target fixtures proved custom snapshot replacement, stale-ID removal, omitted-table fallback and repeated-fallback idempotency. Otheryn feature head `f9aa4261302eb3a42b7b9d9d5bb8e907f5cde7f8` passed Autofix `30151341764`, CI `30151341862` and Required `30151341775`, then merged as `e05109ac6b98fe6761ed7ed7e933b0610b219911`. Otheryn lifecycle merged as `415f559f829c83d79d9c609e7f421d2449e59d74` after Required `30158852271` and a clean audit.

Canary governance head `15087861b9d879342769fbf33be2f5245d5b7f02` passed Agent Task Ownership `30159032723` and full final-gate CI `30159032840`, then merged as `a49f3a3d5fc7bcbca823ec7acf9c3e9a822f1e2e`. Canary lifecycle head `cdc96455350de37bfac3c5ac50ef5f3108512a44` passed Ownership `30159205977` and CI `30159206069`, then merged as `fd338ccc7864e572f8bed8e38144dc53e096293a`.

OAM-046 does not claim exhaustive key/default correspondence, concurrent full-map reload atomicity, production configuration or secret correctness, controlled-feature behavior, protocol/client correctness, physical-client parity or full production readiness.

# Current state

```text
Canary reconciliation base: fd338ccc7864e572f8bed8e38144dc53e096293a
Otheryn target head after OAM-046: 415f559f829c83d79d9c609e7f421d2449e59d74
reviewed upstream: 7323503b3dc61ed86bf1f04a611b2d0aec64b35a
OAM-001..OAM-046: feature/proof and lifecycle complete
OAM-046 task: archived in Canary and Otheryn
OAM-047: NOT STARTED pending a fresh dependency-valid preflight
```

No OAM implementation task is active in this reconciliation record.

# Queue

| Package | Status | Next action |
|---|---|---|
| OAM-001..OAM-046 | completed | preserve durable evidence and nonclaims |
| OAM-047+ | planned, not active | perform fresh live-state, open-PR, ownership, dependency and exact target/upstream/legacy preflight; select exactly one dependency-valid canonical package |

# Retained boundaries

- Canonical registry records remain the sole logical migration inventory; paths and PR history are discovery evidence only.
- `network-transport` remains blocked by overlapping authenticated transport work in Canary PR #514; `login-protocol` remains dependency-blocked behind `network-transport`.
- `physical-client-e2e`, `upstream-intelligence` and `wheel-of-destiny` remain separately governed active programme surfaces until a fresh bounded OAM package proves a target disposition.
- `deployment-operations` and `gameplay-analytics` remain broader platform surfaces and require explicit target-ownership proof before any migration disposition.
- Completed package nonclaims in archived records remain in force; this compaction does not upgrade static, unit, runtime or physical-client evidence.
