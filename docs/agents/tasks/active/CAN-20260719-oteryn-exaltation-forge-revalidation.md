---
task_id: CAN-20260719-oteryn-exaltation-forge-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-020
status: target_merged_governance_reconciling
agent: "GPT-5.5 Thinking"
branch: docs/oam-020-exaltation-forge-revalidation
base_branch: main
created: 2026-07-19
updated: 2026-07-19
last_verified_commit: "c353b89b5a7f783cf4ee22fe1ba91850de837a68"
risk: high
related_issue: ""
related_pr: "598"
depends_on:
  - OAM-004 player-persistence foundation
  - OAM-006 protocol
blocks:
  - OAM-021
owned_paths:
  exclusive:
    - docs/agents/OTERYN_OAM_020_EXALTATION_FORGE_REVALIDATION.md
    - docs/agents/tasks/active/CAN-20260719-oteryn-exaltation-forge-revalidation.md
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/real-tibia/registry/modules/exaltation-forge.yaml
    - docs/agents/programs/EQUIPMENT_UPGRADE_PARITY_PROGRAM.md
    - docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_HANDOFF_2026-07-14.md
    - docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_VALIDATION.md
    - docs/agents/CROSS_REPO_CONTRACTS.md
    - src/creatures/players/**
    - src/game/functions/forge_*
    - src/config/**
    - src/lua/functions/creatures/player/**
    - data/libs/systems/exaltation_forge.lua
    - tests/**forge**
modules_touched:
  - exaltation-forge
reuses:
  - existing clean upstream-based Otheryn Forge core
  - merged Canary Forge policy/transaction/history/defaults/effects evidence
  - existing Otheryn CI and test infrastructure
public_interfaces:
  - existing Forge runtime and configuration surfaces only
cross_repo_tasks:
  - blakinio/Otheryn#44 merged as d59207d05ab6dd9450b05d0a6b4d9122fda60489
---

# Goal

Revalidate canonical OAM-020 `exaltation-forge`, adapt only the strongest coherent dependency-valid Forge corrections into Otheryn, prove the bounded target result on an exact head, then complete Canary governance, lifecycle archival and durable program reconciliation before OAM-021 starts.

# Final disposition

```text
exaltation-forge → ADAPT
```

`REUSE` was rejected because task-start Otheryn and fresh upstream lacked multiple merged legacy correctness repairs. A broad rebuild was rejected because the clean target/upstream Forge core remained usable and the reviewed legacy changes were bounded adaptations.

# Immutable task-start baselines

- Canary: `c353b89b5a7f783cf4ee22fe1ba91850de837a68`
- Otheryn: `63547f30fc21e495217b8a92fa44aaad2db188ef`
- fresh upstream comparison: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- previous OAM upstream pin: `691614c1a302aee776002ca3851eca399be1a82c`
- maintained OTClient: `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`

# Fresh preflight and ownership

- [x] Canary and Otheryn task-start heads independently verified.
- [x] Maintained OTClient and fresh upstream independently verified.
- [x] Durable OAM program, target architecture contract, registry, Forge parity program/handoff/validation and cross-repo contract read.
- [x] Active ownership reviewed; no exclusive Forge runtime/data/test writer found.
- [x] Later Canary PRs #599/#600 checked by actual changed paths; OTBM/E2E-only and non-overlapping.
- [x] Fresh target/upstream/legacy evidence reviewed before disposition.

Shared `MODULE_CATALOG.md` and `CHANGELOG.md` ownership was deliberately avoided. OAM-020 governance changes only its report and active task record.

# Accepted donor chain

- #89 — normal Transfer rules/cost/history;
- #110 — history item identity;
- #177 — Dust killer/party/cap behavior;
- #250 — server authority policies;
- #257 — transaction safety;
- #259 — live defaults;
- #262 — Premium Dust semantics;
- #267 — Forge effect correctness;
- #283 — history correctness.

No broad `player.cpp` or `protocolgame.cpp` copy was accepted.

Target-local build-contract adaptations registered five new helper headers in `vcproj/canary.vcxproj`, added PCH-safe fallback standard includes, and registered exact Forge tests in the target's current CMake layout instead of copying stale donor CMake files.

# Explicit exclusions

- F-014–F-019 bonus/result/protocol/maintained-client contract work;
- F-009/F-010 evidence-blocked rules;
- generic market/combat/item/persistence/protocol rewrites;
- maps, OTBM, `items.otb`, assets, schema and deployment;
- writes to maintained OTClient or upstream repositories;
- claims of exhaustive current Real Tibia Forge parity or physical-client Forge E2E closure.

# Target proof and merge

Target PR: `blakinio/Otheryn#44`

Accepted final head:

```text
f05787db7f165d0dae0584b3e06c6526f89a42cd
```

Final target scope: exactly 24 intended paths — 23 bounded Forge runtime/data/test/build paths plus one target-specific OAM-020 proof test. No temporary materializer workflow/script remained.

Exact-head evidence:

- autofix.ci #142 / `29701626292` — SUCCESS;
- Repository Audit #19 / `29701626282` — SUCCESS;
- CI #164 / `29701626343` — SUCCESS;
- Required #149 / `29701626255` — SUCCESS;
- Fast Checks — PASS;
- Lua Tests — PASS;
- Linux release compile and Canary/global runtime smoke — PASS;
- Linux debug compile/schema/CTest — PASS;
- macOS compile/runtime smoke — PASS;
- Windows CMake compile/runtime smoke — PASS;
- Windows Solution/MSBuild compile — PASS;
- Docker image build/validation — PASS.

Linux debug CTest:

```text
393/393 PASS
```

Focused target proof:

```text
Oam020ExaltationForgeAdaptTest: 2/2 PASS
```

Primary artifact:

```text
id: 8446751016
name: linux-debug-test-logs
digest: sha256:1bc0b22f42693c2eaa4404de0b4e66846d399a1046c1620254a493b9bcba5eef
```

Final target audit:

- comments: 0;
- reviews: 0;
- review threads: 0;
- target-main drift: none before merge;
- changed files: exactly 24 intended paths.

Expected-head squash merge:

```text
d59207d05ab6dd9450b05d0a6b4d9122fda60489
```

Post-merge Otheryn `main` is exactly one commit ahead of task-start baseline and the changed paths match the accepted scope.

# Materializer failure record

The temporary materializer failed closed several times before the accepted tree existed. The material failures were integration mechanics, not accepted Forge runtime failures:

- stale donor CMake layout conflict — replaced with exact deterministic target test registration;
- ignored tracked `vcproj/canary.vcxproj` required explicit force-staging;
- direct execution of the self-modifying script reached EOF after replacing itself — corrected by executing a stable temporary copy.

All nine donor patches subsequently applied cleanly. No failed materializer run produced the accepted target runtime tree. Temporary materializer paths were removed before final validation.

# Acceptance criteria

- [x] Dedicated Otheryn `dudantas/` branch created from exact task-start target SHA.
- [x] Exact donor-hunk/target-context review completed.
- [x] Target adaptation contains no unrelated paths and no broad legacy file copy.
- [x] Focused Forge regression proof covers the accepted adaptation.
- [x] Full applicable Otheryn validation passes on exact final target head.
- [x] Target changed-file, review/thread and main-drift audits are clean.
- [x] Otheryn target PR merged by expected head.
- [x] Canary governance report/task record reconciled to exact target proof.
- [ ] Canary governance exact final head passes ownership/CI and review gates.
- [ ] Governance PR merges by expected head.
- [ ] Separate authoritative active→archive lifecycle PR merges.
- [ ] Separate one-file durable OAM program reconciliation merges.
- [ ] OAM-021 remains not started until all preceding lifecycle/reconciliation steps complete.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19
head: 02a6578f0cd2e4672e8e71c142d892a03c53d41d
branch: docs/oam-020-exaltation-forge-revalidation
pr: 598
status: governance_reconciling
context_routes:
  - agent-governance
  - cpp-runtime
  - lua-data
  - cross-repo
owned_paths:
  - docs/agents/OTERYN_OAM_020_EXALTATION_FORGE_REVALIDATION.md
  - docs/agents/tasks/active/CAN-20260719-oteryn-exaltation-forge-revalidation.md
proven:
  - OAM-020 disposition is exaltation-forge ADAPT
  - target PR 44 final head f05787db7f165d0dae0584b3e06c6526f89a42cd changed exactly 24 intended paths
  - target exact-head autofix 29701626292 Repository Audit 29701626282 CI 29701626343 and Required 29701626255 succeeded
  - Linux debug CTest passed 393 of 393 tests
  - Oam020ExaltationForgeAdaptTest passed 2 of 2 focused cases
  - test artifact 8446751016 digest sha256:1bc0b22f42693c2eaa4404de0b4e66846d399a1046c1620254a493b9bcba5eef
  - target comments reviews and review threads were all zero
  - target main had no drift before expected-head merge
  - target PR 44 merged as d59207d05ab6dd9450b05d0a6b4d9122fda60489
  - Canary main advanced one unrelated OTBM E2E commit after task start without overlap with the two OAM-020 governance paths
derived:
  - the unrelated Canary main drift does not invalidate the OAM-020 target proof or governance scope because the changed paths do not overlap
  - OAM-021 remains blocked until governance merge lifecycle archive and durable program reconciliation all complete
unknown:
  - exact final Canary governance head and gate run ids after this reconciliation commit
  - whether Canary main will advance again before governance merge
conflicts: []
first_failure:
  marker: target-materializer-failed-closed
  evidence: early materializer attempts failed before an accepted target runtime commit; exact artifact-driven diagnosis identified target CMake integration then tracked vcproj staging and self-modifying runner execution issues, all corrected before final proof
rejected_hypotheses:
  - infer REUSE from upstream or target file presence
  - bulk-copy legacy player.cpp or protocolgame.cpp
  - absorb unresolved maintained-client Forge bonus/result work into OAM-020
  - implement F-009 or F-010 from memory or secondary unversioned summaries
changed_paths:
  - docs/agents/OTERYN_OAM_020_EXALTATION_FORGE_REVALIDATION.md
  - docs/agents/tasks/active/CAN-20260719-oteryn-exaltation-forge-revalidation.md
validation:
  - command: live GitHub head open-PR and task ownership preflight
    result: PASS
    evidence: exact task-start baselines and non-overlapping active ownership recorded
  - command: canonical dependency and source-evidence review
    result: PASS
    evidence: dependency-valid exaltation-forge selected and ADAPT disposition established from fresh evidence
  - command: exact target CI and CTest on f05787db7f165d0dae0584b3e06c6526f89a42cd
    result: PASS
    evidence: CI 29701626343 Required 29701626255 and 393 of 393 CTest passed with 2 of 2 focused OAM-020 proof cases
  - command: target changed-file review and review-thread audit
    result: PASS
    evidence: exactly 24 intended paths and zero comments reviews or review threads
  - command: expected-head target squash merge
    result: PASS
    evidence: PR 44 merged at expected head f05787db7f165d0dae0584b3e06c6526f89a42cd as d59207d05ab6dd9450b05d0a6b4d9122fda60489
blockers:
  - Canary governance PR 598 must pass exact-final-head ownership and CI then merge before lifecycle archive
next_action: Validate Canary governance PR 598 on its exact final reconciliation head. Keep the diff limited to the two governance paths. If ownership and CI pass and review plus fresh main-drift audits are clean, squash-merge by expected head. Then create the separate authoritative active-to-archive lifecycle PR. Do not start OAM-021.
```
