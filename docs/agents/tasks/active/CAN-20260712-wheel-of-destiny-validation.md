---
task_id: CAN-20260712-wheel-of-destiny-validation
status: active
agent: "GPT-5.6 Thinking"
branch: feat/wheel-of-destiny-validation-audit
base_branch: main
created: 2026-07-12T19:37:47+02:00
updated: 2026-07-12T21:55:00+02:00
last_verified_commit: "a9ab587c8f21811a0a3b0311eed1b211522c9bb9"
risk: low
related_pr: "169"
owned_paths:
  - .github/workflows/wheel-of-destiny-validation.yml
  - tools/ai-agent/wheel_of_destiny_validation.py
  - tools/ai-agent/test_wheel_of_destiny_validation.py
  - tools/ai-agent/wheel_protocol_validation.py
  - tools/ai-agent/test_wheel_protocol_validation.py
  - tools/ai-agent/wheel_task_shop_validation.py
  - tools/ai-agent/test_wheel_task_shop_validation.py
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
  - canary-wheel-task-shop-audit-v1
  - Wheel runtime test plan schema v1
---

# Goal

Create a deterministic, evidence-based Wheel of Destiny and Gem Atelier audit without changing gameplay in the audit PR.

# Acceptance criteria

- [x] Dedicated project/handoff document and reference baseline.
- [x] Main scanner with seven focused tests.
- [x] Current + legacy protocol scanner with two focused tests.
- [x] Hunting Task Shop scanner with two focused tests.
- [x] Initial report and 20-scenario runtime plan.
- [x] Dedicated CI and first successful repository run.
- [x] Confirm current and legacy Reveal/ImproveGrade boundaries.
- [x] Confirm missing official Taskboard Wheel point shop path.
- [ ] Review latest eleven-test CI and all three audit pairs.
- [ ] Complete persistence/KV/migration review.
- [ ] Map every perk and spell augment.
- [ ] Compare both protocol profiles with compatible OTClient.
- [ ] Execute runtime plan.
- [ ] Update module catalogue and main project link.
- [ ] Split confirmed findings into focused PRs.

# Confirmed findings

- `WOD-F001`: Supreme Grade III 12m instead of 12.5m.
- `WOD-F002`: Grade IV count is not spendable and is added to every domain.
- `WOD-F003`: 16 Revelation Mastery variants have immediate plus queued application.
- `WOD-F004`: current + legacy Reveal and runtime omit cap 225.
- `WOD-F005`: current + legacy Grade position reaches 49/95 arrays before validation.
- `WOD-F006`: official Taskboard shop has zero offers, ShopBuy no purchase path, and Wheel extra points omit Hunting Task source.

# Open risks

- `WOD-R003`: resource removal ordering requires fault-injection evidence.
- `WOD-R005`: duplicate neighbour requires full graph comparison.
- persistence/KV atomicity and malformed-data recovery remain open.

# Work log

## 2026-07-12T21:55:00+02:00

- Changed: added `wheel_task_shop_validation.py` and two focused tests.
- Changed: workflow now runs three audits, eleven focused tests, validates three JSON outputs and uploads six audit files.
- Learned: Taskboard explicitly states it is a minimal official packet shim; shop offer count is zero and ShopBuy only returns an empty window.
- Learned: `getExtraPoints()` has no Hunting Task source; ordinary `task_points` currency is separate.
- Classification: WOD-R001 -> WOD-F006.
- Validation: Task Shop suite 2 tests, OK; existing seven + two suites remain locally passing.
- CI: latest combined run pending.
- Result: audit-only changes, no gameplay/data/protocol change.

## 2026-07-12T21:35:00+02:00

- Added current + legacy protocol audit and two tests.

## 2026-07-12T20:40:00+02:00

- Workflow run `29203018790` passed; artifact: 30 paths, 4 errors, 6 warnings, 16 Revelation variants.

# Validation

| Check | Result |
|---|---|
| main scanner local suite | 7 passed |
| protocol profiles local suite | 2 passed |
| Task Shop local suite | 2 passed |
| run `29203018790` | passed |
| latest three-audit workflow | pending |

Never record `passed` without verification.

# Remaining work

1. Review latest CI and artifacts.
2. Complete persistence/load/KV/migrations.
3. Map perks/spells and compare OTClient.
4. Execute runtime scenarios.
5. Create separate PRs for F001–F006.

# Handoff

Start with PR #169, the specialist project, report and this record. Do not implement fixes in PR #169. Do not convert Task Hunting currency balance directly into Wheel points; F006 requires a bounded purchased-reward model and persistence evidence.

# Completion

- Final status: active
- PR: #169 draft
- Catalogue updated: no
- Main project linked: no
- Cross-repo impact: OTClient comparison pending
