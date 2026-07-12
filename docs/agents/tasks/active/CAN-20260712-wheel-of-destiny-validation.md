---
task_id: CAN-20260712-wheel-of-destiny-validation
status: active
agent: "GPT-5.6 Thinking"
branch: feat/wheel-of-destiny-validation-audit
base_branch: main
created: 2026-07-12T19:37:47+02:00
updated: 2026-07-12T21:35:00+02:00
last_verified_commit: "3d9018f5651ceeffc94dda20bae2656bdbdad54c"
risk: low
related_pr: "169"
owned_paths:
  - .github/workflows/wheel-of-destiny-validation.yml
  - tools/ai-agent/wheel_of_destiny_validation.py
  - tools/ai-agent/test_wheel_of_destiny_validation.py
  - tools/ai-agent/wheel_protocol_validation.py
  - tools/ai-agent/test_wheel_protocol_validation.py
  - docs/ai-agent/OTS_AI_WHEEL_OF_DESTINY_VALIDATION_PROJECT.md
  - docs/ai-agent/WHEEL_OF_DESTINY_REFERENCE_BASELINE.json
  - docs/ai-agent/WHEEL_OF_DESTINY_VALIDATION_REPORT.md
  - docs/ai-agent/WHEEL_OF_DESTINY_RUNTIME_TEST_PLAN.json
  - docs/agents/tasks/active/CAN-20260712-wheel-of-destiny-validation.md
  - docs/agents/ACTIVE_WORK.md
modules_touched:
  - AI world validation
  - Wheel of Destiny and Gem Atelier audit
public_interfaces:
  - canary-wheel-of-destiny-audit-v1
  - canary-wheel-protocol-audit-v1
  - Wheel runtime test plan schema v1
---

# Goal

Create a deterministic, evidence-based audit of Canary's Wheel of Destiny and Gem Atelier without changing gameplay behavior in the audit PR.

# Acceptance criteria

- [x] Dedicated durable project document.
- [x] Versioned reference baseline.
- [x] Main deterministic scanner and seven focused tests.
- [x] Current and legacy protocol-boundary scanner and two focused tests.
- [x] Initial evidence report and 20-scenario runtime plan.
- [x] Dedicated CI workflow and first successful repository run.
- [x] Review current and legacy Reveal/ImproveGrade caller boundaries.
- [ ] Review latest nine-test CI run and both artifacts.
- [ ] Complete Hunting Task Shop point-path review.
- [ ] Complete persistence, KV and migration review.
- [ ] Map every perk and spell augment to runtime effect.
- [ ] Compare both payload profiles with compatible OTClient.
- [ ] Execute runtime plan.
- [ ] Update module catalogue and link main World Validation document.
- [ ] Split confirmed defects into focused follow-up PRs.

# Confirmed findings

- `WOD-F001`: Supreme Grade III is 12,000,000 instead of 12,500,000.
- `WOD-F002`: Grade IV points are not spendable and are added to every domain threshold.
- `WOD-F003`: 16 Revelation Mastery variants contain immediate plus queued application.
- `WOD-F004`: current and legacy Reveal paths plus `revealGem()` do not enforce 225 gems.
- `WOD-F005`: current and legacy Grade-position bytes reach 49/95-element arrays before validation.

Runtime impact remains unverified unless explicitly stated.

# Open risks

- `WOD-R001`: Hunting Task Shop Wheel point award/storage path not found.
- `WOD-R003`: resource removal ordering requires fault-injection evidence.
- `WOD-R005`: duplicate neighbour check requires full graph comparison.
- persistence/KV atomicity and malformed-data recovery remain open.

# Work log

## 2026-07-12T21:35:00+02:00

- Changed: added `wheel_protocol_validation.py` and `test_wheel_protocol_validation.py`.
- Changed: workflow now executes both scanners, nine total focused tests, validates two generated JSON reports and uploads four audit files.
- Learned: legacy `Game::playerWheelGemAction()` repeats the current profile's missing cap and unchecked Grade position.
- Validation: `python -m unittest discover -s /mnt/data -p 'test_wheel_protocol_validation.py' -v` -> 2 tests, OK.
- Validation: existing main suite remains 7 tests, OK.
- CI: latest combined workflow pending; do not record passed yet.
- Result: audit-only changes; no gameplay/protocol/schema/data changes.

## 2026-07-12T20:40:00+02:00

- Workflow run `29203018790` succeeded.
- Artifact: 30 source files, 4 errors, 6 warnings, 16 doubled Revelation variants.

## 2026-07-12T20:25:00+02:00

- Published main scanner, seven tests, baseline, report, runtime plan and workflow.

# Validation

| Commit/run | Check | Result |
|---|---|---|
| local | main scanner focused suite | 7 passed |
| local | protocol profile focused suite | 2 passed |
| run `29203018790` | first repository workflow | passed |
| head after `3d9018f...` | combined nine-test workflow | pending |

Never write `passed` without verification.

# Remaining work

1. Read latest workflow run and artifacts.
2. Trace Task Hunting Shop purchase/reward code.
3. Complete load order, KV, migrations and round-trip analysis.
4. Compare current and legacy payloads with `opentibiabr/otclient`.
5. Map perks/spells and execute runtime scenarios.
6. Create separate defect PRs after audit evidence review.

# Handoff

Start with PR #169, `OTS_AI_WHEEL_OF_DESTINY_VALIDATION_PROJECT.md`, this record and both generated audit artifacts. Do not modify runtime in PR #169 and do not combine F001–F005 into one correction PR.

# Completion

- Final status: active
- PR: #169 draft
- Catalogue updated: no
- Main project linked: no
- Cross-repo impact: OTClient comparison pending
