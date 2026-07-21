---
task_id: CAN-20260721-e2e-controlled-otclient-build-stability
program_id: CAN-PROGRAM-E2E-PLATFORM
coordination_id: E2E-CONTROLLED-OTCLIENT-BUILD-STABILITY
status: complete
agent: "GPT-5.6 Thinking"
branch: fix/e2e-controlled-otclient-build-stability
base_branch: main
created: 2026-07-21
updated: 2026-07-21
last_verified_commit: "c3e774e484de5df40e0fc1c4e74fea9fc36a940f"
risk: low
related_issue: ""
related_pr: "687"
depends_on:
  - merged Universal physical E2E platform PR #245
blocks: []
owned_paths:
  exclusive: []
  read_only:
    - .github/workflows/universal-agent-e2e.yml
    - tests/e2e/test_controlled_otclient_build_workflow.py
    - docs/agents/programs/E2E_AUTOMATION_PROGRAM.md
    - docs/architecture/universal-e2e-gameplay-validation.md
    - tools/e2e/run_physical_e2e.sh
public_interfaces: []
cross_repo_tasks: []
---

# CAN-20260721 — controlled OTClient build stability

## Status

COMPLETE — the controlled OTClient build-stability repair merged through PR #687.

## Delivered

- Isolated the Universal E2E blocker to repeated HTTP 504 responses while pinned vcpkg downloaded FreeType 2.14.3 from `gitlab.freedesktop.org` before OTClient compilation.
- Rejected bounded build parallelism and workflow-level retries as sufficient fixes using retained exact failure evidence.
- Proved the `freetype/freetype` GitHub `VER-2-14-3` archive has the exact SHA512 required by the pinned vcpkg FreeType port.
- Pre-seeded only the standard vcpkg downloads cache with that verified mirror archive while preserving the pinned OTClient revision, vcpkg baseline, FreeType port semantics and original pinned `run-cmake` contract.
- Retained fallback provenance in successful controlled-OTClient artifacts and failure diagnostics.
- Added focused workflow-contract coverage for source pinning, exact hash/cache placement, unchanged build contract, diagnostics, provenance and unrelated route behavior.
- Restored exact-head Universal Physical E2E availability and unblocked PR #685 E2E-GAMEPLAY-003.

## Merge evidence

- Feature PR: #687 — `fix(e2e): stabilize controlled OTClient build`.
- Final feature head: `c3e774e484de5df40e0fc1c4e74fea9fc36a940f`.
- Squash merge: `5b6b904106856b861676bc7f4eaf52b34ddcef87`.
- Implementation-head Agent Task Ownership run `29867906121`: success.
- Implementation-head CI run `29867906077`: success.
- Implementation-head Universal Agent E2E run `29867906420`: success; controlled OTClient build plus physical `login/relog` and Required physical E2E passed.
- Successful OTClient artifact `8510661114` retained verified GitHub-mirror fallback provenance.
- Final-checkpoint Agent Task Ownership run `29870291710`: success.
- Final-gate autofix.ci run `29870291786`: success.
- Final-gate CI run `29870292311`: success across the full required matrix.
- Final-checkpoint Universal Agent E2E run `29870291947`: success; verified fallback, controlled OTClient build, physical `login/relog` and Required physical E2E all passed.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-21T23:59:00+02:00
head: c3e774e484de5df40e0fc1c4e74fea9fc36a940f
branch: fix/e2e-controlled-otclient-build-stability
pr: 687
status: complete
context_routes:
  - universal-e2e
  - ci-repair
owned_paths: []
proven:
  - PR #687 merged to main as 5b6b904106856b861676bc7f4eaf52b34ddcef87.
  - the first failure was a pinned vcpkg FreeType 2.14.3 source download returning repeated HTTP 504 before OTClient compilation.
  - bounded parallelism and workflow-level retries were tested and rejected as sufficient fixes.
  - GitHub freetype/freetype VER-2-14-3 archive SHA512 exactly matches the pinned vcpkg port expectation.
  - final workflow pre-seeds only the standard vcpkg downloads cache and preserves the pinned OTClient revision, vcpkg baseline, port semantics and original run-cmake contract.
  - implementation-head Universal Agent E2E 29867906420 restored a successful controlled OTClient build and physical login/relog lifecycle.
  - final-gate CI 29870292311, ownership 29870291710, autofix 29870291786 and Universal Agent E2E 29870291947 all succeeded on exact final head c3e774e484de5df40e0fc1c4e74fea9fc36a940f.
  - PR #685 E2E-GAMEPLAY-003 is no longer blocked by controlled OTClient build availability.
derived:
  - verified vcpkg download-cache pre-seeding is the narrowest repair because identical source bytes are supplied without changing client or dependency semantics.
unknown: []
conflicts: []
first_failure:
  marker: none on accepted final feature head
  evidence: final-checkpoint Universal Agent E2E 29870291947 completed the controlled OTClient build and physical login/relog gate successfully
rejected_hypotheses:
  - modify PR #685 NPC scenario to repair a pre-physical infrastructure failure
  - change the pinned OTClient revision
  - treat build parallelism or retries alone as sufficient
  - replace or fork the pinned vcpkg FreeType port
changed_paths:
  - .github/workflows/universal-agent-e2e.yml
  - tests/e2e/test_controlled_otclient_build_workflow.py
  - docs/agents/tasks/archive/CAN-20260721-e2e-controlled-otclient-build-stability.md
validation:
  - command: GitHub Actions Agent Task Ownership run 29870291710
    result: PASS
    evidence: final checkpoint ownership and governance passed on exact final feature head
  - command: GitHub Actions CI run 29870292311
    result: PASS
    evidence: full final-gate CI completed successfully on exact final feature head
  - command: GitHub Actions Universal Agent E2E run 29870291947
    result: PASS
    evidence: verified fallback, controlled OTClient build, physical login/relog and Required physical E2E passed
  - command: GitHub squash merge PR #687
    result: PASS
    evidence: feature merged as 5b6b904106856b861676bc7f4eaf52b34ddcef87
blockers: []
next_action: Resume PR #685 E2E-GAMEPLAY-003 from current main, rerun its physical Canary NPC promotion scenario with the merged controlled-OTClient fallback, and do not continue PR #687 or its feature branch.
```
