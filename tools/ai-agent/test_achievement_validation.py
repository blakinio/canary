from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from achievement_validation import (
    audit_registry_helpers,
    audit_repository,
    build_report,
    parse_reference_source_text,
    parse_registry_text,
    scan_persistence_evidence,
    scan_reference_text,
    validate_reference_catalog,
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

    def test_zero_point_definition_is_an_information_exception(self) -> None:
        text = 'ACHIEVEMENTS = {\n[1] = { name = "Zero", grade = 1, points = 0, description = "Zero." },\n}\n'
        _, findings = parse_registry_text(text)
        by_code = {item["code"]: item for item in findings}
        self.assertIn("registry-zero-point-exception", by_code)
        self.assertEqual(by_code["registry-zero-point-exception"]["severity"], "info")
        self.assertNotIn("registry-grade-points-mismatch", by_code)

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

    def test_confirmed_gameplay_trigger_names_resolve_exactly(self) -> None:
        root = Path(__file__).resolve().parents[2]
        registry_path = root / "data/scripts/lib/register_achievements.lua"
        definitions, registry_findings = parse_registry_text(registry_path.read_text(encoding="utf-8"))
        expected = {
            "data/scripts/actions/items/usable_phantasmal_jade_items.lua": "You Got Horse Power",
            "data-otservbr-global/scripts/quests/hero_of_rathleton/actions_reward.lua": "The Professor's Nut",
        }
        references = []
        for relative_path, expected_name in expected.items():
            path = root / relative_path
            file_references = scan_reference_text(path.read_text(encoding="utf-8"), relative_path)
            static_awards = {
                reference.identifier
                for reference in file_references
                if reference.kind == "award" and reference.identifier_type == "name"
            }
            self.assertIn(expected_name, static_awards)
            references.extend(file_references)

        report = build_report(definitions, registry_findings, [], references)
        self.assertEqual(report["summary"]["unknownStaticReferenceCount"], 0, report["unknownStaticReferences"])

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


    def test_parses_reference_catalog_without_copying_source_prose(self) -> None:
        source = json.dumps(
            {
                "parse": {
                    "pageid": 42,
                    "revid": 99,
                    "text": """
                    <p>This list includes 1 common and 1 / 2 secret achievements (2 out of 3 total discovered achievements).</p>
                    <p>The theoretical maximum points one can have is 6. Excluding coinciding achievements, the maximum is 5.</p>
                    <h2>List of Achievements (2)</h2>
                    <table class="wikitable achievements_title_table">
                    <tr><th>Name</th><th>ID</th><th>Grade</th><th>Secret?</th><th>Premium</th><th>Points</th><th>Implemented</th><th>Description</th><th>Spoiler</th></tr>
                    <tr><td><a href="/wiki/Public_One">Public One</a></td><td>1</td><td>1</td><td>✗</td><td>✓</td><td>1</td><td>Today</td><td>Expressive description.</td><td>Obtainable by completing <a href="/wiki/Test_Quest">Test Quest</a> 10 times.</td></tr>
                    <tr><td><a href="/wiki/Secret_Two_(Achievement)">Secret Two (Achievement)</a></td><td>2</td><td>2</td><td>✓</td><td>?</td><td>5</td><td>Tomorrow</td><td>Another description.</td><td></td></tr>
                    </table>
                    """,
                }
            }
        )
        catalog = parse_reference_source_text(source, "2026-07-13", "https://example.invalid/api")
        validate_reference_catalog(catalog)
        self.assertEqual(catalog["summary"]["rows"], 2)
        self.assertEqual(catalog["pageSummary"]["total"], 3)
        self.assertEqual(catalog["achievements"][1]["name"], "Secret Two")
        self.assertIn("quest-or-task", catalog["achievements"][0]["condition"]["kinds"])
        self.assertEqual(catalog["achievements"][0]["condition"]["numbers"], ["10"])
        self.assertEqual(catalog["achievements"][0]["condition"]["entities"][0]["name"], "Test Quest")
        self.assertNotIn("text", catalog["achievements"][0]["condition"])
        self.assertNotIn("description", catalog["achievements"][0])

    def test_comprehensive_statuses_remain_conservative(self) -> None:
        definitions, registry_findings = parse_registry_text(REGISTRY)
        references = scan_reference_text('player:addAchievement("Public One")\n', "data/quest.lua")
        catalog = {
            "format": "canary-achievement-reference-catalog-v1",
            "summary": {"rows": 3},
            "source": {"observedAt": "2026-07-13"},
            "sourceConflicts": [],
            "achievements": [
                {
                    "id": 1,
                    "name": "Public One",
                    "grade": 1,
                    "secret": False,
                    "points": 1,
                    "condition": {"available": True, "kinds": ["quest-or-task"], "entities": [], "numbers": []},
                },
                {
                    "id": 2,
                    "name": "Secret Two",
                    "grade": 2,
                    "secret": True,
                    "points": 4,
                    "condition": {"available": True, "kinds": ["combat"], "entities": [], "numbers": []},
                },
                {
                    "id": 3,
                    "name": "Missing Three",
                    "grade": 1,
                    "secret": False,
                    "points": 1,
                    "condition": {"available": False, "kinds": ["unresolved"], "entities": [], "numbers": []},
                },
            ],
        }
        report = build_report(
            definitions,
            registry_findings,
            [],
            references,
            reference_catalog=catalog,
            persistence={"status": "name-keyed-kv-confirmed", "evidence": [], "backfill": "unresolved"},
        )
        rows = {item["id"]: item for item in report["referenceValidation"]}
        self.assertEqual(rows[1]["status"], "partially-confirmed")
        self.assertEqual(rows[2]["status"], "unresolved")
        self.assertEqual(rows[3]["status"], "conflicting")
        self.assertFalse(report["complete"])
        self.assertEqual(rows[1]["persistence"]["backfill"], "unresolved")
        self.assertEqual(rows[1]["tests"]["status"], "missing")

    def test_reviewed_evidence_can_prove_handler_missing(self) -> None:
        definitions, registry_findings = parse_registry_text(REGISTRY)
        catalog = {
            "format": "canary-achievement-reference-catalog-v1",
            "summary": {"rows": 1},
            "source": {},
            "sourceConflicts": [],
            "achievements": [
                {
                    "id": 2,
                    "name": "Secret Two",
                    "grade": 2,
                    "secret": True,
                    "points": 4,
                    "condition": {"available": True, "kinds": ["progress-threshold"], "entities": [], "numbers": ["10"]},
                }
            ],
        }
        review = {
            2: {
                "id": 2,
                "status": "handler-missing",
                "reason": "Dedicated bounded audit proved no award path.",
                "evidence": [{"path": "docs/report.md", "line": 10}],
                "newPlayerAttainability": "handler-missing",
            }
        }
        report = build_report(definitions, registry_findings, [], [], reference_catalog=catalog, reviewed_evidence=review)
        row = report["referenceValidation"][0]
        self.assertEqual(row["status"], "handler-missing")
        self.assertEqual(row["attainability"]["newPlayers"], "handler-missing")

    def test_persistence_evidence_is_line_grounded(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "player_achievement.cpp"
            path.write_text(
                'getUnlockedKV()->set(achievement.name, timestamp);\n'
                'g_game().getAchievementByName(achievementName);\n'
                'scoped("achievements")->set("points", points);\n',
                encoding="utf-8",
            )
            evidence = scan_persistence_evidence(root, "player_achievement.cpp")
            self.assertEqual(evidence["status"], "name-keyed-kv-confirmed")
            self.assertEqual([item["line"] for item in evidence["evidence"]], [1, 2, 3])
            self.assertEqual(evidence["backfill"], "unresolved")


if __name__ == "__main__":
    unittest.main()
