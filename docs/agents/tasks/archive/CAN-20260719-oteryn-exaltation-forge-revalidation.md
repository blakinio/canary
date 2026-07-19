---
task_id: CAN-20260719-oteryn-exaltation-forge-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-020
status: completed
agent: "GPT-5.5 Thinking"
branch: docs/oam-020-exaltation-forge-lifecycle
base_branch: main
created: 2026-07-19
updated: 2026-07-19
completed: 2026-07-19
last_verified_commit: "2b6ae86539640dfc52323e9d5abbde31d6610c5f"
risk: high
related_pr: "598"
depends_on:
  - OAM-004 player-persistence foundation
  - OAM-006 protocol
blocks:
  - OAM-021
modules_touched:
  - exaltation-forge
---

# Goal

Revalidate canonical OAM-020 `exaltation-forge`, adapt only the strongest coherent dependency-valid Forge corrections into Otheryn, and complete the bounded migration-governance lifecycle.

# Final disposition

```text
exaltation-forge → ADAPT
```

# Immutable task-start baselines

- Canary: `c353b89b5a7f783cf4ee22fe1ba91850de837a68`
- Otheryn: `63547f30fc21e495217b8a92fa44aaad2db188ef`
- fresh upstream comparison: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- previous upstream pin: `691614c1a302aee776002ca3851eca399be1a82c`
- OTClient: `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`

# Accepted donor chain

The accepted coherent adaptation is the bounded result of merged Canary PRs #89, #110, #177, #250, #257, #259, #262, #267 and #283: Transfer rules/cost/history, history item identity, Dust killer/party/cap handling, server authority, transaction rollback, live defaults, exact Premium semantics, Forge effect correctness and history correctness.

No whole-file legacy `player.cpp` or `protocolgame.cpp` import was accepted. Target-local build adaptation registered the new headers in the maintained Visual Studio project, preserved target PCH policy and registered exact Forge tests in the current target CMake layout.

# Exact target proof

```text
Otheryn PR #44 final head: f05787db7f165d0dae0584b3e06c6526f89a42cd
target squash merge: d59207d05ab6dd9450b05d0a6b4d9122fda60489
autofix.ci #142 / 29701626292: SUCCESS
Repository Audit #19 / 29701626282: SUCCESS
CI #164 / 29701626343: SUCCESS
Required #149 / 29701626255: SUCCESS
full Linux debug CTest: 393/393 PASS
focused Oam020ExaltationForgeAdaptTest: 2/2 PASS
artifact: 8446751016
digest: sha256:1bc0b22f42693c2eaa4404de0b4e66846d399a1046c1620254a493b9bcba5eef
```

The target PR changed exactly 24 intended paths: 23 bounded Forge runtime/data/test/build paths plus one OAM-020 target proof test. Temporary materializer paths were absent. Comments, reviews and review threads were empty. Otheryn `main` had no drift before expected-head merge.

# Canary governance proof

```text
governance PR #598 final head: 607b8a7af2f9025993964f858498a70e4bc29a38
Agent Task Ownership #2708 / 29702328659: SUCCESS
full final-gate CI #3855 / 29702328760: SUCCESS
governance changed paths: exactly 2
comments: 0
reviews: 0
review threads: 0
governance squash merge: 2b6ae86539640dfc52323e9d5abbde31d6610c5f
```

The final gate forced the full matrix despite governance-only scope. Fast Checks and Lua Tests passed; Linux debug including schema import and tests passed; Linux release, macOS, Windows CMake, Windows Solution/MSBuild and Docker image validation passed. The merge was accepted only after the exact-head CI completed successfully.

Canary `main` had one unrelated OTBM/E2E commit of drift from the task-start baseline before governance merge. Its actual changed paths did not overlap the two OAM-020 governance paths.

# Reviewed exclusions

OAM-020 does not claim exhaustive current Real Tibia Forge parity or physical-client Forge E2E closure. It does not migrate unresolved F-014 through F-019 bonus/result/protocol/client work, evidence-blocked F-009/F-010 rules, generic market/combat/item/persistence/protocol rewrites, maps, OTBM, `items.otb`, assets, schema or deployment, and it makes no maintained-OTClient or upstream write.

# Lifecycle state

The target and governance stages are merged. This authoritative lifecycle PR owns only the active-task deletion and archive addition.

Durable one-file program reconciliation remains pending after this lifecycle merge. OAM-021 must remain not started until that reconciliation is merged.
