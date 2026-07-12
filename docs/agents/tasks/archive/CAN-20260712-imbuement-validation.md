---
task_id: CAN-20260712-imbuement-validation
status: completed
agent: "GPT-5.6 Thinking"
branch: feat/imbuement-validation-audit
base_branch: main
created: 2026-07-12T17:18:21Z
updated: 2026-07-12T21:45:00Z
last_verified_commit: "bd66586fb492f00535a44076be9131fc4c69a343"
risk: low
related_pr: "#166"
merge_commit: "506ff267fe686c3bcacceb2b547923531252725f"
owned_paths:
  - .github/workflows/imbuement-validation.yml
  - tools/ai-agent/imbuement_validation.py
  - tools/ai-agent/imbuement_storage_validation.py
  - tools/ai-agent/test_imbuement_validation.py
  - tools/ai-agent/test_imbuement_storage_validation.py
  - docs/ai-agent/IMBUEMENT_VALIDATION_REPORT.md
  - docs/ai-agent/IMBUEMENT_RUNTIME_TEST_PLAN.json
modules_touched:
  - AI world validation
  - imbuement definition and runtime audit
  - imbuement unlock-storage wiring audit
public_interfaces:
  - imbuement registry validation CLI
  - imbuement storage validation CLI
  - imbuement validation report format
  - imbuement runtime test-plan schema v1
  - focused Imbuement Validation workflow
---

# Goal

Create a deterministic, evidence-based, read-only audit of Canary's Imbuing system against the referenced mechanics.

# Completed result

PR [#166](https://github.com/blakinio/canary/pull/166) was squash-merged into `main` as:

```text
506ff267fe686c3bcacceb2b547923531252725f
```

The merged change adds:

- a deterministic XML/reference/runtime scanner;
- a separate unlock-storage wiring scanner;
- ten focused unit tests;
- a dedicated read-only GitHub Actions workflow;
- a persistent evidence report;
- a machine-readable runtime scenario plan.

No gameplay XML, active datapack script, C++ runtime, map, item binary, client asset or production configuration was changed.

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

- **IMB-001:** active chance/protection fee model differs from the observed fixed-fee reference; target version/economy decision required.
- **IMB-002:** all three Strike tiers use different critical chance/damage values from the observed reference.
- **IMB-003:** Basic Punch uses item `9690 x20` instead of the observed `10281 x25` chain.
- **IMB-004:** Vibrancy scroll IDs `51466` and `51746` are registered by Lua but unmapped in XML.
- **IMB-005:** XML uses seven nonzero storage IDs absent from active `storages.lua`, affecting 22 Powerful families.
- **IMB-006:** Powerful Featherweight and Vibrancy use `storage=0` and bypass family-specific filtering.

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

This mapping is strong semantic evidence, not authorization for blind replacement. Exact Dangerous Depths and Dream Courts completion values remain unresolved and must not be guessed.

# Validation

Final reviewed head:

```text
bd66586fb492f00535a44076be9131fc4c69a343
```

Verified:

- Imbuement Validation run `29204279686`: success;
- AI Agent Tools run `29204279716`: success;
- CI run `29204279817`: success;
- focused tests: 10/10 passed;
- Python compilation: passed;
- both audit generators: passed;
- generated JSON validation: passed;
- final changed-file list and forbidden-path boundary: reviewed.

Final audit artifact:

```text
artifact id: 8263257100
digest: sha256:17f2ecfab6aa28bac5b8f3f24b4de1b88ecde260d866e35afdaa6852b3581861
```

# Follow-up order

1. Repair the seven Forgotten Knowledge storage mappings with focused before/after unlock tests.
2. Prove exact Dangerous Depths and Dream Courts completion conditions, then gate Featherweight and Vibrancy.
3. Add Vibrancy scroll mappings and atomicity tests.
4. Decide the target Imbuing economy/version.
5. Correct Strike and Basic Punch in a separate data-fidelity PR.
6. Execute the runtime gameplay plan in Canary staging.
7. Audit full equipment eligibility against current item metadata.

# Completion

- Final status: completed
- PR: #166
- Merge commit: `506ff267fe686c3bcacceb2b547923531252725f`
- Catalogue updated: yes
- Changelog updated: specialist report added; global behavior changelog not applicable to a read-only audit
- Archived at: `docs/agents/tasks/archive/CAN-20260712-imbuement-validation.md`
