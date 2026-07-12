---
task_id: CAN-20260712-wheel-of-destiny-validation
coordination_id: ""
status: active
agent: "GPT-5.6 Thinking"
branch: feat/wheel-of-destiny-validation-audit
base_branch: main
created: 2026-07-12T19:37:47+02:00
updated: 2026-07-12T21:05:00+02:00
last_verified_commit: "92dc0572b14cb221dc79a6f86ae29aa50a895b2c"
risk: low
related_issue: ""
related_pr: "169"
depends_on: []
blocks: []
owned_paths:
  - .github/workflows/wheel-of-destiny-validation.yml
  - tools/ai-agent/wheel_of_destiny_validation.py
  - tools/ai-agent/test_wheel_of_destiny_validation.py
  - docs/ai-agent/OTS_AI_WHEEL_OF_DESTINY_VALIDATION_PROJECT.md
  - docs/ai-agent/WHEEL_OF_DESTINY_REFERENCE_BASELINE.json
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
  - canary-wheel-of-destiny-audit-v1
  - Wheel validation CLI
  - Wheel runtime test plan schema v1
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
- [ ] Compare current and legacy protocol payloads with the compatible OTClient.
- [ ] Validate schema, migrations and save/load paths.
- [x] Compare initial core values with the versioned 2026-07-12 TibiaWiki/Fandom snapshot.
- [x] Create a dedicated durable project document beside the main World Validation project.
- [x] Produce an initial human-readable evidence report and machine-readable runtime test plan.
- [x] Add focused deterministic unit tests for the scanner/classifier.
- [x] Add a dedicated CI workflow for the scanner and JSON artifacts.
- [x] Review the first CI run on the actual repository branch.
- [x] Review current-payload Reveal and ImproveGrade caller boundaries.
- [x] Do not modify active Wheel data, combat/spells, protocol, schema, datapacks, map or assets in this audit PR.
- [ ] Review CI for the enhanced protocol-boundary scanner.
- [ ] Module catalogue impact handled.
- [ ] Main World Validation document links this specialist project.
- [ ] Cross-repository impact handled or explicitly recorded.
- [ ] Autonomous merge gate satisfied.

# Confirmed context

- Writable repository: `blakinio/canary`; upstream is reference-only.
- Draft PR: #169.
- Branch merge-base: `dbcc809bac57bb78425ca39c2523c723cef79bb0`.
- No gameplay/runtime files are changed by this task.
- First CI run `29203018790` succeeded on head `13c14437b40db057a094f3625215b10b4061ed6b`.
- First artifact: 30 source files, 4 errors, 6 warnings, 16 doubled Revelation Mastery variants.
- Enhanced scanner commits: `36dbd278cbe032486439d1a1a17c79b9ec81a885` and `92dc0572b14cb221dc79a6f86ae29aa50a895b2c`.

# Current evidence

## Static matches

- 36 slices; Revelation thresholds 250/500/1000.
- level 51+, promoted Premium access; 1 point per level after 50.
- five Promotion Scrolls total 50; Monk quest bonus 10.
- temple-only decrease/reset option.
- reveal costs 125k/1m/6m; rotate costs 125k/250k/500k.
- Basic Grade II–IV and Supreme Grade II/IV costs.
- Grade IV multiplier 1.5.

These remain `static-consistent`, not runtime verified.

## Confirmed findings

- `WOD-F001`: Supreme Grade III returns 12,000,000 instead of 12,500,000.
- `WOD-F002`: Grade IV count is absent from spendable points and added globally to every domain threshold.
- `WOD-F003`: all 16 detected Revelation Mastery cases apply immediately and via queued strategy.
- `WOD-F004`: neither current-payload parser nor `revealGem()` enforces the 225 revealed-gem cap.
- `WOD-F005`: current-payload byte `position` reaches direct indexing of 49/95-element Grade arrays without validation.

## Remaining risks

- `WOD-R001`: Hunting Task Shop points path not found in `getExtraPoints()`.
- `WOD-R003`: resource removal ordering is not visibly atomic; prechecks exist, fault injection pending.
- `WOD-R005`: duplicate neighbour check for `SLOT_GREEN_TOP_100`.
- `WOD-R006`: legacy `Game::playerWheelGemAction` path not yet traced.

# Plan

1. Review the enhanced scanner's GitHub Actions run and artifact.
2. Record exact post-enhancement finding counts.
3. Trace legacy Gem Atelier payload.
4. Complete persistence, migration and malformed-data review.
5. Find Hunting Task Shop point award/storage path.
6. Compare payloads with compatible `opentibiabr/otclient`.
7. Execute focused runtime scenarios.
8. Split confirmed defects into separate minimal PRs.

# Work log

## 2026-07-12T21:05:00+02:00

- Changed: expanded scanner to read `protocolgame.cpp`, array sizes and current-payload boundary validation.
- Changed: updated fixtures/tests, project handoff and evidence report.
- Learned: opcode `0xE7` current payload dispatches Reveal and ImproveGrade directly.
- Learned: Reveal cap is absent in parser and runtime method; WOD-R002 became WOD-F004.
- Learned: ImproveGrade forwards arbitrary byte and indexes 49/95-element arrays first; WOD-R004 became WOD-F005.
- Learned: destroy/switch/lock invalid indexes are rejected through `getGem()` sentinel guard.
- Validation: local focused suite rerun — 7 tests, OK.
- CI: enhanced scanner run pending.
- Result: audit-only changes; no gameplay/protocol behavior changed.

