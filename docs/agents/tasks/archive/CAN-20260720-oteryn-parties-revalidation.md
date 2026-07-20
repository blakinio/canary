---
task_id: CAN-20260720-oteryn-parties-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-023
status: completed
agent: "GPT-5.5 Thinking"
branch: docs/oam-023-parties-lifecycle
base_branch: main
created: 2026-07-20
updated: 2026-07-20
completed: 2026-07-20
last_verified_commit: "e78d927e54d965d742fe762e86c9ea454d068c4a"
risk: medium
related_pr: "616"
depends_on:
  - OAM-005 character-lifecycle
blocks:
  - OAM-024
modules_touched:
  - parties
---

# Goal

Revalidate canonical OAM-023 `parties`, classify the smallest dependency-valid clean-target disposition from current evidence, deliver only the bounded target proof required by that disposition, and complete the migration-governance lifecycle without absorbing separately owned client/protocol/Wheel/E2E work.

# Final disposition

```text
parties → REUSE
```

# Immutable task-start baselines

- Canary: `0a39a0f76d5f811098dfaa7be9deea40347279d5`
- Otheryn: `50dfa248251f245f5519495a4fbd430b6814ffe4`
- fresh upstream Canary: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- maintained OTClient: `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`

# Accepted reuse boundary

Canonical `parties` is bounded to `src/creatures/players/grouping/party.*` and depends only on completed OAM-005 `character-lifecycle`. Exact target/upstream/legacy blob identity was supporting evidence only. Semantic review of Party lifecycle/state/shared-experience fail-closed behavior and relevant legacy-history audits found no stronger independent legacy donor for canonical `party.*`.

Party chat transport, protocol compatibility, maintained-client behavior, generic combat correctness, vocation/Wheel correctness, guild lifecycle, generic persistence redesign and physical-client Party E2E remain outside this package.

# Exact target proof

```text
Otheryn PR #47 final head: c3ff8bb09b736ec835ce1f49ee0d96b8e208ea88
target squash merge: bcc3e9f7e3e704f3c012bda8693648d52741630f
autofix.ci #147 / 29728346604: SUCCESS
CI #172 / 29728346757: SUCCESS
Required #154 / 29728346586: SUCCESS
Linux debug CTest: 403/403 PASS
focused Oam023PartiesReuseTest: 3/3 PASS
test-log artifact: 8455540885
artifact digest: sha256:8c3868b1047057d8419194ce7a555566b8db7dd32024f1ecb1c2cdec1424938b
```

The target PR changed exactly three proof-only paths and no production runtime or maintained OTClient path. Comments, reviews and review threads were empty; Otheryn `main` had no task-start drift before expected-head squash merge.

# Canary governance proof

```text
governance PR #616 final head: d11f692a23e6b185de9bbe94390c4c76c0b3c47b
Agent Task Ownership #2780 / 29729424947: SUCCESS
final-gate CI #3932 / 29729430140: SUCCESS
governance changed paths: exactly 2
comments: 0
reviews: 0
review threads: 0
governance squash merge: e78d927e54d965d742fe762e86c9ea454d068c4a
```

Canary `main` advanced during OAM-023 through independent OTBM/E2E work and its lifecycle archive. Both drift audits were non-overlapping with OAM-023 governance paths and canonical `party.*`; expected-head governance merge remained conflict-free.

# Reviewed exclusions

OAM-023 does not claim party chat/channel transport, protocol packet compatibility, maintained OTClient behavior, exhaustive shared-experience formula parity, generic combat correctness, vocation/Wheel correctness, guild lifecycle, generic persistence redesign, OAM-004 SQL/KV atomicity, physical-client Party E2E closure, or map/OTBM/`items.otb`/asset/schema/deployment changes.

# Lifecycle state

The target and governance stages are merged. This authoritative lifecycle PR owns only the active-task deletion and archive addition. Durable one-file program reconciliation remains pending after this lifecycle merge. OAM-024 must remain NOT STARTED until that reconciliation is merged.
