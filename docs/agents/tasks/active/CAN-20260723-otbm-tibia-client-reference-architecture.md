---
task_id: CAN-20260723-otbm-tibia-client-reference-architecture
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: OTBM-TIBIA-CLIENT-REFERENCE
status: review
agent: GPT-5.6 Thinking
branch: docs/otbm-tibia-client-reference-20260723
base_branch: main
created: 2026-07-23T10:00:00+02:00
updated: 2026-07-23T14:46:31+02:00
last_verified_commit: "b67d2f267f062dfb41dc5cc20e56a2dea012f6dc"
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

Define a durable architecture and phased implementation plan for ingesting exact user-supplied Tibia 15.x client reference files as read-only evidence and correlating them with the existing canonical OTBM/Canary analysis stack without creating a second OTBM parser, pathfinder, renderer, script resolver, mutation engine or E2E platform.

# Scope

Documentation and architecture only. No parser implementation, `.otbm`, `items.otb`, client-asset or datapack/runtime mutation, and no proprietary Tibia client files committed.

# Acceptance criteria

- [x] Add a durable programme with bounded queue entries and exact next action.
- [x] Add a technical architecture defining contracts, provenance, joins, failure states and non-goals.
- [x] Update the OTBM Real Tibia registry record without creating a duplicate tooling module.
- [x] Keep raw client files, `.otbm`, `.widx`, `items.otb` and generated large artifacts out of Git.
- [x] Treat `staticmapdata` as bounded house-layout/reference evidence, not a full OTBM source or automatic map generator.
- [x] Keep minimap evidence subordinate to canonical World Index/Reachability mechanics evidence.
- [x] Route proposed mutation/adoption through existing review/approval and post-mutation validation contracts.
- [x] Include a bounded kickoff prompt for the implementation agent in the programme handoff.
- [x] Regenerate and validate derived Real Tibia registry indexes after the `otbm-tooling` registry change.
- [ ] Add the still-required narrow `CHANGELOG.md` discovery mirror; the live PR changed-file list currently excludes this file.
- [ ] Verify PR #762 required CI on the immutable final head and merge under repository policy.

# Evidence baseline

## PROVEN

- TCR-000 is architecture/governance only and adds no TCR-001/TCR-002/TCR-003 parser or runtime/map mutation implementation.
- PR #762 is open and draft on branch `docs/otbm-tibia-client-reference-20260723`.
- The branch was replayed cleanly on `main` commit `54ce97b3bcaac8c2e1a0d4cc6162a6ff975bbee9` as head `b67d2f267f062dfb41dc5cc20e56a2dea012f6dc`.
- Current `main` then advanced to `115f3ac2fffc36bb4e415c2a6fb45908d9538ba3` through PR #796, which changed only `docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md`; PR #762 remains mergeable.
- Live PR #762 has exactly 11 changed files and does not include `docs/agents/CHANGELOG.md`.
- The `MODULE_CATALOG.md` TCR-000 change was reduced to one additive discovery row relative to the refreshed base.
- On replay head `b67d2f267f062dfb41dc5cc20e56a2dea012f6dc`, Real Tibia Module Registry, Agent Task Ownership, repository CI and Upstream Intelligence completed successfully; AI Agent Tools and OTBM Map Tools were still in progress at the last check.
- The immediately preceding head `826dcc8ab4fa7aa4905965a4beaf63ad0ec91618` had all six relevant workflow runs green.
- PR #768, the former shared `MODULE_CATALOG.md`/`CHANGELOG.md` overlap, is merged and no longer an active ordering conflict.
- A bounded local clone attempt failed with `Could not resolve host: github.com`; no local repository validation result is claimed from that attempt.

## UNKNOWN / deferred

