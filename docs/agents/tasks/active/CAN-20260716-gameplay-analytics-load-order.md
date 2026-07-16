---
task_id: CAN-20260716-gameplay-analytics-load-order
program_id: "CAN-PROGRAM-CI-REPAIR"
coordination_id: "CAN-20260716-incremental-ci-final-gate"
status: validating
agent: chatgpt-ci-repair
branch: fix/gameplay-analytics-load-order
base_branch: main
created: 2026-07-16T18:29:36+02:00
updated: 2026-07-16T18:49:42+02:00
last_verified_commit: "847e80caf93c40d0d52af07b3ae81f8fe72e1998"
risk: medium
related_issue: ""
related_pr: "429"
depends_on: []
blocks:
  - CAN-20260716-incremental-ci-final-gate
owned_paths:
  exclusive:
    - data-otservbr-global/scripts/lib/gameplay_analytics.lua
    - data-otservbr-global/scripts/lib/#gameplay_analytics_core.lua
    - data-otservbr-global/scripts/lib/gameplay_analytics_batching.lua
    - data-otservbr-global/scripts/lib/#gameplay_analytics_batching_impl.lua
    - data-otservbr-global/scripts/lib/gameplay_analytics_schema.lua
    - data-otservbr-global/scripts/lib/#gameplay_analytics_schema_impl.lua
    - data-otservbr-global/scripts/lib/gameplay_analytics_reliability.lua
    - data-otservbr-global/scripts/lib/#gameplay_analytics_reliability_impl.lua
    - data-otservbr-global/scripts/lib/gameplay_analytics_correctness.lua
    - data-otservbr-global/scripts/lib/#gameplay_analytics_correctness_impl.lua
    - data-otservbr-global/scripts/lib/gameplay_analytics_context.lua
    - data-otservbr-global/scripts/lib/#gameplay_analytics_context_impl.lua
    - tests/lua/test_gameplay_analytics_load_order.lua
    - tools/analytics/validate_gameplay_analytics.py
    - tools/analytics/validate_gameplay_analytics_context.py
    - tools/analytics/validate_gameplay_analytics_batching.py
    - tools/analytics/validate_gameplay_analytics_reliability.py
    - tools/analytics/validate_gameplay_analytics_correctness.py
    - docs/agents/tasks/active/CAN-20260716-gameplay-analytics-load-order.md
  shared:
    - docs/agents/CHANGELOG.md
  read_only:
    - .github/scripts/smoke_test_canary.py
    - .github/workflows/reusable-build-linux.yml
    - .github/workflows/reusable-tests-lua.yml
    - src/lua/scripts/scripts.cpp
modules_touched:
  - Global datapack gameplay analytics bootstrap
reuses:
  - existing GameplayAnalytics core implementation blob
  - existing extension implementation blobs
  - existing disabled-script `#` loader convention
  - existing Gameplay Analytics static validators
  - existing Lua test workflow
  - existing Global datapack runtime smoke
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Make gameplay analytics library loading deterministic and order-independent so the Global datapack runtime smoke cannot fail when extension files are enumerated before `gameplay_analytics.lua`.

# Acceptance criteria

- [ ] Core gameplay analytics loading is idempotent.
- [ ] Any public gameplay analytics entrypoint can bootstrap the complete analytics stack.
- [ ] Extension implementations load in the existing canonical order: core, context, schema, batching, reliability, correctness.
- [ ] Loading public entrypoints repeatedly does not overwrite installed extension wrappers.
- [ ] Preserved implementation files are skipped by automatic script discovery and loaded only through explicit `dofile` entrypoints.
- [ ] Static analytics validators continue to inspect the unchanged implementation bodies rather than treating loader entrypoints as implementations.
- [ ] No runtime smoke warning/error filter is weakened.
- [ ] Focused Lua validation covers extension-before-core and repeated entrypoint loading.
- [ ] Global datapack runtime smoke passes in CI on the exact PR head.

# Confirmed context

