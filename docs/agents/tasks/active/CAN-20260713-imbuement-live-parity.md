---
task_id: CAN-20260713-imbuement-live-parity
program_id: ""
coordination_id: ""
status: ready_for_review_pending_ci
agent: "GPT-5.6 Thinking"
branch: fix/imbuement-live-parity
base_branch: main
created: 2026-07-13T14:20:00+02:00
updated: 2026-07-13T15:00:00+02:00
last_verified_commit: "8f67a9c6967f7d6b0db63783e19601d7a9d0ef28"
risk: medium
related_issue: "IMB-001, IMB-002, IMB-003, IMB-006"
related_pr: "#251"
depends_on:
  - merged Imbuement audit PR #166
  - merged Forgotten Knowledge storage repair PR #206
  - merged Vibrancy scroll repair PR #239
blocks: []
owned_paths:
  exclusive:
    - data/XML/imbuements.xml
    - tools/ai-agent/test_imbuement_validation.py
    - tools/ai-agent/imbuement_storage_validation.py
    - tools/ai-agent/test_imbuement_storage_validation.py
    - tests/fixture/core/XML/imbuements.xml
    - tests/unit/players/imbuements/imbuements_test.cpp
    - docs/ai-agent/IMBUEMENT_VALIDATION_REPORT.md
    - docs/ai-agent/IMBUEMENT_RUNTIME_TEST_PLAN.json
    - docs/agents/CHANGELOG.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/tasks/active/CAN-20260713-imbuement-live-parity.md
  shared: []
  read_only:
    - tools/ai-agent/imbuement_validation.py
    - src/creatures/players/imbuements/imbuements.cpp
    - src/creatures/players/imbuements/imbuements.hpp
    - src/creatures/players/player.cpp
    - src/server/network/protocol/protocolgame.cpp
    - data-otservbr-global/lib/core/storages.lua
    - data-otservbr-global/scripts/quests/**
    - data-otservbr-global/npc/**
modules_touched:
  - Imbuement XML registry
  - Imbuement deterministic storage validator
  - Imbuement focused tests, report and runtime plan
reuses:
  - tools/ai-agent/imbuement_validation.py
  - tools/ai-agent/imbuement_storage_validation.py
  - .github/workflows/imbuement-validation.yml
  - tests/shared/imbuements/imbuements_test_fixture.hpp
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Align the active Canary Imbuement registry with the current live Tibia mechanics selected by the user, while preserving the merged Forgotten Knowledge and Vibrancy scroll repairs.

# Acceptance criteria

- [x] Base application fees are exactly 7,500 / 60,000 / 250,000 gold with 100% success and no protection surcharge.
- [x] Basic, Intricate and Powerful Strike are exactly 5% critical chance with +5% / +15% / +40% critical damage.
- [x] Basic Punch consumes item 10281 x25 and higher tiers retain their cumulative material chains.
- [x] Protocol-visible base price/percent/protection fields use the same registry values without a protocol-shape change.
- [x] Powerful Featherweight uses proven Dangerous Depths completion storage 45929.
- [x] Powerful Vibrancy uses proven Dream Courts completion storage 46365.
- [x] Focused deterministic and C++ regression coverage is updated.
- [x] Validation report, rich runtime plan, module catalogue and changelog are current.
- [x] Final changed-file boundary contains only the 11 intended data/test/documentation paths.
- [ ] Current-head GitHub checks are inspected job-by-job and pass before merge.
- [ ] Autonomous merge gate is satisfied and the task is archived in a separate cleanup PR.

# Final implementation state

- Repository: `blakinio/canary`.
- Base main at task start: `3ad10132cbd76adc42f946da3ca3077e5bd6bbd0`.
- Final implementation/cleanup head before ready state: `8f67a9c6967f7d6b0db63783e19601d7a9d0ef28`.
- PR: #251, draft at this record update.
- User-selected authority: current live Tibia, not the historical chance/protection economy.
- IMB-004 from PR #239 and IMB-005 from PR #206 remain preserved.
- No open Imbuement implementation PR or owned-path overlap was found before implementation.
- `docs/agents/ACTIVE_WORK.md` is unchanged.

# Implemented behavior

## IMB-001 — fixed current-live fees

| Tier | Price | Success | Protection surcharge |
|---|---:|---:|---:|
| Basic | 7,500 | 100% | 0 |
| Intricate | 60,000 | 100% | 0 |
| Powerful | 250,000 | 100% | 0 |

`Player::onApplyImbuement` charges the registry price and applies after validation. The protocol reads price, percent and protection price from the same registry, so the XML remains the single authority.

## IMB-002 — Strike

| Tier | Critical chance | Critical damage |
|---|---:|---:|
| Basic | 5% | +5% |
| Intricate | 5% | +15% |
| Powerful | 5% | +40% |

## IMB-003 — Punch

- Basic: item `10281` x25.
- Intricate: item `10281` x25 + item `11489` x20.
- Powerful: previous sources + item `40529` x15.

## IMB-006 — quest completion unlocks

- Powerful Featherweight: storage `45929` (`DangerousDepths.Bosses.LastAchievement`). The active action writes it only after all three final boss-achievement markers are complete.
- Powerful Vibrancy: storage `46365` (`TheDreamCourts.DreamScarGlobal.NightmareTimer`). The active Nightmare Beast death path writes the persistent player marker used by the existing initialized-storage policy.
- Generic questline storages were rejected because they are written at quest start and would unlock the Powerful imbuements too early.

# Deterministic baseline after repair

- 3 tiers, 20 categories, 24 families, 72 entries.
- 48 XML scroll mappings and 48 active Lua scroll registrations.
- 24 Powerful families with nonzero unlock storage.
- No Powerful family with `storage=0`.
- Nonzero storage IDs: `45489..45495`, `45929`, `46365`.
- Registry validator: no findings in the verified focused runner.
- Strict storage validator: no findings in the verified focused runner.

# Final changed-file boundary

Exactly:

1. `data/XML/imbuements.xml`
2. `docs/agents/CHANGELOG.md`
3. `docs/agents/MODULE_CATALOG.md`
4. `docs/agents/tasks/active/CAN-20260713-imbuement-live-parity.md`
5. `docs/ai-agent/IMBUEMENT_RUNTIME_TEST_PLAN.json`
6. `docs/ai-agent/IMBUEMENT_VALIDATION_REPORT.md`
7. `tests/fixture/core/XML/imbuements.xml`
8. `tests/unit/players/imbuements/imbuements_test.cpp`
9. `tools/ai-agent/imbuement_storage_validation.py`
10. `tools/ai-agent/test_imbuement_storage_validation.py`
11. `tools/ai-agent/test_imbuement_validation.py`

No workflow, temporary helper, trigger, diagnostic, map, `items.otb`, binary asset, database schema, production configuration, client, protocol or `ACTIVE_WORK.md` path remains in the diff.

# Validation and evidence

## Local environment

Local checkout and local tests were unavailable:

```text
getent hosts github.com
# no DNS result

git ls-remote https://github.com/blakinio/canary.git HEAD
# fatal: unable to access 'https://github.com/blakinio/canary.git/': Could not resolve host: github.com
```

No local command or local test is claimed as passed. GitHub Actions is separate evidence.

## Focused runner evidence before final ready-head CI

- The temporary focused diagnostic run `29251409297` proved the patch applied and both deterministic audits returned no findings; its single failed test was an obsolete assertion expecting IMB-006 mismatches.
- The assertion was corrected to require `WIKI_POWERFUL_UNLOCK` findings to be absent.
- Finalization diagnostic run `29251754951` then reported:
  - Python compilation success;
  - 13/13 focused unit tests success;
  - registry audit success with `findings=[]`;
  - strict storage audit success with `findings=[]`;
  - runtime-plan JSON validation success.
- The same diagnostic proved `github-actions[bot]` cannot push to this repository (`HTTP 403`). Repository writes were therefore completed through the authorized GitHub API, not represented as local validation.
- Temporary workflows, helper, trigger and diagnostic files were removed, and the canonical Imbuement workflow was restored byte-for-byte from current `main`.

These runs are implementation evidence only. Fresh checks on the final ready head remain the merge gate.

# C++ regression coverage

The fixture and unit test now enforce:

- current live base prices, 100% success, zero protection surcharge, clear cost and duration;
- all three Strike chance/damage pairs;
- Basic Punch item `10281` x25;
- existing Vibrancy scroll resolution and scroll application atomicity.

# Decisions

- Target current live Tibia because the user selected it explicitly.
- Reuse the existing registry/loader/runtime rather than add a second subsystem.
- Use only active, proven completion markers for IMB-006.
- Preserve PR #206 and #239 behavior.
- Keep runtime, gameplay and physical-client evidence separate from static/compiled regression evidence.

# Failed approaches and dead ends

- Several guessed quest paths returned 404; exact paths were found through repository search instead of inferred.
- A validator-generated runtime plan temporarily reduced the rich scenario document; the 319-line plan was restored from the exact base and updated.
- Temporary workflow finalizers initially skipped PR events, used an indentation-sensitive helper anchor, and contained one stale IMB-006 test assertion. Each was diagnosed with artifacts and corrected.
- GitHub Actions push attempts failed with `Permission to blakinio/canary.git denied to github-actions[bot]` / HTTP 403.
- All temporary workflows, scripts, triggers and diagnostics are absent from the final diff.

# Remaining work

1. Update PR #251 body and mark Ready for review.
2. Inspect every final-head workflow and concrete job; do not rely only on aggregate `Required`.
3. Check reviews and changed-file boundary again.
4. Squash-merge if green.
5. Archive this task in a separate lifecycle cleanup PR with exact feature head, merge SHA and workflow/job IDs.

# Handoff

Continue only on PR #251 and branch `fix/imbuement-live-parity`. Do not restore the historical chance/protection model, do not replace storages `45929` or `46365` without stronger active evidence, and do not add workflow or unrelated runtime changes.

# Completion

- Final status: ready for review pending final-head CI.
- PR: #251.
- Merge commit: pending.
- Program record: not applicable.
- Catalogue: updated.
- Changelog: updated.
- Archive: pending cleanup PR.
