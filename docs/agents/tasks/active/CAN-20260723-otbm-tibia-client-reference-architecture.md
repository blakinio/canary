---
task_id: CAN-20260723-otbm-tibia-client-reference-architecture
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: OTBM-TIBIA-CLIENT-REFERENCE
status: active
agent: GPT-5.6 Thinking
branch: docs/otbm-tibia-client-reference-20260723
base_branch: main
created: 2026-07-23T10:00:00+02:00
updated: 2026-07-23T12:05:00+02:00
last_verified_commit: "024694857957b62d8ecc7645a599447f4abe1d6d"
risk: low
related_issue: ""
related_pr: "762"
depends_on:
  - docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md
  - docs/agents/REAL_TIBIA_PARITY_PLAYBOOK.md
  - docs/agents/programs/REAL_TIBIA_PARITY_PROGRAM.md
  - docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md
  - Unified OTBM World Index and existing OTBM QA/repair stack
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260723-otbm-tibia-client-reference-architecture.md
    - docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md
    - docs/ai-agent/OTBM_TIBIA_CLIENT_REFERENCE_ARCHITECTURE.md
  shared:
    - docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md
    - docs/agents/programs/REAL_TIBIA_PARITY_PROGRAM.md
    - docs/agents/real-tibia/registry/modules/otbm-tooling.yaml
    - docs/agents/CHANGELOG.md
  read_only:
    - AGENTS.md
    - docs/agents/REPOSITORY_MAP.md
    - docs/agents/CONTEXT_ROUTING.md
    - beats-dh/Beats-Assets-Editor at ed827be34c279d1279ad3dde3af434b148ac05c7
modules_touched:
  - OTBM analysis tooling
  - Real Tibia parity governance
  - official-client reference evidence
reuses:
  - canary-otbm-world-index-v1
  - canary-appearances-index-v1
  - canary-client-assets-index-v1
  - canary-otbm-asset-compatibility-v1
  - Quest Map Validator
  - OTBM spawn/boss/NPC validator
  - OTBM Geometry Audit
  - OTBM Reachability
  - OTBM Critical Access Integrity
  - Semantic OTBM Diff
  - bounded repair/materialization pipelines
  - release provenance/change risk/evidence gateway
public_interfaces:
  - planned Tibia client reference evidence contracts and programme queue
cross_repo_tasks: []
---

# Goal

Define a concrete, durable architecture and phased implementation plan for ingesting exact user-supplied Tibia 15.x client reference files as read-only evidence and correlating them with the existing canonical OTBM/Canary analysis stack without creating a second OTBM parser, pathfinder, renderer, script resolver, mutation engine or E2E platform.

# Scope

This task is documentation and architecture only. It does not implement parsers, mutate `.otbm`, `items.otb`, client assets or datapack/runtime code, and does not commit proprietary Tibia client files.

The architecture covers:

- exact client-package provenance and SHA-256 pinning;
- `staticdata` old/new schema evidence;
- `staticmapdata` house-layout evidence;
- proficiency reference evidence and item/appearance bindings;
- reuse of existing appearances/assets indexes;
- optional minimap/reference evidence boundaries;
- parity consumers for houses, monsters/bosses/quests and proficiency;
- deterministic drift between two client-reference snapshots;
- adoption routing into existing bounded OTBM repair/materialization or non-OTBM subsystem tasks;
- explicit licensing boundary for `beats-dh/Beats-Assets-Editor` as research/reference, not copied implementation.

# Acceptance criteria

