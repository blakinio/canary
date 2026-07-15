---
task_id: CAN-20260716-oteryn-target-baseline-pinning
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: "OAM-002"
status: blocked
agent: oteryn-architecture-migration-agent
branch: docs/oam-002-target-baseline-pinning
base_branch: main
created: 2026-07-16T00:17:55+02:00
updated: 2026-07-16T01:28:00+02:00
last_verified_commit: "0c0972526814f099b51fd3481f28331b9434446d"
risk: medium
related_issue: ""
related_pr: "407"
depends_on:
  - OAM-001
blocks:
  - OAM-003
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260716-oteryn-target-baseline-pinning.md
    - .github/workflows/oam-002-finalize-governance.yml
  shared:
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
  read_only:
    - docs/architecture/oteryn-target-server-architecture.md
    - blakinio/Otheryn@3cc7c1dfea747bb380f3761ee7ff7ac30141a115
    - opentibiabr/canary@a879c9312e34381e8eedf397b8ed44510698b689
modules_touched: []
reuses:
  - docs/architecture/oteryn-target-server-architecture.md
  - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
  - Git recursive tree manifests
public_interfaces:
  - Oteryn target identity and baseline contract
cross_repo_tasks:
  - blakinio/Otheryn#1
  - blakinio/Otheryn#2
  - blakinio/Otheryn#3
---

# Goal

Establish and prove the exact Oteryn target identity, authorization, default branch, task-start SHA, exact then-current upstream Canary baseline and final target bootstrap relationship required by OAM-002, without starting OAM-003.

# Acceptance criteria

- [x] Target repository identified as `blakinio/Otheryn`.
- [x] User explicitly authorized autonomous writes to `blakinio/Otheryn` for OAM work.
- [x] Target default branch verified as `main`.
- [x] Target task-start SHA pinned as `7d1e9cc5b4e799d31ae481b9a65e3f1442ca985e`.
- [x] Then-current upstream Canary baseline pinned as `opentibiabr/canary@a879c9312e34381e8eedf397b8ed44510698b689`.
- [x] Original manual-upload target proven not equivalent to the pinned upstream baseline.
- [x] Target bootstrapped through reviewed target PRs without bulk-copying legacy `blakinio/canary` history.
- [x] Final target baseline pinned as `blakinio/Otheryn@3cc7c1dfea747bb380f3761ee7ff7ac30141a115`.
- [x] Final post-merge tree relationship to pinned upstream proven deterministically.
- [x] Temporary target verification workflows removed from final target content.
- [x] Canonical module dispositions unchanged; all remain `REVALIDATE`.
- [ ] Architecture contract and OAM program record updated with final OAM-002 state.
- [ ] Exact-current-head Canary ownership/CI and merge gate verified.
- [ ] Feature PR #407 squash-merged and lifecycle archived separately.

# Confirmed context

## PROVEN

- Governance repository task-start base: `blakinio/canary@264a86b1eddf5f68666281c47489166f343c3e84`.
- Latest re-fetched Canary `main` during finalization: `0c0972526814f099b51fd3481f28331b9434446d`.
- Target: `blakinio/Otheryn`, default branch `main`, with explicit user write authorization.
- Target task-start SHA: `7d1e9cc5b4e799d31ae481b9a65e3f1442ca985e`.
- Exact OAM-002 upstream baseline: `opentibiabr/canary@a879c9312e34381e8eedf397b8ed44510698b689`.
- Exact upstream tree: `dfdd43a63cfb26dcc6d0c42a55f71f815aae2fff`.
- Original target full-tree manifest had 32 entries; pinned upstream had 6326. Their manifest SHA-256 values were respectively `bb6eca728acb26061554d79cb284849655f4fa926d4b51f1cf0e0757326ea482` and `f8a9a32c1f55ca45d1f9e0c34f6d7ce4d7a9441d3d7fe453ab85e6c56f0f5c7b`.
- Target bootstrap PR `blakinio/Otheryn#1` passed exact-head `CI`, `Repository Audit`, `autofix.ci` and `Required`, then squash-merged as `b63fa0dd1efcaab4257a6557d6711b1965dce8e8`.
- Target cleanup PR `blakinio/Otheryn#2` restored `.github/workflows/reusable-checks.yml` exactly to upstream blob `045c987911cae6ec9cb321c550b5ea0aad34a920`, passed exact-head `CI` and `Required`, then squash-merged as final target baseline `3cc7c1dfea747bb380f3761ee7ff7ac30141a115`.
- Temporary post-merge evidence PR `blakinio/Otheryn#3` was closed without merge after its read-only full-tree verifier passed. Its branch was reset to final target `main`.
- Post-merge proof established that final target `main@3cc7c1df...` matches pinned upstream content everywhere except exactly two persistent target CI/governance paths: `.github/workflows/required.yml` and `.github/workflows/reusable-docker-quickstart-smoke.yml`.
- The Docker workflow delta only normalizes the mixed-case repository name to lowercase for the PR image tag, matching the existing build workflow behavior.
- No Oteryn runtime, gameplay, database, protocol, Lua implementation, datapack, map, client or canonical-module migration was performed.

## DERIVED

- OAM-002 target identity and bootstrap evidence requirements are satisfied at the target-repository level.
- The final target is an exact pinned-upstream content baseline plus two explicitly bounded target CI/governance deltas; because target PRs were squash-merged, final `main` must not be described as having the same commit SHA or direct Git ancestry as upstream.
- OAM-003 becomes eligible only after OAM-002 governance merge and lifecycle completion; it remains a separate bounded task and is not started by this task.

## UNKNOWN

- None for OAM-002 target identity or baseline pinning.

## CONFLICT

- GitHub repository metadata indicated merge commits were allowed, but an explicit merge-method attempt on target PR #1 was rejected with `Merge commits are not allowed on this repository`. The repository-accepted squash path was used and provenance is therefore recorded as exact content/tree evidence rather than final direct ancestry.

# Ownership and overlap check

- No pre-existing OAM task or open PR claimed OAM-002 target identity when this task started.
- Open Canary PRs inspected at task start were unrelated to OAM target identity/contract ownership.
- Target changes were isolated to dedicated `dudantas/*` branches and PRs #1/#2; PR #3 was evidence-only and closed unmerged.
- No canonical module registry record was modified.

# Work log

## Target discovery and proof

- Verified target identity, permissions, default branch and exact task-start SHA.
- Rejected manual upload commit messages as provenance proof.
- Proved the original target tree was incomplete versus pinned upstream using recursive Git tree manifests.

## Bootstrap delivery

- A direct workflow push of the exact upstream tree was rejected because the Actions token lacked permission to update workflow files; no policy was weakened.
- Reused fetched Git objects and the authorized GitHub connector to construct the exact upstream tree on the target branch.
- Added a meaningful `Required` exact-head aggregation gate because target branch rules required that status.
- Used the existing Lua binding checker native `--base` option only for the one bootstrap PR, then removed the exception in PR #2.
- Fixed a target-repository CI incompatibility where Docker build lowercased `github.repository` but Docker quickstart used mixed-case `blakinio/Otheryn`.
- Merged target bootstrap and cleanup only after exact-head required checks passed.

## Final proof

- Ran a bounded full-tree verifier before cleanup merge and again after final target merge.
- Confirmed `.github/workflows/reusable-checks.yml` equals the exact pinned upstream blob.
- Confirmed only the two documented target CI/governance paths remain different from pinned upstream content.

# Failed approaches and rejected hypotheses

- Local cross-repository `git diff` was unavailable because the execution sandbox could not resolve `github.com`; hosted GitHub Actions tree manifests were used instead.
- Creating a target ref directly at the upstream SHA initially failed because that commit object was not yet present in the target repository.
- Manual `Add files via upload` history was rejected as sufficient bootstrap provenance.
- Initial Actions-token bootstrap push was rejected by workflow-file permission enforcement; branch protection and workflow security were not bypassed.
- Explicit merge-commit delivery was rejected by repository merge policy; squash merge was used with separate deterministic post-merge tree proof.
- Initial bootstrap Fast Checks treated the entire imported tree as new Lua bindings; the existing checker `--base` contract was used rather than disabling the check.
- Initial Docker quickstart failed because mixed-case target repository naming disagreed with the existing lowercased build image tag; the target-only workflow normalization fixed the verified mismatch.
- An accidental temporary Canary marker file was created and removed; two mistaken existing-file create calls were rejected by GitHub. None has a net PR diff.

# Validation and CI

| Evidence | Result |
|---|---|
| Original target vs pinned upstream recursive tree manifests | FAIL as bootstrap candidate; 32 vs 6326 entries |
| Target PR #1 current-head CI / Repository Audit / Required | PASS |
| Target PR #1 merge | PASS; squash merge `b63fa0dd1efcaab4257a6557d6711b1965dce8e8` |
| Target PR #2 final cleanup current-head CI / Required | PASS |
| Target PR #2 merge | PASS; final target baseline `3cc7c1dfea747bb380f3761ee7ff7ac30141a115` |
| Post-merge final-tree verifier | PASS; exactly two persistent target CI/governance deltas |
| Canonical module dispositions | unchanged; all `REVALIDATE` |

# Risks and compatibility

- Runtime/game behavior: unchanged by OAM-002.
- Legacy migration: none.
- Protocol/client: none.
- Map/datapack/assets: no migration decision or donor import.
- Remaining target deltas are CI/governance-only and explicitly proven.
- Residual branch `dudantas/oam-002-upstream-object-probe` may remain because no branch-delete action is exposed; it is not `main`, is not a merged implementation branch and grants no migration authorization.

# Remaining work

1. Update the durable architecture contract and authoritative program record, then verify and merge Canary PR #407 through the normal gates.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T01:28:00+02:00
head: 0c0972526814f099b51fd3481f28331b9434446d
branch: docs/oam-002-target-baseline-pinning
pr: 407
status: finalizing
context_routes:
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/CAN-20260716-oteryn-target-baseline-pinning.md
  - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
  - .github/workflows/oam-002-finalize-governance.yml
proven:
  - target is blakinio/Otheryn with explicit user write authorization and default branch main
  - target task-start SHA is 7d1e9cc5b4e799d31ae481b9a65e3f1442ca985e
  - pinned upstream baseline is a879c9312e34381e8eedf397b8ed44510698b689
  - final target baseline is 3cc7c1dfea747bb380f3761ee7ff7ac30141a115
  - final target content equals pinned upstream except required.yml and reusable-docker-quickstart-smoke.yml
  - all canonical modules remain REVALIDATE
derived:
  - OAM-002 target-level evidence gate is satisfied
  - OAM-003 remains separate and must not start before OAM-002 governance/lifecycle completion
unknown: []
conflicts:
  - target repository metadata advertised merge commits but GitHub rejected explicit merge-method delivery
first_failure:
  marker: original target manual upload was not an exact upstream bootstrap
  evidence: 32 target tree entries versus 6326 upstream entries
rejected_hypotheses:
  - manual upload history proves upstream provenance
  - passing legacy CI authorizes migration
changed_paths:
  - docs/agents/tasks/active/CAN-20260716-oteryn-target-baseline-pinning.md
  - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
validation:
  - command: target bootstrap and cleanup exact-head GitHub Actions
    result: PASS
    evidence: target PRs 1 and 2
  - command: post-merge recursive tree-manifest proof
    result: PASS
    evidence: closed unmerged target PR 3
blockers:
  - Canary governance contract/program update and PR 407 merge/lifecycle remain
next_action: Update OTERYN_TARGET_ARCHITECTURE_CONTRACT.md and OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md with the proven OAM-002 target identity and baseline.
```

# Completion

- Final status: finalizing
- Canary feature PR: #407
- Target bootstrap PR: `blakinio/Otheryn#1` merged
- Target cleanup PR: `blakinio/Otheryn#2` merged
- Target evidence PR: `blakinio/Otheryn#3` closed unmerged
- Final target baseline: `3cc7c1dfea747bb380f3761ee7ff7ac30141a115`
- Program record updated: pending
- Architecture contract updated: pending
- Catalogue updated: not applicable
- Changelog updated: not applicable
- Archived at: not archived
