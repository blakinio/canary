---
task_id: CAN-20260729-game-catalog-loot-integrity
program_id: CAN-PROGRAM-GAME-CATALOG-COMPLETENESS
coordination_id: "OTS-20260728-game-catalog-v1"
status: in-progress
agent: "chatgpt"
branch: feat/CAN-20260729-game-catalog-loot-integrity
base_branch: main
created: 2026-07-29T17:26:42Z
updated: 2026-07-29T17:30:37Z
last_verified_commit: "d8e3aeafe93d44f2949ec25f84293b943606389b"
risk: high
related_issue: ""
related_pr: 1010
depends_on:
  - CAN-20260729-game-catalog-metadata-evidence
blocks:
  - Game Catalog staging snapshot
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260729-game-catalog-loot-integrity.md
    - src/game/catalog/game_catalog_exporter.cpp
    - tests/unit/game/catalog/game_catalog_test.cpp
    - tests/game_catalog/test_default_loot_integrity.py
  shared:
    - docs/agents/programs/GAME_CATALOG_COMPLETENESS_PROGRAM.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CROSS_REPO_CONTRACTS.md
    - docs/contracts/GAME_CATALOG_EXPORT_CONTRACT.md
    - docs/systems/GAME_CATALOG_EXPORTER.md
    - docs/agents/CHANGELOG.md
    - .github/workflows/game-catalog.yml
  read_only:
    - data-otservbr-global/monster/**
    - data/items/**
    - data/libs/functions/functions.lua
    - data/libs/functions/monstertype.lua
    - src/items/**
    - src/creatures/monsters/**
modules_touched:
  - oteryn.game-catalog runtime item and loot collection
reuses:
  - Game Catalog exporter from PR #991
  - tools/game-catalog/validate_snapshot.py
  - .github/workflows/game-catalog.yml
public_interfaces:
  - oteryn.game-catalog creature_loot endpoint and chance semantics
cross_repo_tasks: []
---

# Goal

Resolve the repository-default Game Catalog loot-integrity blocker without dropping relations, clamping runtime values, inventing item facts, or activating production.

# Acceptance criteria

- [ ] Reproduce the exact default-datapack dangling-endpoint and invalid-probability findings from a final runtime export.
- [ ] Prove whether loot-referenced appearance items with runtime IDs and names but no `items.xml` `loaded` flag belong to the final `Items` registry contract.
- [ ] Export every valid runtime loot target as an item entity and leave no dangling loot endpoints.
- [ ] Prove the runtime meaning of configured loot chance, `MAX_LOOTCHANCE`, schedule/rate scaling, and the dynamic factor.
- [ ] Preserve configured loot thresholds exactly; do not silently drop, clamp, normalize, or rewrite source loot records.
- [ ] If schema 1.1 cannot represent the proven runtime chance semantics, record an explicit versioned producer/consumer follow-up instead of weakening validation.
- [ ] Keep deterministic ordering, atomic publication, SHA-256 sidecars, and export-only database/network isolation.
- [ ] Add focused regression tests and run the applicable exact-head Game Catalog and repository CI.
- [ ] Update program, module, contract, architecture, changelog, and cross-repository impact or explicitly record no change.
- [ ] Do not import or activate a staging or production snapshot.
- [ ] Satisfy the autonomous merge gate.

# Confirmed context

- PR #1005 merged the reviewed schema 1.1 metadata seed as `9926b69728ed2945a5c957047447b537dcec4dbe`.
- Lifecycle PRs #1008 and #1009 archived stale schema/export-architecture ownership before this task began.
- Current `main` was verified at `ac407413d64882ab0968436dccda86b6e2b9b199`.
- A full repository-default runtime export fails closed with 53 dangling loot relations covering 25 unique item IDs and 92 invalid-probability relations.
- `Items::loadFromProtobuf` assigns appearance-backed runtime IDs and names without setting the XML-specific `loaded` flag; `Items::parseItemNode` sets `loaded`.
- The exporter currently requires `item.loaded`, while runtime monster loot may resolve items through the final name-to-ID registry populated from appearances.
- Runtime loot compares `getLootRandom()` against `chance * dynamicFactor`; the default schedule rate is 100 and the dynamic factor ranges from 0.95 through 1.05.
- Default datapack source includes configured chance values above the profile denominator, including deliberate repeated quest/boss patterns; those values must not be guessed into corrected probabilities.

# Ownership and overlap check

- Active ownership was validated after lifecycle PRs #1008 and #1009 merged: 33 active task records, no conflict.
- The previously owning schema task is archived.
- Source loot, item definitions, runtime Lua, and monster registries are read-only evidence in this task.
- No production paths, secrets, maps, binary appearances, or deployment state are owned.

# Current state

The endpoint and chance findings have different causes and must remain separate. The endpoint hypothesis is testable inside the existing producer: appearance-backed runtime item records are currently excluded by an XML-only flag. The chance findings expose a possible contract mismatch: schema 1.1 models a bounded probability fraction, while runtime stores a threshold that is modified by live rate and random dynamic factors.

# Plan

1. Add focused tests for appearance-backed item inclusion and exact raw loot threshold preservation.
2. Change only final-registry item collection if the endpoint hypothesis is proven.
3. Run a full default-datapack export and verify the endpoint finding count reaches zero.
4. Add a deterministic evidence test for source chance ranges and pin the runtime formula.
5. Decide whether existing schema semantics are sufficient; if not, create a separate synchronized producer/consumer contract task.
6. Run exact-head checks, update the checkpoint, merge, and archive this bounded task.

# Work log

## 2026-07-29T17:26:42Z

- Changed: created this bounded task after lifecycle cleanup.
- Learned: appearance loading and XML item enrichment use distinct flags; loot chance is a runtime threshold with live modifiers, not safely reducible by clamping to the current manifest denominator.
- Failed/blocked: full default-datapack publication remains blocked by both categories of findings.
- Result: implementation may proceed only through focused tests and preserved runtime evidence; production remains excluded.

## 2026-07-29T17:30:37Z

- Changed: published the ownership/evidence checkpoint and opened draft PR #1010.
- Validated: local ownership accepted 34 active task records before publication.
- Result: the bounded implementation branch is established; focused tests are next.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Keep datapack loot source read-only | No reviewed evidence authorizes rewriting 92 thresholds or 25 item identities. | none |
| Split endpoint repair from chance-contract evolution | One is a registry collection defect; the other may require a versioned cross-repository interface. | pending evidence |
| Preserve raw configured thresholds | Runtime consumes the configured values with dynamic/rate modifiers. | none |

# Validation and CI

Never write `passed` without verification on the stated commit.

# Remaining work

1. Prove appearance-backed endpoint inclusion with a focused unit test.
2. Prove and document chance representation compatibility or create the synchronized follow-up contract task.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-29T17:34:55Z
head: a083041e4a3ea45359bd4ba28a3332f4ea23db88
branch: feat/CAN-20260729-game-catalog-loot-integrity
pr: 1010
status: validating
context_routes:
  - agent-governance
  - cpp-runtime
  - lua-data
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260729-game-catalog-loot-integrity.md
  - src/game/catalog/game_catalog_exporter.cpp
  - tests/unit/game/catalog/game_catalog_test.cpp
  - tests/game_catalog/test_default_loot_integrity.py
  - .github/workflows/game-catalog.yml
proven:
  - A baseline default runtime export reports 53 dangling relations for 25 unique item IDs.
  - A baseline default runtime export reports 92 chance values above the declared denominator.
  - Appearance loading assigns final runtime item IDs and names without setting the XML-specific loaded flag.
  - The implementation head includes appearance-backed items and preserves configured loot thresholds exactly.
derived:
  - Removing the XML-only loaded filter should resolve all appearance-backed loot endpoints without source data rewrites.
  - Schema 1.1 cannot publish the 92 proven runtime thresholds because its probability validator rejects numerator values above denominator.
unknown:
  - Exact versioned representation required for modifier-dependent runtime loot thresholds.
conflicts:
  - Runtime compares a dynamically modified threshold, while schema 1.1 requires a bounded static probability fraction.
first_failure:
  marker: agent-task-checkpoint-shape
  evidence: Agent Task Ownership run 30475914811 rejected nine missing required checkpoint fields.
rejected_hypotheses:
  - Drop appearance-backed relations: every relation endpoint must exist and runtime already resolves these item IDs.
  - Clamp thresholds to the denominator: this would change configured runtime evidence and hide modifier semantics.
  - Increase one universal denominator: this would misrepresent ordinary thresholds under the default runtime roll scale.
changed_paths:
  - .github/workflows/game-catalog.yml
  - docs/agents/MODULE_CATALOG.md
  - docs/agents/programs/GAME_CATALOG_COMPLETENESS_PROGRAM.md
  - docs/agents/tasks/active/CAN-20260729-game-catalog-loot-integrity.md
  - src/game/catalog/game_catalog_exporter.cpp
  - tests/game_catalog/test_default_loot_integrity.py
  - tests/unit/game/catalog/game_catalog_test.cpp
validation:
  - command: python3 -m unittest discover -s tests/game_catalog -p test_*.py -v
    result: PASS
    evidence: 15 focused tests passed, including the two new runtime/source evidence tests.
  - command: python3 tools/agents/task_ownership.py
    result: PASS
    evidence: 34 active task records validated locally.
  - command: Agent Task Ownership 30475914811
    result: FAIL
    evidence: The implementation was accepted, but the task checkpoint omitted required schema fields.
blockers:
  - Exact-head C++ compilation and default-datapack runtime proof are still running.
  - Schema 1.1 probability compatibility requires a separate synchronized producer/consumer contract.
next_action: publish the checkpoint-shape correction, require rerun ownership success, then inspect exact-head Game Catalog compilation and default-datapack endpoint evidence.
```
