---
task_id: CAN-20260716-oteryn-target-baseline-pinning
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: "OAM-002"
status: ready
agent: oteryn-architecture-migration-agent
branch: docs/oam-002-target-baseline-pinning
base_branch: main
created: 2026-07-16T00:17:55+02:00
updated: 2026-07-16T01:40:00+02:00
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

Establish and prove the exact Oteryn target identity, authorization, default branch, task-start SHA, exact then-current upstream Canary bootstrap SHA and final target baseline required by OAM-002, without starting OAM-003.

# Acceptance criteria

- [x] Target repository identified as `blakinio/Otheryn`.
- [x] Explicit user write authorization recorded.
- [x] Target default branch verified as `main`.
- [x] Target task-start SHA pinned as `7d1e9cc5b4e799d31ae481b9a65e3f1442ca985e`.
- [x] Upstream bootstrap SHA pinned as `opentibiabr/canary@a879c9312e34381e8eedf397b8ed44510698b689`.
- [x] Original manual-upload target proven not equivalent to pinned upstream.
- [x] Clean target bootstrap delivered through reviewed target PRs without importing legacy `blakinio/canary` history.
- [x] Final target baseline pinned as `blakinio/Otheryn@3cc7c1dfea747bb380f3761ee7ff7ac30141a115`.
- [x] Final post-merge target/upstream tree relationship proven deterministically.
- [x] Temporary target and Canary verification workflows removed from final diffs/content.
- [x] Architecture contract updated with final OAM-002 target identity and baseline.
- [x] Authoritative OAM program record updated with final OAM-002 state.
- [x] Canonical module dispositions unchanged; all 62 remain `REVALIDATE`.
- [ ] Exact-current-head Canary ownership/CI and merge gate verified.
- [ ] Feature PR #407 squash-merged.
- [ ] Task archived through a separate lifecycle-only PR.

# PROVEN

- Governance task-start base: `blakinio/canary@264a86b1eddf5f68666281c47489166f343c3e84`.
- Latest re-fetched Canary `main` before finalization: `0c0972526814f099b51fd3481f28331b9434446d`.
- Target repository: `blakinio/Otheryn`; default branch: `main`; write authorization: explicitly granted by the user for autonomous OAM work.
- Target task-start SHA: `7d1e9cc5b4e799d31ae481b9a65e3f1442ca985e`.
- Exact OAM-002 upstream baseline: `a879c9312e34381e8eedf397b8ed44510698b689`; upstream tree: `dfdd43a63cfb26dcc6d0c42a55f71f815aae2fff`.
- Original target recursive tree manifest had 32 entries versus 6326 upstream entries, so the manual upload was rejected as an exact bootstrap.
- Target PR #1 passed exact-head `CI`, `Repository Audit`, `autofix.ci` and `Required`, then squash-merged as `b63fa0dd1efcaab4257a6557d6711b1965dce8e8`.
- Target PR #2 restored `.github/workflows/reusable-checks.yml` exactly to upstream blob `045c987911cae6ec9cb321c550b5ea0aad34a920`, passed exact-head `CI` and `Required`, then squash-merged as final target baseline `3cc7c1dfea747bb380f3761ee7ff7ac30141a115`.
- Closed, unmerged target PR #3 provided post-merge read-only proof that final target content equals pinned upstream everywhere except exactly `.github/workflows/required.yml` and `.github/workflows/reusable-docker-quickstart-smoke.yml`.
- The Docker delta only normalizes the mixed-case target repository name for the PR image tag; the other delta is the target repository's explicit `Required` merge gate.
- OAM-002 changed no runtime/gameplay/database/protocol/Lua/datapack/map/client behavior and no canonical module migration disposition.
- `docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md` now records the established target identity, exact SHAs and bootstrap relationship.
- `docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md` now marks OAM-002 ready for governance merge/lifecycle and keeps OAM-003 blocked until completion.

# DERIVED

- The OAM-002 target identity and repository-level bootstrap evidence gate is satisfied.
- Final target provenance is exact pinned-upstream content plus two bounded target CI/governance deltas; final direct Git ancestry is not claimed because repository policy required squash merge.
- OAM-003 becomes eligible only after this feature PR merges and OAM-002 lifecycle archival completes; it remains a separate task.

# UNKNOWN

