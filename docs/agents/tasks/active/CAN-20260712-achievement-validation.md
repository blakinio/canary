---
task_id: CAN-20260712-achievement-validation
coordination_id: ""
status: active
agent: "GPT-5.6 Thinking"
branch: feat/achievement-validation-audit
base_branch: main
created: 2026-07-12T17:16:14Z
updated: 2026-07-12T17:50:00Z
last_verified_commit: "bb7f3cf8558ac03c71547697a61192de7e56dc88"
risk: low
related_issue: ""
related_pr: "#165"
depends_on: []
blocks: []
owned_paths:
  - tools/ai-agent/achievement_validation.py
  - tools/ai-agent/test_achievement_validation.py
  - docs/ai-agent/OTS_AI_ACHIEVEMENT_VALIDATION_PROJECT.md
  - docs/ai-agent/ACHIEVEMENT_VALIDATION_REPORT.md
  - docs/ai-agent/ACHIEVEMENT_REFERENCE_BASELINE.json
  - docs/ai-agent/ACHIEVEMENT_RUNTIME_TEST_PLAN.json
  - docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md
  - .github/workflows/achievement-validation.yml
  - docs/agents/tasks/active/CAN-20260712-achievement-validation.md
  - docs/agents/ACTIVE_WORK.md
  - docs/agents/MODULE_CATALOG.md
modules_touched:
  - AI world validation
  - achievement registry and trigger audit
reuses:
  - OTS AI World Validation evidence methodology
  - existing ACHIEVEMENTS registry
  - existing Player achievement APIs
public_interfaces:
  - canary-achievement-audit-v1
  - achievement validation CLI
  - canary-achievement-reference-baseline-v1
  - canary-achievement-runtime-test-plan-v1
cross_repo_tasks: []
---

# Goal

Create a deterministic, evidence-based audit of Canary achievements that validates registry metadata and active award paths without changing gameplay data.

# Acceptance criteria

- [x] Parse the active `ACHIEVEMENTS` registry and report structural/metadata defects.
- [x] Scan active datapacks for static and dynamic achievement award/progress paths.
- [x] Distinguish definitions, runtime awards, progress-only references, checks, removals, admin-only paths, and unresolved dynamic references.
- [x] Record a versioned TibiaWiki/Fandom metadata baseline without copying spoiler acquisition text.
- [x] Create a dedicated durable project document beside the main World Validation project.
- [x] Produce a machine-readable runtime test plan.
- [x] Add focused unit tests for parser and classifier behavior.
- [x] Add a dedicated read-only CI workflow that publishes JSON/Markdown artifacts.
- [x] Do not modify the achievement registry, active datapacks, map, assets, or engine behavior in this audit PR.
- [ ] Produce the final human-readable evidence report from a complete repository run.
- [ ] Verify GitHub Actions on the current head and inspect the generated artifact.
- [x] Module catalogue impact handled.
- [ ] Link the specialist document from the main World Validation document.
- [ ] Autonomous merge gate satisfied.

# Confirmed context

- The writable repository is `blakinio/canary`; `opentibiabr/canary` is reference-only.
- `data/scripts/lib/register_achievements.lua` reaches ID 570 and contains explicit gaps.
- TibiaWiki/Fandom reported 562 listed achievements out of 563 total on 2026-07-12: 362 common, 200 discovered secret, 201 total secret; theoretical point sum 1470.
- The current helper layer consumes the sparse table using `#ACHIEVEMENTS`.
- `Game.isAchievementSecret` resolves `foundAchievement` but returns `achievement.secret`; its invalid-input message also references undefined variable `ach`.
- A grade-1 zero-point definition exists and is retained as an informational exception rather than automatically treated as corruption.
- Open PR state was inspected repeatedly; no achievement-validation overlap exists. PR #166 reads the main project document but explicitly leaves shared ownership to this task.

# Existing work to reuse