- PR #415 exact-head CI failed twice in `Build - Linux / Compile (linux-release)` at `Smoke test Global datapack runtime`.
- Both failures logged `GameplayAnalytics must be loaded before ...` from five extension libraries.
- The affected runtime files are outside PR #415 and require a separate narrow CI-repair PR.
- Current task-start `main` was `0507fc5de8049d712345f43db0b05a23a6577a8a`.
- Draft repair PR #429 targets the gameplay analytics bootstrap, focused regression, affected static-validator source paths and task/changelog governance.
- `Scripts::loadScripts` enumerates Lua files with `std::filesystem::recursive_directory_iterator` without sorting, so filesystem enumeration order is not a valid dependency.
- The same loader deliberately skips files whose filename starts with `#`; explicit `dofile` remains available to public loader entrypoints.
- The canonical Lua test workflow executes every `tests/lua/test_*.lua` with LuaJIT.
- Existing runtime composition order is core, context, schema, batching, reliability, correctness and is preserved by the deterministic loader.
- Draft CI #2810 passed its draft-allowed aggregate, but draft state does not prove ready-state Lua/heavy execution.
- Draft Agent Task Ownership #1672 failed because the checkpoint omitted required fields and used unsupported checkpoint status `active`.
- Draft Agent Task Ownership #1674 then narrowed to one remaining governance defect: frontmatter status `active` is unsupported for a record under `tasks/active`; this update changes it to `validating`.
- Draft Gameplay Analytics #138 and Dry Run #27 failed because static validators still read public loader paths as implementation files.
- The five affected validators now point to the byte-for-byte preserved implementation bodies while retaining all original validation assertions.
- Gameplay Analytics Spell Telemetry #52 and Supply and Loot Telemetry #48 passed on the earlier draft head.
- No open PR or issue matching gameplay analytics load-order repair was found through available GitHub search; negative code-search results are not treated as proof of absence.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T18:49:42+02:00
head: 847e80caf93c40d0d52af07b3ae81f8fe72e1998
branch: fix/gameplay-analytics-load-order
pr: 429
status: validating
context_routes:
  - lua-data
  - ci-repair
owned_paths:
  - data-otservbr-global/scripts/lib/gameplay_analytics.lua
  - data-otservbr-global/scripts/lib/#gameplay_analytics_core.lua
  - data-otservbr-global/scripts/lib/gameplay_analytics_batching.lua
  - data-otservbr-global/scripts/lib/#gameplay_analytics_batching_impl.lua
  - data-otservbr-global/scripts/lib/gameplay_analytics_schema.lua
  - data-otservbr-global/scripts/lib/#gameplay_analytics_schema_impl.lua
  - data-otservbr-global/scripts/lib/gameplay_analytics_reliability.lua
  - data-otservbr-global/scripts/lib/#gameplay_analytics_reliability_impl.lua
  - data-otservbr-global/scripts/lib/gameplay_analytics_correctness.lua
  - data-otservbr-global/scripts/lib/#gameplay_analytics_correctness_impl.lua
  - data-otservbr-global/scripts/lib/gameplay_analytics_context.lua
  - data-otservbr-global/scripts/lib/#gameplay_analytics_context_impl.lua
  - tests/lua/test_gameplay_analytics_load_order.lua
  - tools/analytics/validate_gameplay_analytics.py
  - tools/analytics/validate_gameplay_analytics_context.py
  - tools/analytics/validate_gameplay_analytics_batching.py
  - tools/analytics/validate_gameplay_analytics_reliability.py
  - tools/analytics/validate_gameplay_analytics_correctness.py
  - docs/agents/tasks/active/CAN-20260716-gameplay-analytics-load-order.md
  - docs/agents/CHANGELOG.md
proven:
  - PR 415 exact-head Linux release build succeeds before the Global datapack smoke step.
  - The Global datapack smoke fails on gameplay analytics extension load-order errors.
  - Five extension files fail closed when GameplayAnalytics is nil.
  - Existing implementation blobs are preserved byte-for-byte behind deterministic public loader files.
  - Automatic script discovery skips filenames beginning with `#`.
  - Lua Tests runs `tests/lua/test_*.lua` through LuaJIT.
  - Existing runtime composition order is core, context, schema, batching, reliability, correctness.
  - Draft CI 2810 completed successfully under draft-allowed aggregation.
  - Draft Spell Telemetry 52 and Supply and Loot Telemetry 48 completed successfully.
  - Ownership 1674 reduced the task-record failure to unsupported frontmatter status active; this update sets validating.
  - Five static validators retain their original assertions and now read the preserved implementation paths.
