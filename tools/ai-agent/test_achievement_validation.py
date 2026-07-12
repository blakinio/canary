from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from achievement_validation import (
    audit_registry_helpers,
    audit_repository,
    build_report,
    parse_registry_text,
    scan_reference_text,
)


REGISTRY = '''ACHIEVEMENTS = {
    [1] = { name = "Public One", grade = 1, points = 1, description = "Public." },
    [2] = { name = "Secret Two", grade = 2, points = 4, secret = true, description = "Secret." },
    -- [3] = Unknown/non-existent
    [4] = { name = 'High Four', grade = 3, points = 7, description = "High." },
}
ACHIEVEMENT_FIRST = 1
ACHIEVEMENT_LAST = #ACHIEVEMENTS
for achievIdentifier = 1, #ACHIEVEMENTS do
end
function Game.isAchievementSecret(achievement)
    local foundAchievement = Game.getAchievementInfoById(achievement)
    if not foundAchievement then
        return Spdlog.error(string.format("[isAchievementSecret] - Invalid achievement '%s'", ach)) and false
    end
    return achievement.secret
end
'''


class AchievementValidationTests(unittest.TestCase):
    def test_parse_sparse_registry_and_defaults(self) -> None:
        definitions, findings = parse_registry_text(REGISTRY)
        self.assertEqual([item.id for item in definitions], [1, 2, 4])
        self.assertFalse(definitions[0].secret)
        self.assertTrue(definitions[1].secret)
        sparse = [finding for finding in findings if finding["code"] == "registry-sparse-id-space"]
        self.assertEqual(sparse[0]["evidence"]["ids"], [3])

    def test_grade_points_mismatch_is_error(self) -> None:
        text = 'ACHIEVEMENTS = {\n[1] = { name = "Bad", grade = 1, points = 5, description = "Bad." },\n}\n'
        _, findings = parse_registry_text(text)
        self.assertIn("registry-grade-points-mismatch", {item["code"] for item in findings})

    def test_scans_static_dynamic_and_admin_references(self) -> None:
        text = '''
player:addAchievement("Public One")
player:addAchievementProgress(2, 10)
player:hasAchievement(nameFromTable)
player:removeAchievement('Secret Two')
player:addAllAchievements(false)
'''
        refs = scan_reference_text(text, "data/scripts/talkactions/god/achievement_functions.lua")
        self.assertEqual([ref.kind for ref in refs], ["award", "progress", "check", "removal", "bulk-award"])
        self.assertEqual(refs[0].identifier, "Public One")
        self.assertEqual(refs[1].identifier, 2)
        self.assertEqual(refs[2].identifier_type, "dynamic")
        self.assertTrue(all(ref.admin_only for ref in refs))

    def test_helper_defects_are_detected(self) -> None:
        codes = {finding["code"] for finding in audit_registry_helpers(REGISTRY)}
        self.assertIn("sparse-table-length-operator", codes)
        self.assertIn("secret-helper-returns-input", codes)
        self.assertIn("secret-helper-undefined-error-variable", codes)

    def test_report_resolves_names_ids_and_preserves_dynamic_uncertainty(self) -> None:
        definitions, registry_findings = parse_registry_text(REGISTRY)
        refs = scan_reference_text(
            'player:addAchievement("Public One")\nplayer:addAchievementProgress(2, 10)\nplayer:addAchievement(variable)\n',
            "data/quest.lua",
        )
        report = build_report(definitions, registry_findings, [], refs)
        rows = {item["id"]: item for item in report["achievements"]}
        self.assertEqual(rows[1]["disposition"], "direct-static-award")
        self.assertEqual(rows[2]["disposition"], "static-progress-path")
        self.assertEqual(rows[4]["disposition"], "no-direct-static-reference")
        self.assertEqual(report["summary"]["dynamicReferenceCount"], 1)
        self.assertEqual(report["summary"]["unknownStaticReferenceCount"], 0)

    def test_unknown_static_reference_is_error(self) -> None:
        definitions, registry_findings = parse_registry_text(REGISTRY)
        refs = scan_reference_text('player:addAchievement("Missing")', "data/quest.lua")
        report = build_report(definitions, registry_findings, [], refs)
        self.assertFalse(report["ok"])
        self.assertEqual(report["summary"]["unknownStaticReferenceCount"], 1)

    def test_repository_audit_and_baseline(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            registry = root / "data/scripts/lib/register_achievements.lua"
            registry.parent.mkdir(parents=True)
            registry.write_text(REGISTRY, encoding="utf-8")
            (root / "data/quest.lua").write_text('player:addAchievement("Public One")\n', encoding="utf-8")
            (root / "data-otservbr-global").mkdir()
            baseline = root / "baseline.json"
            baseline.write_text(
                json.dumps(
                    {
                        "counts": {"listed": 3, "common": 2, "secretDiscovered": 1},
                        "points": {"theoretical": 12},
                    }
                ),
                encoding="utf-8",
            )
            report = audit_repository(root, registry, reference_baseline=baseline)
            self.assertTrue(report["baselineComparison"]["matches"])
            self.assertEqual(report["summary"]["registryCount"], 3)
            self.assertEqual(report["summary"]["referenceCount"], 1)


if __name__ == "__main__":
    unittest.main()
