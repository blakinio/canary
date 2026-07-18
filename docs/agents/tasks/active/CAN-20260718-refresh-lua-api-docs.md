---
task_id: CAN-20260718-refresh-lua-api-docs
program_id: agent-governance
coordination_id: ""
status: implementing
agent: codex
branch: ci/refresh-lua-api-docs
base_branch: main
created: 2026-07-18T08:51:23Z
updated: 2026-07-18T08:51:23Z
last_verified_commit: 8f91d8667b93db08969d04579059f77343194ac6
risk: low
related_issue: ""
related_pr: ""
depends_on: []
blocks:
  - "PR #527 task archival cleanup"
owned_paths:
  exclusive:
    - docs/lua-api/lua_api.d.lua
    - docs/lua-api/lua_api.json
    - docs/lua-api/lua_api.md
    - docs/lua-api/lua_api_quality_baseline.json
    - docs/agents/tasks/active/CAN-20260718-refresh-lua-api-docs.md
  shared: []
  read_only:
    - src/lua/**
    - src/lua/docgen/**
    - .github/workflows/reusable-build-linux.yml
modules_touched: []
reuses:
  - canary --generate-lua-api-docs-only
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Refresh the generated Lua API documentation artifacts and their quality baseline from the existing bindings so that the canonical CI generator and quality checks are clean, without changing runtime code or generator behavior.

# Acceptance criteria

- [x] The canonical generator updates only `docs/lua-api/lua_api.d.lua`, `lua_api.json`, and `lua_api.md`.
- [x] The quality baseline records the single pre-existing undocumented variadic API exposed by regeneration.
- [ ] Lua API quality, binding-doc, governance, and lifecycle checks pass.
- [ ] Required GitHub checks pass on the exact final head.
- [ ] The narrow repair is squash-merged before retrying PR #527.
- [ ] No module catalogue, changelog, public-interface, or cross-repository update is required because this task only refreshes generated documentation.

# Confirmed context

- PR #527 differs from its green parent only by archiving the PR #487 task record.
- CI run 29637326197 attempts 1 and 2 both failed because the canonical generator changed the same three Lua API documentation files.
- No open PR owns `docs/lua-api/**` or `src/lua/**` at task creation time.
- The stale generated artifacts are independent of the portable Windows test-path fix in PR #487.
- The regenerated `Game.getClusterOnlinePlayers` signature contributes one `...: any`, increasing both guarded metrics by one; the binding predates this repair and no runtime-code change belongs here.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| Canonical Lua API generator | `--generate-lua-api-docs-only` | `.github/workflows/reusable-build-linux.yml` | This is the command enforced by CI. |

# Ownership and overlap check

- Program record: `agent-governance`
- Open PRs inspected: no Lua API documentation overlap found.
- Active tasks inspected: no ownership overlap found.
- Ownership checker result: passed for 14 active task records.
- Exclusive claims: the three generated docs, their quality baseline, and this task record.
- Shared claims: none.
- Read-only dependencies: Lua bindings/docgen and the enforcing workflow.
- Overlaps: none known.
- Resolution: keep this as a separate narrow CI-repair PR.

# Current state

The generated Lua API documentation committed on `main` was stale relative to the canonical generator output. The local generator is deterministic and the quality baseline now explicitly records the one additional pre-existing fallback signature.

# Plan

1. Build and run the canonical documentation generator, then validate and publish the narrow repair.

# Work log

## 2026-07-18T08:51:23Z

- Changed: created the dedicated task and branch.
- Learned: two identical CI failures prove the cleanup PR is exposing stale generated artifacts.
- Failed/blocked: PR #527 cannot become green until this independent repair lands.
- Result: implementation started with an isolated ownership scope.

## 2026-07-18T08:55:00Z

- Changed: regenerated the three canonical artifacts and updated `lua_api_quality_baseline.json` from 166/48 to 167/49 for `param_any`/`param_vararg`.
- Learned: both metric increases come from the same pre-existing `Game.getClusterOnlinePlayers(...: any)` fallback; all other guarded metrics are unchanged.
- Failed/blocked: the first quality check correctly rejected the stale baseline.
- Result: a second generator run was byte-identical; quality, binding-doc, ownership, and diff checks pass locally.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Use a separate PR | Adding unrelated generated docs to cleanup PR #527 would obscure both changes. | N/A |

# Files and interfaces

| Path/interface/config/schema | Ownership mode | Purpose | Status |
|---|---|---|---|
| `docs/lua-api/lua_api.d.lua` | exclusive | Generated Lua type declarations | planned |
| `docs/lua-api/lua_api.json` | exclusive | Generated machine-readable API | planned |
| `docs/lua-api/lua_api.md` | exclusive | Generated reference documentation | planned |
| `docs/lua-api/lua_api_quality_baseline.json` | exclusive | Explicit quality-debt baseline | generated |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| `8f91d8667b93db08969d04579059f77343194ac6` | CI run 29637326197, Lua API generation check | FAIL | Same three generated docs differ on attempts 1 and 2. |
| working tree | `canary-debug.exe --generate-lua-api-docs-only` twice | passed | Exit 0; second-run SHA-256 values unchanged. |
| working tree | `python tools/check_lua_api_quality.py` | passed | Metrics 167/114/49/0/22. |
| working tree | `python tools/check_lua_api_binding_docs.py` | passed | 0 new registrations inspected. |
| working tree | `python tools/agents/task_ownership.py` | passed | 14 active records validated. |

# Failed approaches and dead ends

- A single failed-job rerun reproduced the exact failure; further blind reruns are forbidden.

# Risks and compatibility

- Runtime: none; generated documentation only.
- Data/migration: none.
- Security: none.
- Backward compatibility: no runtime behavior changes.
- Cross-repo rollout: none.
- Rollback: revert the generated-doc refresh commit.

# Remaining work

1. Review the complete diff, commit, and open the dedicated draft PR.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-18T08:51:23Z
head: 8f91d8667b93db08969d04579059f77343194ac6
branch: ci/refresh-lua-api-docs
pr: none
status: implementing
context_routes:
  - agent-governance
  - ci-repair
owned_paths:
  - docs/lua-api/lua_api.d.lua
  - docs/lua-api/lua_api.json
  - docs/lua-api/lua_api.md
  - docs/lua-api/lua_api_quality_baseline.json
  - docs/agents/tasks/active/CAN-20260718-refresh-lua-api-docs.md
proven:
  - CI run 29637326197 attempts 1 and 2 produced the same generated-doc failure.
  - PR #527 changes only the PR #487 task-record location and completion metadata.
derived:
  - The stale generated documentation requires a separate narrow repair before PR #527 can pass.
unknown:
  - Whether Linux CI produces byte-identical canonical output.
conflicts: []
first_failure:
  marker: generated Lua API documentation differs from canonical generator output
  evidence: GitHub Actions run 29637326197, Linux Release, attempts 1 and 2
rejected_hypotheses:
  - transient CI failure: the failed-job rerun reproduced the same diff
changed_paths:
  - docs/agents/tasks/active/CAN-20260718-refresh-lua-api-docs.md
  - docs/lua-api/lua_api.d.lua
  - docs/lua-api/lua_api.json
  - docs/lua-api/lua_api.md
  - docs/lua-api/lua_api_quality_baseline.json
validation:
  - command: canonical Lua API generator
    result: PASS
    evidence: two local runs exited 0 and the second run preserved all three artifact hashes
  - command: python tools/check_lua_api_quality.py
    result: PASS
    evidence: metrics 167/114/49/0/22 match the refreshed baseline
blockers:
  - PR #527 remains blocked until this repair is merged
next_action: Review and publish the narrow generated-documentation repair PR.
```

# Completion

- Final status: in progress
- PR:
- Merge commit:
- Program record updated: not required
- Catalogue updated: not required
- Changelog updated: not required
- Archived at:
