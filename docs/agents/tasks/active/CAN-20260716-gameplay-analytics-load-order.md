---
task_id: CAN-20260716-gameplay-analytics-load-order
program_id: "CAN-PROGRAM-CI-REPAIR"
coordination_id: "CAN-20260716-incremental-ci-final-gate"
status: review
agent: chatgpt-ci-repair
branch: fix/gameplay-analytics-load-order
base_branch: main
created: 2026-07-16T18:29:36+02:00
updated: 2026-07-16T19:02:20+02:00
last_verified_commit: "7da5fed6b69c14a3142bdb2f0f605cd54338286d"
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
    - tools/analytics/validate_gameplay_analytics_migrations.py
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
  - existing GameplayAnalytics implementation bodies
  - existing disabled-script `#` loader convention
  - existing Gameplay Analytics validators and tests
  - existing Global datapack runtime smoke
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Make Gameplay Analytics library loading deterministic and filesystem-order-independent without weakening analytics behavior, persistence contracts, tests, or fail-closed runtime smoke validation.

# Acceptance criteria

- [x] Any public analytics entrypoint can bootstrap the complete production stack.
- [x] Existing layer order remains core, context, schema, batching, reliability, correctness.
- [x] Repeated production entrypoint loading is idempotent and preserves wrappers.
- [x] Explicit decoration of a pre-existing analytics table retains prior isolated-extension semantics.
- [x] Original implementation bodies are preserved byte-for-byte behind auto-skipped `#` paths.
- [x] Static validators inspect the preserved implementation bodies without weakening assertions.
- [x] Focused public-entrypoint load-order regression is included in canonical Lua Tests.
- [x] Draft Gameplay Analytics, Dry Run, MariaDB integration, static validators, mocked Lua layer tests and ownership validation pass on the repaired code head.
- [ ] Ready-state exact-head Lua Tests execute and pass.
- [ ] Ready-state exact-head Linux release Global datapack runtime smoke executes and passes.
- [ ] Autonomous merge gate is clean and PR #429 is squash-merged.

# Confirmed context

- PR #415 exact-head CI #2791 failed twice at `Build - Linux / Compile (linux-release)` / `Smoke test Global datapack runtime` because five analytics extension files were enumerated before the core and raised `GameplayAnalytics must be loaded before ...`.
- `Scripts::loadScripts` uses unsorted `std::filesystem::recursive_directory_iterator`; filenames beginning with `#` are skipped by automatic Lua loading.
- The original core and five extension implementation blobs are preserved byte-for-byte under `#...` paths.
- The public master loader composes core, context, schema, batching, reliability and correctness in the pre-existing runtime order and becomes idempotent after completion.
- Public extension entrypoints bootstrap the full stack when no analytics table exists, while preserving historical isolated-decoration behavior for an explicitly pre-existing table used by focused layer tests.
- Six existing validators were retargeted only to the preserved implementation paths; their assertions remain intact.
- Draft code head `27e4d3e5a056cbab94f4ca7a715a287a0cd5e94d` passed Gameplay Analytics #145, Gameplay Analytics Dry Run #34, Agent Task Ownership #1679, CI #2817, Spell Telemetry #59, Supply and Loot Telemetry #55, OTBM Spawn/NPC #32 and Achievement Validation #285.
- Gameplay Analytics #145 passed all static validators, validator unit tests, mocked Lua context/batching/reliability/correctness/runtime-hook/schema tests and MariaDB integration.
- `main` advanced to `91d2b64ae914ef5d53d52dae873bcd2a71633371` only through OAM-004 lifecycle docs. Sync merge `7da5fed6b69c14a3142bdb2f0f605cd54338286d` is 0 behind current main, contains only the twenty repair paths relative to main, and adds only the two OAM lifecycle paths relative to the prior repair head.
- No upstream or donor repository was mutated.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T19:02:20+02:00
head: 7da5fed6b69c14a3142bdb2f0f605cd54338286d
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
  - tools/analytics/validate_gameplay_analytics_migrations.py
  - docs/agents/tasks/active/CAN-20260716-gameplay-analytics-load-order.md
  - docs/agents/CHANGELOG.md
proven:
  - PR 415 CI 2791 and its one allowed Linux-release rerun failed identically on analytics library load order.
  - Automatic script discovery is unsorted and skips filenames beginning with #.
  - Existing implementation blobs are preserved byte-for-byte.
  - Existing runtime composition order is preserved.
  - Draft Gameplay Analytics 145 passes all static, mocked Lua and MariaDB integration checks.
  - Draft Dry Run 34 and Ownership 1679 pass.
  - Sync merge 7da5fed6 is 0 behind main and preserves current-main OAM lifecycle content.
derived:
  - Deterministic master loading removes filesystem-order dependence while preserving existing wrapper composition and isolated-extension test semantics.
unknown:
  - Ready-state exact-head Lua Tests and Linux Global datapack smoke results after the final pre-ready checkpoint/changelog commit.
conflicts: []
first_failure:
  marker: PR 415 CI 2791 / Build - Linux / Smoke test Global datapack runtime
  evidence: Five extension libraries raised GameplayAnalytics must be loaded before errors; the one allowed rerun failed at the same step with the same class of errors.
rejected_hypotheses:
  - The failure was transient; the allowed rerun failed identically.
  - Core-only bootstrap is sufficient; extensions wrap shared APIs and require canonical composition order.
  - Filesystem enumeration order is reliable; source uses unsorted recursive_directory_iterator.
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
  - docs/agents/CHANGELOG.md
  - docs/agents/tasks/active/CAN-20260716-gameplay-analytics-load-order.md
  - tests/lua/test_gameplay_analytics_load_order.lua
  - tools/analytics/validate_gameplay_analytics.py
  - tools/analytics/validate_gameplay_analytics_batching.py
  - tools/analytics/validate_gameplay_analytics_context.py
  - tools/analytics/validate_gameplay_analytics_correctness.py
  - tools/analytics/validate_gameplay_analytics_migrations.py
  - tools/analytics/validate_gameplay_analytics_reliability.py
validation:
  - command: PR 429 Gameplay Analytics 145
    result: PASS
    evidence: All static validators, validator tests, mocked Lua layer tests, runtime-hook/schema tests and MariaDB integration passed on 27e4d3e5.
  - command: PR 429 Gameplay Analytics Dry Run 34
    result: PASS
    evidence: No-server/no-database analytics validation passed on 27e4d3e5.
  - command: PR 429 Agent Task Ownership 1679
    result: PASS
    evidence: Checkpoint validation, task ownership and rendered ownership index passed on 27e4d3e5.
  - command: PR 429 CI 2817
    result: PASS
    evidence: Draft-allowed CI aggregate passed on 27e4d3e5; ready-state heavy evidence is still required and this draft result is not substituted for it.
  - command: PR 429 focused analytics telemetry workflows
    result: PASS
    evidence: Spell Telemetry 59 and Supply/Loot Telemetry 55 passed on 27e4d3e5.
  - command: Sync with main 91d2b64a
    result: PASS
    evidence: 7da5fed6 is 0 behind main; main-to-head diff is exactly the twenty repair paths and old-head-to-sync diff is only two OAM lifecycle paths.
blockers: []
next_action: Mark PR 429 ready and verify the unchanged exact final head runs real Lua Tests and Linux release Global datapack smoke plus all required analytics/ownership/review gates; if clean, squash-merge PR 429 without any further checkpoint or changelog commit.
```