- [x] Add a durable programme with bounded queue entries and exact next action.
- [x] Add a technical architecture defining contracts, provenance, joins, failure states and non-goals.
- [x] Update the OTBM real-Tibia registry record without creating a duplicate tooling module.
- [x] Ensure the plan does not authorize raw client files, `.otbm`, `.widx`, `items.otb` or generated large artifacts in Git.
- [x] Ensure `staticmapdata` is treated as bounded house-layout/reference evidence, not a full OTBM source or automatic map generator.
- [x] Ensure minimap evidence cannot replace canonical World Index/Reachability mechanics evidence.
- [x] Ensure all proposed mutation/adoption routes require existing review/approval and post-mutation validation contracts.
- [x] Include a bounded kickoff prompt for the implementation agent in the programme handoff.
- [x] Regenerate and validate the derived Real Tibia registry indexes after the `otbm-tooling` registry change.
- [x] Add only still-required narrow discovery mirrors to `MODULE_CATALOG.md`, `OTS_OTBM_TOOLING_ROADMAP.md`, `REAL_TIBIA_EVIDENCE_SOURCES.md`, `REAL_TIBIA_PARITY_PROGRAM.md` and `CHANGELOG.md` after re-reading current main.
- [ ] Run repository-required documentation/registry validation and verify PR #762 CI on its immutable final head.

# Evidence baseline

## PROVEN

- The task branch started from `blakinio/canary:main` at `8837f35eb43da6a3ed7efc6a1e8f3bca19342d2e`.
- Current `main` was re-fetched at `f9fc157dad3668b5051761264ebeecf5bdf1f055`; changes since the previous preflight are QA-006/QA-007, OAM-038 and lifecycle-only paths and do not overlap this task's TCR-000 paths.
- PR #759 was merged as `cc376677178e7de3551675bc17639b1fe0422c6f`; its QA-006/QA-007 implementation paths do not overlap TCR-000 architecture/governance paths.
- Draft PR #762 owns this task.
- Searches of current `MODULE_CATALOG.md`, repository code and `tools/ai-agent` found no existing equivalent canonical Tibia client-reference package/manifest interface; TCR-000 remains a governance extension of `otbm-tooling`, not a duplicate tooling module.
- `beats-dh/Beats-Assets-Editor` baseline for the design is pinned to `ed827be34c279d1279ad3dde3af434b148ac05c7` and is read-only format/interoperability research.
- Existing Canary OTBM tooling already owns canonical OTBM parsing/indexing, appearances/assets indexing, script resolution, reachability, semantic diff, geometry, QA evidence and bounded mutation pipelines.
- Shared discovery mirrors are limited to narrow TCR-000 entries in the module catalogue, OTBM tooling roadmap, Real Tibia evidence registry, Real Tibia parity programme and agent changelog.
- Derived registry output changed only `MODULE_DEPENDENCIES.md`, `MODULE_PATH_INDEX.md` and `STALE_MODULES.md`; fresh Real Tibia Module Registry CI passed `generate --check` on head `024694857957b62d8ecc7645a599447f4abe1d6d`.
- One bounded local clone attempt failed with `Could not resolve host: github.com`; no local validation result is claimed. GitHub Actions is the authoritative execution environment for this task.

## UNKNOWN / deferred

- Exact Tibia client build/version carried by future user-supplied files must be recorded per ingestion and never inferred from filename alone.
- Exact filenames/packaging of proficiency data may vary by client build and must be discovered by a bounded implementation task rather than hard-coded by TCR-000.
- Whether every proposed client-reference field has stable semantic meaning across builds remains implementation evidence, not assumed architecture truth.
- Immutable-final-head CI and review-thread state remain pending.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: "2026-07-23T12:05:00+02:00"
head: "024694857957b62d8ecc7645a599447f4abe1d6d"
branch: "docs/otbm-tibia-client-reference-20260723"
pr: "762"
status: "validating"
next_action: "Validate this corrected checkpoint on fresh PR CI, then audit the complete diff and review/ownership state before applying ci:final-gate and creating the immutable final checkpoint commit."
context_routes:
  - "agent-governance"
  - "otbm"
  - "real-tibia-parity"
owned_paths:
  - "docs/agents/tasks/active/CAN-20260723-otbm-tibia-client-reference-architecture.md"
  - "docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md"
  - "docs/ai-agent/OTBM_TIBIA_CLIENT_REFERENCE_ARCHITECTURE.md"
  - "docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md"
  - "docs/agents/MODULE_CATALOG.md"
  - "docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md"
  - "docs/agents/programs/REAL_TIBIA_PARITY_PROGRAM.md"
  - "docs/agents/real-tibia/registry/modules/otbm-tooling.yaml"
  - "docs/agents/CHANGELOG.md"
