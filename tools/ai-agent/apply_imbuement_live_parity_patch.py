#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

BASE_SHA = "3ad10132cbd76adc42f946da3ca3077e5bd6bbd0"


def replace_once(path: str, old: str, new: str) -> None:
    file = Path(path)
    text = file.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one occurrence, found {count}: {old[:100]!r}")
    file.write_text(text.replace(old, new, 1), encoding="utf-8")


def patch_xml() -> None:
    path = "data/XML/imbuements.xml"
    replace_once(
        path,
        '<imbuement name="Vibrancy" base="3" category="19" iconid="79" premium="1" storage="0">',
        '<imbuement name="Vibrancy" base="3" category="19" iconid="79" premium="1" storage="46365">',
    )
    replace_once(
        path,
        '<imbuement name="Featherweight" base="3" category="17" iconid="76" premium="1" storage="0">',
        '<imbuement name="Featherweight" base="3" category="17" iconid="76" premium="1" storage="45929">',
    )


def patch_storage_validator() -> None:
    path = Path("tools/ai-agent/imbuement_storage_validation.py")
    text = path.read_text(encoding="utf-8")
    old = """CURRENT_FORGOTTEN_KNOWLEDGE_STORAGE_IDS = set(
    EXPECTED_FORGOTTEN_KNOWLEDGE_GROUPS
)
"""
    new = """EXPECTED_QUEST_UNLOCK_GROUPS: dict[int, tuple[str, ...]] = {
    45929: ("Featherweight",),
    46365: ("Vibrancy",),
}
EXPECTED_POWERFUL_STORAGE_GROUPS = {
    **EXPECTED_FORGOTTEN_KNOWLEDGE_GROUPS,
    **EXPECTED_QUEST_UNLOCK_GROUPS,
}
CURRENT_FORGOTTEN_KNOWLEDGE_STORAGE_IDS = set(
    EXPECTED_FORGOTTEN_KNOWLEDGE_GROUPS
)
"""
    if old not in text:
        raise RuntimeError("storage validator insertion anchor missing")
    text = text.replace(old, new, 1)
    text = text.replace(
        "set(actual) | set(EXPECTED_FORGOTTEN_KNOWLEDGE_GROUPS)",
        "set(actual) | set(EXPECTED_POWERFUL_STORAGE_GROUPS)",
        1,
    )
    text = text.replace(
        "expected_families = EXPECTED_FORGOTTEN_KNOWLEDGE_GROUPS.get(storage_id, ())",
        "expected_families = EXPECTED_POWERFUL_STORAGE_GROUPS.get(storage_id, ())",
        1,
    )
    text = text.replace(
        'f"Forgotten Knowledge mapping: {group_mismatches}"',
        'f"Forgotten Knowledge and quest-unlock mapping: {group_mismatches}"',
        1,
    )
    old_actual = """            "actual_forgotten_knowledge_groups": {
                str(storage_id): list(families)
                for storage_id, families in actual_groups.items()
            },
"""
    new_actual = """            "expected_quest_unlock_groups": {
                str(storage_id): list(families)
                for storage_id, families in EXPECTED_QUEST_UNLOCK_GROUPS.items()
            },
            "actual_powerful_storage_groups": {
                str(storage_id): list(families)
                for storage_id, families in actual_groups.items()
            },
"""
    if old_actual not in text:
        raise RuntimeError("storage validator baseline anchor missing")
    path.write_text(text.replace(old_actual, new_actual, 1), encoding="utf-8")


def patch_storage_tests() -> None:
    path = Path("tools/ai-agent/test_imbuement_storage_validation.py")
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "for storage_id, names in validation.EXPECTED_FORGOTTEN_KNOWLEDGE_GROUPS.items()",
        "for storage_id, names in validation.EXPECTED_POWERFUL_STORAGE_GROUPS.items()",
        1,
    )
    text = text.replace(
        """    return entries + (
        FakeEntry("Featherweight", 3, 0),
        FakeEntry("Vibrancy", 3, 0),
    )
""",
        "    return entries\n",
        1,
    )
    text = text.replace(
        "        LastLoreKilled = 45495,\n",
        "        LastLoreKilled = 45495,\n        LastAchievement = 45929,\n        NightmareTimer = 46365,\n",
        1,
    )
    text = text.replace(
        "def test_validate_accepts_confirmed_mapping_and_retains_zero_storage_warning(",
        "def test_validate_accepts_confirmed_mapping_without_unlock_bypass(",
        1,
    )
    text = text.replace(
        '        self.assertIn("POWERFUL_UNLOCK_BYPASS", by_code)',
        '        self.assertNotIn("POWERFUL_UNLOCK_BYPASS", by_code)',
        1,
    )
    text = text.replace(
        'self.assertEqual(baseline["powerful_with_nonzero_storage"], 22)',
        'self.assertEqual(baseline["powerful_with_nonzero_storage"], 24)',
        2,
    )
    text = text.replace(
        """        self.assertEqual(
            baseline["powerful_with_zero_storage"], ["Featherweight", "Vibrancy"]
        )
""",
        '        self.assertEqual(baseline["powerful_with_zero_storage"], [])\n',
        1,
    )
    anchor = """        self.assertEqual(
            validation.EXPECTED_FORGOTTEN_KNOWLEDGE_GROUPS[45495],
            ("Epiphany", "Strike"),
        )
"""
    addition = anchor + """        self.assertEqual(
            validation.EXPECTED_QUEST_UNLOCK_GROUPS,
            {45929: ("Featherweight",), 46365: ("Vibrancy",)},
        )
"""
    if anchor not in text:
        raise RuntimeError("storage test mapping anchor missing")
    path.write_text(text.replace(anchor, addition, 1), encoding="utf-8")


def patch_fixture() -> None:
    replace_once(
        "tests/fixture/core/XML/imbuements.xml",
        '<imbuement name="Vibrancy" base="3" category="19" iconid="79" premium="1" storage="0">',
        '<imbuement name="Vibrancy" base="3" category="19" iconid="79" premium="1" storage="46365">',
    )


def patch_report() -> None:
    path = Path("docs/ai-agent/IMBUEMENT_VALIDATION_REPORT.md")
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "> **Status:** IMB-001/002/003 repaired in PR #251; IMB-004/005 preserved; IMB-006 evidence pending; final CI pending",
        "> **Status:** IMB-001/002/003/006 repaired in PR #251; IMB-004/005 preserved; final CI pending",
        1,
    )
    text = text.replace(
        "The only remaining material reference discrepancy is IMB-006: Powerful Featherweight and Vibrancy still use `storage=0` because their exact active completion storage/value semantics have not yet been proven from the implemented quest paths.",
        "All six audited discrepancy groups now have evidence-backed repairs. Powerful Featherweight uses the permanent all-three-boss Dangerous Depths completion marker `45929`; Powerful Vibrancy uses the persistent Nightmare Beast completion marker `46365`. Neither marker is written at quest start.",
        1,
    )
    pattern = re.compile(r"### IMB-006 .*?(?=## 6\.)", re.S)
    replacement = """### IMB-006 — Featherweight and Vibrancy quest unlocks repaired

**Disposition:** `repaired-in-pr-251`
**Confidence:** high

- Powerful Featherweight uses storage `45929` (`DangerousDepths.Bosses.LastAchievement`). The active action writes it only after all three final boss-achievement markers equal `1`.
- Powerful Vibrancy uses storage `46365` (`TheDreamCourts.DreamScarGlobal.NightmareTimer`). The active death handler writes this player storage only for The Nightmare Beast; the quest catalogue and Vanys NPC identify that kill as the final main Dream Courts step. The timestamp remains set after the cooldown expires, so the existing `storage != -1` policy preserves the unlock permanently.

The generic questline storages were deliberately rejected: both are set when the quest starts and would unlock Powerful imbuements too early. No new storage ID or threshold semantics were invented.

"""
    text, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        raise RuntimeError("report IMB-006 section missing")
    text = text.replace(
        "1. Prove the exact Dangerous Depths and Dream Courts completion conditions before assigning Featherweight/Vibrancy storages.\n2. Execute the remaining runtime plan in controlled Canary staging.\n3. Audit full equipment eligibility against item metadata.",
        "1. Execute the remaining runtime plan in controlled Canary staging.\n2. Audit full equipment eligibility against item metadata.",
        1,
    )
    path.write_text(text, encoding="utf-8")


def restore_runtime_plan() -> None:
    raw = subprocess.check_output(
        ["git", "show", f"{BASE_SHA}:docs/ai-agent/IMBUEMENT_RUNTIME_TEST_PLAN.json"],
        text=True,
    )
    plan = json.loads(raw)
    baseline = plan["baseline"]
    baseline["nonzero_xml_storage_ids"] = [45489, 45490, 45491, 45492, 45493, 45494, 45495, 45929, 46365]
    baseline["powerful_with_nonzero_storage"] = 24
    baseline["powerful_with_zero_storage"] = []
    baseline["active_quest_unlock_storage_ids"] = [45929, 46365]
    repaired = {
        "IMB-001": ("repaired-in-pr-251", "Current fixed fees are 7,500/60,000/250,000 gold at 100% success with no protection surcharge."),
        "IMB-002": ("repaired-in-pr-251", "Strike uses 5% critical chance and +5%/+15%/+40% critical damage."),
        "IMB-003": ("repaired-in-pr-251", "Basic Punch uses item 10281 x25 and higher-tier cumulative chains remain intact."),
        "IMB-004": ("repaired-in-pr-239", "Vibrancy scroll IDs 51746 and 51466 are mapped and atomicity-tested."),
        "IMB-005": ("repaired-by-pr-206", "Forgotten Knowledge Powerful families use the active 45489..45495 boss storages."),
        "IMB-006": ("repaired-in-pr-251", "Powerful Featherweight uses 45929 and Powerful Vibrancy uses 46365, both proven completion markers."),
    }
    for finding in plan["known_findings"]:
        finding["kind"], finding["summary"] = repaired[finding["id"]]
    unlock = next(s for s in plan["scenarios"] if s["id"] == "powerful-unlock-storage")
    unlock["fixtures"]["dangerous_depths_completion_storage_id"] = 45929
    unlock["fixtures"]["dream_courts_completion_storage_id"] = 46365
    cost = next(s for s in plan["scenarios"] if s["id"] == "application-cost-and-atomicity")
    cost["matrix"] = [
        {"tier": "Basic", "active_fee": 7500, "active_success_percent": 100, "active_protection_price": 0},
        {"tier": "Intricate", "active_fee": 60000, "active_success_percent": 100, "active_protection_price": 0},
        {"tier": "Powerful", "active_fee": 250000, "active_success_percent": 100, "active_protection_price": 0},
    ]
    cost["assertions"] = [
        "Displayed fee and charged fee match the current fixed-fee model.",
        "Every valid application succeeds after resource validation.",
        "Insufficient gold leaves all resources and slot state unchanged.",
        "Insufficient materials leave all resources and slot state unchanged.",
        "Successful application consumes each material and the fixed gold charge exactly once.",
    ]
    Path("docs/ai-agent/IMBUEMENT_RUNTIME_TEST_PLAN.json").write_text(
        json.dumps(plan, indent=2) + "\n", encoding="utf-8"
    )


def patch_task() -> None:
    path = Path("docs/agents/tasks/active/CAN-20260713-imbuement-live-parity.md")
    text = path.read_text(encoding="utf-8")
    text = text.replace("status: in_progress", "status: implementation_complete_pending_ci", 1)
    prefixes = (
        "Base application fees",
        "Basic, Intricate and Powerful Strike",
        "Basic Punch consumes",
        "Protocol-visible base price",
        "IMB-006 storages are changed",
        "Focused deterministic and C++ regression coverage",
        "Validation report, runtime plan and agent changelog",
        "No map, items.otb",
    )
    for prefix in prefixes:
        text = text.replace(f"- [ ] {prefix}", f"- [x] {prefix}", 1)
    text = text.replace(
        "# Remaining work\n\n1. Open a draft PR for discovery.\n2. Complete IMB-006 evidence search.\n3. Implement and validate confirmed repairs.",
        "# Remaining work\n\n1. Remove temporary patch files and confirm the final changed-file boundary.\n2. Inspect final-head focused and repository CI job by job.\n3. Mark ready, merge and archive if all gates pass.",
        1,
    )
    text += """

## 2026-07-13T14:35:00+02:00

- Implemented IMB-001/002/003 and exact deterministic/C++ regressions in `1f5819d045815e6aa548112cacb62727fec5255b`.
- Proved Featherweight completion storage `45929` from the all-three-boss achievement action.
- Proved Vibrancy completion storage `46365` from the Nightmare Beast death handler plus final quest/NPC state.
- Rejected generic questline storages because they are written at quest start and the current policy only checks for an initialized storage.
- Restored the rich runtime plan instead of retaining the validator-generated reduced JSON.
- Local commands remain unavailable because `github.com` DNS resolution fails; no local result is claimed.
"""
    path.write_text(text, encoding="utf-8")


def main() -> None:
    patch_xml()
    patch_storage_validator()
    patch_storage_tests()
    patch_fixture()
    patch_report()
    restore_runtime_plan()
    patch_task()


if __name__ == "__main__":
    main()
