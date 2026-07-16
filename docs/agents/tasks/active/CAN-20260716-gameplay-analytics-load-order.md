---
task_id: CAN-20260716-gameplay-analytics-load-order
program_id: "CAN-PROGRAM-CI-REPAIR"
coordination_id: "CAN-20260716-incremental-ci-final-gate"
status: implementing
agent: chatgpt-ci-repair
branch: fix/gameplay-analytics-load-order
base_branch: main
created: 2026-07-16T18:29:36+02:00
updated: 2026-07-16T18:49:42+02:00
last_verified_commit: "5159d835dd25bf2d9b61fa07732d6b8d16e3de29"
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

Make Gameplay Analytics library loading deterministic and order-independent without weakening analytics contracts or runtime smoke validation.

# Acceptance criteria

- [ ] Any public analytics entrypoint bootstraps the complete stack.
- [ ] Existing layer order remains core, context, schema, batching, reliability, correctness.
- [ ] Repeated public entrypoint loading is idempotent and preserves wrappers.
- [ ] Preserved implementation files are skipped by automatic discovery and explicitly loaded.
- [ ] Static validators inspect the preserved unchanged implementations.
- [ ] Focused Lua regression passes.
- [ ] Ready-state Lua Tests and Linux Global datapack runtime smoke pass on the exact PR head.
- [ ] No smoke warning/error filter, runtime safety, persistence, retry or schema assertion is weakened.

# Confirmed context

- PR #415 CI #2791 failed twice at Linux release Global datapack smoke with five `GameplayAnalytics must be loaded before ...` errors.
- `Scripts::loadScripts` uses unsorted `recursive_directory_iterator`; filenames beginning with `#` are skipped by automatic Lua loading.
- Original core and five extension blobs are preserved byte-for-byte under `#...` implementation paths.
- Public entrypoints now delegate to one idempotent master loader using the existing runtime layer order.
- Draft CI aggregates are green but are not accepted as ready-state heavy evidence.
- After adapting the first five validators, Gameplay Analytics #141 proves core/context/batching/reliability/correctness validation all pass; the next failure is migration validation because its schema-guard path still points to the public loader.
- Ownership failures were checkpoint-schema/status issues; canonical frontmatter active statuses are `planned`, `implementing`, `blocked`, `review`, `ready`, while checkpoint status supports `validating`.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-16T18:49:42+02:00
head: 5159d835dd25bf2d9b61fa07732d6b8d16e3de29
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
  - PR 415 exact-head Linux release build reaches Global datapack smoke before failing on analytics load order.
  - One allowed rerun failed identically, disproving a transient-only failure.
  - Automatic Lua discovery is unsorted and skips filenames beginning with #.
  - Existing implementation blobs are preserved byte-for-byte.
  - Existing runtime composition order is core, context, schema, batching, reliability, correctness.
  - Gameplay Analytics 141 passes core, context, batching, reliability and correctness validator steps.
  - Draft Spell Telemetry and Supply/Loot workflows pass.
derived:
  - Deterministic master loading removes filesystem-order dependence while preserving existing wrapper composition order.
unknown:
  - Exact result after adapting the migration validator schema-guard path.
conflicts: []
first_failure:
  marker: PR 415 CI 2791 / Build - Linux / Smoke test Global datapack runtime
  evidence: Five extension libraries raised GameplayAnalytics must be loaded before errors; one allowed rerun failed identically.
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
  - docs/agents/tasks/active/CAN-20260716-gameplay-analytics-load-order.md
  - tests/lua/test_gameplay_analytics_load_order.lua
  - tools/analytics/validate_gameplay_analytics.py
  - tools/analytics/validate_gameplay_analytics_batching.py
  - tools/analytics/validate_gameplay_analytics_context.py
  - tools/analytics/validate_gameplay_analytics_correctness.py
  - tools/analytics/validate_gameplay_analytics_reliability.py
validation:
  - command: PR 429 draft CI aggregates 2810-2814
    result: PASS
    evidence: Draft-allowed aggregates are green; they are not accepted as ready-state heavy evidence.
  - command: PR 429 Gameplay Analytics 141
    result: FAIL
    evidence: Core, context, batching, reliability and correctness validator steps pass; migration validator is the first failing step because schema guard moved behind a loader entrypoint.
  - command: PR 429 Gameplay Analytics Dry Run 30-31
    result: FAIL
    evidence: Static validation stops at the same migration-contract stage after the five earlier validator paths were repaired.
  - command: PR 429 Agent Task Ownership 1672-1676
    result: FAIL
    evidence: Successive failures isolated checkpoint schema then frontmatter lifecycle status; frontmatter is now set to implementing and checkpoint remains validating.
  - command: PR 429 focused Spell Telemetry and Supply/Loot workflows
    result: PASS
    evidence: Focused telemetry workflows pass on draft repair heads.
blockers: []
next_action: Point the migration validator at the preserved schema implementation, then re-run exact-head draft validation and continue until all task-owned failures are green.
```
