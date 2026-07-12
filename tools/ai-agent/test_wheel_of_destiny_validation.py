from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from wheel_of_destiny_validation import (
    FILES,
    audit_repository,
    audit_sources,
    count_revelation_double_application,
    duplicate_adjacency_checks,
    parse_config_defaults,
    parse_enum_values,
    parse_grade_costs,
    parse_promotion_scrolls,
)


DEFINITIONS = r"""
enum WheelSlots_t : uint8_t {
    SLOT_GREEN_50 = 1,
    SLOT_GREEN_TOP_75,
    SLOT_GREEN_BOTTOM_75,
    SLOT_GREEN_TOP_100,
    SLOT_GREEN_MIDDLE_100,
    SLOT_GREEN_BOTTOM_100,
    SLOT_GREEN_TOP_150,
    SLOT_GREEN_BOTTOM_150,
    SLOT_GREEN_200,
    SLOT_RED_50,
    SLOT_RED_TOP_75,
    SLOT_RED_BOTTOM_75,
    SLOT_RED_TOP_100,
    SLOT_RED_MIDDLE_100,
    SLOT_RED_BOTTOM_100,
    SLOT_RED_TOP_150,
    SLOT_RED_BOTTOM_150,
    SLOT_RED_200,
    SLOT_PURPLE_50,
    SLOT_PURPLE_TOP_75,
    SLOT_PURPLE_BOTTOM_75,
    SLOT_PURPLE_TOP_100,
    SLOT_PURPLE_MIDDLE_100,
    SLOT_PURPLE_BOTTOM_100,
    SLOT_PURPLE_TOP_150,
    SLOT_PURPLE_BOTTOM_150,
    SLOT_PURPLE_200,
    SLOT_BLUE_50,
    SLOT_BLUE_TOP_75,
    SLOT_BLUE_BOTTOM_75,
    SLOT_BLUE_TOP_100,
    SLOT_BLUE_MIDDLE_100,
    SLOT_BLUE_BOTTOM_100,
    SLOT_BLUE_TOP_150,
    SLOT_BLUE_BOTTOM_150,
    SLOT_BLUE_200,
};
enum class WheelStagePointsEnum_t : uint16_t {
    ONE = 250,
    TWO = 500,
    THREE = 1000,
};
"""

PLAYER = r"""
const std::vector<PromotionScroll> WheelOfDestinyPromotionScrolls = {
    { 43946, "Abridged Promotion Scroll", 3 },
    { 43947, "Basic Promotion Scroll", 5 },
    { 43948, "Revised Promotion Scroll", 9 },
    { 43949, "Extended Promotion Scroll", 13 },
    { 43950, "Advanced Promotion Scroll", 20 },
};

bool PlayerWheel::canPlayerSelectPointOnSlot(WheelSlots_t slot, bool recursive) const {
    if (slot == WheelSlots_t::SLOT_GREEN_TOP_100) {
        if (canSelectSlotFullOrPartial(WheelSlots_t::SLOT_GREEN_MIDDLE_100)) return true;
        if (canSelectSlotFullOrPartial(WheelSlots_t::SLOT_GREEN_MIDDLE_100)) return true;
    } else if (slot == WheelSlots_t::SLOT_GREEN_50) {
        return true;
    }
    return false;
}

uint16_t PlayerWheel::getExtraPoints() const {
    uint16_t totalBonus = 0;
    for (const auto &scroll : m_unlockedScrolls) totalBonus += scroll.extraPoints;
    if (hasCompletedMonkQuest()) totalBonus += 10;
    return totalBonus;
}

WheelStageEnum_t PlayerWheel::getPlayerSliceStage(const std::string &color) const {
    int totalPoints = 0;
    totalPoints += m_modsMaxGrade;
    return WheelStageEnum_t::NONE;
}

void PlayerWheel::revealGem(WheelGemQuality_t quality) {
    if (!g_game().removeMoney(m_player.getPlayer(), getGemRevealCost(quality), 0, true)) return;
    if (!m_player.removeItemCountById(123, 1, false)) return;
    m_revealedGems.emplace_back(PlayerWheelGem{});
}

void PlayerWheel::improveGemGrade(WheelFragmentType_t fragmentType, uint8_t pos) {
    uint8_t grade = fragmentType == WheelFragmentType_t::Lesser ? m_basicGrades[pos] : m_supremeGrades[pos];
    if (!g_game().removeMoney(m_player.getPlayer(), 1, 0, true)) return;
    if (!m_player.removeItemCountById(123, 1, true)) return;
}

std::tuple<int, int> PlayerWheel::getLesserGradeCost(uint8_t grade) const {
    switch (grade) {
        case 1: return std::make_tuple(2000000, 5);
        case 2: return std::make_tuple(5000000, 15);
        case 3: return std::make_tuple(30000000, 30);
        default: return {};
    }
}

std::tuple<int, int> PlayerWheel::getGreaterGradeCost(uint8_t grade) const {
    switch (grade) {
        case 1: return std::make_tuple(5000000, 5);
        case 2: return std::make_tuple(12000000, 15);
        case 3: return std::make_tuple(75000000, 30);
        default: return {};
    }
}
"""

GEMS = r"""
void WheelModifierContext::addStrategies(WheelGemBasicModifier_t modifier, uint8_t grade) {
    float gradeMultiplier = 1.0;
    if (grade == 1) {
        gradeMultiplier = 1.1;
    } else if (grade == 2) {
        gradeMultiplier = 1.2;
    } else if (grade == 3) {
        gradeMultiplier = 1.5;
    }
}

void WheelModifierContext::addStrategies(WheelGemSupremeModifier_t modifier, uint8_t grade) {
    switch (modifier) {
        case WheelGemSupremeModifier_t::General_RevelationMastery_GiftOfLife:
            m_strategies.emplace_back(std::make_unique<GemModifierRevelationStrategy>(
                m_wheel, WheelGemAffinity_t::Green, 150
            ));
            m_wheel.addRevelationBonus(WheelGemAffinity_t::Green, 150);
            break;
        default:
            break;
    }
}

void WheelModifierContext::executeStrategies() const {
    for (const auto &strategy : m_strategies) strategy->execute();
}
"""

CONFIG = r"""
loadIntConfig(L, WHEEL_MONK_QUEST_BONUS, "wheelMonkQuestBonus", 10);
loadIntConfig(L, WHEEL_ATELIER_REVEAL_GREATER_COST, "wheelAtelierRevealGreaterCost", 6000000);
loadIntConfig(L, WHEEL_ATELIER_REVEAL_LESSER_COST, "wheelAtelierRevealLesserCost", 125000);
loadIntConfig(L, WHEEL_ATELIER_REVEAL_REGULAR_COST, "wheelAtelierRevealRegularCost", 1000000);
loadIntConfig(L, WHEEL_ATELIER_ROTATE_GREATER_COST, "wheelAtelierRotateGreaterCost", 500000);
loadIntConfig(L, WHEEL_ATELIER_ROTATE_LESSER_COST, "wheelAtelierRotateLesserCost", 125000);
loadIntConfig(L, WHEEL_ATELIER_ROTATE_REGULAR_COST, "wheelAtelierRotateRegularCost", 250000);
loadIntConfig(L, WHEEL_POINTS_PER_LEVEL, "wheelPointsPerLevel", 1);
"""

BASELINE = {
    "source": {"url": "https://example.test", "checkedAt": "2026-07-12"},
    "wheel": {
        "sliceCount": 36,
        "revelationThresholds": [250, 500, 1000],
        "pointsPerLevel": 1,
        "monkQuestBonus": 10,
        "promotionScrollPoints": 50,
    },
    "atelier": {
        "maxRevealedGems": 225,
        "costs": {
            "reveal": {"lesser": 125000, "regular": 1000000, "greater": 6000000},
            "rotate": {"lesser": 125000, "regular": 250000, "greater": 500000},
        },
        "basicGradeCosts": {
            "2": {"gold": 2000000, "fragments": 5},
            "3": {"gold": 5000000, "fragments": 15},
            "4": {"gold": 30000000, "fragments": 30},
        },
        "supremeGradeCosts": {
            "2": {"gold": 5000000, "fragments": 5},
            "3": {"gold": 12000000, "fragments": 15},
            "4": {"gold": 75000000, "fragments": 30},
        },
        "gradeMultipliers": {"1": 1.0, "4": 1.5},
    },
}


def fixture_sources() -> dict[str, str]:
    return {
        "definitions": DEFINITIONS,
        "player_header": "",
        "player": PLAYER,
        "gems": GEMS,
        "enums": "",
        "io_header": "",
        "io": "",
        "config": CONFIG,
    }


class WheelOfDestinyValidationTests(unittest.TestCase):
    def test_parses_core_definitions_and_scrolls(self) -> None:
        slots = parse_enum_values(DEFINITIONS, "WheelSlots_t")
        thresholds = parse_enum_values(DEFINITIONS, "WheelStagePointsEnum_t")
        scrolls = parse_promotion_scrolls(PLAYER)
        self.assertEqual(len(slots), 36)
        self.assertEqual([thresholds["ONE"], thresholds["TWO"], thresholds["THREE"]], [250, 500, 1000])
        self.assertEqual(sum(item["points"] for item in scrolls), 50)

    def test_parses_costs_and_config_defaults(self) -> None:
        config = parse_config_defaults(CONFIG)
        self.assertEqual(config["revealGreater"], 6000000)
        self.assertEqual(parse_grade_costs(PLAYER, "getLesserGradeCost")[4], {"gold": 30000000, "fragments": 30})

    def test_detects_duplicate_adjacency(self) -> None:
        self.assertEqual(
            duplicate_adjacency_checks(PLAYER),
            [{"slot": "SLOT_GREEN_TOP_100", "neighbor": "SLOT_GREEN_MIDDLE_100", "count": 2}],
        )

    def test_detects_double_revelation_application(self) -> None:
        self.assertEqual(
            count_revelation_double_application(GEMS),
            ["General_RevelationMastery_GiftOfLife"],
        )

    def test_report_records_confirmed_and_risk_findings(self) -> None:
        report = audit_sources(fixture_sources(), BASELINE)
        codes = {item["code"] for item in report["findings"]}
        self.assertIn("revelation-bonus-double-applied", codes)
        self.assertIn("grade-iv-points-not-spendable", codes)
        self.assertIn("grade-iv-points-injected-into-every-domain", codes)
        self.assertIn("revealed-gem-cap-not-enforced-in-reveal", codes)
        self.assertIn("reveal-operation-not-transactional", codes)
        self.assertIn("grade-upgrade-not-transactional", codes)
        self.assertIn("grade-position-unvalidated", codes)
        self.assertFalse(report["ok"])
        self.assertTrue(all(item["matches"] for item in report["comparisons"].values()))

    def test_detects_reference_cost_mismatch(self) -> None:
        baseline = json.loads(json.dumps(BASELINE))
        baseline["atelier"]["supremeGradeCosts"]["3"]["gold"] = 12500000
        report = audit_sources(fixture_sources(), baseline)
        mismatch = report["comparisons"]["atelier.supremeGradeCosts"]
        self.assertFalse(mismatch["matches"])
        self.assertIn("reference-baseline-mismatch", {item["code"] for item in report["findings"]})

    def test_repository_audit_reads_required_paths_and_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            content_by_key = fixture_sources()
            for key, source in FILES.items():
                path = root / source.path
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content_by_key[key], encoding="utf-8")
            baseline_path = root / "baseline.json"
            baseline_path.write_text(json.dumps(BASELINE), encoding="utf-8")
            report = audit_repository(root, baseline_path)
            self.assertEqual(report["summary"]["sliceCount"], 36)
            self.assertGreaterEqual(report["summary"]["sourceFileCount"], 2)


if __name__ == "__main__":
    unittest.main()
