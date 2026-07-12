---
task_id: CAN-20260712-imbuement-forgotten-knowledge-storages
coordination_id: ""
status: active
agent: "GPT-5.6 Thinking"
branch: fix/imbuement-forgotten-knowledge-storages
base_branch: main
created: 2026-07-12T20:55:00Z
updated: 2026-07-12T23:03:00+02:00
last_verified_commit: "ef88c689b59c476c1cfea18357384b9280043c7d"
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

Active `storages.lua` declares and the boss-death script writes:

| Boss group | Active storage | Powerful families |
|---|---:|---|
| Lady Tenebris | 45489 | Reap, Vampirism, Lich Shroud |
| Lloyd | 45490 | Electrify, Cloud Fabric, Swiftness |
| Thorn Knight | 45491 | Venom, Snake Skin, Chop, Slash, Bash, Punch |
| Dragonking | 45492 | Scorch, Void, Dragon Hide |
| Frozen Horror | 45493 | Frost, Quara Scale, Blockade |
| Time Guardian | 45494 | Demon Presence, Precision |
| Last Lore Keeper | 45495 | Strike, Epiphany |

Current XML instead uses undeclared `50488, 50490, 50492, 50494, 50496, 50498, 50501` for those same groups.

# Acceptance criteria

- [ ] Replace all 22 affected Powerful entries with the corresponding active storage IDs.
- [ ] Preserve every unrelated Imbuement value, item, scroll, category and effect.
- [x] Extend the deterministic storage audit to verify exact family-to-storage grouping.
- [x] Make undeclared nonzero Imbuement storage IDs fail the focused workflow.
- [x] Add fixture and repository-level regression coverage.
- [ ] Update the Imbuement report with repaired status and retained unresolved findings.
- [ ] Run focused tests, generators and repository CI.
- [ ] Review changed files and confirm no map, item binary, client asset or unrelated gameplay changes.
- [ ] Mark ready and merge only after current-head checks pass.
- [ ] Archive this task and remove its Active Work row after merge.

# Safety boundary

- Do not change `storage=0` for Featherweight or Vibrancy until their exact quest completion conditions are proven.
- Do not change fees, success chances, Strike values, Punch materials or Vibrancy scrolls in this PR.
- Do not edit `.otbm`, `items.otb`, assets, production configuration, boss scripts or storage declarations.

# Log

- Confirmed writable target `blakinio/canary`; upstream remains reference-only.
- Reviewed open PRs and `ACTIVE_WORK.md`; no active Imbuement storage repair overlaps this scope.
- Revalidated the seven active Forgotten Knowledge storage declarations and boss write paths on current `main`.
- Published draft PR #206 before the gameplay data change.
- Extended the storage validator to reject undeclared IDs, legacy IDs and incorrect family grouping.
- Added fixture coverage plus a repository-level regression test.
- Updated the focused workflow to run storage validation with `--strict` and publish the reviewed XML source as an artifact.
- XML replacement, report update and final CI remain in progress.