| Module/task/PR | Reuse | Evidence/path | Why it fits |
|---|---|---|---|
| OTS AI World Validation | Evidence layers and handoff rules | `docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md` | Defines structure/reference/semantic/runtime/regression layers. |
| Achievement registry | Canonical active definitions | `data/scripts/lib/register_achievements.lua` | IDs, names, grades, points, secrecy and descriptions. |
| Player achievement API | Runtime operations | engine/Lua Player achievement sources | Defines award, progress, check, persistence and removal behavior. |
| AI Agent workflow conventions | Python discovery and artifact publication | `.github/workflows/ai-agent-tools.yml` | Existing standard-library test conventions and artifact policy. |

# Ownership and overlap check

- Open PRs inspected: #167, #166, #165, #157, #156, #155, #136 and current open-state search.
- Active tasks inspected: `docs/agents/ACTIVE_WORK.md` plus open PR state.
- Overlaps: PR #166 reads but does not edit the shared World Validation document; no source/tool overlap.
- Resolution: dedicated branch and read-only achievement audit scope.

# Current state

The deterministic scanner, focused tests, reference baseline, runtime test plan, dedicated project document, dedicated workflow and module catalogue entry are committed on PR #165. The remaining blocker is a complete GitHub-hosted repository run and inspection of its generated artifact; the execution container cannot clone GitHub because DNS resolution is unavailable.

# Work log

## 2026-07-12T17:50:00Z

- Changed: added the eighth focused test for the documented zero-point exception; refreshed the PR body; closed and reopened the draft to emit a `pull_request/reopened` event.
- Learned: neither reopening nor earlier synchronize events exposed any pull-request workflow run through the GitHub connector. A follow-up task-record commit is being used to emit a fresh `push` and `pull_request/synchronize` event.
- Failed/blocked: Actions/check status remains unavailable; no CI success is claimed.
- Result: all known local parser cases have focused coverage; full-repository artifact remains the only validation blocker.

## 2026-07-12T17:43:00Z

- Changed: added `achievement_validation.py`, seven focused tests, external metadata baseline, runtime scenario plan, dedicated workflow and module catalogue entry.
- Learned: grade/point ranges need an explicit zero-point informational exception; otherwise the current `King's Council` definition would be falsely classified as structural corruption.
- Validation: local isolated test copy ran `python -m unittest -v`; 7 tests passed. JSON files passed `python -m json.tool`; Python files passed `py_compile`.
- Failed/blocked: no pull-request workflow run was visible yet for current commits; do not claim CI success.
- Result: implementation is reviewable and read-only; full-repository artifact remains pending.

## 2026-07-12T17:22:00Z

- Changed: added `docs/ai-agent/OTS_AI_ACHIEVEMENT_VALIDATION_PROJECT.md` beside the main World Validation project.
- Learned: definition validity, runtime award paths and gameplay dependencies are independent dimensions and require a specialist handoff.
- Result: project scope, dispositions, helper findings and handoff became persistent in Git.

## 2026-07-12T17:16:14Z

- Changed: created task branch, task record, Active Work row and draft PR #165.
- Learned: maximum ID is not a count because the registry is sparse.
- Failed/blocked: `git clone` cannot resolve `github.com` in the execution container.
- Result: scope claimed; no gameplay files changed.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Keep a separate project document | Achievement definitions, triggers, persistence and runtime scenarios need a durable specialist handoff without bloating the main project file. | none |
| Keep the first PR read-only | Evidence and classifier coverage must precede gameplay/helper fixes. | none |
| Preserve dynamic uncertainty | A missing literal call does not prove unobtainability; table/wrapper paths need semantic or runtime review. | none |
| Publish large per-achievement output only as CI artifact | Repository policy keeps generated reports out of Git while retaining schema, small reports, tests and docs. | none |
| Treat zero-point grade entries as informational exceptions | Current canonical data and reference metadata include such an entry; rigid grade-range rejection would be a false positive. | none |

# Files and interfaces

| Path/interface/config/schema | Purpose | Status |
|---|---|---|
| `docs/ai-agent/OTS_AI_ACHIEVEMENT_VALIDATION_PROJECT.md` | durable methodology, state and handoff | created |
| `tools/ai-agent/achievement_validation.py` | deterministic registry/reference scanner and Markdown renderer | implemented |
| `tools/ai-agent/test_achievement_validation.py` | parser, helper, classifier and baseline tests | implemented; 8 local tests passed |
| `docs/ai-agent/ACHIEVEMENT_REFERENCE_BASELINE.json` | versioned external metadata snapshot | created and JSON-validated |
| `docs/ai-agent/ACHIEVEMENT_RUNTIME_TEST_PLAN.json` | machine-readable runtime/E2E scenarios | created and JSON-validated |
| `.github/workflows/achievement-validation.yml` | focused tests, full scan, summary and artifact upload | implemented; CI run pending |
| `docs/ai-agent/ACHIEVEMENT_VALIDATION_REPORT.md` | bounded evidence report based on complete artifact | pending artifact |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| local candidate matching scanner/tests | `python -m unittest -v` in isolated tool directory | passed | 8 tests after zero-point case |
| local candidate | `python -m py_compile achievement_validation.py test_achievement_validation.py` | passed | no syntax error |
| local candidate | `python -m json.tool` for reference baseline and runtime plan | passed | both valid JSON |
| `bb7f3cf8558ac03c71547697a61192de7e56dc88` | changed-file/diff scope review | reviewed | tools/docs/workflow/agent-memory only; no gameplay or binary path |
| current PR head | Achievement Validation workflow | not-run/unknown | no associated pull-request run visible after synchronize and reopen |
| current PR head | existing AI Agent Tools workflow | not-run/unknown | no associated pull-request run visible after synchronize and reopen |

Never write `passed` without verification.

# Failed approaches and dead ends

- Direct `git clone` and `git ls-remote` from the execution container fail because DNS cannot resolve `github.com`.
- GitHub code search does not index the user fork sufficiently for a complete repository scan.
- GitHub file fetch cannot retrieve a recursive repository tree/archive; the complete scan must therefore run in Actions or another real checkout.
- The connector exposes only pull-request-associated workflow runs; push-run discovery is not available through its current Actions surface.

# Risks and compatibility

- Runtime: no runtime code change.
- Data/migration: no registry or player data change.
- Security: no secrets or player data.
- Backward compatibility: additive tool/schema/workflow only.
- Cross-repo rollout: none.
- CI: workflow intentionally exits zero with confirmed findings while the JSON `ok` field remains false; findings are evidence, not silently passed behavior.
- Rollback: revert PR #165.

# Remaining work

1. Obtain the first complete workflow run and download `achievement-validation-audit`.
2. Inspect exact counts, unknown static references, dynamic references and per-achievement dispositions.
3. Correct scanner false positives or parser limitations, rerun, and repeat until the report is trustworthy.
4. Commit `ACHIEVEMENT_VALIDATION_REPORT.md` with bounded findings and follow-up PR order.
5. Link this specialist project from `OTS_AI_WORLD_VALIDATION_PROJECT.md`.
6. Update PR body/task with final commit, checks and changed-file review.
7. Keep confirmed helper/gameplay fixes in separate focused PRs.

# Handoff

## Start here

Read `docs/ai-agent/OTS_AI_ACHIEVEMENT_VALIDATION_PROJECT.md`, this task and PR #165. Run the CLI against a complete checkout and inspect the JSON artifact before classifying any achievement as missing.

## Do not repeat

- Do not infer unobtainability from absence of a literal `addAchievement` call.
- Do not fix `register_achievements.lua` inside this audit PR.
- Do not commit generated full per-achievement JSON/Markdown reports.
- Do not treat the maximum ID as registry count.
- Do not reintroduce rigid rejection of documented zero-point definitions.

## Required reads

- `AGENTS.md`
- `docs/agents/ACTIVE_WORK.md`
- `docs/agents/MODULE_CATALOG.md`
- `docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md`
- `docs/ai-agent/OTS_AI_ACHIEVEMENT_VALIDATION_PROJECT.md`
- achievement registry and Player achievement API sources

## Open questions

- Which dynamic table/wrapper calls can be resolved deterministically without guessing?
- Does the complete registry exactly match all four recorded baseline dimensions?
- Which no-direct-static-reference achievements are genuinely unavailable versus awarded through indirect paths?

# Completion

- Final status: active
- PR: #165
- Merge commit:
- Catalogue updated: yes, active #165 entry
- Changelog updated: not applicable until behavior/module status is final
- Archived at:
