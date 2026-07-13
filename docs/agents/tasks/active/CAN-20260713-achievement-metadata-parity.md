---
task_id: CAN-20260713-achievement-metadata-parity
status: active
agent: "GPT-5.6 Thinking"
branch: fix/achievement-metadata-parity
base_branch: main
created: 2026-07-13T15:30:00+02:00
updated: 2026-07-13T15:30:00+02:00
last_verified_commit: "0aea5c00b6fadb2837dec59318a0589187daf94d"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - "merged comprehensive achievement audit PR #238"
  - "merged achievement validator/helper repairs #165, #176 and #184"
blocks:
  - "achievement handler and backfill parity work"
owned_paths:
  exclusive:
    - data/scripts/lib/register_achievements.lua
    - tools/ai-agent/test_achievement_validation.py
    - docs/agents/tasks/active/CAN-20260713-achievement-metadata-parity.md
    - docs/ai-agent/ACHIEVEMENT_VALIDATION_REPORT.md
    - docs/ai-agent/ACHIEVEMENT_COMPREHENSIVE_VALIDATION.md
  shared:
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
  read_only:
    - docs/ai-agent/ACHIEVEMENT_REFERENCE_CATALOG.json
    - docs/ai-agent/ACHIEVEMENT_REFERENCE_BASELINE.json
    - tools/ai-agent/achievement_validation.py
    - src/creatures/players/components/player_achievement.*
modules_touched:
  - achievement registry metadata
  - achievement validation regression coverage
reuses:
  - canary-achievement-audit-v2
  - Achievement Validation workflow
  - factual reference revision 1188274 from PR #238
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Resolve the seven metadata conflicts confirmed by the comprehensive achievement audit, without changing award conditions, handlers, persistence format, backfill, quests, maps or unrelated gameplay.

# Exact scope

Candidate metadata corrections from audit #238:

1. ID 406 `The More the Merrier`: grade 1 -> 0.
2. ID 513 `Soul Mender`: secret false -> true.
3. ID 526 `King's Council`: points 0 -> 2.
4. ID 555 `Inner Peace`: points 2 -> 3.
5. ID 556 `Fiend Rider`: points 2 -> 3.
6. ID 559 `Hope of the Merudri`: points 3 -> 2.
7. ID 562 `Alpha Rider`: points 2 -> 3.

No value will be changed until the exact current registry entry, factual catalogue row and current supported-content evidence are inspected.

# Acceptance criteria

- [x] Current main and open achievement-related PR state inspected.
- [x] No open PR owns `register_achievements.lua`, `player_achievement.cpp` or `achievement_validation.py`.
- [x] Dedicated branch and durable task record created.
- [ ] Draft PR opened.
- [ ] Exact seven registry definitions and reference catalogue rows inspected.
- [ ] Current external source evidence and supported-version boundary recorded.
- [ ] Only evidence-backed metadata fields changed.
- [ ] No achievement name/ID, handler, storage, backfill, map, item or quest condition changed.
- [ ] Focused regression tests fail before and pass after the metadata corrections.
- [ ] Comprehensive validator reports no metadata conflicts for corrected IDs.
- [ ] Existing handler/unresolved classifications remain unchanged except removal of these metadata mismatches.
- [ ] Documentation and task record updated with exact commands, runs, SHA and results.
- [ ] Current-head dedicated audit, AI Agent Tools, ownership, autofix and required CI pass.
- [ ] PR marked Ready and auto-merge enabled only after all gates pass.
- [ ] Task archived in a separate cleanup PR after merge.

# Sources read

| Source | Date | Purpose |
|---|---|---|
| `docs/ai-agent/ACHIEVEMENT_VALIDATION_REPORT.md` | 2026-07-13 | seven confirmed metadata conflicts |
| `docs/ai-agent/ACHIEVEMENT_REFERENCE_CATALOG.json` | pending exact row read | factual reference metadata |
| `data/scripts/lib/register_achievements.lua` | pending exact entry read | active Canary registry |
| merged PR #238 | 2026-07-13 | validator v2, provenance and evidence model |
| live open PR search | 2026-07-13 | ownership/overlap check |

# Confirmed findings

- PR #238 merged as `3ad10132cbd76adc42f946da3ca3077e5bd6bbd0`.
- Audit v2 records exactly seven grade/secret/points conflicts.
- Current main at task start is `0aea5c00b6fadb2837dec59318a0589187daf94d`.
- No open PR matching achievement metadata, registry or PlayerAchievement paths was found.
- This package is metadata-only and does not claim runtime obtainability parity.

# Uncertain findings

- Whether all seven reference values still match the current live Tibia state after revision 1188274.
- Whether any Canary-supported-version policy intentionally preserves a historical value.
- Whether changing points affects any cached/derived player total requiring recalculation or backfill; this must be proven from `PlayerAchievement` behavior before implementation.

# Decisions

| Decision | Reason |
|---|---|
| Start with metadata-only package | smallest verified scope and no handler/backfill guessing |
| Keep names unchanged | persistence is keyed by canonical name |
| Do not bundle missing definitions or handlers | different evidence and risk boundaries |
| Require a deterministic regression test | prevents future drift and proves exact seven values |

# Commands and tests

No local command has been claimed as passed yet. GitHub API inspections performed:

```text
search recent main commits
search open PRs for achievement/registry/PlayerAchievement overlap
create branch fix/achievement-metadata-parity from 0aea5c00b6fadb2837dec59318a0589187daf94d
```

# Failed approaches

None in this task so far.

# Remaining work

1. Open draft PR.
2. Read exact registry and reference rows.
3. Verify persistence/points recomputation behavior.
4. Add failing regression expectations.
5. Apply only proven metadata changes.
6. Run validator and full gates.

# Handoff

Continue on branch `fix/achievement-metadata-parity`. First read the seven exact registry entries and matching catalogue rows. Do not change names, IDs, handlers, storages or quest logic. Do not edit `docs/agents/ACTIVE_WORK.md`.

# Completion

- Final status: active
- PR:
- Merge commit:
- Archived at:
