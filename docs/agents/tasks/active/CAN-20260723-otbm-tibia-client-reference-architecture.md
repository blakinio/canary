---
task_id: CAN-20260723-otbm-tibia-client-reference-architecture
program_id: CAN-PROGRAM-OTBM-TIBIA-CLIENT-REFERENCE
coordination_id: OTBM-TIBIA-CLIENT-REFERENCE
status: review
agent: GPT-5.6 Thinking
branch: docs/otbm-tibia-client-reference-20260723
base_branch: main
created: 2026-07-23T10:00:00+02:00
updated: 2026-07-23T16:01:25+02:00
last_verified_commit: "15e4672ab49bb8ef3710e793e802be01e4f434a1"
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
- [x] Add the narrow `CHANGELOG.md` TCR-000 discovery mirror while preserving unrelated current-main changelog content.
- [ ] Verify PR #762 required CI on the immutable final head and merge under repository policy.

# Evidence baseline

## PROVEN

- TCR-000 is architecture/governance only and adds no TCR-001/TCR-002/TCR-003 parser or runtime/map mutation implementation.
- PR #762 is open, draft and mergeable on pre-checkpoint head `15e4672ab49bb8ef3710e793e802be01e4f434a1`.
- The branch remains rooted at replay base `54ce97b3bcaac8c2e1a0d4cc6162a6ff975bbee9`; live `main` advanced to `489607174f22b8b36663fe2251cdba0423388fbd` through five later commits.
- The only live-main path overlapping those five commits with the TCR diff is `docs/agents/CHANGELOG.md`.
- The live PR changed-file list now contains 12 files and includes `docs/agents/CHANGELOG.md`.
- The changelog diff preserves the current-main post-008 Universal Physical E2E entry and adds one separate TCR-000 discovery entry; no unrelated historical changelog wording remains changed.
- The `MODULE_CATALOG.md` TCR-000 change remains one additive discovery row.
- PR #777 is an internal coordination PR with `main` as head and a historical TCR reconciliation branch as base; its body explicitly says it is not intended for direct merge to `main`, so it is not a competing main-targeted owner for this final TCR change.
- On head `e7cf8aac2da9b9cc061b3367522ebf6e831c1651`, Real Tibia Module Registry, repository CI, Upstream Intelligence, OTBM Map Tools and AI Agent Tools passed; Agent Task Ownership failed only because frontmatter `status: review` was paired with checkpoint `status: implementing`.
- Repository lifecycle validation allows frontmatter `review` only with checkpoint `validating` or `ready`; this checkpoint uses `validating`.
- The `ci:final-gate` label was present on PR #762 before this checkpoint commit.
- A bounded local clone attempt previously failed with `Could not resolve host: github.com`; no local repository validation result is claimed from that attempt.

## UNKNOWN / deferred

- Exact Tibia client build/version carried by future user-supplied files must be recorded per ingestion and never inferred from filename alone.
- Exact filenames/packaging of proficiency data may vary by client build and must be discovered by a bounded implementation task rather than hard-coded by TCR-000.
- Whether every proposed client-reference field has stable semantic meaning across builds remains implementation evidence, not assumed architecture truth.
- Exact final-head CI run IDs/results triggered by this checkpoint commit are pending.
- Exact squash-merge SHA remains pending.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: "2026-07-23T16:01:25+02:00"
head: "15e4672ab49bb8ef3710e793e802be01e4f434a1"
branch: "docs/otbm-tibia-client-reference-20260723"
pr: "762"
status: "validating"
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
  - "PR 762 is open, draft and mergeable on pre-checkpoint head 15e4672ab49bb8ef3710e793e802be01e4f434a1."
  - "Live main advanced from replay base 54ce97b3bcaac8c2e1a0d4cc6162a6ff975bbee9 to 489607174f22b8b36663fe2251cdba0423388fbd; only docs/agents/CHANGELOG.md overlaps the TCR diff across those five commits."
  - "The live PR changed-file list contains 12 files including docs/agents/CHANGELOG.md."
  - "The changelog now has one separate TCR-000 discovery entry and preserves the current-main post-008 Universal Physical E2E entry without unrelated historical wording changes."
  - "The MODULE_CATALOG.md TCR change is one additive discovery row."
  - "PR 777 is internal reconciliation with main as head and a historical TCR branch as base, not a main-targeted competing delivery PR."
  - "Real Tibia Module Registry run 30008665407 passed on head e7cf8aac2da9b9cc061b3367522ebf6e831c1651."
  - "Repository CI run 30008665715 passed on head e7cf8aac2da9b9cc061b3367522ebf6e831c1651."
  - "Upstream Intelligence run 30008665447 passed on head e7cf8aac2da9b9cc061b3367522ebf6e831c1651."
  - "OTBM Map Tools run 30008665498 passed on head e7cf8aac2da9b9cc061b3367522ebf6e831c1651."
  - "AI Agent Tools run 30008665406 passed on head e7cf8aac2da9b9cc061b3367522ebf6e831c1651."
  - "Agent Task Ownership run 30008665413 failed on head e7cf8aac2da9b9cc061b3367522ebf6e831c1651 because task status review was paired with checkpoint status implementing."
  - "This checkpoint corrects the lifecycle state to validating, which is compatible with frontmatter status review."
  - "ci:final-gate was applied before this checkpoint commit."
derived:
  - "The prior TCR-000 CHANGELOG acceptance blocker is resolved in the live PR diff."
  - "The remaining acceptance gate is exact-final-head ci:final-gate validation before readiness and merge."
unknown:
  - "Exact final-head CI run IDs/results after this checkpoint commit are pending."
  - "Exact squash-merge SHA is pending."
conflicts: []
first_failure:
  marker: "none"
  evidence: "The prior first failure was Agent Task Ownership run 30008665413 on e7cf8aac2da9b9cc061b3367522ebf6e831c1651; its review/implementing lifecycle mismatch is corrected in this checkpoint by status validating. Exact-final-head CI remains pending rather than failed."
rejected_hypotheses:
  - "Rejected: the missing CHANGELOG mirror remains absent; the live PR now contains docs/agents/CHANGELOG.md."
  - "Rejected: PR 777 is a competing main-targeted CHANGELOG owner; it has main as head, a historical reconciliation branch as base and is explicitly internal-only."
  - "Rejected: staticmapdata.object_id can be treated as OTBM/server itemId; exact mapping remains unproven."
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
validation:
  - command: "GitHub Actions workflow Real Tibia Module Registry"
    result: "PASS"
    evidence: "run 30008665407 on head e7cf8aac2da9b9cc061b3367522ebf6e831c1651"
  - command: "GitHub Actions workflow Agent Task Ownership"
    result: "FAIL"
    evidence: "run 30008665413 on head e7cf8aac2da9b9cc061b3367522ebf6e831c1651; changed-task checkpoint validation reported task status review inconsistent with checkpoint status implementing"
  - command: "GitHub Actions workflow CI"
    result: "PASS"
    evidence: "run 30008665715 on head e7cf8aac2da9b9cc061b3367522ebf6e831c1651"
  - command: "GitHub Actions workflow Upstream Intelligence"
    result: "PASS"
    evidence: "run 30008665447 on head e7cf8aac2da9b9cc061b3367522ebf6e831c1651"
  - command: "GitHub Actions workflow OTBM Map Tools"
    result: "PASS"
    evidence: "run 30008665498 on head e7cf8aac2da9b9cc061b3367522ebf6e831c1651"
  - command: "GitHub Actions workflow AI Agent Tools"
    result: "PASS"
    evidence: "run 30008665406 on head e7cf8aac2da9b9cc061b3367522ebf6e831c1651"
  - command: "git clone --depth 1 https://github.com/blakinio/canary.git"
    result: "BLOCKED"
    evidence: "sandbox DNS failure: Could not resolve host github.com"
blockers:
  - "Require all ci:final-gate workflows green on the exact immutable final PR head before readiness and merge."
next_action: "Require all ci:final-gate workflows on the exact final PR head to finish green; then recheck mergeability and review threads, mark PR 762 ready, and squash-merge under repository policy."
```
