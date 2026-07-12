---
task_id: CAN-20260712-required-ci-gate
coordination_id: ""
status: in-progress
agent: "GPT-5.6 Thinking"
branch: ci/required-gate-and-repo-policy
base_branch: main
created: 2026-07-12T20:43:21Z
updated: 2026-07-12T20:43:21Z
last_verified_commit: "32c12436894d3c6c836be238eb6d8733dcc2459f"
risk: medium
related_issue: ""
related_pr: ""
depends_on: []
blocks: []
owned_paths:
  - .github/workflows/ci.yml
  - docs/agents/tasks/active/CAN-20260712-required-ci-gate.md
modules_touched:
  - github-actions-ci
reuses:
  - blakinio/otclient:.github/workflows/ci.yml#required
public_interfaces:
  - "GitHub check context CI / Required"
cross_repo_tasks: []
---

# Goal

Add one always-emitted aggregate `CI / Required` check to Canary so the final `main` ruleset can require a stable check instead of a conditional nested matrix job.

# Acceptance criteria

- [ ] `CI / Required` runs for every Canary pull request that triggers `CI`.
- [ ] Non-draft PRs fail the aggregate when a mandatory fast check, Lua test, scoped build, or scoped smoke test fails or is unexpectedly skipped.
- [ ] Draft PRs may keep heavy jobs skipped without manufacturing a false successful merge gate.
- [ ] Existing path-scoped heavy-build behavior remains intact.
- [ ] Relevant checks completed.
- [ ] Module catalogue impact handled or none.
- [ ] Documentation/changelog impact handled or none.
- [ ] Cross-repository impact handled or none.
- [ ] Autonomous merge gate satisfied.

# Confirmed context

- `main` was verified at `32c12436894d3c6c836be238eb6d8733dcc2459f` before branch creation.
- Canary CI currently emits `Build - Linux / Compile (linux-release)` for every PR but has no aggregate `Required` job.
- The active bootstrap ruleset has no required status check; the disabled final ruleset is intended to require `CI / Required`.
- Legacy Branch protection rules are confirmed empty by the repository owner.
- OTClient already uses an aggregate `required` job and is the implementation pattern to reuse.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| OTClient aggregate gate | Adapt result/scope evaluation | `blakinio/otclient/.github/workflows/ci.yml` | Proven stable required context while allowing scoped jobs to skip. |
| Canary scope detector | Reuse existing outputs | `.github/workflows/ci.yml` | Avoid changing build selection or adding duplicate path logic. |

# Ownership and overlap check

- Open PRs inspected: recent Canary PRs through #195 and search for an existing Required CI gate.
- Active tasks inspected: `docs/agents/ACTIVE_WORK.md` and live PR state.
- Overlaps: no open PR found whose declared purpose is adding the aggregate gate.
- Resolution: limit code ownership to `.github/workflows/ci.yml` and this task record.

# Current state

Branch created from current `main`; implementation pending.

# Plan

1. Add the aggregate `required` job without changing existing build scopes.
2. Open a draft PR early and verify the workflow syntax and emitted check name.
3. Repair any CI failure on the same branch.
4. Merge only after the current head is green.
5. Verify `CI / Required` on a real PR before the repository owner activates the final ruleset.

# Work log

## 2026-07-12T20:43:21Z

- Changed: created the dedicated branch and durable task record.
- Learned: repository settings still allow merge and rebase methods; those are live settings outside repository contents.
- Failed/blocked: the available GitHub connector does not expose repository-settings or ruleset mutation endpoints.
- Result: CI implementation can be completed autonomously; live Settings changes may require the owner UI after the check is verified.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Reuse one aggregate job rather than requiring matrix jobs directly | Conditional reusable jobs do not always emit stable contexts. | none |
| Keep current path-scoped builds | This task is protection hardening, not a build-matrix redesign. | none |

# Files and interfaces

| Path/interface/config/schema | Purpose | Status |
|---|---|---|
| `.github/workflows/ci.yml` | Emit and evaluate `CI / Required` | planned |
| `CI / Required` | Stable ruleset-required check context | planned |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| pending | GitHub Actions `CI` | not-run | Must verify the exact `Required` job on the branch head. |

Never write `passed` without verification.

# Failed approaches and dead ends

- No repository/ruleset mutation action is available in the connected GitHub tool, so live Settings cannot be changed through that connector.

# Risks and compatibility

- Runtime: none; CI-only.
- Data/migration: none.
- Security: aggregate job uses no secrets and empty permissions.
- Backward compatibility: existing individual checks and build selection remain unchanged.
- Cross-repo rollout: none.
- Rollback: revert the CI commit and keep the bootstrap ruleset active.

# Remaining work

1. Implement the aggregate job and open the PR.

# Handoff

## Start here

Open this task and `.github/workflows/ci.yml`; verify current `main` and live PR checks before editing.

## Do not repeat

Do not require a conditional matrix job directly in the final ruleset.

## Required reads

- `AGENTS.md`
- `docs/agents/ACTIVE_WORK.md`
- `docs/agents/MODULE_CATALOG.md`
- `.github/workflows/ci.yml`
- `blakinio/otclient/.github/workflows/ci.yml`

## Open questions

- Whether the repository owner wants a merge queue later; this task does not enable one.

# Completion

- Final status: in-progress
- PR:
- Merge commit:
- Catalogue updated: not required; no reusable runtime module added
- Changelog updated: not required; CI-only repository policy
- Archived at:
