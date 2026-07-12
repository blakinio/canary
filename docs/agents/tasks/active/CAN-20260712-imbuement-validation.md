---
task_id: CAN-20260712-imbuement-validation
coordination_id: ""
status: active
agent: "GPT-5.6 Thinking"
branch: feat/imbuement-validation-audit
base_branch: main
created: 2026-07-12T17:18:21Z
updated: 2026-07-12T17:42:23Z
last_verified_commit: "a249670a2dd8543174ff967d2fb9fdc9a7e0ad5b"
risk: low
related_issue: ""
related_pr: "#166"
depends_on: []
blocks: []
owned_paths:
  - tools/ai-agent/imbuement_validation.py
  - tools/ai-agent/test_imbuement_validation.py
  - docs/ai-agent/IMBUEMENT_VALIDATION_REPORT.md
  - docs/ai-agent/IMBUEMENT_RUNTIME_TEST_PLAN.json
  - docs/agents/tasks/active/CAN-20260712-imbuement-validation.md
  - docs/agents/MODULE_CATALOG.md
modules_touched:
  - AI world validation
  - imbuement definitions, shrine protocol and runtime audit
reuses:
  - OTS AI World Validation evidence methodology
  - existing Imbuements XML loader and registry
  - existing shrine, scroll and Player imbuement runtime APIs
public_interfaces:
  - imbuement validation report format
  - imbuement validation CLI
  - imbuement runtime test-plan schema v1
cross_repo_tasks: []
---

# Goal

Create a deterministic, evidence-based audit of Canary's Imbuing system against the current reference mechanics without changing gameplay data or engine behavior.

# Acceptance criteria

- [x] Parse the active `data/XML/imbuements.xml` registry and report structural, tier, cost, duration, source-item and effect defects.
- [x] Audit engine loading, item-slot eligibility, shrine visibility/application, scroll application, removal/clearing and duration consumption paths.
- [x] Distinguish confirmed static behavior, configuration-dependent behavior and unresolved runtime behavior.
- [x] Compare the current registry and mechanics baseline with the referenced TibiaWiki/Fandom Imbuing page using evidence, without copying large wiki tables into the repository.
- [x] Produce a human-readable evidence report and a machine-readable runtime test plan.
- [x] Add focused unit tests for parser and classifier behavior.
- [x] Do not modify `data/XML/imbuements.xml`, active datapacks, map, assets, item binaries, protocol behavior or engine behavior in this audit PR.
- [ ] Relevant checks completed.
- [x] Module catalogue impact handled.
- [x] Documentation/changelog impact handled: specialist report and plan added; agent changelog not required for an unmerged audit.
- [x] Cross-repository impact handled as none.
- [ ] Autonomous merge gate satisfied.

# Confirmed context

- The writable repository is `blakinio/canary`; `opentibiabr/canary` is reference-only.
- The repository contains engine Imbuements code, `data/XML/imbuements.xml`, active shrine scripts, imbuement scroll handling and storage integrations.
- Merged PR #86 fixed configured imbuement-storage filtering and added focused policy coverage.
- The referenced TibiaWiki/Fandom page observed on 2026-07-12 describes 20-hour duration, current tier fees, clearing fee, account restrictions, source requirements, duplicate-category restrictions, scroll availability and item-type eligibility.
- The world-validation project requires explicit structure/reference/semantic/runtime/regression layers and forbids guessing runtime behavior.
- Open PRs were inspected on 2026-07-12; no active Imbuement-validation overlap was found.
- PR #165 owns the general achievement/world-validation documentation paths; this task reads but does not edit `OTS_AI_WORLD_VALIDATION_PROJECT.md`.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| OTS AI World Validation | Evidence layers and handoff rules | `docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md` | Defines structure/reference/semantic/runtime/regression boundaries. |
| Imbuements registry/loader | Canonical server definitions | `data/XML/imbuements.xml`, `src/creatures/players/imbuements/**` | Defines tiers, costs, sources, effects, categories and storage gates. |
| Shrine/scroll runtime | Application and removal entry points | active shrine and scroll scripts plus Player/Lua APIs | Provides the real gameplay call paths to classify. |
| PR #86 | Storage-filter policy and focused tests | merged imbuement storage-filter fix | Prevents repeating a known defect and supplies reusable policy coverage. |

# Ownership and overlap check

- Open PRs inspected: current open PR set including #165, #164, #163, #157, #156, #155 and #136.
- Imbuement-specific PR history inspected: merged #86.
- Active tasks inspected: `docs/agents/ACTIVE_WORK.md` and GitHub open PR state.
- Overlap: shared coordination indexes only; PR #165 also changes `ACTIVE_WORK.md` and owns its specialist validation paths.
- Resolution: do not edit `ACTIVE_WORK.md` in this branch while the overlap is active; PR #166 and this task record provide discovery. Do not edit `OTS_AI_WORLD_VALIDATION_PROJECT.md`.

# Current state

The read-only audit implementation is complete on branch `feat/imbuement-validation-audit` and published in draft/active PR #166.

Deterministic baseline encoded by the scanner:

```text
base tiers: 3
categories: 20
families: 24
tier entries: 72
XML-mapped scroll IDs: 46
Lua-registered scroll IDs: 48
duration: 72,000 seconds
clear cost: 15,000 gold
```

Confirmed discrepancy groups:

1. application fee/success model differs from the current fixed-fee reference;
2. Strike differs in all three tiers;
3. Basic Punch uses a different source item/count;
4. Vibrancy scroll IDs `51466` and `51746` are registered by Lua but unmapped in XML;
5. Powerful Featherweight has `storage=0` despite the documented Dangerous Depths unlock;
6. Powerful Vibrancy has `storage=0` despite the documented Dream Courts unlock.

No gameplay, XML, engine, map, asset, item-binary or production-configuration file was changed.

# Plan

1. Verify focused tests and scanner execution through the AI Agent Tools workflow or an available full checkout.
2. Inspect the complete PR diff and any review/CI feedback.
3. Keep this audit PR read-only and update evidence if CI exposes scanner assumptions.
4. Deliver confirmed gameplay fixes as separate focused PRs only after the audit is reviewed.

# Work log

## 2026-07-12T17:18:21Z

- Changed: created a dedicated task branch and persistent task record.
- Learned: Imbuing spans XML definitions, C++ runtime, Lua bindings, shrine/scroll scripts, item metadata, storage gates and protocol/UI messages; a single-file comparison would be insufficient.
- Failed/blocked: local shell cannot resolve `github.com`, so repository-wide execution must use GitHub/CI or files fetched through the GitHub connector.
- Result: audit scope claimed; no gameplay files changed.

## 2026-07-12T17:42:23Z

- Changed: added `imbuement_validation.py`, focused unit tests, the specialist validation report, runtime test plan and module-catalogue entry.
- Learned: the active XML is structurally complete at 72 entries; most current effects/materials align, but six discrepancy groups remain.
- Confirmed defect: the active Lua action registers Vibrancy scroll IDs `51466` and `51746`, while XML provides no corresponding scroll mapping.
- Confirmed reference mismatches: Strike values, Basic Punch source, two missing Powerful storage gates and the fee/success model.
- Failed/blocked: GitHub returned no workflow runs or commit statuses for head `a249670a2dd8543174ff967d2fb9fdc9a7e0ad5b`; local clone/test execution is unavailable because DNS resolution for `github.com` fails in the execution container.
- Result: implementation and evidence are committed; validation remains explicitly `not-run`, not passed.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Keep the first PR read-only | Definition/runtime evidence must precede gameplay fixes under the world-validation methodology. | none |
| Treat TibiaWiki/Fandom as a dated reference baseline, not executable truth | The server may contain intentional historical/custom behavior and the page can change. | none |
| Separate the fee model from data corrections | Moving from chance/protection to fixed fees affects economy, UI/protocol and charging logic. | future ADR if changed |
| Classify Vibrancy scrolls as a confirmed cross-file defect | Both IDs are registered by active Lua ranges but absent from the XML-derived scroll map. | none |
| Do not invent Featherweight/Vibrancy storage IDs | Exact active quest completion storages must be traced before a data fix. | none |
| Do not edit the shared project document or `ACTIVE_WORK.md` during overlap | Avoid path-ownership conflict with PR #165. | none |

# Files and interfaces

| Path/interface/config/schema | Purpose | Status |
|---|---|---|
| `tools/ai-agent/imbuement_validation.py` | deterministic XML/runtime/reference correlation scanner | implemented |
| `tools/ai-agent/test_imbuement_validation.py` | focused parser/classifier/regression tests | implemented, not yet executed |
| `docs/ai-agent/IMBUEMENT_VALIDATION_REPORT.md` | evidence report, findings, confidence and limitations | implemented |
| `docs/ai-agent/IMBUEMENT_RUNTIME_TEST_PLAN.json` | machine-readable gameplay/runtime scenarios | implemented |
| `docs/agents/MODULE_CATALOG.md` | reusable audit-tool discovery | updated |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| `a249670a2dd8543174ff967d2fb9fdc9a7e0ad5b` | `python -m py_compile tools/ai-agent/imbuement_validation.py tools/ai-agent/test_imbuement_validation.py` | not-run | full checkout unavailable in execution container |
| `a249670a2dd8543174ff967d2fb9fdc9a7e0ad5b` | `python -m unittest tools/ai-agent/test_imbuement_validation.py -v` | not-run | full checkout unavailable in execution container |
| `a249670a2dd8543174ff967d2fb9fdc9a7e0ad5b` | scanner generation command from report | not-run | full checkout unavailable in execution container |
| `a249670a2dd8543174ff967d2fb9fdc9a7e0ad5b` | AI Agent Tools workflow | not-run | GitHub API returned no workflow run/status for current head |

Never write `passed` without verification.

# Failed approaches and dead ends

- Direct `git clone` / `git ls-remote` from the execution container fails because DNS resolution for `github.com` is unavailable.
- GitHub Actions had not emitted a run or status for the current head when last checked; no result was inferred.
- Static evidence cannot identify exact quest storage IDs for the two missing Powerful gates without tracing the corresponding quest completion paths.

# Risks and compatibility

- Runtime: no runtime change in the audit PR.
- Data/migration: none.
- Security: no secrets or player data.
- Backward compatibility: report/tool only.
- Cross-repo rollout: none; no OTClient change is proposed.
- Reference drift: the external baseline is dated 2026-07-12 and must be re-observed before future corrections.
- Rollback: revert documentation/tool commits.

# Remaining work

1. Obtain an actual AI Agent Tools workflow run or execute the documented commands in a full checkout.
2. Repair scanner/test assumptions if validation fails.
3. Inspect complete changed-file list and diff.
4. Update PR body and task validation table with exact results.
5. Keep the PR unmerged until the autonomous merge gate is satisfied.

# Handoff

## Start here

Read this task, then:

1. inspect PR #166 and its current head;
2. read `docs/ai-agent/IMBUEMENT_VALIDATION_REPORT.md`;
3. run `tools/ai-agent/test_imbuement_validation.py`;
4. run the scanner command from the report;
5. inspect the AI Agent Tools workflow logs;
6. verify the full changed-file list contains only the six read-only audit files plus this task/catalogue record.

## Do not repeat

- Do not reclassify the fee model as an automatic bug without choosing the target Tibia economy/version.
- Do not add guessed quest storage IDs.
- Do not modify `data/XML/imbuements.xml` in this audit PR.
- Do not merge gameplay fixes into PR #166.
- Do not claim runtime or CI success without an actual run.

## Required reads

- `AGENTS.md`
- `docs/agents/ACTIVE_WORK.md`
- `docs/agents/MODULE_CATALOG.md`
- `docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md`
- `docs/ai-agent/IMBUEMENT_VALIDATION_REPORT.md`
- `docs/ai-agent/IMBUEMENT_RUNTIME_TEST_PLAN.json`
- `data/XML/imbuements.xml`
- engine Imbuements sources and active shrine/scroll scripts
- merged PR #86 and its focused tests

## Open questions

- Does the project intentionally target the historical chance/protection economy or the current fixed-fee model?
- Which exact active storages represent Dangerous Depths and Dream Courts completion for the missing Powerful gates?
- Does the full item metadata set match every currently documented imbuable equipment item?
- Do real save/load and combat scenarios satisfy the machine-readable runtime plan?

# Completion

- Final status: active; implementation complete, validation pending
- PR: #166
- Merge commit:
- Catalogue updated: yes
- Changelog updated: not applicable before merge; specialist report added
- Archived at:
