---
task_id: CAN-20260714-table-unserialize-security
program_id: CAN-PROGRAM-CRYSTALSERVER-COMPARISON
coordination_id: CS-007
status: active
agent: "GPT-5.6 Thinking"
branch: security/table-unserialize-safe
base_branch: main
created: 2026-07-14T12:45:00+02:00
updated: 2026-07-14T13:20:00+02:00
last_verified_commit: "79f9e327da4e4a4b2ba7e5f896cbe4df69139cc5"
risk: high
related_issue: ""
related_pr: "#328"
depends_on:
  - "CAN-PROGRAM-CRYSTALSERVER-COMPARISON Stage 1 / PR #291"
  - "CS-006 completed and archived through PRs #326/#327"
blocks: []
owned_paths:
  exclusive:
    - data/libs/functions/tables.lua
    - tests/lua/test_tables.lua
    - docs/agents/tasks/active/CAN-20260714-table-unserialize-security.md
    - artifacts/upstream/crystalserver/CS007_TABLE_UNSERIALIZE_AUDIT.md
    - artifacts/upstream/crystalserver/cs007_table_unserialize_audit.json
  shared:
    - docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md
    - docs/agents/CHANGELOG.md
    - docs/agents/MODULE_CATALOG.md
  read_only:
    - AGENTS.md
    - docs/agents/README.md
    - docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md
    - docs/agents/REAL_TIBIA_PARITY_PLAYBOOK.md
    - docs/agents/BUILD_TEST_MATRIX.md
    - docs/agents/CROSS_REPO_CONTRACTS.md
    - data/libs/functions/functions.lua
    - .github/workflows/reusable-tests-lua.yml
modules_touched:
  - Lua table serialization boundary
reuses:
  - existing `table.serialize` canonical output
  - existing standalone Lua test workflow
public_interfaces:
  - "table.serialize(value) -> string"
  - "table.unserialize(serialized) -> value[, errorMessage]"
cross_repo_tasks: []
---

# Goal

Remove arbitrary Lua evaluation from `table.unserialize` with the smallest strict data parser justified by current Canary evidence, while preserving valid serialized values and explicitly separating unrelated serializer/helper defects.

# Candidate evidence

- CrystalServer commit `891685169745e46f665069edcc35847f0704aa21`, PR #816, is donor evidence only.
- Baseline Canary executed `loadstring("return " .. str)()`.
- Audit reports:
  - `artifacts/upstream/crystalserver/CS007_TABLE_UNSERIALIZE_AUDIT.md`;
  - `artifacts/upstream/crystalserver/cs007_table_unserialize_audit.json`.
- Full checkout audit scanned 6,894 tracked files and 6,858 text files.
- The baseline exploit executed successfully, proving arbitrary evaluation at the public helper boundary but not remote exploitability.
- Focused post-workflow inventory found no tracked production call site for `table.unserialize` or the separate `unserializeTable` helper.

# Acceptance criteria

- [x] Inventory every tracked `table.serialize`, `table.unserialize`, direct `loadstring` and relevant persisted-string call site with exact paths and lines.
- [x] Classify every decoder input by provenance; both public helpers are dormant in tracked production code.
- [x] Define the accepted data grammar and compatibility corpus for strings, finite numbers, booleans, nil, mixed/nested tables and key types.
- [x] Add a deterministic exploit regression proving the baseline helper executes code and the replacement does not.
- [x] Reject arbitrary Lua expressions, globals, function calls, statements, comments, trailing code and malformed input without executing them.
- [x] Preserve evidence-backed valid output from `table.serialize`; record the pre-existing false-value corruption separately.
- [x] Do not copy CrystalServer's whitespace-stripping parser or weaken tests.
- [x] Enforce 1 MiB input, depth 64 and 100,000 parsed-value limits.
- [x] Focused validator run `29327491822` passes all 14 standalone tests and confirms no `load`/`loadstring` in `tables.lua`.
- [ ] Refresh onto exact current main, integrate shared documentation and pass Ready-state repository CI.
- [x] No client, protocol, database schema, map, item, asset or production-config changes.
- [ ] Archive in a separate cleanup PR after merge.

# Final design

