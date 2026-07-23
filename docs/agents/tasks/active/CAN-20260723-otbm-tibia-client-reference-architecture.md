---
task_id: CAN-20260723-otbm-tibia-client-reference-architecture
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: OTBM-TIBIA-CLIENT-REFERENCE
status: review
agent: GPT-5.6 Thinking
branch: docs/otbm-tibia-client-reference-20260723
base_branch: main
created: 2026-07-23T10:00:00+02:00
updated: 2026-07-23T12:30:00+02:00
last_verified_commit: "59ef2007fe58635f9188dc2431159509d1099f2e"
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
  - OTBM Region and Quest Certification
  - OTBM Continuous Assurance Gate
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
- reuse of existing canonical appearances/assets evidence;
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
- [ ] Verify PR #762 required CI on the immutable final head and merge under repository policy.

# Evidence baseline

## PROVEN

- The task branch started from `blakinio/canary:main` at `8837f35eb43da6a3ed7efc6a1e8f3bca19342d2e`.
- Current `main` was re-fetched at `57e26e3a22db90b41a005a467c2f2411e0e1039b`. Changes after the original base include OAM/lifecycle documentation and merged OTBM QA-006/QA-007; no post-base change creates a competing client-reference parser, OTBM parser, World Index, pathfinder, renderer or Physical E2E platform.
- PR #759 merged as `cc376677178e7de3551675bc17639b1fe0422c6f`. Its QA-006 certification and QA-007 continuous-assurance layers are downstream evidence composition and remain compatible with TCR's existing QA/certification/E2E reuse boundary.
- Draft PR #768 now has additive changes to the two TCR shared paths `docs/agents/MODULE_CATALOG.md` and `docs/agents/CHANGELOG.md`. Ownership remains `shared`; a coordination comment records merge order #762 first and refresh/reapply #768 afterward so both discovery entries are retained.
- Draft PR #762 owns this task and remains mergeable before final-head validation.
- Searches of current `MODULE_CATALOG.md`, repository code and `tools/ai-agent` found no existing equivalent canonical Tibia client-reference package/manifest interface; TCR-000 remains a governance extension of `otbm-tooling`, not a duplicate tooling module.
- `beats-dh/Beats-Assets-Editor` baseline for the design is pinned to `ed827be34c279d1279ad3dde3af434b148ac05c7` and is read-only format/interoperability research.
- Existing Canary OTBM tooling already owns canonical OTBM parsing/indexing, appearances/assets indexing, script resolution, reachability, semantic diff, geometry, QA evidence and bounded mutation pipelines.
- Shared discovery mirrors are limited to narrow TCR-000 entries in the module catalogue, OTBM tooling roadmap, Real Tibia evidence registry, Real Tibia parity programme and agent changelog.
- Derived registry output changed only `MODULE_DEPENDENCIES.md`, `MODULE_PATH_INDEX.md` and `STALE_MODULES.md`; current candidate-head Real Tibia Module Registry CI passes `generate --check`.
- Candidate head `59ef2007fe58635f9188dc2431159509d1099f2e` passed Real Tibia Module Registry, Agent Task Ownership, OTBM Map Tools, repository CI and Upstream Intelligence.
- Review-thread inspection returned zero unresolved inline review threads and zero submitted reviews before the final checkpoint commit.
- The `ci:final-gate` label was applied before this final checkpoint commit as required by repository policy.
- One bounded local clone attempt failed with `Could not resolve host: github.com`; no local validation result is claimed. GitHub Actions is the authoritative execution environment for this task.

## UNKNOWN / deferred

- Exact Tibia client build/version carried by future user-supplied files must be recorded per ingestion and never inferred from filename alone.
- Exact filenames/packaging of proficiency data may vary by client build and must be discovered by a bounded implementation task rather than hard-coded by TCR-000.
- Whether every proposed client-reference field has stable semantic meaning across builds remains implementation evidence, not assumed architecture truth.
- The immutable final commit SHA and the CI run IDs triggered by that commit cannot be self-recorded inside the same commit; repository lifecycle/archive handling must record the exact final feature head, final-head CI and squash-merge SHA after merge.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: "2026-07-23T12:30:00+02:00"
head: "59ef2007fe58635f9188dc2431159509d1099f2e"
branch: "docs/otbm-tibia-client-reference-20260723"
pr: "762"
status: "validating"
next_action: "Make no further commits. Require the ci:final-gate workflows on the exact final PR head to finish green, recheck review threads and mergeability, mark PR 762 ready, squash-merge it, then archive the task through the separate lifecycle flow before starting TCR-001 on a new task/branch/PR."
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
  - "TCR-000 is architecture/governance only and adds no TCR-001/TCR-002/TCR-003 parser or runtime/map mutation implementation."
  - "Current main 57e26e3a22db90b41a005a467c2f2411e0e1039b introduces no exclusive-path ownership conflict with TCR-000."
  - "Merged PR 759 adds downstream QA-006/QA-007 evidence composition and does not duplicate TCR-owned parsing/indexing surfaces."
  - "Real Tibia Module Registry run 29997673612 passed on candidate head 59ef2007fe58635f9188dc2431159509d1099f2e."
  - "Agent Task Ownership run 29997673549 passed both changed-checkpoint validation and full ownership-index validation on candidate head 59ef2007fe58635f9188dc2431159509d1099f2e."
  - "OTBM Map Tools run 29997673662 passed on candidate head 59ef2007fe58635f9188dc2431159509d1099f2e."
  - "Repository CI run 29997674124 passed with Required success on candidate head 59ef2007fe58635f9188dc2431159509d1099f2e."
  - "Upstream Intelligence run 29997673528 passed on candidate head 59ef2007fe58635f9188dc2431159509d1099f2e."
  - "AI Agent Tools run 29997473114 passed on the preceding candidate head ac547147bfaa3d58b65307c394d48121979266e4; exact-final-head final-gate validation remains authoritative."
  - "Generated registry diffs are limited to one dependency edge, three path-index rows and otbm-tooling freshness."
  - "Inline review-thread inspection returned zero threads and review-submission inspection returned zero reviews before the final checkpoint."
  - "ci:final-gate was applied to PR 762 before the final checkpoint commit."
