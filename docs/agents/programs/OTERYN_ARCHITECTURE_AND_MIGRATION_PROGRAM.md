---
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
name: Oteryn Architecture and Migration
status: active
owner: oteryn-architecture-migration-agent
created: 2026-07-15T15:28:18+02:00
updated: 2026-07-25T20:34:00+02:00
last_verified_commit: "62c3124fa2331e58ad675e059f8e33f87cb15ad7"
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
| OAM-047 | `lua-runtime → ADAPT` | target `5b3bee0dd6eedf8c2f9578c686ca85c0fde519cf`; Otheryn lifecycle `68e2b233b02356a79a03422ed51d757b85915bc5`; governance `06f3f78724f8f74b704272b9b97837b2ba1819d7`; Canary lifecycle `62c3124fa2331e58ad675e059f8e33f87cb15ad7` |

Detailed package narratives, exact task-start baselines, gate runs, rejected hypotheses and nonclaims remain authoritative in archived Canary/Otheryn task records and package revalidation reports.

# OAM-047 durable completion

Final disposition:

```text
lua-runtime ADAPT
```

OAM-047 preserved the shared Lua architecture and corrected one lifecycle defect: attached child `LuaScriptInterface` objects retained pointers and registry references belonging to a main Lua state after `LuaEnvironment::reInitState()` closed and replaced it. Otheryn now inventories only live children attached to the old shared state, closes their event tables before `lua_close()`, creates the replacement state and rebinds the same children. Dormant, destroyed and independently overridden interfaces are excluded.

Focused fixtures cover active children, stale IDs, new event registration, dormant/destroyed interfaces and the shared test interface. Final target head `a7349190a51d627e4668af56912337ff8cadec46` passed Autofix `30167797667`, CI `30167797744` and Required `30167797642`, then merged as `5b3bee0dd6eedf8c2f9578c686ca85c0fde519cf`. Target lifecycle merged as `68e2b233b02356a79a03422ed51d757b85915bc5`. Canary governance head `4ed59d4d11bd8d9f82f95c25ddb50a08f6103c7b` passed Ownership `30169261944` and CI `30169262061`, merged as `06f3f78724f8f74b704272b9b97837b2ba1819d7`, and Canary lifecycle merged as `62c3124fa2331e58ad675e059f8e33f87cb15ad7` after Ownership `30169502984` and CI `30169503091`.

OAM-047 does not claim complete production reload ordering, callback timing, concurrent reload safety, exhaustive userdata or wrapper lifetime safety, feature-specific script reload, physical-client behavior, protocol/client compatibility, production gameplay parity or full server readiness.

# Current state

```text
Canary reconciliation base: 62c3124fa2331e58ad675e059f8e33f87cb15ad7
Otheryn target head after OAM-047: 68e2b233b02356a79a03422ed51d757b85915bc5
reviewed upstream for OAM-047: 7323503b3dc61ed86bf1f04a611b2d0aec64b35a
OAM-001..OAM-047: feature/proof and lifecycle complete
OAM-047 task: archived in Canary and Otheryn
OAM-048: NOT STARTED pending a fresh dependency-valid preflight
```

No OAM implementation task is active in this reconciliation record.

# Queue

| Package | Status | Next action |
|---|---|---|
| OAM-001..OAM-047 | completed | preserve durable evidence and nonclaims |
| OAM-048+ | planned, not active | perform fresh live-state, open-PR, ownership, dependency and exact target/upstream/legacy preflight; select exactly one dependency-valid canonical package |

# Retained boundaries

- Canonical registry records remain the sole logical migration inventory; paths and PR history are discovery evidence only.
- `network-transport` remains blocked by overlapping authenticated transport work in Canary PR #514; `login-protocol` remains dependency-blocked behind `network-transport`.
- `physical-client-e2e`, `upstream-intelligence` and `wheel-of-destiny` remain separately governed programme surfaces until a fresh bounded OAM package proves a target disposition.
- `deployment-operations` and `gameplay-analytics` require explicit target-ownership proof before any migration disposition.
- Completed package nonclaims in archived records remain in force; this compaction does not upgrade static, unit, runtime or physical-client evidence.