proven:
  - "TCR-000 is architecture/governance only and adds no parser or runtime/map mutation implementation."
  - "Current main f9fc157dad3668b5051761264ebeecf5bdf1f055 introduces no changed-path overlap with TCR-000."
  - "PR 759 merged as cc376677178e7de3551675bc17639b1fe0422c6f and does not overlap TCR-000 paths."
  - "Real Tibia Module Registry run 29997172825 passed on head 024694857957b62d8ecc7645a599447f4abe1d6d."
  - "Repository CI run 29997172908 passed on head 024694857957b62d8ecc7645a599447f4abe1d6d."
  - "Upstream Intelligence run 29997172716 passed on head 024694857957b62d8ecc7645a599447f4abe1d6d."
  - "Generated registry diffs are limited to one dependency edge, three path-index rows and otbm-tooling freshness."
derived:
  - "The architecture remains compatible with current main because all post-baseline changes are outside the TCR-000 owned/shared paths and preserve the canonical OTBM reuse boundaries."
unknown:
  - "AI Agent Tools and OTBM Map Tools results for the prior candidate head were still running at the last checkpoint."
  - "Fresh Agent Task Ownership result after converting the checkpoint to the required fenced YAML v1 contract is pending."
  - "Immutable-final-head full CI and unresolved review-thread state are pending."
conflicts: []
rejected_hypotheses:
  - "Rejected: PR 759 overlaps TCR-000; changed-path comparison shows separate QA-006/QA-007 implementation paths."
  - "Rejected: create a second canonical client-reference or OTBM analysis stack; current repository discovery shows the existing OTBM stack must be extended and reused."
changed_paths:
  - "docs/agents/CHANGELOG.md"
  - "docs/agents/MODULE_CATALOG.md"
  - "docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md"
  - "docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md"
  - "docs/agents/programs/REAL_TIBIA_PARITY_PROGRAM.md"
  - "docs/agents/real-tibia/generated/MODULE_DEPENDENCIES.md"
  - "docs/agents/real-tibia/generated/MODULE_PATH_INDEX.md"
  - "docs/agents/real-tibia/generated/STALE_MODULES.md"
  - "docs/agents/real-tibia/registry/modules/otbm-tooling.yaml"
  - "docs/agents/tasks/active/CAN-20260723-otbm-tibia-client-reference-architecture.md"
  - "docs/ai-agent/OTBM_TIBIA_CLIENT_REFERENCE_ARCHITECTURE.md"
  - "docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md"
blockers:
  - "Fresh Agent Task Ownership must pass with the corrected checkpoint contract."
  - "All required exact-final-head checks and review/ownership gates must be green before merge."
first_failure:
  marker: "Agent Task Ownership run 29997172655 / Validate changed active task checkpoints"
  evidence: "The task used prose after the checkpoint heading instead of the required fenced YAML v1 schema, and related_pr was encoded as #762 instead of 762."
validation:
  - command: "python -m py_compile tools/agents/real_tibia_registry.py tools/agents/real_tibia_registry_lib.py tools/agents/test_real_tibia_registry.py"
    result: "PASS"
    evidence: "Real Tibia Module Registry run 29997172825"
  - command: "python -m unittest -v tools/agents/test_real_tibia_registry.py"
    result: "PASS"
    evidence: "Real Tibia Module Registry run 29997172825"
  - command: "python tools/agents/real_tibia_registry.py validate"
    result: "PASS"
    evidence: "Real Tibia Module Registry run 29997172825"
  - command: "python tools/agents/real_tibia_registry.py generate --check"
    result: "PASS"
    evidence: "Real Tibia Module Registry run 29997172825"
  - command: "python tools/agents/task_lifecycle.py validate-changed --changed-files-file artifacts/agent-coordination/CHANGED_FILES.txt --current-pr 762"
    result: "FAIL"
    evidence: "Agent Task Ownership run 29997172655 diagnosed the prior invalid checkpoint contract; this commit corrects it."
  - command: "GitHub Actions workflow CI"
    result: "PASS"
    evidence: "run 29997172908"
  - command: "GitHub Actions workflow Upstream Intelligence"
    result: "PASS"
    evidence: "run 29997172716"
```