- None for OAM-002 target identity or baseline pinning.

# CONFLICT

- Target repository metadata indicated merge commits were allowed, but GitHub rejected an explicit merge-method attempt with `Merge commits are not allowed on this repository`. Squash delivery plus deterministic tree proof is the recorded provenance model.

# Failed approaches and rejected hypotheses

- Local cross-repository `git diff` was unavailable because the execution sandbox could not resolve `github.com`; hosted GitHub Actions recursive tree manifests replaced it.
- Manual `Add files via upload` history was rejected as provenance proof.
- Direct initial target ref creation at the upstream SHA failed before the upstream objects were present.
- Initial Actions-token bootstrap push was rejected because the token could not update workflow files; security policy was not weakened.
- The bootstrap Lua-binding-doc check initially compared the full imported tree to the 32-file target base; the checker's native pinned `--base` mode was used temporarily and then removed.
- Docker quickstart initially disagreed with the build workflow on mixed-case repository image naming; the verified target-only lowercase normalization fixed it.
- Temporary finalizer workflows in Canary did not self-run from connector-generated pushes; the durable contract/program files were updated directly through the GitHub Contents API and the temporary workflow was removed.
- An accidental temporary Canary marker file was created and removed; two mistaken existing-file create calls were rejected by GitHub. None remains in the final diff.

# Validation and CI

| Evidence | Result |
|---|---|
| Original target vs pinned upstream recursive tree manifests | rejected bootstrap candidate; 32 vs 6326 entries |
| Target PR #1 exact-head required checks | PASS |
| Target PR #1 merge | PASS; `b63fa0dd1efcaab4257a6557d6711b1965dce8e8` |
| Target PR #2 exact-head required checks | PASS |
| Target PR #2 merge | PASS; final target `3cc7c1dfea747bb380f3761ee7ff7ac30141a115` |
| Post-merge final-tree proof | PASS; exactly two persistent target CI/governance deltas |
| OAM architecture contract/program durable updates | complete on PR #407 |
| Canonical module dispositions | unchanged; all `REVALIDATE` |

# Risks and compatibility

- Runtime/game behavior: unchanged by OAM-002.
- Protocol/client coupling: none introduced.
- Map/datapack/assets: no migration or donor import.
- Legacy Canary remains evidence/governance source, not the target image.
- Residual branch `dudantas/oam-002-upstream-object-probe` may remain because no branch-delete action is exposed; it is not `main`, not a merged implementation branch and grants no migration authorization.

# Remaining work

1. Verify exact-current-head Canary PR #407 ownership/CI/review gates and merge when green; lifecycle archive follows separately.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T01:40:00+02:00
head: 0c0972526814f099b51fd3481f28331b9434446d
branch: docs/oam-002-target-baseline-pinning
pr: 407
status: ready
context_routes:
  - agent-governance
owned_paths:
  - docs/agents/tasks/active/CAN-20260716-oteryn-target-baseline-pinning.md
  - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
  - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
proven:
  - target repository is blakinio/Otheryn with explicit user write authorization
  - target task-start SHA is 7d1e9cc5b4e799d31ae481b9a65e3f1442ca985e
  - pinned upstream baseline is a879c9312e34381e8eedf397b8ed44510698b689
  - final target baseline is 3cc7c1dfea747bb380f3761ee7ff7ac30141a115
  - final target content equals pinned upstream except required.yml and reusable-docker-quickstart-smoke.yml
  - architecture contract and program record now contain the OAM-002 result
  - all canonical modules remain REVALIDATE
derived:
  - OAM-002 is ready for Canary feature merge gates
  - OAM-003 remains separate and blocked until OAM-002 lifecycle completion
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
blockers: []
next_action: Verify exact-current-head Canary PR #407 ownership, CI, changed files and review state; squash-merge if all gates pass.
```

# Completion

- Final status: ready
- Canary feature PR: #407
- Target bootstrap PR: `blakinio/Otheryn#1` merged
- Target cleanup PR: `blakinio/Otheryn#2` merged
- Target evidence PR: `blakinio/Otheryn#3` closed unmerged
- Final target baseline: `3cc7c1dfea747bb380f3761ee7ff7ac30141a115`
- Program record updated: yes
- Architecture contract updated: yes
- Catalogue updated: not applicable
- Changelog updated: not applicable
- Archived at: not archived