- Exact Tibia client build/version carried by future user-supplied files must be recorded per ingestion and never inferred from filename alone.
- Exact filenames/packaging of proficiency data may vary by client build and must be discovered by a bounded implementation task rather than hard-coded by TCR-000.
- Whether every proposed client-reference field has stable semantic meaning across builds remains implementation evidence, not assumed architecture truth.
- Exact final-head CI results after the missing changelog/checkpoint commit are not yet available.
- Exact squash-merge SHA remains pending.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: "2026-07-23T14:46:31+02:00"
head: "b67d2f267f062dfb41dc5cc20e56a2dea012f6dc"
branch: "docs/otbm-tibia-client-reference-20260723"
pr: "762"
status: "implementing"
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
  - "PR 762 is open, draft and mergeable on replay head b67d2f267f062dfb41dc5cc20e56a2dea012f6dc."
  - "Replay head b67d2f267f062dfb41dc5cc20e56a2dea012f6dc is based on main 54ce97b3bcaac8c2e1a0d4cc6162a6ff975bbee9; current main 115f3ac2fffc36bb4e415c2a6fb45908d9538ba3 adds only the unrelated OAM programme file from PR 796."
  - "The live PR changed-file list contains 11 TCR files and excludes docs/agents/CHANGELOG.md."
  - "The MODULE_CATALOG.md TCR change is one additive discovery row after current-main reconciliation."
  - "Real Tibia Module Registry run 30008538433 passed on replay head b67d2f267f062dfb41dc5cc20e56a2dea012f6dc."
  - "Agent Task Ownership run 30008538780 passed on replay head b67d2f267f062dfb41dc5cc20e56a2dea012f6dc."
  - "Repository CI run 30008538742 passed on replay head b67d2f267f062dfb41dc5cc20e56a2dea012f6dc."
  - "Upstream Intelligence run 30008538764 passed on replay head b67d2f267f062dfb41dc5cc20e56a2dea012f6dc."
  - "Previous head 826dcc8ab4fa7aa4905965a4beaf63ad0ec91618 had Real Tibia Registry, Upstream Intelligence, Agent Task Ownership, CI, AI Agent Tools and OTBM Map Tools all green."
  - "PR 768 is merged, so its former shared-document ordering conflict is resolved."
derived:
  - "TCR-000 remains architecture-compatible with current main because post-replay main movement is outside all TCR-owned/shared paths."
  - "PR 762 is not acceptance-complete until the missing changelog mirror is restored and exact-final-head validation reruns after the final commit."
unknown:
  - "AI Agent Tools run 30008538935 and OTBM Map Tools run 30008538462 were still in progress on replay head b67d2f267f062dfb41dc5cc20e56a2dea012f6dc at the last check."
  - "Exact final-head CI run IDs/results after the missing changelog and final checkpoint commit are pending."
  - "Exact squash-merge SHA is pending."
conflicts:
  - "The task/PR description previously claimed CHANGELOG.md delivery, but the live PR 762 changed-file list excludes docs/agents/CHANGELOG.md. Live diff is authoritative."
first_failure:
  marker: "TCR-000 acceptance: required CHANGELOG discovery mirror is absent from PR 762"
  evidence: "GitHub list_pr_changed_filenames for PR 762 returned 11 files and did not include docs/agents/CHANGELOG.md."
rejected_hypotheses:
  - "Rejected: PR 768 is still an active shared-document ordering blocker; it is merged."
  - "Rejected: current main PR 796 overlaps TCR paths; it changes only docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md."
  - "Rejected: staticmapdata.object_id can be treated as OTBM/server itemId; exact mapping remains unproven."
changed_paths:
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
validation:
  - command: "GitHub Actions workflow Real Tibia Module Registry"
    result: "PASS"
    evidence: "run 30008538433 on replay head b67d2f267f062dfb41dc5cc20e56a2dea012f6dc"
  - command: "GitHub Actions workflow Agent Task Ownership"
    result: "PASS"
    evidence: "run 30008538780 on replay head b67d2f267f062dfb41dc5cc20e56a2dea012f6dc"
  - command: "GitHub Actions workflow CI"
    result: "PASS"
    evidence: "run 30008538742 on replay head b67d2f267f062dfb41dc5cc20e56a2dea012f6dc"
  - command: "GitHub Actions workflow Upstream Intelligence"
    result: "PASS"
    evidence: "run 30008538764 on replay head b67d2f267f062dfb41dc5cc20e56a2dea012f6dc"
  - command: "git clone --depth 1 https://github.com/blakinio/canary.git"
    result: "BLOCKED"
    evidence: "sandbox DNS failure: Could not resolve host github.com"
blockers:
  - "Restore the missing narrow docs/agents/CHANGELOG.md TCR-000 discovery entry from current main without overwriting unrelated entries."
  - "After the final changelog/checkpoint commit, require all ci:final-gate workflows green on that exact immutable head before readiness/merge."
next_action: "Add the missing narrow docs/agents/CHANGELOG.md TCR-000 discovery entry from current main and batch the final checkpoint update in the same ci:final-gate commit."
```