- Accepted scalars: `nil`, booleans, finite decimal/exponent numbers and quoted strings.
- Accepted aggregates: nested tables with bracketed keys and bounded implicit array entries.
- String handling preserves whitespace and implements canonical Lua escapes, decimal byte escapes, hexadecimal escapes and escaped newlines.
- Whitespace is ignored only between tokens.
- The parser must consume the complete input.
- Invalid input returns `nil, errorMessage`; successful callers reading only the first return retain the existing value contract.
- The parser never calls `load`, `loadstring`, `setfenv`, bytecode or any global named by the input.

# Work log

## 2026-07-14T12:45:00+02:00

- Refreshed main at `06f8ba4464d6a18ad48445737444bab5b3a2efcb` after merged/archived CS-006.
- Reviewed open PRs; no active task owns `data/libs/functions/tables.lua` or the focused test/report paths.
- Confirmed the unsafe current implementation and opened the exact CrystalServer bundled diff.
- Local Git/build remains unavailable because this session cannot resolve GitHub; GitHub API/Actions are the execution evidence.

## 2026-07-14T13:00:00+02:00

- Audit v3 run `29326420697` passed after two earlier probes exposed the pre-existing `table.serialize(false)` corruption rather than a decoder failure.
- Focused inventory run `29326629631` passed after excluding temporary workflows/reports.
- `table.unserialize` occurs only as its definition plus task documentation.
- `unserializeTable` occurs only as its definition; it has a different serializer/copy contract.
- Reclassified CS-007 from `PARTIAL_VALUE` to `VALID_FIX_MISSING`: the dangerous primitive is deterministic, even though no default runtime call site is tracked.

## 2026-07-14T13:20:00+02:00

- Added the regression first. Diagnostic run captured the expected baseline result: zero passed, fourteen failed because the old helper reached `loadstring`; non-string input also preserved the old concatenation failure.
- Added the independent strict parser without modifying `table.serialize`, `serializeTable` or `unserializeTable`.
- Focused validator run `29327491822` passed all fourteen cases and the no-dynamic-loader scan.
- Removed every temporary validator/runner and the diagnostic failure log from the intended final diff.

# Decisions

| Decision | Reason |
|---|---|
| Keep CS-007 independent from CS-006 | Directory shell execution and Lua data decoding have different compatibility and denial-of-service boundaries. |
| Replace evaluation with a parser | Sandboxing compiled Lua still permits hostile computation and is not a data grammar. |
| Reject the donor parser | Global whitespace removal corrupts strings and its grammar/resource behavior is not proven. |
| Support implicit array entries | It safely preserves a useful subset of historical Lua table-constructor inputs without enabling identifiers or expressions. |
| Return `nil, errorMessage` on invalid input | The first-return success contract remains stable while failures become deterministic and non-executing. |
| Keep serializer defects out | `table.serialize(false)` and nil handling are distinct output/persistence questions. |
| Keep `unserializeTable` out | It has a separate serializer and output-copy contract; changing both would hide compatibility risk. |

# Follow-up findings excluded from CS-007

1. `table.serialize(false)` and false values nested in tables are serialized as `true` because the implementation tests the type string instead of the value. This needs an independent serializer-correctness and persisted-data review.
2. `unserializeTable` in `data/libs/functions/functions.lua` also uses dynamic `load`, but has no tracked call sites and a different serializer/copy contract.

# Validation

| Commit/run | Check | Result |
|---|---|---|
| baseline audit / `29326420697` | full inventory, round-trip mismatches and exploit probe | passed; exploit executed on baseline |
| focused inventory / `29326629631` | post-workflow identifier/call-site classification | passed |
| pre-patch diagnostic | new regression against old helper | expected failure: 0 passed, 14 failed via `loadstring` |
| `5322a404d11214d89e03f7291c052d387c700afc` / `29327491822` | fourteen standalone parser/security cases and no-loader grep | passed |

Never record `passed` without verification on the stated commit.

# Remaining work

1. Refresh branch from current main after the merged Real Tibia registry work.
2. Add the public boundary to current changelog/module catalogue without overwriting newer shared content.
3. Run exact-head ownership, autofix, Fast Checks, standalone Lua and selected full CI in Ready state.
4. Review final diff, comments, reviews, threads and current main; merge only the unchanged validated SHA.
5. Archive the task and close CS-007 in a separate lifecycle PR.

# Handoff

Read this task, PR #328, both CS-007 reports, `data/libs/functions/tables.lua` and `tests/lua/test_tables.lua`. Preserve full-input consumption, the resource limits and the no-dynamic-loader invariant. Do not bundle the serializer false-value defect or `unserializeTable` into this PR.