## 2026-07-12T20:40:00+02:00

- Validation: workflow run `29203018790` succeeded.
- Artifact: 30 source files, 4 errors, 6 warnings, 16 doubled Revelation modifiers.
- Result: parser works on actual repository merge ref.

## 2026-07-12T20:25:00+02:00

- Changed: published scanner, seven tests, versioned baseline, report, 20-scenario runtime plan and CI workflow.
- Validation: local focused suite — 7 tests, OK.
- Failed/blocked: runtime server and compatible-client packet capture unavailable locally.

## 2026-07-12T19:45:00+02:00

- Changed: published active-work entry and draft PR #169.

## 2026-07-12T19:37:47+02:00

- Changed: created task record and claimed validation paths.
- Failed/blocked: direct local clone cannot resolve `github.com`; GitHub connector is used for authoritative reads/writes.

# Files and interfaces

| Path/interface | Purpose | Status |
|---|---|---|
| `docs/ai-agent/OTS_AI_WHEEL_OF_DESTINY_VALIDATION_PROJECT.md` | durable scope, changelog and handoff | current |
| `docs/ai-agent/WHEEL_OF_DESTINY_REFERENCE_BASELINE.json` | versioned requested reference values | current |
| `tools/ai-agent/wheel_of_destiny_validation.py` | static and current-payload boundary scanner | enhanced |
| `tools/ai-agent/test_wheel_of_destiny_validation.py` | parser/finding regression tests | enhanced |
| `docs/ai-agent/WHEEL_OF_DESTINY_VALIDATION_REPORT.md` | evidence report | current |
| `docs/ai-agent/WHEEL_OF_DESTINY_RUNTIME_TEST_PLAN.json` | 20 runtime/protocol/persistence scenarios | current |
| `.github/workflows/wheel-of-destiny-validation.yml` | CI and audit artifact publication | active |

# Validation and CI

| Commit/run | Command/check | Result | Evidence/notes |
|---|---|---|---|
| local enhanced workspace | `python -m unittest discover -s /mnt/data -p 'test_wheel_of_destiny_validation.py' -v` | passed | 7 tests, 0 failures, 0 errors |
| run `29203018790` | Wheel of Destiny Validation | passed | first scanner; all steps success |
| head after `92dc0572...` | Wheel of Destiny Validation | pending | expected counts are not authoritative until artifact review |

Never write `passed` without verification.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Keep first PR read-only | Evidence baseline must precede gameplay/schema/protocol changes. | none |
| Store external values in versioned JSON | Preserves the exact requested snapshot. | none |
| Split findings by behavior | Cost, points, double effect, cap and bounds safety have distinct risk/test surfaces. | none |
| Upgrade cap and bounds findings only after caller review | Parser and runtime evidence now close the missing validation layer for current payload. | none |
| Keep atomicity as risk | Item-count prechecks exist; failure behavior still needs runtime/fault evidence. | none |

# Failed approaches and dead ends

- Direct `git clone` failed because the execution container cannot resolve `github.com`.
- Private-fork code search is incomplete; direct fork file fetches and public raw primary sources were used for path/function discovery.
- Local unit tests validate parser behavior and fixtures only; they do not replace repository CI or gameplay tests.

# Risks and compatibility

- Runtime: no runtime code changed.
- Data/migration: no schema/migration changed.
- Protocol: no payload changed; current-payload input defects are documented only.
- Security: WOD-F005 is a confirmed current-payload bounds-safety defect; exploitability/runtime impact still needs controlled testing.
- Backward compatibility: documentation/tool/workflow only.
- Rollback: revert audit commits.

# Remaining work

1. Inspect latest CI and artifact.
2. Link specialist project from main World Validation document.
3. Update module catalogue.
4. Trace legacy protocol, persistence and Hunting Task points.
5. Compare compatible OTClient contract.
6. Execute runtime plan.
7. Create separate focused defect PRs after evidence review.

# Handoff

## Start here

Read `AGENTS.md`, `docs/agents/**`, the main World Validation project, the specialist project, the report, this task record and PR #169.

## Next exact action

Inspect the `Wheel of Destiny Validation` workflow for the latest head after `92dc0572...`. If successful, record artifact-backed counts in all three documents and PR body. Then trace `Game::playerWheelGemAction`, persistence/KV and Hunting Task points.

## Do not repeat

- Do not infer runtime correctness from static matches.
- Do not downgrade F004/F005 without contrary caller evidence.
- Do not upgrade R001/R003/R005/R006 without missing evidence.
- Do not repair gameplay in PR #169.
- Do not combine WOD-F001..F005 in one correction PR.
- Do not modify `opentibiabr/canary`.

# Completion

- Final status: active
- PR: #169 draft
- Merge commit:
- Catalogue updated: no
- Main project linked: no
- Cross-repo impact: pending legacy/OTClient review
- Archived at:
