---
task_id: CAN-20260712-imbuement-validation
coordination_id: ""
status: ready-for-review
agent: "GPT-5.6 Thinking"
branch: feat/imbuement-validation-audit
base_branch: main
created: 2026-07-12T17:18:21Z
updated: 2026-07-12T20:43:00Z
last_verified_commit: "eec25a5e354cf40e86e62f03512df0717623d1f6"
risk: low
related_issue: ""
related_pr: "#166"
depends_on: []
blocks: []
owned_paths:
  - .github/workflows/imbuement-validation.yml
  - tools/ai-agent/imbuement_validation.py
  - tools/ai-agent/imbuement_storage_validation.py
  - tools/ai-agent/test_imbuement_validation.py
  - tools/ai-agent/test_imbuement_storage_validation.py
  - docs/ai-agent/IMBUEMENT_VALIDATION_REPORT.md
  - docs/ai-agent/IMBUEMENT_RUNTIME_TEST_PLAN.json
  - docs/agents/tasks/active/CAN-20260712-imbuement-validation.md
  - docs/agents/ACTIVE_WORK.md
  - docs/agents/MODULE_CATALOG.md
modules_touched:
  - AI world validation
  - imbuement definition and runtime audit
  - imbuement unlock-storage wiring audit
reuses:
  - OTS AI World Validation evidence methodology
  - existing Imbuements XML loader and registry
  - existing shrine, scroll and Player imbuement runtime APIs
  - active Lua storage registry and Forgotten Knowledge boss storage paths
public_interfaces:
  - imbuement registry validation CLI
  - imbuement storage validation CLI
  - imbuement validation report format
  - imbuement runtime test-plan schema v1
  - focused Imbuement Validation workflow
cross_repo_tasks: []
---

# Goal

Create a deterministic, evidence-based, read-only audit of Canary's Imbuing system against the current referenced mechanics.

# Acceptance criteria

- [x] Parse the active `data/XML/imbuements.xml` registry.
- [x] Validate structure, tiers, costs, duration, materials, effects, scrolls and storage gates.
- [x] Audit engine, Lua, shrine, scroll, clearing and decay paths.
- [x] Correlate every nonzero XML unlock storage with active Lua declarations.
- [x] Produce a human-readable evidence report.
- [x] Produce machine-readable registry, storage and runtime-plan JSON artifacts.
- [x] Add focused tests and a dedicated CI workflow.
- [x] Keep the audit read-only: no gameplay XML, datapack, engine, map, asset, item-binary or production-config changes.
- [x] Verify focused workflow, AI Agent Tools and repository CI on the reviewed head.
- [x] Review the complete changed-file list and forbidden-path boundary.
- [x] Update module catalogue and persistent handoff.
- [ ] Mark PR #166 ready and merge after final current-head checks.
- [ ] Archive the task and remove the Active Work row after merge.

# Deterministic baseline

```text
base tiers: 3
categories: 20
families: 24
tier entries: 72
XML-mapped Intricate/Powerful scrolls: 46
Lua-registered scroll IDs: 48
duration: 72,000 seconds
clear cost: 15,000 gold
nonzero XML unlock storage IDs: 7
Powerful families using stale nonzero IDs: 22
Powerful families using storage=0: 2
storage filtering default: disabled
```

# Confirmed findings

## IMB-001 — fee/success model differs

Active XML uses chance plus optional protection; the observed reference uses fixed fees. This requires an explicit target-version/economy decision and is not an automatic fix.

## IMB-002 — Strike values differ

All three Strike tiers use different critical chance/damage values from the observed reference.

## IMB-003 — Basic Punch source differs

Active Basic Punch uses item `9690 x20`; the observed reference chain begins with item `10281 x25`.

## IMB-004 — Vibrancy scrolls are registered but unmapped

Lua registers `51466` and `51746`, while XML maps neither ID. The active scroll action therefore cannot resolve either Vibrancy tier through `getImbuementByScrollID()`.

## IMB-005 — seven nonzero Powerful storage IDs are stale

XML uses:

```text
50488, 50490, 50492, 50494, 50496, 50498, 50501
```

None is declared in active `storages.lua`. They affect 22 Powerful families. Active Forgotten Knowledge boss paths instead write named storages `45489..45495`.

## IMB-006 — two Powerful families bypass filtering

Powerful Featherweight and Vibrancy use `storage=0`, so the policy does not hide them even when family-specific filtering is enabled. Exact Dangerous Depths and Dream Courts completion storage/value remains unresolved and must not be guessed.

# Storage evidence

| Stale XML storage | Families | Strong current semantic counterpart |
|---:|---|---:|
| 50488 | Reap, Vampirism, Lich Shroud | 45489 — Lady Tenebris |
| 50490 | Electrify, Cloud Fabric, Swiftness | 45490 — Lloyd |
| 50492 | Venom, Snake Skin, Chop, Slash, Bash, Punch | 45491 — Thorn Knight |
| 50494 | Scorch, Void, Dragon Hide | 45492 — Dragonking |
| 50496 | Frost, Quara Scale, Blockade | 45493 — Frozen Horror |
| 50498 | Demon Presence, Precision | 45494 — Time Guardian |
| 50501 | Strike, Epiphany | 45495 — Last Lore Keeper |

This mapping is strong semantic evidence, not authorization for blind replacement. A separate fix PR must verify before/after visibility for every group.

# Validation

Reviewed head:

```text
eec25a5e354cf40e86e62f03512df0717623d1f6
```

| Check | Result |
|---|---|
| Imbuement Validation run `29204201080` | success |
| AI Agent Tools run `29204201098` | success |
| CI run `29204201176` | success |
| focused tests | 10/10 passed |
| Python compilation | passed |
| both audit generators | passed |
| generated JSON validation | passed |
| artifact download and parse | passed |
| full changed-file list | reviewed |
| forbidden runtime/map/asset paths | none |

Audit artifact:

```text
artifact id: 8263257100
digest: sha256:17f2ecfab6aa28bac5b8f3f24b4de1b88ecde260d866e35afdaa6852b3581861
```

Artifact evidence:

```text
IMBUEMENT_VALIDATION.json:
  base tiers: 3
  categories: 20
  families: 24
  entries: 72
  findings: 1 error, 11 mismatches

IMBUEMENT_STORAGE_VALIDATION.json:
  undeclared storage IDs: 7
  affected Powerful families: 22
  storage=0 Powerful families: Featherweight, Vibrancy
  boss named-storage wiring: present

IMBUEMENT_RUNTIME_TEST_PLAN.json:
  scenarios: 12
```

The audit reports confirmed defects as findings; their presence is expected and does not mean the audit execution failed.

# Failure and repair history

- Initial focused run failed one structural assertion because `applyImbuementScroll` was incorrectly expected in `player.hpp`.
- Full test diagnostics identified the exact false marker.
- The scanner now checks `applyImbuementScroll` in `src/lua/functions/creatures/player/player_functions.cpp` while retaining the Player declarations in `player.hpp`.
- A clean read-only workflow run then passed all steps.

# Coordination and safety

- Writable repository verified as `blakinio/canary`.
- `opentibiabr/canary` was used only as a reference.
- Branch contains current `main` commit `ab0ca005625ca4f80fc5931d86a3f8d0b0304299` as an ancestor and is not behind.
- PR #166 changes exactly ten focused audit/coordination files.
- No `.otbm`, `items.otb`, client assets, active gameplay XML, Lua gameplay scripts, C++ runtime or production configuration were changed.
- Shared `ACTIVE_WORK.md` and `MODULE_CATALOG.md` were reconciled after achievement audit archival.

# Follow-up order

1. Repair the seven Forgotten Knowledge storage mappings with focused before/after unlock tests.
2. Prove exact Dangerous Depths and Dream Courts completion conditions, then gate Featherweight and Vibrancy.
3. Add Vibrancy scroll mappings and atomicity tests.
4. Decide the target Imbuing economy/version.
5. Correct Strike and Basic Punch in a separate data-fidelity PR.
6. Execute the runtime gameplay plan in Canary staging.
7. Audit full equipment eligibility against current item metadata.

# Handoff

## Start here

1. Inspect PR #166 and current checks.
2. Read `docs/ai-agent/IMBUEMENT_VALIDATION_REPORT.md`.
3. Inspect the final artifact from run `29204201080`.
4. Re-check current `main`, mergeability and changed files before merge.

## Do not repeat

- Do not treat the historical/current fee-model difference as an automatic bug.
- Do not blindly replace stale storage IDs.
- Do not invent Dangerous Depths or Dream Courts completion values.
- Do not put gameplay fixes into this audit PR.
- Do not claim runtime gameplay validation; only static/semantic audits and planned scenarios are complete.

# Completion

- Final status: ready-for-review
- PR: #166
- Merge commit:
- Catalogue updated: yes
- Changelog updated: specialist report added; global behavior changelog not applicable to read-only audit
- Archived at:
