from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from weapon_proficiency_achievement_audit import (
    FORBIDDEN_BUILD_NAMES,
    audit_repository,
    extract_function_body,
    parse_items_xml_candidates,
    parse_registry,
)


class WeaponProficiencyAchievementAuditTests(unittest.TestCase):
    def test_parse_target_registry_entries(self) -> None:
        text = '''ACHIEVEMENTS = {
[564] = { name = "The First of Many", grade = 1, points = 3, description = "One." },
[565] = { name = "A Well-Honed Arsenal", grade = 2, points = 5, description = "Ten." },
[566] = { name = "Arsenal of War", grade = 3, points = 7, description = "Fifty." },
}
'''
        entries = parse_registry(text)
        self.assertEqual(entries[564]["name"], "The First of Many")
        self.assertEqual(entries[565]["points"], 5)
        self.assertNotIn(567, entries)

    def test_extract_function_body_handles_nested_blocks(self) -> None:
        text = '''void Test::run() {
    if (enabled) {
        value++;
    }
}
void Test::other() {}
'''
        body = extract_function_body(text, "void Test::run")
        self.assertIn("value++", body)
        self.assertNotIn("Test::other", body)

    def test_parse_items_xml_requires_explicit_valid_override_for_proven_eligibility(self) -> None:
        text = '''
<items>
  <item id="100" name="Club of the Fury">
    <attribute key="proficiency" value="8" />
  </item>
  <item id="101" name="Snowball">
    <attribute key="weight" value="80" />
  </item>
  <item id="102" name="Ice Rapier">
    <attribute key="proficiency" value="999" />
  </item>
</items>
'''
        result = parse_items_xml_candidates(text, FORBIDDEN_BUILD_NAMES, {8})
        self.assertEqual(result["Club of the Fury"][0]["resolvedEligibility"], "explicit-valid-xml-override")
        self.assertEqual(result["Snowball"][0]["resolvedEligibility"], "protobuf-or-runtime-resolution-required")
        self.assertEqual(result["Ice Rapier"][0]["resolvedEligibility"], "explicit-invalid-xml-override")

    def test_fixture_detects_missing_hooks_and_initial_mastery_edge(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            registry = root / "data/scripts/lib/register_achievements.lua"
            registry.parent.mkdir(parents=True)
            registry.write_text(
                '''ACHIEVEMENTS = {
[564] = { name = "The First of Many", grade = 1, points = 3, description = "One." },
[565] = { name = "A Well-Honed Arsenal", grade = 2, points = 5, description = "Ten." },
[566] = { name = "Arsenal of War", grade = 3, points = 7, description = "Fifty." },
}
''',
                encoding="utf-8",
            )
            cpp = root / "src/creatures/players/components/weapon_proficiency.cpp"
            cpp.parent.mkdir(parents=True)
            cpp.write_text(
                '''
void WeaponProficiency::load() {
    normalizeStoredState(weaponId);
}
void WeaponProficiency::normalizeStoredState(uint16_t weaponId) {
    data.mastered = data.experience >= maxExperience;
}
void WeaponProficiency::addExperience(uint32_t experience, uint16_t weaponId) {
    if (!proficiency.contains(weaponId)) {
        proficiency.try_emplace(weaponId, std::min(experience, maxExperience));
        return;
    }
    if (newExperience >= maxExperience) {
        proficiency[weaponId].mastered = true;
        return;
    }
}
''',
                encoding="utf-8",
            )
            hpp = root / "src/creatures/players/components/weapon_proficiency.hpp"
            hpp.write_text("class WeaponProficiency { public: std::vector<uint16_t> getTrackedWeaponIds() const; };", encoding="utf-8")
            achievement = root / "src/creatures/players/components/player_achievement.hpp"
            achievement.write_text("class PlayerAchievement { public: bool add(uint16_t id, bool message = true); };", encoding="utf-8")
            proficiencies = root / "data/items/proficiencies.json"
            proficiencies.parent.mkdir(parents=True)
            proficiencies.write_text(json.dumps([{"ProficiencyId": 8, "Levels": []}]), encoding="utf-8")
            items = root / "data/items/items.xml"
            items.write_text("<items></items>", encoding="utf-8")
            (root / "data-otservbr-global").mkdir()

            report = audit_repository(root)
            codes = {finding["code"] for finding in report["findings"]}
            self.assertIn("target-definition-missing", codes)
            self.assertIn("mastery-achievement-hook-missing", codes)
            self.assertIn("initial-mastery-flag-not-set", codes)
            self.assertIn("mastered-count-api-missing", codes)
            self.assertTrue(report["runtimeEvidence"]["loadCallsNormalizeStoredState"])
            self.assertTrue(report["runtimeEvidence"]["normalizeDerivesMasteredFromExperience"])

    def test_real_repository_confirms_current_bounded_findings(self) -> None:
        root = Path(__file__).resolve().parents[2]
        report = audit_repository(root)
        self.assertEqual(report["summary"]["missingTargetIds"], [567])
        self.assertFalse(report["runtimeEvidence"]["achievementHookPresent"])
        self.assertFalse(report["runtimeEvidence"]["initialCreationSetsMastered"])
        self.assertTrue(report["runtimeEvidence"]["initialCreationCapsExperience"])
        self.assertTrue(report["runtimeEvidence"]["loadCallsNormalizeStoredState"])
        codes = {finding["code"] for finding in report["findings"]}
        self.assertIn("mastery-achievement-hook-missing", codes)
        self.assertIn("initial-mastery-flag-not-set", codes)
        self.assertIn("target-award-path-missing", codes)


if __name__ == "__main__":
    unittest.main()
