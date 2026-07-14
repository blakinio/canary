---
task_id: CAN-20260714-table-unserialize-security
program_id: CAN-PROGRAM-CRYSTALSERVER-COMPARISON
coordination_id: CS-007
status: active
agent: "GPT-5.6 Thinking"
branch: security/table-unserialize-safe
base_branch: main
created: 2026-07-14T12:45:00+02:00
updated: 2026-07-14T12:45:00+02:00
last_verified_commit: "06f8ba4464d6a18ad48445737444bab5b3a2efcb"
risk: high
related_issue: ""
related_pr: "pending"
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
    - .github/workflows/reusable-tests-lua.yml
modules_touched:
  - Lua table serialization boundary
reuses:
  - existing `table.serialize` canonical output
  - existing standalone Lua test workflow
public_interfaces:
  - "table.serialize(value) -> string"
  - "table.unserialize(serialized) -> value"
cross_repo_tasks: []
---

# Goal

Determine whether current Canary's `table.unserialize` execution boundary is reachable with untrusted or persistence-derived data, define the exact compatibility grammar produced by `table.serialize`, and implement only the smallest safe behavior justified by deterministic evidence.

# Candidate evidence

- CrystalServer commit: `891685169745e46f665069edcc35847f0704aa21`, PR #816.
- Current Canary `data/libs/functions/tables.lua` still executes `loadstring("return " .. str)()`.
- The donor recursive parser is evidence only and must not be copied without independent correctness and compatibility proof.

# Acceptance criteria

- [ ] Inventory every tracked `table.serialize`, `table.unserialize`, direct `loadstring` and persisted-string call site with exact paths and lines.
- [ ] Classify every unserialize input by provenance and attacker control; absence of indexed search results is not evidence.
- [ ] Define the exact serialization grammar and round-trip corpus for strings, numbers, booleans, nil, mixed/nested tables and key types.
- [ ] Add a deterministic exploit regression proving the current helper can execute code.
- [ ] Reject arbitrary Lua expressions, function calls, statements, trailing code and malformed input without executing them.
- [ ] Preserve all evidence-backed outputs produced by current `table.serialize` or document a concrete compatibility hold.
- [ ] Do not copy CrystalServer's whitespace-stripping parser or weaken errors/tests to obtain green CI.
- [ ] Run standalone Lua validation plus selected repository CI on the exact final head.
- [ ] No client, protocol, database schema, map, item, asset or production-config changes.
- [ ] Update program/catalogue/changelog and archive in a separate cleanup PR after final outcome.

# Work log

## 2026-07-14T12:45:00+02:00

- Refreshed main at `06f8ba4464d6a18ad48445737444bab5b3a2efcb` after merged/archived CS-006.
- Reviewed open PRs; no current PR owns `data/libs/functions/tables.lua` or the proposed test/report paths.
- Confirmed the unsafe current implementation and opened the exact CrystalServer bundled diff.
- Local Git/build remains unavailable because this session cannot resolve GitHub; GitHub API/Actions will be recorded as execution evidence.

# Decisions

| Decision | Reason |
|---|---|
| Keep CS-007 independent from CS-006 | Directory shell execution and Lua data decoding have different compatibility and denial-of-service boundaries. |
| Audit before parser design | A safe decoder must match actual persisted/call-site grammar, not donor assumptions. |
| Treat donor parser as untrusted | It removes all whitespace, accepts incomplete constructs and does not prove round-trip compatibility. |

# Remaining work

1. Publish the draft PR and run a bounded full-checkout audit.
2. Classify call sites and build a failing exploit/round-trip corpus.
3. Select a safe architecture only after evidence review.
4. Validate and merge or record a justified compatibility blocker.

# Handoff

Read this task, the CrystalServer commit, current `tables.lua`, the generated CS-007 reports and all exact call sites. Never classify unresolved provenance as safe, and never replace `loadstring` with a parser that silently corrupts valid serialized data.
