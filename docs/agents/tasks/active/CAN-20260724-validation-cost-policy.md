---
task_id: CAN-20260724-validation-cost-policy
coordination_id: OTS-20260724-validation-cost-policy
status: active
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
updated_at: 2026-07-24T09:18:00+02:00
head: d239992744b79bb850c70501a0a241cc527b3155
branch: dudantas/validation-cost-policy
pr: 857
status: validating
context_routes:
  - agent-governance
  - ci-repair
owned_paths:
  - .github/workflows/ci.yml
  - docs/agents/BUILD_TEST_MATRIX.md
  - docs/agents/tasks/active/CAN-20260724-validation-cost-policy.md
proven:
  - BUILD_TEST_MATRIX.md now requires focused checks during individual steps and defers heavy builds until a coherent milestone or implementation package is complete.
  - Early compilation remains required for CMake/build manifests, source registration, dependencies, toolchains, generated compile inputs, public headers/ABI, required binaries or material compile-break risk.
  - The build-macos caller was removed from .github/workflows/ci.yml.
  - build-macos was removed from the Required job dependencies and required_builds evaluation.
  - .github/workflows/reusable-build-macos.yml remains available for a future explicit re-enable task.
  - PR 857 has the ci:final-gate label before the final checkpoint commits.
derived:
  - Normal Canary CI can no longer schedule or require the macOS build while Linux, Windows, Docker and focused checks retain their existing selection logic.
unknown:
  - Exact current-head CI conclusions until workflows complete.
conflicts: []
first_failure:
  marker: missing checkpoint fields
  evidence: Agent Task Ownership run 30073488939 reported only missing first_failure, head, owned_paths and rejected_hypotheses fields in this new task checkpoint.
rejected_hypotheses:
  - The initial ownership failure was not caused by the macOS CI removal or YAML syntax; its artifact identified only missing task-checkpoint fields.
changed_paths:
  - .github/workflows/ci.yml
  - docs/agents/BUILD_TEST_MATRIX.md
  - docs/agents/tasks/active/CAN-20260724-validation-cost-policy.md
validation:
  - command: exact PR patch and changed-file audit
    result: PASS
    evidence: PR 857 changes exactly the CI caller, build/test matrix and task record; macOS caller and Required references are absent while other job definitions remain intact.
  - command: Agent Task Ownership artifacts 8588910055, 8588948333 and 8589084281
    result: PASS
    evidence: Added required checkpoint fields, used a supported validation result and set active-task frontmatter status to active while retaining checkpoint status validating.
blockers: []
next_action: Verify the new exact-head ownership and CI runs, confirm no macOS job is emitted and require all remaining selected checks to pass.
```
