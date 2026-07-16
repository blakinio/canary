---
task_id: CAN-20260716-gameplay-analytics-load-order
program_id: "CAN-PROGRAM-CI-REPAIR"
coordination_id: "CAN-20260716-incremental-ci-final-gate"
status: active
agent: chatgpt-ci-repair
branch: fix/gameplay-analytics-load-order
base_branch: main
created: 2026-07-16T18:29:36+02:00
updated: 2026-07-16T18:32:41+02:00
last_verified_commit: "f2405c074551811cebe2c25774eb01e0e65a976b"
risk: medium
related_issue: ""
related_pr: "429"
depends_on: []
blocks:
  - CAN-20260716-incremental-ci-final-gate
owned_paths:
  exclusive:
    - data-otservbr-global/scripts/lib/gameplay_analytics.lua
    - data-otservbr-global/scripts/lib/gameplay_analytics_core.lua
    - data-otservbr-global/scripts/lib/gameplay_analytics_batching.lua
    - data-otservbr-global/scripts/lib/gameplay_analytics_batching_impl.lua
    - data-otservbr-global/scripts/lib/gameplay_analytics_schema.lua
    - data-otservbr-global/scripts/lib/gameplay_analytics_schema_impl.lua
    - data-otservbr-global/scripts/lib/gameplay_analytics_reliability.lua
    - data-otservbr-global/scripts/lib/gameplay_analytics_reliability_impl.lua
    - data-otservbr-global/scripts/lib/gameplay_analytics_correctness.lua
    - data-otservbr-global/scripts/lib/gameplay_analytics_correctness_impl.lua
    - data-otservbr-global/scripts/lib/gameplay_analytics_context.lua
    - data-otservbr-global/scripts/lib/gameplay_analytics_context_impl.lua
    - docs/agents/tasks/active/CAN-20260716-gameplay-analytics-load-order.md
  shared:
    - docs/agents/CHANGELOG.md
  read_only:
    - .github/scripts/smoke_test_canary.py
    - .github/workflows/reusable-build-linux.yml
modules_touched:
  - Global datapack gameplay analytics bootstrap
reuses:
  - existing GameplayAnalytics core implementation blob
  - existing extension implementation blobs
  - existing Global datapack runtime smoke
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Make gameplay analytics library loading deterministic and order-independent so the Global datapack runtime smoke cannot fail when extension files are enumerated before `gameplay_analytics.lua`.

# Acceptance criteria

- [ ] Core gameplay analytics loading is idempotent.
- [ ] Each gameplay analytics extension can bootstrap the core when it is loaded first.
- [ ] Loading the core again after an extension does not overwrite installed extension wrappers.
- [ ] No runtime smoke warning/error filter is weakened.
- [ ] Focused validation covers extension-before-core and repeated-core loading.
- [ ] Global datapack runtime smoke passes in CI on the exact PR head.

# Confirmed context

- PR #415 exact-head CI failed twice in `Build - Linux / Compile (linux-release)` at `Smoke test Global datapack runtime`.
- Both failures logged `GameplayAnalytics must be loaded before ...` from five extension libraries.
- The affected runtime files are outside PR #415 and require a separate narrow CI-repair PR.
- Current `main` is `0507fc5de8049d712345f43db0b05a23a6577a8a`.
- Draft repair PR #429 targets only the gameplay analytics bootstrap plus task/changelog governance.
- No open PR or issue matching gameplay analytics load-order repair was found through available GitHub search; negative code-search results are not treated as proof of absence.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T18:32:41+02:00
head: f2405c074551811cebe2c25774eb01e0e65a976b
branch: fix/gameplay-analytics-load-order
pr: 429
status: active
context_routes:
  - lua-data
  - ci-repair
owned_paths:
  - data-otservbr-global/scripts/lib/gameplay_analytics.lua
  - data-otservbr-global/scripts/lib/gameplay_analytics_core.lua
  - data-otservbr-global/scripts/lib/gameplay_analytics_batching.lua
  - data-otservbr-global/scripts/lib/gameplay_analytics_batching_impl.lua
  - data-otservbr-global/scripts/lib/gameplay_analytics_schema.lua
  - data-otservbr-global/scripts/lib/gameplay_analytics_schema_impl.lua
  - data-otservbr-global/scripts/lib/gameplay_analytics_reliability.lua
  - data-otservbr-global/scripts/lib/gameplay_analytics_reliability_impl.lua
  - data-otservbr-global/scripts/lib/gameplay_analytics_correctness.lua
  - data-otservbr-global/scripts/lib/gameplay_analytics_correctness_impl.lua
  - data-otservbr-global/scripts/lib/gameplay_analytics_context.lua
  - data-otservbr-global/scripts/lib/gameplay_analytics_context_impl.lua
  - docs/agents/tasks/active/CAN-20260716-gameplay-analytics-load-order.md
  - docs/agents/CHANGELOG.md
proven:
  - PR 415 exact-head Linux release build succeeds before the Global datapack smoke step.
  - The Global datapack smoke fails on gameplay analytics extension load-order errors.
  - Five extension files fail closed when GameplayAnalytics is nil.
  - Existing implementation blobs can be preserved byte-for-byte behind small deterministic loader files.
derived:
  - Extension loading must not depend on filesystem enumeration order.
unknown:
  - Whether an existing focused Lua test harness covers direct library load order.
conflicts: []
blockers: []
next_action: Replace the six public library entrypoints with deterministic loaders backed by the preserved implementation blobs, then validate PR 429.
```
