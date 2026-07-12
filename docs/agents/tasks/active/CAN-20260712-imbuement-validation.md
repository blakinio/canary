---
task_id: CAN-20260712-imbuement-validation
coordination_id: ""
status: active
agent: "GPT-5.6 Thinking"
branch: feat/imbuement-validation-audit
base_branch: main
created: 2026-07-12T17:18:21Z
updated: 2026-07-12T18:12:32Z
last_verified_commit: "2f0828f06f1b4510d906056de6f3f261fda1a63b"
risk: low
related_issue: ""
related_pr: "#166"
depends_on: []
blocks: []
owned_paths:
  - .github/workflows/imbuement-validation.yml
  - tools/ai-agent/imbuement_validation.py
  - tools/ai-agent/imbuement_storage_validation.py
  - tools/ai-agent/test_imbuement_validation.py
  - tools/ai-agent/test_imbuement_storage_validation.py
  - docs/ai-agent/IMBUEMENT_VALIDATION_REPORT.md
  - docs/ai-agent/IMBUEMENT_RUNTIME_TEST_PLAN.json
  - docs/agents/tasks/active/CAN-20260712-imbuement-validation.md
  - docs/agents/ACTIVE_WORK.md
  - docs/agents/MODULE_CATALOG.md
modules_touched:
  - AI world validation
  - imbuement definitions, shrine protocol and runtime audit
  - imbuement unlock-storage wiring audit
reuses:
  - OTS AI World Validation evidence methodology
  - existing Imbuements XML loader and registry
  - existing shrine, scroll and Player imbuement runtime APIs
  - active Lua storage registry and Forgotten Knowledge boss storage paths
public_interfaces:
  - imbuement validation report format
  - imbuement registry validation CLI
  - imbuement storage validation CLI
  - imbuement runtime test-plan schema v1
  - focused Imbuement Validation workflow
cross_repo_tasks: []
---

# Goal

Create a deterministic, evidence-based audit of Canary's Imbuing system against the current reference mechanics without changing gameplay data or engine behavior.

# Acceptance criteria

- [x] Parse the active `data/XML/imbuements.xml` registry and report structural, tier, cost, duration, source-item and effect defects.
- [x] Audit engine loading, item-slot eligibility, shrine visibility/application, scroll application, removal/clearing and duration consumption paths.
- [x] Correlate every nonzero imbuement unlock storage with active Lua storage declarations.
- [x] Distinguish confirmed static behavior, configuration-dependent behavior and unresolved runtime behavior.
- [x] Compare the baseline with the referenced TibiaWiki/Fandom Imbuing page using dated evidence.
- [x] Produce a human-readable evidence report and a machine-readable runtime test plan.
- [x] Add focused unit tests and a focused CI workflow.
- [x] Do not modify XML gameplay data, active datapacks, map, assets, item binaries, protocol behavior or engine behavior.
- [ ] Full focused workflow and repository checks completed.
- [x] Module catalogue impact handled.
- [x] Documentation impact handled; changelog deferred until final merged behavior is known.
- [x] Cross-repository impact handled as none.
- [ ] Autonomous merge gate satisfied.

# Confirmed context

- The writable repository is `blakinio/canary`; `opentibiabr/canary` is reference-only.
- Merged PR #86 corrected the storage policy to read the configured storage ID.
- `toggleImbuementShrineStorage` is disabled by default.
- The active storage policy hides a configured entry only when its storage reads `-1`; `storage=0` bypasses family-specific filtering.
- The active Forgotten Knowledge boss path writes named storages `45489..45495`.
- The XML instead uses nonzero storage IDs `50488, 50490, 50492, 50494, 50496, 50498, 50501`, none declared in active `storages.lua`.
- Those seven IDs affect 22 Powerful families. Powerful Featherweight and Vibrancy use `storage=0`.
- `main` advanced during implementation; shared coordination files were refreshed from current `main` and retain only the narrow #166 entries.
- This task reads but does not edit `docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md`.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| OTS AI World Validation | Evidence layers and handoff rules | `docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md` | Defines structure/reference/semantic/runtime/regression boundaries. |
| Imbuements registry/loader | Canonical server definitions | `data/XML/imbuements.xml`, `src/creatures/players/imbuements/**` | Defines tiers, costs, sources, effects, categories and storage gates. |
| Storage registry | Active identifier declarations | `data-otservbr-global/lib/core/storages.lua` | Distinguishes valid named storage IDs from stale numeric XML values. |
| Forgotten Knowledge boss path | Runtime unlock writes | `data-otservbr-global/scripts/quests/forgotten_knowledge/creaturescripts_bosses_kill.lua` | Confirms current boss storage names and write path. |
| Shrine/scroll runtime | Application and removal entry points | active shrine/scroll scripts plus Player/Lua APIs | Provides real gameplay call paths. |
| PR #86 | Corrected storage policy | merged focused fix/tests | Prevents repeating a known boolean-vs-ID defect. |
| Achievement validation PR #165 | Focused validation-workflow pattern | its validation workflow | Repository-consistent Python test/artifact pattern. |

# Ownership and overlap check

- Open PRs and merged state were inspected while the task was active.
- PR #165 also edits `ACTIVE_WORK.md` and `MODULE_CATALOG.md`; specialist Imbuement paths do not overlap.
- Shared files are edited narrowly using current `main` as the content baseline.
- Any later base update must re-resolve the two shared files rather than taking either branch wholesale.

# Current state

The read-only implementation is published in draft PR #166.

```text
base tiers: 3
categories: 20
families: 24
tier entries: 72
XML-mapped scroll IDs: 46
Lua-registered scroll IDs: 48
duration: 72,000 seconds
clear cost: 15,000 gold
nonzero XML unlock storage IDs: 7
Powerful families using stale nonzero IDs: 22
Powerful families using storage=0: 2
```

Confirmed discrepancy groups:

1. fee/success model differs from the current fixed-fee reference;
2. Strike differs in all three tiers;
3. Basic Punch uses a different source item/count;
4. Vibrancy scroll IDs `51466` and `51746` are registered by Lua but unmapped in XML;
5. seven nonzero Powerful storage IDs are absent from active `storages.lua`, affecting 22 families;
6. Powerful Featherweight and Vibrancy use `storage=0` and bypass family-specific filtering.

No gameplay, XML, engine, map, asset, item-binary or production-configuration file was changed.

# Storage evidence

| Stale XML storage | Affected families | Strong current semantic counterpart |
|---:|---|---:|
| 50488 | Reap, Vampirism, Lich Shroud | 45489 — Lady Tenebris |
| 50490 | Electrify, Cloud Fabric, Swiftness | 45490 — Lloyd |
| 50492 | Venom, Snake Skin, Chop, Slash, Bash, Punch | 45491 — Thorn Knight |
| 50494 | Scorch, Void, Dragon Hide | 45492 — Dragonking |
| 50496 | Frost, Quara Scale, Blockade | 45493 — Frozen Horror |
| 50498 | Demon Presence, Precision | 45494 — Time Guardian |
| 50501 | Strike, Epiphany | 45495 — Last Lore Keeper |

The grouping is strong evidence, but a separate data-fix PR must verify each mapping and test before/after visibility. Exact Dangerous Depths and Dream Courts completion conditions remain unresolved; do not invent them.

# Plan

1. Obtain an actual focused workflow run or execute the complete commands in a full checkout.
2. Repair any scanner/test assumptions exposed by that run.
3. Re-check current `main`, PR mergeability, full diff and shared-file overlap.
4. Keep PR #166 read-only and draft until all checks pass.
5. Deliver storage, scroll, effect/material and economy changes as separate focused PRs.

# Work log

## 2026-07-12T17:18:21Z

- Created the dedicated branch and persistent task record.
- Confirmed Imbuing spans XML, C++, Lua, item metadata, storage gates and protocol/UI paths.
- Local shell could not resolve `github.com`; repository-wide execution required connector/CI access.

## 2026-07-12T17:42:23Z

- Added the registry/runtime scanner, tests, report and runtime plan.
- Confirmed structural baseline of 72 entries.
- Confirmed Vibrancy scroll, Strike, Punch and fee-model discrepancies.

## 2026-07-12T17:53:42Z

- Added the focused workflow.
- Refreshed shared coordination files from current `main`.
- No GitHub workflow run or combined status was emitted; PR remained draft.

## 2026-07-12T18:12:32Z

- Added `imbuement_storage_validation.py` and focused tests.
- Expanded the workflow to audit `storages.lua`, default configuration and Forgotten Knowledge boss wiring.
- Expanded the report and runtime plan with the 22 stale-gated families and two zero-storage bypasses.
- Locally validated the exact new storage-tool/test contents: Python compilation passed; four focused unit tests passed; runtime-plan JSON syntax passed.
- Full repository tests, original registry scanner tests and GitHub workflow remain not run.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Keep PR #166 read-only | Evidence must precede gameplay/data changes. | none |
| Treat the wiki as a dated reference, not executable truth | Server may intentionally target historical/custom behavior. | none |
| Separate economy from data corrections | Fixed fees affect protocol, charging and balance. | future ADR if changed |
| Classify Vibrancy scrolls as confirmed cross-file defect | Active Lua registers both IDs; XML maps neither. | none |
| Classify seven nonzero XML storage IDs as stale | They are absent from active storage declarations and current boss scripts write different IDs. | none |
| Do not blindly replace stale IDs | Semantic mapping is strong but each replacement needs focused regression evidence. | none |
| Do not invent Featherweight/Vibrancy completion IDs | Exact Dangerous Depths/Dream Courts completion semantics are not yet proven. | none |
| Keep the general project document unchanged | Specialist evidence belongs in the dedicated report. | none |

# Files and interfaces

| Path/interface/config/schema | Purpose | Status |
|---|---|---|
| `.github/workflows/imbuement-validation.yml` | focused tests, audit generation, JSON validation and artifacts | implemented; no GitHub run emitted |
| `tools/ai-agent/imbuement_validation.py` | XML/runtime/reference audit | implemented; full run pending |
| `tools/ai-agent/imbuement_storage_validation.py` | XML storage-to-Lua declaration audit | implemented; focused local tests passed |
| `tools/ai-agent/test_imbuement_validation.py` | registry/parser/classifier tests | implemented; full run pending |
| `tools/ai-agent/test_imbuement_storage_validation.py` | storage parser/wiring tests | implemented; 4/4 local tests passed |
| `docs/ai-agent/IMBUEMENT_VALIDATION_REPORT.md` | evidence report and findings | implemented |
| `docs/ai-agent/IMBUEMENT_RUNTIME_TEST_PLAN.json` | machine-readable gameplay/runtime scenarios | implemented; local JSON syntax passed |
| `docs/agents/ACTIVE_WORK.md` | discoverability | updated narrowly from current main |
| `docs/agents/MODULE_CATALOG.md` | reusable-tool discovery | updated narrowly from current main |

# Validation and CI

| Scope | Command/check | Result | Evidence/notes |
|---|---|---|---|
| exact new storage tool | `python -m py_compile /tmp/imbuement_storage_validation.py` | passed | temporary file content was identical to committed file |
| exact new storage tests | `python -m py_compile /tmp/test_imbuement_storage_validation.py` | passed | temporary file content was identical to committed file |
| focused storage tests | `cd /tmp && python -m unittest test_imbuement_storage_validation.py -v` | passed | 4 tests, 0 failures |
| runtime plan | `python -m json.tool /tmp/IMBUEMENT_RUNTIME_TEST_PLAN.json` | passed | temporary file content was identical to committed JSON |
| full focused suite | repository commands from report | not-run | no full checkout; DNS failure for `github.com` |
| GitHub Actions | Imbuement Validation workflow | not-run | no workflow run/status emitted for connector commits |

Never write `passed` for unexecuted checks.

# Failed approaches and dead ends

- `git clone` and `git ls-remote` fail because the execution container cannot resolve `github.com`.
- Connector-created commits did not emit an Actions run visible through workflow-run or combined-status APIs.
- Closing/reopening draft PR #166 did not emit a workflow run.
- Questline storage `45851` is set when Dangerous Depths tasks begin and is not sufficient evidence for the final Featherweight unlock condition.

# Risks and compatibility

- Runtime/data: no runtime or gameplay data change in this PR.
- Security: no secrets or player data.
- Cross-repo rollout: none; no OTClient change.
- Reference drift: re-observe the external baseline before future corrections.
- Configuration: default-disabled storage filtering masks the broad stale-ID defect.
- Shared indexes: re-resolve `ACTIVE_WORK.md` and `MODULE_CATALOG.md` from current `main` before readiness.
- Rollback: revert audit/tool/workflow/docs commits.

# Remaining work

1. Run the complete focused suite and both generators in a full checkout or GitHub Actions.
2. Inspect generated artifacts and repair failures.
3. Rebase/update from current `main` using a safe supported mechanism.
4. Resolve shared coordination-file overlap.
5. Review the full changed-file list and diff again.
6. Keep the PR draft and unmerged until the autonomous merge gate is satisfied.

# Handoff

## Start here

1. Inspect PR #166 base/head, mergeability, checks and changed files.
2. Read `docs/ai-agent/IMBUEMENT_VALIDATION_REPORT.md`.
3. Run the reproduction commands from the report.
4. Inspect both JSON audits and the runtime-plan artifact.
5. Re-resolve shared files from current `main` if changed.

## Do not repeat

- Do not classify the fee model as an automatic bug without choosing the target economy/version.
- Do not replace storage IDs blindly or invent Dangerous Depths/Dream Courts completion values.
- Do not modify `data/XML/imbuements.xml` in PR #166.
- Do not merge gameplay fixes into this audit PR.
- Do not claim CI/runtime success without an actual run.
- Do not take stale shared-index content wholesale from another branch.

## Required reads

- `AGENTS.md`
- `docs/agents/ACTIVE_WORK.md`
- `docs/agents/MODULE_CATALOG.md`
- `docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md`
- `docs/ai-agent/IMBUEMENT_VALIDATION_REPORT.md`
- `docs/ai-agent/IMBUEMENT_RUNTIME_TEST_PLAN.json`
- `.github/workflows/imbuement-validation.yml`
- both Imbuement audit tools/tests
- `data/XML/imbuements.xml`
- active `storages.lua`, boss-kill script and shrine/scroll runtime
- merged PR #86

## Open questions

- Does the project target historical chance/protection or current fixed-fee Imbuing?
- Which exact active completion storage/value should unlock Powerful Featherweight?
- Which exact active completion storage/value should unlock Powerful Vibrancy?
- Does the complete equipment metadata match every current imbuable item?
- Do real save/load, combat and client scenarios satisfy the runtime plan?

# Completion

- Final status: active; implementation complete, full validation pending
- PR: #166
- Merge commit:
- Catalogue updated: yes
- Changelog updated: deferred until final merged state
- Archived at:
