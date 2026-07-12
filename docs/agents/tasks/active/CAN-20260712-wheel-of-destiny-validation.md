---
task_id: CAN-20260712-wheel-of-destiny-validation
coordination_id: ""
status: active
agent: "GPT-5.6 Thinking"
branch: feat/wheel-of-destiny-validation-audit
base_branch: main
created: 2026-07-12T19:37:47+02:00
updated: 2026-07-12T20:25:00+02:00
last_verified_commit: "ecd31f646a39f0ac4aa9d59ba47dc918f2d292b6"
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
- [ ] Map protocol handlers and compare payloads with the compatible OTClient when required.
- [ ] Validate schema, migrations and save/load paths.
- [x] Compare initial core values with the versioned 2026-07-12 TibiaWiki/Fandom snapshot.
- [x] Create a dedicated durable project document beside the main World Validation project.
- [x] Produce an initial human-readable evidence report and machine-readable runtime test plan.
- [x] Add focused deterministic unit tests for the scanner/classifier.
- [x] Add a dedicated CI workflow for the scanner and JSON artifacts.
- [x] Do not modify active Wheel data, combat/spells, protocol, schema, datapacks, map or assets in this audit PR.
- [ ] Review the first CI run on the actual repository branch.
- [ ] Module catalogue impact handled.
- [ ] Main World Validation document links this specialist project.
- [ ] Cross-repository impact handled or explicitly recorded.
- [ ] Autonomous merge gate satisfied.

# Confirmed context

- Writable repository: `blakinio/canary`; upstream is reference-only.
- Draft PR: #169.
- Branch merge-base: `dbcc809bac57bb78425ca39c2523c723cef79bb0`.
- `main` moved after branch creation by an unrelated documentation commit; no owned-path overlap was found.
- Dedicated handoff: `docs/ai-agent/OTS_AI_WHEEL_OF_DESTINY_VALIDATION_PROJECT.md`.
- External baseline: `docs/ai-agent/WHEEL_OF_DESTINY_REFERENCE_BASELINE.json`.
- No gameplay/runtime files are changed by this task.

# Current evidence

## Static matches

- 36 slices.
- Revelation thresholds 250/500/1000.
- level 51+, promoted Premium access gate.
- 1 point per level after 50.
- five Promotion Scrolls total 50 points.
- Monk quest bonus 10.
- temple-only decrease/reset option.
- reveal costs 125k/1m/6m.
- rotate costs 125k/250k/500k.
- Basic Grade II–IV costs.
- Supreme Grade II and IV costs.
- Grade IV multiplier 1.5.

These remain `static-consistent`, not runtime verified.

## Confirmed static findings

- `WOD-F001`: Supreme Grade III returns 12,000,000 instead of the selected reference value 12,500,000.
- `WOD-F002`: `m_modsMaxGrade` is absent from `getExtraPoints()` and is added to every domain in `getPlayerSliceStage()`.
- `WOD-F003`: Revelation Mastery Supreme Mod cases both apply immediately and queue a strategy that applies the same value again.

## Risks pending caller/protocol/runtime evidence

- `WOD-R001`: Hunting Task Shop points path not found in `getExtraPoints()`.
- `WOD-R002`: no 225 cap check inside `revealGem()`.
- `WOD-R003`: reveal/upgrade resource removal is not visibly atomic.
- `WOD-R004`: grade arrays appear indexed with client-supplied position before local validation.
- `WOD-R005`: duplicate neighbour check for `SLOT_GREEN_TOP_100`.

# Plan

1. Review the first GitHub Actions run and generated audit artifact.
2. Fix scanner parser assumptions if the actual branch run fails; update project/task/report immediately.
3. Record exact source inventory, finding counts and comparisons from CI.
4. Complete protocol handler and call-site mapping.
5. Complete persistence, migration and malformed-data review.
6. Compare payloads with compatible `opentibiabr/otclient`.
7. Execute focused runtime scenarios.
8. Split confirmed gameplay defects into separate minimal PRs.

# Work log

## 2026-07-12T20:25:00+02:00

- Changed: published scanner, seven focused tests, versioned baseline, initial report, 20-scenario runtime plan and dedicated CI workflow.
- Changed: updated durable project/handoff with PR, findings, risks, test result and next steps.
- Learned: the selected reference confirms 12.5m Supreme Grade III, 225 revealed-gem cap, 50 Hunting Task points and 69 Grade IV points.
- Learned: three high-confidence static implementation problems are separable into cost, point-accounting and Revelation Mastery follow-up work.
- Validation: `python -m unittest discover -s /mnt/data -p 'test_wheel_of_destiny_validation.py' -v` -> 7 tests, OK.
- Failed/blocked: runtime execution and compatible-client packet capture are not available locally; CI and later integration environment are required.
- Result: audit infrastructure exists; no gameplay behavior changed.

## 2026-07-12T19:45:00+02:00

