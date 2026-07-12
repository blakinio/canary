---
task_id: CAN-20260712-achievement-trigger-names
status: completed
agent: "GPT-5.6 Thinking"
branch: fix/achievement-trigger-names
base_branch: main
created: 2026-07-12T19:47:00Z
updated: 2026-07-12T20:35:00Z
last_verified_commit: "c1740537aba9b220920ef7027f7ea62270386478"
risk: low
related_pr: "#184"
merge_commit: "f4ee347c7f9d40e9ea800514fad9f5117259031d"
owned_paths:
  - data/scripts/actions/items/usable_phantasmal_jade_items.lua
  - data-otservbr-global/scripts/quests/hero_of_rathleton/actions_reward.lua
  - tools/ai-agent/test_achievement_validation.py
  - docs/ai-agent/ACHIEVEMENT_TRIGGER_FIX.md
modules_touched:
  - achievement gameplay triggers
---

# Goal

Correct two active literal achievement award names so exact case-sensitive runtime lookup resolves the canonical registry entries without changing progression, definitions or persistence.

# Completed behavior

- `You got Horse Power` was corrected to canonical `You Got Horse Power` (ID 514).
- `The Professors Nut` was corrected to canonical `The Professor's Nut` (ID 360).
- A real-source scanner contract loads the active registry and both gameplay files and verifies every static achievement reference resolves.
- Existing items, counts, mount `167`, storage `24850`, rewards, messages, C++ runtime and KV keys remain unchanged.

# Validation

Reviewed full-CI head:

```text
c1740537aba9b220920ef7027f7ea62270386478
```

Verified:

- Achievement Validation run `29207496284`: success;
- AI Agent Tools run `29207496285`: success;
- Account Quests run `29207496289`: success;
- autofix.ci run `29207496295`: success;
- CI run `29207496349`: success;
- formatter and Lua Tests: success;
- Canary datapack smoke: success;
- global datapack smoke: success;
- audit artifact: `ok=true`, 160/160 static references resolved, `unknownStaticReferenceCount=0`, no error findings;
- exact seven-file diff reviewed;
- no review threads or requested changes.

The branch was refreshed against unrelated concurrent `main` changes only to preserve coordination indexes; no achievement code changed after the successful full validation.

# Completion

- Final status: completed
- PR: #184
- Merge commit: `f4ee347c7f9d40e9ea800514fad9f5117259031d`
- Changelog updated: yes
- Archived at: `docs/agents/tasks/archive/CAN-20260712-achievement-trigger-names.md`

# Follow-up

The next bounded achievement work is a read-only Weapon Proficiency audit for IDs 564–567. Do not add ID 567 or engine hooks until mastery thresholds, item IDs, existing-player backfill and PlayerAchievement integration are evidenced and tested.