derived:
  - A single master loader can make both core and extension composition order deterministic regardless of which public entrypoint is enumerated first while preserving the existing layer order.
unknown:
  - Exact workflow results on validator-adaptation head 847e80caf93c40d0d52af07b3ae81f8fe72e1998 are pending.
conflicts: []
first_failure:
  marker: PR 415 CI 2791 / Build - Linux / Smoke test Global datapack runtime
  evidence: Five gameplay analytics extension libraries raised GameplayAnalytics must be loaded before errors; one allowed rerun failed identically.
rejected_hypotheses:
  - The first Global datapack smoke failure was transient; the one allowed rerun failed at the same step with the same class of load-order errors.
  - Bootstrapping only the core is sufficient; analytics extensions wrap shared functions and must also compose in one deterministic canonical order.
  - Filesystem or lexical enumeration order can be relied on; the repository loader uses unsorted recursive_directory_iterator and explicitly skips only filenames beginning with #.
changed_paths:
  - data-otservbr-global/scripts/lib/#gameplay_analytics_batching_impl.lua
  - data-otservbr-global/scripts/lib/#gameplay_analytics_context_impl.lua
  - data-otservbr-global/scripts/lib/#gameplay_analytics_core.lua
  - data-otservbr-global/scripts/lib/#gameplay_analytics_correctness_impl.lua
  - data-otservbr-global/scripts/lib/#gameplay_analytics_reliability_impl.lua
  - data-otservbr-global/scripts/lib/#gameplay_analytics_schema_impl.lua
  - data-otservbr-global/scripts/lib/gameplay_analytics.lua
  - data-otservbr-global/scripts/lib/gameplay_analytics_batching.lua
  - data-otservbr-global/scripts/lib/gameplay_analytics_context.lua
  - data-otservbr-global/scripts/lib/gameplay_analytics_correctness.lua
  - data-otservbr-global/scripts/lib/gameplay_analytics_reliability.lua
  - data-otservbr-global/scripts/lib/gameplay_analytics_schema.lua
  - docs/agents/tasks/active/CAN-20260716-gameplay-analytics-load-order.md
  - tests/lua/test_gameplay_analytics_load_order.lua
  - tools/analytics/validate_gameplay_analytics.py
  - tools/analytics/validate_gameplay_analytics_batching.py
  - tools/analytics/validate_gameplay_analytics_context.py
  - tools/analytics/validate_gameplay_analytics_correctness.py
  - tools/analytics/validate_gameplay_analytics_reliability.py
validation:
  - command: PR 429 draft CI 2810
    result: PASS
    evidence: Draft-allowed CI aggregate completed successfully; this is not accepted as ready-state Lua or heavy runtime evidence.
  - command: PR 429 Agent Task Ownership 1672
    result: FAIL
    evidence: Checkpoint schema omitted changed_paths, first_failure, rejected_hypotheses and validation and used unsupported checkpoint status active; checkpoint schema fields were added.
  - command: PR 429 Agent Task Ownership 1674
    result: FAIL
    evidence: The remaining task-record defect is frontmatter status active for a record under tasks/active; this update changes it to validating.
  - command: PR 429 Gameplay Analytics 138 and Gameplay Analytics Dry Run 27
    result: FAIL
    evidence: Existing static validators pointed at public gameplay analytics files that are now loader entrypoints; implementation bodies remain byte-for-byte preserved under disabled # implementation paths and validator paths have now been adapted without removing assertions.
  - command: PR 429 Gameplay Analytics Spell Telemetry 52 and Supply and Loot Telemetry 48
    result: PASS
    evidence: Both focused analytics workflows completed successfully on draft head a63ed2a03b2cf02398d1a8424e2c7dbd7a3b1884.
blockers: []
next_action: Verify exact-head draft workflows after validator and governance repairs; if green, batch the changelog/final checkpoint, mark PR 429 ready, and require real ready-state Lua plus Linux Global datapack smoke before merge.
```
