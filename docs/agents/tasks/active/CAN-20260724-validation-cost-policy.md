---
task_id: CAN-20260724-validation-cost-policy
coordination_id: OTS-20260724-validation-cost-policy
status: validating
agent: "GPT-5.6 Thinking"
branch: dudantas/validation-cost-policy
base_branch: main
created: 2026-07-24
updated: 2026-07-24
risk: low
related_pr: "857"
depends_on: []
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260724-validation-cost-policy.md
    - docs/agents/BUILD_TEST_MATRIX.md
    - .github/workflows/ci.yml
  shared: []
  read_only: []
modules_touched:
  - agent-governance
  - ci
cross_repo_tasks:
  - OTH-20260724-validation-cost-policy
  - OTC-20260724-validation-cost-policy
  - OTERYN-20260724-validation-cost-policy
---

# Risk-based validation and macOS CI suspension

## Goal

Make validation proportional to the changed paths, risk and coherent project milestones. Preserve focused checks during individual steps, defer compilation until a phase or implementation package is complete, retain early builds for build-system or blocking-risk changes, and suspend Canary macOS compilation until explicitly re-enabled.

## Acceptance criteria

- Agent guidance does not require compilation for documentation-only or clearly non-build-affecting changes.
- Multi-step work uses focused checks during steps and heavy validation at coherent milestone completion.
- C++, CMake, dependency, toolchain, ABI and platform changes still receive appropriate compilation and tests.
- Canary CI no longer invokes or requires the macOS build job.
- Linux, Windows, fast checks, Lua tests, Docker and required aggregation remain intact.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T08:56:00+02:00
branch: dudantas/validation-cost-policy
pr: 857
status: validating
context_routes:
  - agent-governance
  - ci-repair
proven:
  - BUILD_TEST_MATRIX.md now requires focused checks during individual steps and defers heavy builds until a coherent milestone or implementation package is complete.
  - Early compilation remains required for CMake/build manifests, source registration, dependencies, toolchains, generated compile inputs, public headers/ABI, required binaries or material compile-break risk.
  - The build-macos caller was removed from .github/workflows/ci.yml.
  - build-macos was removed from the Required job dependencies and required_builds evaluation.
  - .github/workflows/reusable-build-macos.yml remains available for a future explicit re-enable task.
  - PR 857 has the ci:final-gate label before this final checkpoint commit.
derived:
  - Normal Canary CI can no longer schedule or require the macOS build while Linux, Windows, Docker and focused checks retain their existing selection logic.
unknown:
  - Exact current-head CI conclusions until PR 857 is marked ready and workflows complete.
conflicts: []
changed_paths:
  - .github/workflows/ci.yml
  - docs/agents/BUILD_TEST_MATRIX.md
  - docs/agents/tasks/active/CAN-20260724-validation-cost-policy.md
validation:
  - command: exact PR patch and changed-file audit
    result: PASS
    evidence: PR 857 changes exactly the CI caller, build/test matrix and task record; macOS caller and Required references are absent while other job definitions remain intact.
blockers: []
next_action: Mark PR 857 ready, verify the exact-head emitted jobs contain no macOS build and require all remaining selected checks to pass.
```
