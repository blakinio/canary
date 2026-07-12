---
task_id: CAN-20260712-wheel-of-destiny-validation
coordination_id: ""
status: active
agent: "GPT-5.6 Thinking"
branch: feat/wheel-of-destiny-validation-audit
base_branch: main
created: 2026-07-12T19:37:47+02:00
updated: 2026-07-12T19:37:47+02:00
last_verified_commit: "ca93c9dbcec380cc1bd0cce13ef1e248e334f18d"
risk: low
related_issue: ""
related_pr: "pending"
depends_on: []
blocks: []
owned_paths:
  - tools/ai-agent/wheel_of_destiny_validation.py
  - tools/ai-agent/test_wheel_of_destiny_validation.py
  - docs/ai-agent/OTS_AI_WHEEL_OF_DESTINY_VALIDATION_PROJECT.md
  - docs/ai-agent/WHEEL_OF_DESTINY_VALIDATION_REPORT.md
  - docs/ai-agent/WHEEL_OF_DESTINY_RUNTIME_TEST_PLAN.json
  - docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md
  - docs/agents/tasks/active/CAN-20260712-wheel-of-destiny-validation.md
  - docs/agents/ACTIVE_WORK.md
  - docs/agents/MODULE_CATALOG.md
modules_touched:
  - AI world validation
  - Wheel of Destiny and Gem Atelier audit
reuses:
  - OTS AI World Validation evidence methodology
  - existing Wheel runtime components
  - existing protocol and persistence implementation
public_interfaces:
  - Wheel validation report format
  - Wheel validation CLI
cross_repo_tasks: []
---

# Goal

Create a deterministic, evidence-based audit of Canary's Wheel of Destiny and Gem Atelier that validates definitions, activation paths, effects, persistence and protocol contracts without changing gameplay behavior in the audit PR.

# Acceptance criteria

- [ ] Inventory all active Wheel of Destiny and Gem Atelier definitions and call sites.
- [ ] Validate promotion-point sources, limits, spending, refund and temple reset rules.
- [ ] Validate topology, slice adjacency, costs, Conviction and Revelation thresholds.
- [ ] Map every Dedication/Conviction/Revelation perk to its runtime effect path.
- [ ] Validate gem reveal, affinity, socketing, resonance, grades, fragments, costs and persistence.
- [ ] Map protocol handlers and compare payloads with the compatible OTClient when required.
- [ ] Validate schema, migrations and save/load paths.
- [ ] Compare current behavior and values with the referenced versioned Tibia sources.
- [x] Create a dedicated durable project document beside the main World Validation project.
- [ ] Produce a human-readable evidence report and machine-readable runtime test plan.
- [ ] Add focused deterministic unit tests for the scanner/classifier.
- [ ] Do not modify active Wheel data, combat/spells, protocol, schema, datapacks, map or assets in this audit PR.
- [ ] Relevant checks completed.
- [ ] Module catalogue impact handled.
- [ ] Documentation/changelog impact handled or recorded as none.
- [ ] Cross-repository impact handled or explicitly recorded.
- [ ] Autonomous merge gate satisfied.

# Confirmed context

- The writable repository is `blakinio/canary`; `opentibiabr/canary` is reference-only.
- The main World Validation project requires separate evidence for definitions, references, semantics, runtime and regression.
- The referenced TibiaWiki/Fandom page describes the base Wheel, Gem Atelier and Fragment Workshop, including version-sensitive additions.
- Current Canary contains dedicated Wheel runtime, gem, IO, protocol, Lua and persistence paths.
- Open PRs inspected on 2026-07-12; no Wheel of Destiny validation overlap was found.
- Dedicated project document: `docs/ai-agent/OTS_AI_WHEEL_OF_DESTINY_VALIDATION_PROJECT.md`.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| OTS AI World Validation | Evidence layers and handoff rules | `docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md` | Defines structure/reference/semantic/runtime/regression separation. |
| Wheel runtime components | Canonical server implementation | `src/creatures/players/components/wheel/**` | Definitions, activation, effects and gem behavior live here. |
| Wheel IO/persistence | Canonical save/load path | `src/io/io_wheel.*`, player load/save sources | Required for round-trip and migration validation. |
| Protocol implementation | Server payload contract | `src/server/network/protocol/**` | Required for client compatibility evidence. |
| Existing achievement/imbuing validation PR pattern | Coordination and audit structure | PRs #165 and #166 | Confirms read-only specialist audit, task record and draft PR workflow. |

# Ownership and overlap check

- Open PR state inspected on 2026-07-12.
- Active work index inspected; it is stale relative to GitHub and therefore not treated as authoritative.
- No active branch or PR was found claiming Wheel of Destiny/Gem Atelier validation paths.
- Resolution: dedicated branch and documentation/tool-only audit scope.

# Current state

A dedicated project document exists and records scope, evidence layers, safety boundary, preliminary source inventory and handoff. No gameplay or runtime files have been changed. The next step is a deterministic source inventory and baseline extraction.

# Plan

1. Inventory all Wheel/Gem symbols and files from current branch.
2. Extract static definitions, topology, costs, thresholds and persistence fields.
3. Map all runtime effect call sites and spell augments.
4. Map protocol handlers and client-facing payloads.
5. Implement a deterministic read-only scanner and focused tests.
6. Generate the evidence report and runtime test plan.
7. Split confirmed defects into separate focused PRs after evidence review.

# Work log

## 2026-07-12T19:37:47+02:00

- Changed: created the persistent task record and claimed Wheel validation paths.
- Learned: existing repository governance requires the specialist document, task record, active-work visibility and early draft PR before substantial implementation.
- Failed/blocked: local shell cannot resolve `github.com`; repository analysis and writes use the GitHub connector, and runtime execution may require CI.
- Result: task ownership is explicit; no gameplay files changed.

## 2026-07-12T19:35:00+02:00

- Changed: created `docs/ai-agent/OTS_AI_WHEEL_OF_DESTINY_VALIDATION_PROJECT.md`.
- Learned: Wheel validation must separate definition, activation, effect, persistence, protocol, runtime and regression evidence.
- Failed/blocked: none for documentation creation.
- Result: durable project scope and handoff now exist in Git.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Keep a separate project document beside the main World Validation project | Wheel/Gem definitions, effects, persistence and protocol require a durable specialist handoff without bloating the general project document. | none |
| Keep the first PR read-only | A complete evidence baseline must precede balance, gameplay, schema or protocol changes. | none |
| Treat wiki values as versioned comparison data, not automatic truth | Wheel and Gem Atelier changed across updates; source date/version must accompany every mismatch. | none |
| Split protocol changes from server-only audit | Canary ↔ OTClient payload changes require an explicit cross-repository contract. | none |

# Files and interfaces

| Path/interface/config/schema | Purpose | Status |
|---|---|---|
| `docs/ai-agent/OTS_AI_WHEEL_OF_DESTINY_VALIDATION_PROJECT.md` | durable methodology, state, changelog and handoff | created |
| `tools/ai-agent/wheel_of_destiny_validation.py` | deterministic source scanner/classifier | planned |
| `tools/ai-agent/test_wheel_of_destiny_validation.py` | focused parser/classifier tests | planned |
| `docs/ai-agent/WHEEL_OF_DESTINY_VALIDATION_REPORT.md` | evidence report and findings | planned |
| `docs/ai-agent/WHEEL_OF_DESTINY_RUNTIME_TEST_PLAN.json` | machine-readable runtime scenarios | planned |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| `ca93c9dbcec380cc1bd0cce13ef1e248e334f18d` | documentation path/content review | reviewed | specialist project file created on task branch |
| | focused Python tests | not-run | implementation pending |
| | AI Agent Tools workflow | not-run | tool implementation pending |

Never write `passed` without verification.

# Failed approaches and dead ends

- Direct `git clone` from the execution container failed because DNS resolution for `github.com` is unavailable.
- Code search on the private fork index returned no Wheel matches; upstream code search was used only to discover paths, then fork files are fetched directly for authoritative content.

# Risks and compatibility

- Runtime: no runtime change in audit PR.
- Data/migration: no schema or migration change in audit PR.
- Protocol: read-only mapping only; any change requires Canary ↔ OTClient contract work.
- Security: no secrets or player data.
- Backward compatibility: report/tool only.
- Cross-repo rollout: none unless a protocol defect is confirmed later.
- Rollback: revert documentation/tool commits.

# Remaining work

1. Open the early draft PR and publish active-work visibility.
2. Fetch and classify all current Wheel source files.
3. Implement scanner and tests.
4. Produce evidence report and runtime test plan.
5. Link the specialist project from the main World Validation document.

# Handoff

## Start here

Read `docs/ai-agent/OTS_AI_WHEEL_OF_DESTINY_VALIDATION_PROJECT.md`, then inspect `src/creatures/players/components/wheel/**`, `src/io/io_wheel.*`, protocol handlers, player save/load, migrations and every Wheel-related spell/combat call site.

## Do not repeat

Do not infer correctness from a getter, enum or protocol handler existing. Each perk needs an activation path, effect path, persistence evidence and eventually a runtime test.

## Required reads

- `AGENTS.md`
- `docs/agents/ACTIVE_WORK.md`
- `docs/agents/MODULE_CATALOG.md`
- `docs/agents/CROSS_REPO_CONTRACTS.md`
- `docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md`
- `docs/ai-agent/OTS_AI_WHEEL_OF_DESTINY_VALIDATION_PROJECT.md`
- current Wheel, IO, protocol and persistence sources

## Open questions

- Which Wheel features are fully implemented for every vocation and which are partial?
- Which values correspond to the active protocol/version rather than older Tibia balance?
- Are all gem operations transactional and round-trip safe?
- Does the compatible OTClient consume every emitted payload exactly as Canary sends it?

# Completion

- Final status: active
- PR: pending
- Merge commit:
- Catalogue updated: no
- Changelog updated: no
- Archived at:
