---
task_id: CAN-20260724-validation-cost-policy
coordination_id: OTS-20260724-validation-cost-policy
status: implementing
agent: "GPT-5.6 Thinking"
branch: dudantas/validation-cost-policy
base_branch: main
created: 2026-07-24
updated: 2026-07-24
risk: low
related_pr: ""
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

Make validation proportional to the changed paths and risk. Preserve focused checks for non-build changes, require relevant compilation for build-affecting changes, reserve clean/full rebuilds for justified cases, and suspend Canary macOS compilation until explicitly re-enabled.

## Acceptance criteria

- Agent guidance does not require compilation for documentation-only or clearly non-build-affecting changes.
- C++, CMake, dependency, toolchain, ABI and platform changes still receive appropriate compilation and tests.
- Canary CI no longer invokes or requires the macOS build job.
- Linux, Windows, fast checks, Lua tests, Docker and required aggregation remain intact.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T08:00:00+02:00
branch: dudantas/validation-cost-policy
status: implementing
context_routes:
  - agent-governance
  - ci-repair
proven:
  - Current CI calls .github/workflows/reusable-build-macos.yml from the build-macos job.
  - Required currently treats build-macos as mandatory whenever full_matrix is selected.
derived:
  - Removing the caller and Required references suspends macOS compilation while keeping the reusable workflow available for future re-enablement.
unknown: []
conflicts: []
changed_paths:
  - docs/agents/tasks/active/CAN-20260724-validation-cost-policy.md
validation: []
blockers: []
next_action: Update the build/test matrix and CI caller, then inspect the exact branch diff and emitted checks.
```