derived:
  - "The architecture remains compatible with current main because post-base OTBM QA additions consume existing evidence and do not replace or weaken the canonical TCR reuse boundaries."
  - "PR 768 is a non-exclusive shared-document coordination overlap rather than an ownership conflict; preserving both additive discovery entries requires explicit merge ordering."
unknown:
  - "Exact-final-head ci:final-gate run IDs and results are pending and must be recorded by the post-merge lifecycle/archive update."
  - "Exact squash-merge SHA is pending and must be recorded by the post-merge lifecycle/archive update."
conflicts:
  - "Draft PR 768 touches shared MODULE_CATALOG.md and CHANGELOG.md. Coordination is resolved as PR 762 first, then refresh/reapply PR 768 against updated main; a PR 768 conversation comment records this ordering."
rejected_hypotheses:
  - "Rejected: merged PR 759 overlaps TCR-000 implementation ownership; it adds downstream QA-006/QA-007 evidence composition only."
  - "Rejected: create a second canonical client-reference or OTBM analysis stack; current repository discovery shows the existing OTBM stack must be extended and reused."
  - "Rejected: staticmapdata.object_id can be treated as OTBM/server itemId; exact mapping is unproven and the namespace remains separate."
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
  - "All required ci:final-gate checks on the exact immutable final head must be green before readiness/merge."
  - "If PR 768 merges first or changes shared-document state before PR 762 merges, re-evaluate mergeability without committing past the immutable final-head policy; otherwise preserve the recorded #762-first ordering."
first_failure:
  marker: "Agent Task Ownership integration failures on heads 368ee3bbc42d48276761db056e5dd8e2ec11afed and ac547147bfaa3d58b65307c394d48121979266e4"
  evidence: "The first failure was stale generated registry state plus a missing fenced checkpoint contract. After adding fenced YAML, the second ownership failure was exact: record under tasks/active has non-active status 'active'. Generated indexes, checkpoint schema, related_pr normalization and frontmatter status were corrected; candidate-head ownership run 29997673549 is green."
validation:
  - command: "python -m py_compile tools/agents/real_tibia_registry.py tools/agents/real_tibia_registry_lib.py tools/agents/test_real_tibia_registry.py"
    result: "PASS"
    evidence: "Real Tibia Module Registry run 29997673612"
  - command: "python -m unittest -v tools/agents/test_real_tibia_registry.py"
    result: "PASS"
    evidence: "Real Tibia Module Registry run 29997673612"
  - command: "python tools/agents/real_tibia_registry.py validate"
    result: "PASS"
    evidence: "Real Tibia Module Registry run 29997673612"
  - command: "python tools/agents/real_tibia_registry.py generate --check"
    result: "PASS"
    evidence: "Real Tibia Module Registry run 29997673612"
  - command: "python tools/agents/task_lifecycle.py validate-changed --changed-files-file artifacts/agent-coordination/CHANGED_FILES.txt --current-pr 762"
    result: "PASS"
    evidence: "Agent Task Ownership run 29997673549"
  - command: "GitHub Actions workflow Agent Task Ownership"
    result: "PASS"
    evidence: "run 29997673549; changed checkpoint and full ownership index both succeeded"
  - command: "GitHub Actions workflow OTBM Map Tools"
    result: "PASS"
    evidence: "run 29997673662"
  - command: "GitHub Actions workflow CI"
    result: "PASS"
    evidence: "run 29997674124; Required succeeded"
  - command: "GitHub Actions workflow Upstream Intelligence"
    result: "PASS"
    evidence: "run 29997673528"
  - command: "GitHub Actions workflow AI Agent Tools"
    result: "PASS"
    evidence: "run 29997473114 on preceding candidate head; exact-final-head final-gate run remains required"
```
