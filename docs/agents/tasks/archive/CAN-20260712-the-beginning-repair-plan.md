---
task_id: CAN-20260712-the-beginning-repair-plan
status: completed
agent: "GPT-5.6 Thinking"
branch: docs/the-beginning-repair-plan
base_branch: main
created: 2026-07-12
updated: 2026-07-14T18:56:00+02:00
last_verified_commit: "f96680987955cde24d4264e9473bde70501ed534"
risk: low
related_pr: "#207"
depends_on:
  - "Merged PR #204 The Beginning OTBM/runtime audit"
  - "Merged PR #186 Zirella door and reward tutorials"
  - "Merged PR #157 Carlos tutorial trade flow"
  - "map SHA-256 a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2"
blocks: []
owned_paths:
  - docs/ai-agent/THE_BEGINNING_REPAIR_PLAN.md
  - docs/agents/tasks/archive/CAN-20260712-the-beginning-repair-plan.md
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

Turn the evidence report into an ordered set of minimal, independently reviewable repair tasks without changing gameplay in the planning PR.

# Delivered result

PR #207 merged the documentation-only plan as commit `f96680987955cde24d4264e9473bde70501ed534`.

The plan correctly preserved the following safety boundaries:

- no OTBM, item, asset, NPC, Lua/XML, spawn, engine or configuration edits in the planning PR;
- no historical coordinates, town IDs or storages adopted without current evidence;
- AID `50999`, `skip tutorial`, static cart branch, extra dead trees and `0,0,0` teleport attributes remain blocked where the current contract is incomplete;
- implementation tasks must start from current `main`, remain bounded and pass focused plus runtime validation.

# Post-merge correction discovered during handoff

The merged plan is stale in its first package and in its treatment of PR #157.

PR #157 is not a stale candidate: it merged as commit `813a2ce39daced46802e6801e4abd275709b8672` and current `carlos.lua` contains the repaired state machine. Therefore:

- remove the planned "fresh Carlos repair PR" package;
- record Carlos as completed baseline;
- do not reopen or duplicate the Carlos implementation;
- update the dependency and merge-order sections before relying on the plan for future work.

# Corrected continuation order

1. Open a documentation-only corrective PR that synchronizes `THE_BEGINNING_OTBM_AUDIT.md` and `THE_BEGINNING_REPAIR_PLAN.md` with merged PR #157.
2. Revalidate Santiago `easy` persistence on current `main`; implement only if the mismatch still exists.
3. Revalidate rope-success hint state 22 on current `main`; implement only if the write is still missing and remains bounded to the tutorial branch.
4. Resolve the AID `50999` crossing contract using the existing OTBM audit, resolver, real-asset renderer and disposable live-world traces before writing any MoveEvent.
5. Keep `skip tutorial`, cockroach tutorial events and other unresolved map-only findings blocked until their current contracts are proved.
6. Finish with a fresh-character runtime E2E of Santiago → Zirella → cave → Carlos → Rookgaard plus reconnect tests at NPC boundaries.

# Validation history

The content head `3cc5375e110d8450023f709443db0ad9690ac1a3` passed:

- CI run 1096;
- AI Agent Tools run 506;
- Agent Task Ownership run 60.

The final task-record head `00e1e390847ccc0a7c2e567e9ac8a117cff330ed` passed CI 1097, AI Agent Tools 507 and Agent Task Ownership 61; CI 1098 also completed successfully after the PR was marked ready.

# Completion

- Final status: completed, with post-merge documentation correction required
- PR: #207
- Merge commit: `f96680987955cde24d4264e9473bde70501ed534`
- Gameplay changed: no
- Archived at: 2026-07-14T18:56:00+02:00
