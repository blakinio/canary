---
task_id: CAN-20260712-imbuement-forgotten-knowledge-storages
coordination_id: ""
status: ready-for-review
agent: "GPT-5.6 Thinking"
branch: fix/imbuement-forgotten-knowledge-storages
base_branch: main
created: 2026-07-12T20:55:00Z
updated: 2026-07-13T09:27:00+02:00
last_verified_commit: "34b821a526b85fd16d98690b819ee0c538a6d638"
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
  - docs/agents/tasks/active/CAN-20260712-imbuement-forgotten-knowledge-storages.md
  - docs/agents/ACTIVE_WORK.md
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

# Evidence

| Boss group | Active storage | Powerful families |
|---|---:|---|
| Lady Tenebris | 45489 | Reap, Vampirism, Lich Shroud |
| Lloyd | 45490 | Electrify, Cloud Fabric, Swiftness |
| Thorn Knight | 45491 | Venom, Snake Skin, Chop, Slash, Bash, Punch |
| Dragonking | 45492 | Scorch, Void, Dragon Hide |
| Frozen Horror | 45493 | Frost, Quara Scale, Blockade |
| Time Guardian | 45494 | Demon Presence, Precision |
| Last Lore Keeper | 45495 | Strike, Epiphany |

The original XML used undeclared `50488, 50490, 50492, 50494, 50496, 50498, 50501` for the same groups.

# Acceptance criteria

- [x] Replace all 22 affected Powerful entries with the corresponding active storage IDs.
- [x] Preserve every unrelated Imbuement value, item, scroll, category and effect.
- [x] Extend the deterministic storage audit to verify exact family-to-storage grouping.
- [x] Make undeclared nonzero Imbuement storage IDs fail the focused workflow.
- [x] Add fixture and repository-level regression coverage.
- [x] Update the Imbuement report with repaired status and retained unresolved findings.
- [x] Run focused tests, generators and repository CI on the refreshed head.
- [x] Review changed files and confirm no map, item binary, client asset or unrelated gameplay changes.
- [ ] Mark ready and merge only after final metadata-only head checks pass.
- [ ] Archive this task and remove its Active Work row after merge.

# Implemented change

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

The validator now rejects undeclared IDs, all seven legacy IDs, incorrect family grouping and missing boss storage tokens. The focused workflow runs it with `--strict` and remains read-only.

# Validation evidence

Reviewed implementation head:

```text
34b821a526b85fd16d98690b819ee0c538a6d638
```

| Check | Result |
|---|---|
| Imbuement Validation run `29231753033` | success |
| AI Agent Tools run `29231753005` | success |
| Agent Task Ownership run `29231753066` | success |
| CI run `29231753194` / `Required` | success |
| focused Imbuement tests | success |
| both generators and JSON validation | success |
| branch behind `main` | 0 |
| changed files | exactly 7 |
| temporary write-enabled workflows | none |
| forbidden map/item/asset/runtime paths | none |

Audit artifact:

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

# Safety boundary

- Featherweight and Vibrancy remain `storage=0` until exact quest completion conditions are proven.
- Fees, success chances, Strike values, Punch materials and Vibrancy scroll mappings are unchanged.
- No `.otbm`, `items.otb`, assets, production configuration, boss script, storage declaration, protocol or C++ runtime change.

# Log

- Confirmed writable target `blakinio/canary`; upstream remained reference-only.
- Revalidated all seven active storage declarations and boss write paths.
- Published draft PR #206 before changing gameplay data.
- Replaced exactly 22 Powerful XML storage attributes.
- Extended validator/tests and enabled strict CI.
- Updated the audit report while retaining unresolved findings.
- Removed all temporary write-enabled/diagnostic workflows and XML export steps.
- Reconciled shared coordination files with current `main`.
- Final metadata-only head validation remains before merge.