- Changed: published active work entry and draft PR #169.
- Learned: branch merge-base predates one unrelated main documentation commit.
- Result: ownership and overlap are explicit.

## 2026-07-12T19:37:47+02:00

- Changed: created persistent task record and claimed validation paths.
- Failed/blocked: direct local clone cannot resolve `github.com`; GitHub connector is used for authoritative reads/writes.

## 2026-07-12T19:35:00+02:00

- Changed: created the specialist project document beside the main World Validation project.

# Files and interfaces

| Path/interface | Purpose | Status |
|---|---|---|
| `docs/ai-agent/OTS_AI_WHEEL_OF_DESTINY_VALIDATION_PROJECT.md` | durable scope, changelog and handoff | current |
| `docs/ai-agent/WHEEL_OF_DESTINY_REFERENCE_BASELINE.json` | versioned requested reference values | created |
| `tools/ai-agent/wheel_of_destiny_validation.py` | deterministic static scanner | created |
| `tools/ai-agent/test_wheel_of_destiny_validation.py` | parser/finding regression tests | created |
| `docs/ai-agent/WHEEL_OF_DESTINY_VALIDATION_REPORT.md` | initial evidence report | created |
| `docs/ai-agent/WHEEL_OF_DESTINY_RUNTIME_TEST_PLAN.json` | 20 runtime/protocol/persistence scenarios | created |
| `.github/workflows/wheel-of-destiny-validation.yml` | CI and audit artifact publication | created |

# Validation and CI

| Commit | Command/check/workflow | Result | Evidence/notes |
|---|---|---|---|
| local workspace | `python -m unittest discover -s /mnt/data -p 'test_wheel_of_destiny_validation.py' -v` | passed | 7 tests, 0 failures, 0 errors |
| `ecd31f646a39f0ac4aa9d59ba47dc918f2d292b6` | specialist project/handoff update | written | records all changes through this iteration |
| latest PR head | Wheel of Destiny Validation workflow | pending review | must inspect run, job logs and generated artifact |

Never write `passed` without verification.

# Decisions

| Decision | Reason/evidence | ADR |
|---|---|---|
| Keep first PR read-only | Complete evidence baseline must precede gameplay, schema or protocol changes. | none |
| Store external values in a versioned JSON baseline | Prevents silent drift and preserves the exact requested snapshot. | none |
| Compare only externally supported multiplier values | The page explicitly supports Grade I and Grade IV/+50%; intermediate multipliers are not guessed. | none |
| Split confirmed defects by behavior | Cost, point accounting and double effect have different risk and test surfaces. | none |
| Keep cap/atomicity/index issues as risks | Direct method inspection is insufficient without caller/protocol/runtime evidence. | none |

# Failed approaches and dead ends

- Direct `git clone` failed because the execution container cannot resolve `github.com`.
- Private-fork code search returned incomplete Wheel results; authoritative files are fetched directly from `blakinio/canary` after upstream path discovery.
- Local unit tests validate parser behavior and fixtures only; they do not replace repository CI or gameplay tests.

# Risks and compatibility

- Runtime: no runtime code changed.
- Data/migration: no schema/migration changed.
- Protocol: read-only analysis only; any correction needs Canary ↔ OTClient contract work.
- Security: malformed client positions and partial resource consumption are under review, not yet confirmed exploitable.
- Backward compatibility: documentation/tool/workflow only.
- Rollback: revert audit commits.

# Remaining work

1. Inspect CI for the latest PR head.
2. Update generated finding counts and source inventory in the report.
3. Link specialist project from the main World Validation document.
4. Update module catalogue.
5. Complete protocol/persistence/call-site analysis.
6. Execute runtime plan.
7. Create separate focused defect PRs after evidence review.

# Handoff

## Start here

Read:

- `AGENTS.md`
- `docs/agents/ACTIVE_WORK.md`
- `docs/agents/MODULE_CATALOG.md`
- `docs/agents/CROSS_REPO_CONTRACTS.md`
- `docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md`
- `docs/ai-agent/OTS_AI_WHEEL_OF_DESTINY_VALIDATION_PROJECT.md`
- `docs/ai-agent/WHEEL_OF_DESTINY_VALIDATION_REPORT.md`
- PR #169 and its latest workflow run

## Next exact action

Inspect the `Wheel of Destiny Validation` workflow for the latest head. If it fails, use the job log to correct only the scanner or fixture assumptions, then update the specialist project, this task record and PR body. If it succeeds, record exact generated comparisons/findings/inventory and continue with protocol and persistence mapping.

## Do not repeat

- Do not infer runtime correctness from a static match.
- Do not upgrade WOD-R001..R005 to confirmed defects without missing evidence.
- Do not repair gameplay in PR #169.
- Do not combine WOD-F001/F002/F003 in one correction PR.
- Do not modify `opentibiabr/canary`.

# Completion

- Final status: active
- PR: #169 draft
- Merge commit:
- Catalogue updated: no
- Main project linked: no
- Cross-repo impact: pending protocol review
- Archived at:
