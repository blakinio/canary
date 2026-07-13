---
task_id: CAN-20260712-imbuement-forgotten-knowledge-storages
coordination_id: ""
status: merged
agent: "GPT-5.6 Thinking"
branch: fix/imbuement-forgotten-knowledge-storages
base_branch: main
created: 2026-07-12T20:55:00Z
updated: 2026-07-13T09:40:00+02:00
last_verified_commit: "54fc263c792c10cf321a3a1b747eb971863f072a"
risk: medium
related_issue: ""
related_pr: "#206"
depends_on:
  - merged audit PR #166
blocks: []
owned_paths:
  - data/XML/imbuements.xml
  - tools/ai-agent/imbuement_storage_validation.py
  - tools/ai-agent/test_imbuement_storage_validation.py
  - .github/workflows/imbuement-validation.yml
  - docs/ai-agent/IMBUEMENT_VALIDATION_REPORT.md
modules_touched:
  - Imbuement registry
  - Forgotten Knowledge unlock wiring
  - Imbuement validation CI
reuses:
  - merged Imbuement validation audit from #166
  - active Forgotten Knowledge named storages
  - existing ImbuementStoragePolicy
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Repair the seven stale Powerful Imbuement unlock storage IDs so the optional shrine storage filter reads the active Forgotten Knowledge boss storages.

# Final result

PR [#206](https://github.com/blakinio/canary/pull/206) was squash-merged into `main` as:

```text
d7e9af64bab306ca3de1d290ac5c81b916a7692c
```

Exactly 22 Powerful entries were remapped:

```text
50488 -> 45489: 3
50490 -> 45490: 3
50492 -> 45491: 6
50494 -> 45492: 3
50496 -> 45493: 3
50498 -> 45494: 2
50501 -> 45495: 2
Total: 22
```

| Boss group | Active storage | Powerful families |
|---|---:|---|
| Lady Tenebris | 45489 | Reap, Vampirism, Lich Shroud |
| Lloyd | 45490 | Electrify, Cloud Fabric, Swiftness |
| Thorn Knight | 45491 | Venom, Snake Skin, Chop, Slash, Bash, Punch |
| Dragonking | 45492 | Scorch, Void, Dragon Hide |
| Frozen Horror | 45493 | Frost, Quara Scale, Blockade |
| Time Guardian | 45494 | Demon Presence, Precision |
| Last Lore Keeper | 45495 | Strike, Epiphany |

Every unrelated Imbuement value, item, scroll, category, effect and description was preserved.

# Regression protection

The merged validator rejects:

- undeclared nonzero Imbuement storage IDs;
- all seven legacy IDs;
- incorrect Powerful family-to-storage grouping;
- missing active Forgotten Knowledge boss storage tokens.

The focused workflow runs the storage validator with `--strict` and remains read-only.

# Final validation

Final reviewed head:

```text
54fc263c792c10cf321a3a1b747eb971863f072a
```

| Check | Result |
|---|---|
| Imbuement Validation run `29232084236` | success |
| AI Agent Tools run `29232084218` | success |
| Agent Task Ownership run `29232084226` | success |
| CI rerun `29232117278` / Fast Checks | success |
| CI rerun `29232117278` / Lua Tests | success |
| CI rerun `29232117278` / Linux release | success |
| Canary datapack smoke | success |
| Global datapack smoke | success |
| CI rerun `29232117278` / Required | success |
| branch behind main before merge | 0 |
| changed files | exactly 7 |
| temporary write-enabled workflows | none |
| forbidden map/item/asset/runtime paths | none |

Audit artifact from the implementation-equivalent head:

```text
artifact id: 8271792953
digest: sha256:34b2c970639471ed086313c80496fac81ec9ce51e9e6c3b6f044de06aca2d0d8
```

Artifact result:

```text
undeclared storage IDs: []
legacy storage IDs in use: []
family group mismatches: []
remaining finding: POWERFUL_UNLOCK_BYPASS for Featherweight and Vibrancy
runtime scenarios: 12
```

# Explicitly unresolved follow-ups

- Powerful Featherweight and Vibrancy still use `storage=0`; exact Dangerous Depths and Dream Courts completion conditions must be proven before changing them.
- Vibrancy scroll IDs remain unmapped.
- Fee/success model target version remains undecided.
- Strike values and Basic Punch material remain separate data-fidelity findings.
- Live gameplay/database persistence scenarios remain unexecuted.

# Safety boundary

- No `.otbm`, `items.otb`, map, client asset, boss script, storage declaration, C++ runtime, protocol or production configuration change.
- No guessing of unresolved quest storages.

# Completion

- Final status: merged
- PR: #206
- Merge commit: `d7e9af64bab306ca3de1d290ac5c81b916a7692c`
- Catalogue updated: yes
- Archived at: `docs/agents/tasks/archive/CAN-20260712-imbuement-forgotten-knowledge-storages.md`
