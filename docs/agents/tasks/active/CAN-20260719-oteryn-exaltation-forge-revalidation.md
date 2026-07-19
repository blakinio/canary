---
task_id: CAN-20260719-oteryn-exaltation-forge-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-020
status: implementing
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
  - blakinio/Otheryn#44 on dudantas/oam-020-exaltation-forge-adapt
---

# Goal

Revalidate canonical OAM-020 `exaltation-forge`, adapt only the strongest coherent dependency-valid Forge corrections into Otheryn, prove the bounded target result on an exact head, then complete Canary governance, lifecycle archival and durable program reconciliation before OAM-021 starts.

# Task-start disposition

```text
exaltation-forge → ADAPT
```

`REUSE` is rejected because task-start Otheryn and fresh upstream lack multiple merged legacy correctness repairs. A broad rebuild is rejected because the clean target/upstream Forge core remains usable and the reviewed legacy changes are bounded adaptations.

# Immutable task-start baselines

- Canary: `c353b89b5a7f783cf4ee22fe1ba91850de837a68`
- Otheryn: `63547f30fc21e495217b8a92fa44aaad2db188ef`
- fresh upstream comparison: `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`
- previous OAM upstream pin: `691614c1a302aee776002ca3851eca399be1a82c`
- maintained OTClient: `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`

# Fresh preflight

- [x] Canary `main` independently verified.
- [x] Otheryn `main` independently verified.
- [x] Maintained OTClient head independently verified.
- [x] Fresh upstream head independently verified; one-commit drift is dispatcher-only and non-overlapping.
- [x] All live/open Canary and Otheryn PRs reviewed.
- [x] Active task ownership reviewed; no exclusive Forge runtime/data/test writer found.
- [x] Durable OAM program and target architecture contract read.
- [x] Canonical registry dependency gate reviewed.
- [x] Local Otheryn `AGENTS.md` read; no nearer nested `AGENTS.md` exists at checked `src/`, `src/creatures/players/`, `data/` or `tests/` paths.
- [x] Forge parity program, handoff and validation evidence read.
- [x] Cross-repository contract registry reviewed.
- [x] Fresh target/upstream/legacy evidence reviewed before disposition.

# Ownership audit

Open Canary PRs at task start:

- #559 — MyAAC documentation closeout; no overlap;
- #526 — evidence-only security audit; source/data paths are read-only evidence;
- #514 — authenticated-session security validation; `protocolgame.*` is read-only and Forge paths are not owned;
- #479 — archive-only lifecycle cleanup.

Otheryn had no open PR at task start.

No active task owns Forge production paths exclusively. Shared `MODULE_CATALOG.md` and `CHANGELOG.md` are intentionally excluded from the start-up scope while unrelated security work is open.

Fresh later Canary PRs #599 and #600 are OTBM/E2E work. Their live changed paths do not overlap the OAM-020 governance files or Forge target runtime/data/test boundary.

# Reviewed donor evidence

The exact target adaptation must remain narrower than legacy whole files. Reviewed merged donor candidates are:

- #89 normal Transfer rules/cost/history;
- #110 history item identity;
- #177 Dust killer/party/cap behavior;
- #250 server authority policies;
- #257 transaction safety;
- #259 live defaults;
- #262 Premium Dust semantics;
- #267 Forge effect correctness;
- #283 history correctness.

Fresh target evidence confirms missing/different bounded surfaces including Forge policy helpers, transaction/effect helpers, Forge config defaults, Fiendish default and Forge history item IDs. Direct target-context inspection also confirms the task-start Player Forge flow still has the pre-transaction mutation ordering, older Transfer tier-cost semantics and stale Momentum/Transcendence gating addressed by the accepted donor chain.

Target-local architecture review additionally requires two bounded adaptations not present in the legacy donor commits themselves:

- register the five newly introduced Forge/config helper headers in tracked `vcproj/canary.vcxproj`, as required by the target `AGENTS.md` build-entry policy;
- guard donor standard-library includes with `#ifndef USE_PRECOMPILED_HEADERS` because `cstdint`, `functional`, `utility` and `vector` are already provided by target `src/pch.hpp`.

These are build-contract adaptations only. They do not broaden Forge runtime behavior.

# Explicit exclusions

- F-014–F-019 bonus/result/protocol/maintained-client contract work;
- F-009/F-010 rules lacking pinned authoritative evidence;
- broad `player.cpp` or `protocolgame.cpp` copy;
- generic market/combat/item/persistence/protocol rewrites;
- maps, OTBM, `items.otb`, assets, schema and deployment;
- writes to `blakinio/otclient` or upstream repositories.

# Target delivery rules

- target branch must use the Otheryn-required `dudantas/` prefix;
- no direct write to Otheryn `main`;
- materialize only exact Forge-specific hunks/helpers after target-context review;
- add focused target tests for every adapted boundary;
- register new C++ sources/headers in every maintained build entry point when required;
- inspect full changed-file list and diff before readiness;
- run exact-head CI and applicable full/focused tests;
- audit comments/reviews/threads and target-main drift before expected-head merge.

# Acceptance criteria

- [x] Dedicated Otheryn `dudantas/` branch created from exact task-start target SHA.
- [x] Exact donor-hunk/target-context review completed for every selected production mutation boundary.
- [ ] Target adaptation contains no unrelated paths and no broad legacy file copy.
- [ ] Focused Forge regression tests cover the accepted adaptation.
- [ ] Applicable full Otheryn validation passes on the exact final target head.
- [ ] Target changed-file, review/thread and main-drift audits are clean.
- [ ] Otheryn target PR merges by expected head.
- [ ] Canary governance report/task record reconciled to exact target proof.
- [ ] Canary governance exact final head passes ownership/CI and review gates.
- [ ] Governance PR merges by expected head.
- [ ] Separate authoritative active→archive lifecycle PR merges.
- [ ] Separate one-file durable OAM program reconciliation merges.
- [ ] OAM-021 remains not started until all preceding lifecycle/reconciliation steps complete.

# Target materialization checkpoint

Target PR: `blakinio/Otheryn#44`

Target branch: `dudantas/oam-020-exaltation-forge-adapt`

Current target helper head at this checkpoint: `7a3fdf87a9909dbd040f0d0e6a5e852c37943bd5`

The temporary fail-closed materializer is pinned to legacy `c353b89b5a7f783cf4ee22fe1ba91850de837a68`, applies only explicit production/test paths from the nine accepted merge commits using three-way context checks, validates an explicit final-path allowlist, applies target PCH and Visual Studio project-registration requirements, and self-removes its workflow on success. A temporary no-op script stub is retained only to make stale queued runs harmless and must be deleted before final target validation.

Observed materializer failures:

- stale early run `29700037539` — failed inside the materialization step before any accepted target commit;
- exact observable run `29700919724` / run #15 — failed inside the materialization step before any accepted target commit.

Neither failure changed the accepted target tree. The first diagnostic wrapper did not persist a usable failure log, so the workflow has been changed to always upload the complete materializer log as artifact and fail only after artifact publication. The next controlled run must use that artifact to identify the first conflicting donor hunk rather than guessing.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-19
head: 10a46ab94f48bd98576c23d3772f6277f0638026
branch: docs/oam-020-exaltation-forge-revalidation
pr: 598
status: implementing
context_routes:
  - agent-governance
  - cpp-runtime
  - lua-data
  - cross-repo
owned_paths:
  - docs/agents/OTERYN_OAM_020_EXALTATION_FORGE_REVALIDATION.md
  - docs/agents/tasks/active/CAN-20260719-oteryn-exaltation-forge-revalidation.md
proven:
  - Canary task-start main is c353b89b5a7f783cf4ee22fe1ba91850de837a68
  - Otheryn task-start main is 63547f30fc21e495217b8a92fa44aaad2db188ef
  - maintained OTClient remains 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
  - fresh upstream is 71a0f92b4da3f550b292fa7536a0e35c2769f1ae and its drift from 691614c1a302aee776002ca3851eca399be1a82c is dispatcher-only
  - no active exclusive Forge writer exists in live Canary/Otheryn PR/task ownership
  - canonical exaltation-forge dependencies player-persistence and protocol are completed
  - task-start target/upstream lack multiple reviewed legacy Forge helper/default/history repairs
  - whole-module REUSE is rejected and bounded ADAPT is selected
  - unresolved F-014 through F-019 protocol/client work and F-009/F-010 evidence-blocked rules are excluded
  - target branch dudantas/oam-020-exaltation-forge-adapt was created from exact baseline 63547f30fc21e495217b8a92fa44aaad2db188ef
  - target draft PR 44 is open and remains based on exact task-start Otheryn main
  - selected materialization scope is restricted to explicit Forge production/test paths from donor PRs 89 110 177 250 257 259 262 267 and 283
  - target-local build contract requires vcproj registration and PCH-guard adaptation for newly added helper headers
unknown:
  - first exact conflicting donor hunk from the failed materializer runs
  - accepted post-materialization target head
  - exact final target changed-file set after helper removal
  - exact focused/full target test results and artifacts
  - exact target CI run IDs on the accepted final head
conflicts: []
first_failure:
  marker: target-materializer-failed
  evidence: runs 29700037539 and 29700919724 failed inside the materialization step before any accepted target commit; artifact-based failure capture is now enabled for the next controlled run
rejected_hypotheses:
  - infer REUSE from upstream/target file presence
  - bulk-copy legacy player.cpp or protocolgame.cpp
  - absorb unresolved maintained-client Forge bonus/result work into OAM-020
  - implement F-009/F-010 from memory or secondary unversioned summaries
changed_paths:
  - docs/agents/OTERYN_OAM_020_EXALTATION_FORGE_REVALIDATION.md
  - docs/agents/tasks/active/CAN-20260719-oteryn-exaltation-forge-revalidation.md
validation:
  - command: live GitHub head/open-PR/task ownership preflight
    result: PASS
    evidence: exact baselines and non-overlapping active ownership recorded above
  - command: canonical dependency and source-evidence review
    result: PASS
    evidence: dependency-valid exaltation-forge selected and ADAPT disposition established from fresh target/upstream/legacy evidence
  - command: target branch and draft PR creation
    result: PASS
    evidence: Otheryn PR 44 uses dudantas/oam-020-exaltation-forge-adapt from exact target base 63547f30fc21e495217b8a92fa44aaad2db188ef
  - command: function-level donor and target-context review
    result: PASS
    evidence: exact donor merge/path set is bounded and task-start target retains the reviewed Forge correctness gaps without OAM-019 overlap
  - command: target materializer runs 29700037539 and 29700919724
    result: FAIL
    evidence: both runs failed closed inside the materialization step and produced no accepted target implementation commit
blockers:
  - exact first donor conflict must be identified from the artifact-enabled materializer run before target implementation can proceed
next_action: Run the artifact-enabled OAM-020 materializer on current target helper head 7a3fdf87a9909dbd040f0d0e6a5e852c37943bd5. Fetch the complete oam-020-materializer-log artifact. Repair only the first exact conflicting donor hunk or target-context mismatch, rerun, then inspect the post-materialization changed-file allowlist before any target CI or readiness claim.
```
