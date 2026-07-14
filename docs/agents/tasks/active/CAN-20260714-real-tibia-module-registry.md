---
task_id: CAN-20260714-real-tibia-module-registry
program_id: CAN-PROGRAM-REAL-TIBIA-PARITY
coordination_id: REAL-TIBIA-MODULE-REGISTRY
status: ready-for-review
agent: "GPT-5.6 Thinking"
branch: feat/real-tibia-module-registry
base_branch: main
created: 2026-07-14T11:40:00+02:00
updated: 2026-07-14T12:50:00+02:00
last_verified_commit: "3485b73b81464706629415be74088187d63f375d"
risk: medium
related_issue: ""
related_pr: "#324"
depends_on:
  - "merged Real Tibia parity governance PR #318"
  - "archived governance lifecycle PR #321"
blocks:
  - "scalable machine-readable module discovery and validation for future parity tasks"
owned_paths:
  exclusive:
    - docs/agents/real-tibia/**
    - tools/agents/real_tibia_registry.py
    - tools/agents/real_tibia_registry_lib.py
    - tools/agents/test_real_tibia_registry.py
    - .github/workflows/real-tibia-registry.yml
    - docs/agents/decisions/ADR-20260714-real-tibia-registry-as-code.md
    - docs/agents/tasks/active/CAN-20260714-real-tibia-module-registry.md
  shared:
    - docs/agents/README.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
    - docs/agents/programs/REAL_TIBIA_PARITY_PROGRAM.md
  read_only:
    - AGENTS.md
    - docs/agents/ACTIVE_WORK.md
    - docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md
    - docs/agents/REAL_TIBIA_PARITY_PLAYBOOK.md
    - docs/agents/REPOSITORY_MAP.md
    - docs/agents/KNOWN_RISKS.md
    - docs/agents/BUILD_TEST_MATRIX.md
    - docs/agents/CROSS_REPO_CONTRACTS.md
modules_touched:
  - Real Tibia registry-as-code
  - agent module discovery and dependency graph
  - parity evidence governance
reuses:
  - existing Real Tibia evidence registry and parity playbook
  - existing task/program records and ownership checker
  - existing deterministic Python agent-tooling conventions
  - existing generated-index policy
public_interfaces:
  - "python tools/agents/real_tibia_registry.py validate"
  - "python tools/agents/real_tibia_registry.py generate --check"
  - "python tools/agents/real_tibia_registry.py module <module-id>"
  - "python tools/agents/real_tibia_registry.py lookup-path <repository-path>"
  - "python tools/agents/real_tibia_registry.py affected --base <base> --head <head>"
  - "python tools/agents/real_tibia_registry.py stale"
cross_repo_tasks: []
---

# Goal

Deliver a professional registry-as-code foundation for Real Tibia modules: one independent record per module, formal schemas, deterministic generated indexes, dependency/path lookup, freshness reporting, reusable templates, ADR-backed policy and required CI validation.

# Acceptance criteria

- [x] Document taxonomy, maturity, source/baseline and generated-file policy.
- [x] Use one JSON-compatible YAML record per module to minimize conflicts.
- [x] Add JSON Schemas for module, category, source and baseline records.
- [x] Add a deterministic dependency-free validator/generator with module, path, affected-module and stale commands.
- [x] Add focused tests for schema/domain validation, generation drift, cycles, traversal, lookup, affected modules and freshness.
- [x] Add dedicated CI for compile, tests, schemas, registry validation, generated drift and CLI smoke.
- [x] Add module-program, audit, evidence-matrix, bounded-task and ADR templates.
- [x] Add ADR for registry-as-code, one-file-per-module and generated-index policy.
- [x] Bootstrap 18 major modules without copying gameplay content or claiming parity.
- [x] Integrate startup docs, module catalogue, changelog and global parity program.
- [x] Keep `ACTIVE_WORK.md` and gameplay/runtime/protocol/database/map/item/asset code unchanged.
- [x] Refresh the published branch onto current main `06f8ba4464d6a18ad48445737444bab5b3a2efcb` without losing current-main or registry changes.
- [x] Remove the temporary same-branch refresh workflow before readiness.
- [x] Review the exact intended 49-file scope and forbidden-path boundary.
- [ ] Verify final-head ownership, focused registry workflow, repository `Required` and review state.
- [ ] Mark PR #324 ready, squash-merge and archive this task separately.

# Delivered design

```text
docs/agents/real-tibia/
├── README.md, TAXONOMY.md, MATURITY_MODEL.md, SOURCE_POLICY.md
├── registry/{categories,sources,versions}.yaml
├── registry/modules/<module-id>.yaml
├── schemas/*.json
├── templates/*.md
└── generated/*.md

tools/agents/real_tibia_registry.py
tools/agents/real_tibia_registry_lib.py
tools/agents/test_real_tibia_registry.py
.github/workflows/real-tibia-registry.yml
```

Registry files use the YAML 1.2 JSON-compatible subset. Runtime validation uses only the Python standard library; CI installs `jsonschema` for formal Draft 2020-12 validation.

# Safety and proof boundaries

- Registry metadata is discovery and navigation, not gameplay evidence or edit authorization.
- Maturity dimensions do not imply full parity.
- External repositories and wiki/official sources remain read-only.
- Path patterns may overlap and only help discovery; active task ownership remains authoritative.
- Generated Markdown is derived and CI-checked.
- No production behavior, persistence schema, protocol, map, item, asset or client code is changed.

# Work log

## 2026-07-14T11:40:00+02:00

Created the task, branch and draft PR from main `0d1eb94c8e8e3033d95fd73f56711b830624540f`; no exclusive overlap was found.

## 2026-07-14T12:25:00+02:00

Implemented policy docs, source/category/version/module records, four schemas, five generated indexes, five templates, the ADR, validator/generator CLI/library, focused tests and dedicated workflow. Integrated README, changelog, catalogue and the global parity program.

## 2026-07-14T12:38:00+02:00

Full comparison exposed an unintended historical changelog deletion; the complete current-main inventory was restored. Main #326/#327 additions were preserved in shared files.

## 2026-07-14T12:47:00+02:00

A bounded temporary workflow rebuilt the branch as one commit on exact current main using force-with-lease against its own observed head. PR #324 became mergeable with base `06f8ba4464d6a18ad48445737444bab5b3a2efcb`. The workflow was then deleted; it is not part of the final scope.

# Validation and CI

| Commit | Check | Result | Evidence boundary |
|---|---|---|---|
| standalone registry tree | `py_compile`, focused unit tests, `validate`, `generate --check` | passed | Synthetic local tree only; not a local Canary checkout/build claim. |
| `935896606a81cceaa75934417fd33affaca54f32` | Real Tibia Module Registry `29324972108`, job `87059002227` | success | Compile, tests, formal schemas, domain validation, generated drift and CLI smoke. |
| `81b10f1737731d924cd2ad419df5b7c6ec64da34` | Registry `29325074733`; ownership `29325074722` | success | Exact-head focused validation and structured ownership. |
| `c9cf5251dc4c322fa06f152570d1a8cfc4abbb5b` | Registry `29325202821`; ownership `29325202682`; CI `29325202898`; Required `87059800947` | success | Full PR-triggered proof for implementation plus shared-doc integration. Build/Lua jobs were correctly path-skipped. |
| final refreshed head | all required workflows | pending | Must be green before readiness and merge. |

# Decisions

| Decision | Reason | Record |
|---|---|---|
| One record per module | Avoid a monolithic conflict hotspot. | ADR-20260714 |
| JSON-compatible YAML | Valid YAML plus deterministic dependency-free parsing. | ADR-20260714 |
| Multidimensional maturity | Existing code/test/protocol/runtime/E2E are separate proof levels. | `MATURITY_MODEL.md` |
| Generated indexes | Human discovery without duplicate manual state. | ADR-20260714 |
| Programs on demand | Avoid empty/speculative program files. | global parity program |

# Failed approaches and dead ends

- A guessed tree SHA commit failed with HTTP 422 and created no commit.
- The first shared changelog update accidentally omitted the bootstrap inventory; comparison caught it and it was restored.
- Content alignment alone did not clear GitHub's three-way merge conflict because the branch merge base remained older than shared lifecycle PRs; the bounded refresh solved this without editing another branch.
- Direct local GitHub DNS resolution was unavailable; no local repository fetch/build claim is made.

# Remaining work

1. Verify all final-head workflows and review state.
2. Mark #324 ready and squash-merge.
3. Archive this task and clear the global-program active row in a separate lifecycle PR.

# Handoff

Read this task, PR #324, the registry README/ADR, current open PRs and current main. Do not replace the registry with one monolithic file, copy wiki gameplay prose, manually edit generated indexes or treat module path matching as ownership.

# Completion

- Final status: ready-for-review pending final-head CI
- Feature PR: #324
- Feature merge: pending
- Archived at: pending
