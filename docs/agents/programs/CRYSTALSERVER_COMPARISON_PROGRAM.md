---
program_id: CAN-PROGRAM-CRYSTALSERVER-COMPARISON
name: CrystalServer Comparison Program
status: active
owner: GPT-5.6 Thinking
created: 2026-07-13T21:01:05Z
updated: 2026-07-13T21:01:05Z
last_verified_commit: "360d79ebad5802edd4d89e99d0f210ab19b36b60"
primary_paths:
  - docs/agents/programs/CRYSTALSERVER_COMPARISON_PROGRAM.md
  - artifacts/upstream/crystalserver/**
shared_integration_paths: []
related_programs: []
cross_repo_contracts: []
---

# Mission

Continuously compare `zimbadev/crystalserver` with current `blakinio/canary`, using CrystalServer only as a read-only source of candidates. Accept, adapt, reject, or defer each candidate from independent evidence about current Canary behavior, tests, architecture, protocol compatibility, active work, and runtime risk.

# Repository and baseline register

Analysis date: 2026-07-13.

| Role | Repository | Baseline `main` SHA | Declared server version | Declared client protocol | Access |
|---|---|---|---|---:|---|
| target | `blakinio/canary` | `360d79ebad5802edd4d89e99d0f210ab19b36b60` | `3.6.1` | `1525` / 15.25 | write through task branches and PRs only |
| comparison | `zimbadev/crystalserver` | `fc0d53b9f9965463b6082c07e6d3d482294541a7` | `4.1.9` | `1525` / 15.25 | read-only |
| reference | `opentibiabr/canary` | `9365c1c4aa63529b9ff757f53737274894c02b8e` | verify per selected task | verify per selected task | read-only |

Last analyzed CrystalServer commit: `fc0d53b9f9965463b6082c07e6d3d482294541a7`.

The baseline is immutable evidence for Stage 1 only. Every later task must re-fetch all three current heads and record its own baseline.

# Scope

- Review CrystalServer commits and diffs associated with crashes, regressions, desynchronization, overflow, leaks, security, databases, deadlocks, races, invalid state, missing validation, duplicate rewards, item loss, and protocol errors.
- Compare exact behavior against current Canary source, tests, documentation, active tasks, and open PRs.
- Preserve provenance: repository, commit SHA, author, date, related PR/issue, files, symbols, and the exact idea adapted.
- Create a reproducible failing test or deterministic proof before implementation whenever practical.
- Adapt only the smallest complete fix to current Canary architecture.
- Maintain Markdown and JSON inventories under `artifacts/upstream/crystalserver/`.

# Explicit exclusions

- No writes to `zimbadev/crystalserver`, `opentibiabr/canary`, or any other repository.
- No direct push to `main`.
- No mass cherry-pick, broad file replacement, or assumption that CrystalServer is newer or better.
- No `.otbm`, `items.otb`, binary assets, sprites, private dumps, secrets, or production configuration changes.
- No custom CrystalServer content presented as a Canary fix.
- No client, protocol, protobuf, login, DB schema, migration, multichannel, instance, shared-Lua-userdata, map, identifier, or asset change without the required extended contract analysis.
- No weakened tests or validators.

# Existing systems to reuse

| Module/tool/contract | Source | Required reuse rule |
|---|---|---|
| Agent coordination | `AGENTS.md`, `docs/agents/**` | One candidate implementation per task, branch, worktree, and draft PR. |
| Build/test matrix | `docs/agents/BUILD_TEST_MATRIX.md` | Select validation by changed surface and record exact command/head SHA. |
| Cross-repository contracts | `docs/agents/CROSS_REPO_CONTRACTS.md` | Protocol/client changes require linked server and maintained-client evidence. |
| Current Canary architecture | `src/**`, `data/**`, `tests/**`, relevant system docs | Prefer existing abstractions and newer Canary behavior. |
| Universal E2E platform | active PR #245 after it is merged and stable | Reuse instead of creating feature-specific orchestration. |

# Methodology

1. Record current repository heads, declared versions/protocols, open PRs, active tasks, ownership claims, and local worktree state.
2. Search CrystalServer history broadly, then open each candidate diff and related PR/issue.
3. Split bundled commits into independently evaluated behavior units.
4. Identify the exact defect, trigger, state transition, and impact.
5. Find the corresponding Canary symbols, call sites, tests, and later changes.
6. Determine whether Canary already has an equivalent or safer solution and whether the change originated upstream from Canary.
7. Check dependency on CrystalServer-only content, client, protocol, schema, IDs, assets, or other commits.
8. Define a failing test or deterministic validator before assigning `VALID_FIX_MISSING`.
9. Classify the candidate exactly once and record uncertainty.
10. Implement only through a new bounded task after ownership and extended gates pass.

Text similarity, `patch-id`, symbol search, and commit messages are signals only. They never replace behavioral evidence.

# Candidate status model

- `ALREADY_PRESENT`: current Canary already contains equivalent behavior.
- `CANARY_SUPERIOR`: current Canary solves the problem with a safer/newer design.
- `VALID_FIX_MISSING`: defect is deterministically present and the bounded fix is absent.
- `PARTIAL_VALUE`: the problem or idea has value, but the CrystalServer patch is incomplete, unsafe to copy, or needs separate adaptation.
- `CLIENT_COUPLED`: correctness depends on a maintained client/protocol contract.
- `CONTENT_ONLY`: difference is content or project policy, not a verified Canary defect.
- `UNVERIFIED`: evidence is insufficient for a behavior claim.
- `DANGEROUS`: direct application risks corrupt state, regression, security failure, or incompatible behavior.
- `REJECTED`: evidence shows the candidate should not be pursued.

# Risk classes

| Risk | Meaning | Minimum gate |
|---|---|---|
| critical | item/currency loss or duplication, corrupt state, remote security, unrecoverable DB/protocol failure | deterministic reproduction, regression test, focused integration, full required CI, rollback review |
| high | crash, leak, invalid lifetime, client crash, privilege/input boundary | reproduction or strong proof, focused tests, architecture/security review, full affected CI |
| medium | bounded correctness or performance issue without proven destructive impact | focused unit/integration test or benchmark, affected CI |
| low | documentation, diagnostics, refactor with unchanged behavior | docs/format checks and relevant CI |

# Active tasks

| Task ID | Branch | PR | State | Exact next action |
|---|---|---:|---|---|
| `CAN-20260713-crystalserver-comparison-inventory` | `docs/crystalserver-comparison-inventory` | pending | active | Open draft PR, verify its exact diff and current-head checks. |

# Stage 1 candidate queue

| ID | CrystalServer commit | Status | Risk | Affected area | Exact next action |
|---|---|---|---|---|---|
| `CS-001` | `a7350014528002fb27ed64d260a96d28a580d41a` | `VALID_FIX_MISSING` | high | `ConditionLight` zero-level division/deserialization | Create a separate test-first task after this inventory merges and ownership is rechecked. |
| `CS-002` | `0c0f1acafd77a86fb5ce56fe768ff6d98d100c35` | `ALREADY_PRESENT` | medium | NPC shop-window iteration | No implementation; retain as closed evidence. |
| `CS-003` | `90ac0eb7d2ba0a88476881c972d9de83fbbcb3e8` | `CANARY_SUPERIOR` | high | KV shared Lua userdata GC | No implementation; preserve current typed shared-class registration. |
| `CS-004` | `dcb4f00ffd55ede2399c979eee3b7fe6e7e0ee6e` | `ALREADY_PRESENT` | high | `Container::replaceThing` validation | No implementation; retain regression coverage expectation. |
| `CS-005` | `fc0d53b9f9965463b6082c07e6d3d482294541a7` | `PARTIAL_VALUE` | medium | player GUID lookup index | Benchmark and consistency-test only after PR #289 no longer owns `game.cpp`/`game.hpp`. |
| `CS-006` | `891685169745e46f665069edcc35847f0704aa21` | `PARTIAL_VALUE` | high | `FS.mkdir` shell construction | Create an independent security-audit task; do not copy the upstream sanitizer. |
| `CS-007` | `891685169745e46f665069edcc35847f0704aa21` | `PARTIAL_VALUE` | high | `table.unserialize` dynamic evaluation | Create a separate call-site/compatibility/security task; do not copy the bespoke parser. |
| `CS-008` | `34cbec0c34325619ef23c5d12c940b7b1c276975` | `CLIENT_COUPLED` | high | Market offer count/payload limits | Establish maintained OTClient limits and server/client tests before any design. |
| `CS-009` | `cfc0c5c496eae53f1f33a07f563068f44914ddbb` | `CLIENT_COUPLED` | high | disconnect message reason byte | Create a cross-repo contract task only with exact 15.25 client evidence. |
| `CS-010` | `ffe4db548371c44ce01dfc280af0209318272292` | `DANGEROUS` | critical | `Game::removeCreature` parent lifetime | Reproduce the invariant violation; design cleanup ordering rather than copying the early return. |

# Deferred screening backlog

These are not approved findings and are not counted among the ten deep-reviewed Stage 1 candidates:

| CrystalServer commit | Preliminary state | Reason |
|---|---|---|
| `9e046413b965982745ca63559f68bd30264bfc9d` | `UNVERIFIED` | Duplicate item-definition claim needs current Canary XML/ID and asset-contract validation. |
| `809633b1f9fc9a690bef70ac0ecb916d5a5aa5d6` | `UNVERIFIED` | God-command item-count limit is arbitrary without current command parsing and resource-bound evidence. |
| `55db69b7be12fa7b6a8865038033d953ae8cff18` | `UNVERIFIED` | Corpse/reward-chest parent handling needs current symbol location and state-transition tests. |
| `6bda45e7d7b8f0e9a9c55b3b6b779b492504102f` | `UNVERIFIED` | Broad spell-formula rewrite is high-scope gameplay work and requires official formula evidence. |

# Proposed task sequence

1. `CS-001`: isolated zero-light crash regression test and minimal normalization fix.
2. `CS-006`: `FS.mkdir` trust-boundary and safe filesystem-operation audit.
3. `CS-007`: serialized-table call-site inventory, compatibility corpus, and non-executing decoder design.
4. `CS-010`: creature-removal parent invariant reproduction and lifecycle-safe remediation design.
5. `CS-008` and `CS-009`: separate maintained-OTClient contract investigations after the universal E2E platform is usable.
6. `CS-005`: performance benchmark and index-lifecycle proof after `game.cpp`/`game.hpp` ownership clears.

Each sequence item still requires a fresh ownership check. Order may change when new critical evidence appears.

# Rejected and closed candidates

| ID | Status | Decision |
|---|---|---|
| `CS-002` | `ALREADY_PRESENT` | Canary pre-increments the iterator before callbacks that can erase entries; no patch needed. |
| `CS-003` | `CANARY_SUPERIOR` | Canary already uses typed `registerSharedClass<KV>` and shared userdata APIs. |
| `CS-004` | `ALREADY_PRESENT` | Canary already checks null input and bounds before replacement. |

No candidate is marked `REJECTED` in Stage 1; insufficient evidence is retained as `UNVERIFIED` rather than guessed.

# Dependencies and blockers

- Local Git/worktree inspection is unavailable in the current environment because shell DNS cannot resolve GitHub. GitHub state is inspected through the connector; local commands remain explicitly unverified.
- Open PR #289 currently changes `src/game/game.cpp` and `src/game/game.hpp`; `CS-005` and any other overlapping implementation are blocked pending a fresh ownership resolution.
- Open PR #245 is the intended future reusable physical-client E2E platform; protocol/client candidates must not create parallel orchestration.
- Market and disconnect candidates require maintained OTClient evidence and a recorded cross-repository contract.
- `CS-010` cannot be implemented from the CrystalServer patch because its early return occurs after partial removal side effects.

# Decisions and invariants

- `repository_full_name` must equal `blakinio/canary` before every write.
- CrystalServer and OpenTibiaBR Canary remain read-only.
- Every candidate has exactly one status at a given baseline.
- `VALID_FIX_MISSING` requires deterministic evidence against current Canary, not an upstream claim.
- A bundled upstream commit may produce multiple independent candidate records.
- No candidate implementation may replace an entire Canary file.
- Generated reports stay under `artifacts/upstream/crystalserver/`.
- Protocol, schema, migration, multichannel, instance, shared userdata, map, identifiers, and assets always use extended gates.
- Uncertainty is recorded as `UNVERIFIED`; it is never upgraded to handled or fixed without evidence.

# Validation strategy

- Documentation inventory: Markdown/path review, exact changed-file review, full PR diff review, `git diff --check`, and current-head repository checks.
- C++ candidates: failing focused test first where practical, correct preset build, focused tests, and all required platform CI.
- Lua/security candidates: call-site inventory, compatibility corpus, malicious-input tests, syntax/format checks, and runtime smoke where behavior changes.
- DB candidates: clean import, migration and rollback tests, temporary MariaDB integration.
- Protocol/client candidates: server tests, maintained-client tests, exact field-order/width/version gate, and physical integration.
- Performance candidates: reproducible benchmark plus lifecycle/correctness tests; performance claims require measurements.

# Handoff

## Start here

Read `AGENTS.md`, `docs/agents/README.md`, this program record, the latest Stage 1 Markdown/JSON reports, all active task records, and all open PRs. Re-fetch current heads before selecting a candidate.

## Task creation protocol

1. Select one bounded candidate from the queue.
2. Re-open its CrystalServer diff and related discussion.
3. Compare the new current Canary code and tests; update classification if evidence changed.
4. Inspect ownership and overlapping PRs.
5. Create one task record, branch, worktree, and draft PR with exact path claims.
6. Add a failing test or deterministic proof before the fix where practical.
7. Implement the smallest architecture-native adaptation.
8. Validate, review the complete diff, update provenance/program state, and merge only through the autonomous gate.

## Do not repeat

- Do not rescan from scratch without first checking `last analyzed commit` and the candidate JSON.
- Do not copy the CrystalServer `table.unserialize` parser or `removeCreature` early return.
- Do not combine security candidates because they share an upstream commit.
- Do not infer official client limits from CrystalServer constants.
- Do not start overlapping `game.cpp`/`game.hpp` work without resolving PR #289 or its successor.

## Open questions

- Can `ConditionLight` level zero be triggered by current serialized player conditions, scripts, or malformed persistence, and which test fixture best proves it?
- Which inputs reach `FS.mkdir` and `table.unserialize`, and are any attacker-controlled?
- What exact protocol 15.25 disconnect and Market payload constraints are implemented by the maintained OTClient?
- What lifecycle invariant should replace the unsafe `removeCreature` parent-null early return?
