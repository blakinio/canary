---
task_id: CAN-20260712-the-beginning-repair-plan
status: ready
agent: "GPT-5.6 Thinking"
branch: docs/the-beginning-repair-plan
base_branch: main
created: 2026-07-12
updated: 2026-07-13
risk: low
related_pr: "#207"
depends_on:
  - "PR #204 The Beginning OTBM/runtime audit — merge first"
  - "merged PR #186 Zirella door and reward tutorials"
  - "map SHA-256 a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2"
blocks:
  - "fresh Carlos repair PR"
  - "AID 50999 contract-resolution task"
  - "Santiago persistence repair PR"
  - "rope-hint state repair PR"
owned_paths:
  - docs/ai-agent/THE_BEGINNING_REPAIR_PLAN.md
  - docs/agents/tasks/active/CAN-20260712-the-beginning-repair-plan.md
modules_touched:
  - World Semantic Review
  - repair sequencing and merge gates
reuses:
  - docs/ai-agent/THE_BEGINNING_OTBM_AUDIT.md
  - existing OTBM item/mechanic audit
  - existing OTBM script resolver
  - existing factual OTBM renderer
cross_repo_tasks: []
---

# Goal

Turn the completed evidence report into an ordered set of minimal, independently reviewable repair tasks without changing gameplay in this planning PR.

# Boundaries

- This branch is documentation-only.
- No OTBM, item, asset, NPC, Lua/XML, spawn, engine or production configuration change is permitted.
- PR #204 is the evidence authority and must merge before PR #207; if its findings change, this plan must be synchronized before merge.
- A `confirmed` defect may enter an implementation PR only with an exact current-source contract and focused tests.
- A `map-only`, `script-only` or `unresolved` finding may not be converted into gameplay code by historical analogy alone.
- AID `50999` and `skip tutorial` remain blocked until their missing current-world contracts are resolved.
- Each behavior fix must use a fresh branch from current `main`; stale PR #157 is evidence/candidate code only and must not be rebased or merged as-is.

# Acceptance criteria

- [x] publish an ordered repair matrix covering every outstanding finding from PR #204;
- [x] define exact files, preconditions, tests, regression risk and merge order for every repair candidate;
- [x] separate implementation-ready work from contract-blocked work;
- [x] define when stale PR #157 may be closed;
- [x] define resolver/render/runtime revalidation gates where map mechanics are involved;
- [x] keep the PR documentation-only with exactly the plan and task record;
- [x] documentation, AI Agent Tools and Agent Task Ownership checks pass on the validated content head.

# Validation record

Content head `3cc5375e110d8450023f709443db0ad9690ac1a3` passed:

- CI run 1096;
- AI Agent Tools run 506;
- Agent Task Ownership run 60.

This final commit changes only the task status and validation record. GitHub checks on the resulting PR head remain authoritative before merge.

The branch was one unrelated commit behind `main` during review (`#233`, InstanceManager timeout sweep). It does not overlap either owned documentation path. PR mergeability and the dependency on #204 must be reverified immediately before merge.
