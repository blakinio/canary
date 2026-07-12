---
task_id: CAN-20260712-imbuement-validation
coordination_id: ""
status: active
agent: "GPT-5.6 Thinking"
branch: feat/imbuement-validation-audit
base_branch: main
created: 2026-07-12T17:18:21Z
updated: 2026-07-12T17:18:21Z
last_verified_commit: "44524dd8d442fb174ba77211c5bd50bdd9e63d51"
risk: low
related_issue: ""
related_pr: ""
depends_on: []
blocks: []
owned_paths:
  - tools/ai-agent/imbuement_validation.py
  - tools/ai-agent/test_imbuement_validation.py
  - docs/ai-agent/IMBUEMENT_VALIDATION_REPORT.md
  - docs/ai-agent/IMBUEMENT_RUNTIME_TEST_PLAN.json
  - docs/agents/tasks/active/CAN-20260712-imbuement-validation.md
  - docs/agents/ACTIVE_WORK.md
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
cross_repo_tasks: []
---

# Goal

Create a deterministic, evidence-based audit of Canary's Imbuing system against the current reference mechanics without changing gameplay data or engine behavior.

# Acceptance criteria

- [ ] Parse the active `data/XML/imbuements.xml` registry and report structural, tier, cost, duration, source-item and effect defects.
- [ ] Audit engine loading, item-slot eligibility, shrine visibility/application, scroll application, removal/clearing and duration consumption paths.
- [ ] Distinguish confirmed static behavior, configuration-dependent behavior, dynamic/custom definitions and unresolved runtime behavior.
- [ ] Compare the current registry and mechanics baseline with the referenced TibiaWiki/Fandom Imbuing page using evidence, without copying large wiki tables into the repository.
- [ ] Produce a human-readable evidence report and a machine-readable runtime test plan.
- [ ] Add focused unit tests for parser and classifier behavior.
- [ ] Do not modify `data/XML/imbuements.xml`, active datapacks, map, assets, item binaries, protocol behavior or engine behavior in this audit PR.
- [ ] Relevant checks completed.
- [ ] Module catalogue impact handled.
- [ ] Documentation/changelog impact handled or recorded as none.
- [ ] Cross-repository impact handled as none unless protocol evidence proves otherwise.
- [ ] Autonomous merge gate satisfied.

# Confirmed context

- The writable repository is `blakinio/canary`; `opentibiabr/canary` is reference-only.
- The repository contains engine Imbuements code, `data/XML/imbuements.xml`, active shrine scripts, imbuement scroll handling and NPC/storage integrations.
- Merged PR #86 fixed configured imbuement-storage filtering and added focused policy coverage.
- The referenced TibiaWiki/Fandom page describes 20-hour duration, tier fees, clearing fee, account restrictions, source consumption order, duplicate-category restrictions and item-type eligibility.
- The world-validation project requires explicit structure/reference/semantic/runtime/regression layers and forbids guessing runtime behavior.
- Open PRs were inspected on 2026-07-12; no active imbuement-validation overlap was found.
- PR #165 owns `docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md`; this task will read but not edit that shared file unless ownership is explicitly resolved.

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
- Overlaps: shared coordination indexes only; PR #165 owns the general world-validation project document.
- Resolution: use a dedicated branch, edit shared indexes narrowly, do not edit `OTS_AI_WORLD_VALIDATION_PROJECT.md`, and keep the first PR read-only.

# Current state

The system has a mature Imbuements implementation and one recent storage-filter fix, but no deterministic repository-wide audit that correlates XML definitions, item eligibility, runtime entry points, protocol-visible behavior and current reference mechanics.

# Plan

1. Inventory all Imbuing definitions, engine classes, Lua APIs, scripts, configuration and existing tests.
2. Build a normalized reference baseline from the cited Imbuing page and clearly mark version-sensitive facts.
3. Implement a deterministic read-only scanner and focused parser/classifier tests.
4. Generate the evidence report and runtime test plan against the branch state.
5. Run available checks through GitHub CI, inspect failures and update the task/PR.
6. Split any confirmed gameplay defect into separate focused fixes after evidence review.

# Work log

## 2026-07-12T17:18:21Z

- Changed: created a dedicated task branch and persistent task record.
- Learned: Imbuing spans XML definitions, C++ runtime, Lua bindings, shrine/scroll scripts, item metadata, storage gates and protocol/UI messages; a single-file comparison would be insufficient.
- Failed/blocked: local shell cannot resolve `github.com`, so repository-wide execution must use GitHub/CI or files fetched through the GitHub connector.
- Result: audit scope claimed; no gameplay files changed.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Keep the first PR read-only | Definition/runtime evidence must precede gameplay fixes under the world-validation methodology. | none |
| Treat TibiaWiki/Fandom as a reference baseline, not executable truth | The server may contain intentional custom/configurable behavior and the page can change. | none |
| Do not infer a defect from a missing direct text match | XML aliases, category logic, item metadata, Lua wrappers and protocol paths can be indirect. | none |
| Do not edit the shared project document while PR #165 owns it | Avoid overlapping path ownership and unnecessary merge conflicts. | none |

# Files and interfaces

| Path/interface/config/schema | Purpose | Status |
|---|---|---|
| `tools/ai-agent/imbuement_validation.py` | deterministic XML/runtime/reference correlation scanner | planned |
| `tools/ai-agent/test_imbuement_validation.py` | focused parser/classifier tests | planned |
| `docs/ai-agent/IMBUEMENT_VALIDATION_REPORT.md` | evidence report, findings and confidence | planned |
| `docs/ai-agent/IMBUEMENT_RUNTIME_TEST_PLAN.json` | machine-readable gameplay/runtime scenarios | planned |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| | focused Python tests | not-run | implementation pending |
| | Python bytecode compilation | not-run | implementation pending |
| | AI Agent Tools workflow | not-run | draft PR pending |

Never write `passed` without verification.

# Failed approaches and dead ends

- Direct `git clone` from the execution container failed because DNS resolution for `github.com` is unavailable.

# Risks and compatibility

- Runtime: no runtime change in the audit PR.
- Data/migration: none.
- Security: no secrets or player data.
- Backward compatibility: report/tool only.
- Cross-repo rollout: expected none; OTClient involvement will only be recorded if protocol evidence requires it.
- Rollback: revert documentation/tool commits.

# Remaining work

1. Inspect all active Imbuing sources and tests.
2. Implement the scanner and tests.
3. Produce the current evidence report and runtime test plan.
4. Open and maintain a draft PR, then verify CI.

# Handoff

## Start here

Read this task, then inspect `data/XML/imbuements.xml`, `src/creatures/players/imbuements/**`, the active shrine/scroll scripts, item parsing/eligibility code, protocol handlers and PR #86.

## Do not repeat

Do not declare an imbuement missing or unusable solely because its display name is absent from one script; definitions and runtime behavior are distributed across XML, C++, Lua and item metadata.

## Required reads

- `AGENTS.md`
- `docs/agents/ACTIVE_WORK.md`
- `docs/agents/MODULE_CATALOG.md`
- `docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md`
- `data/XML/imbuements.xml`
- engine Imbuements sources and active shrine/scroll scripts
- merged PR #86 and its focused tests

## Open questions

- Which current XML definitions differ from the referenced tier costs, effects, source requirements or item categories?
- Are account-type restrictions, material/gold consumption order, duplicate-category rules and duration decrement behavior fully represented by current runtime paths?
- Which item-specific exceptions are encoded in item data rather than the generic Imbuement category model?
- Which mechanics require a real client/server scenario rather than static confirmation?

# Completion

- Final status: active
- PR:
- Merge commit:
- Catalogue updated: no
- Changelog updated: no
- Archived at:
