from __future__ import annotations

import unittest

from wheel_protocol_validation import audit_sources


PROTOCOL = r"""
void ProtocolGame::parseWheelGemAction(NetworkMessage &msg) {
    const auto action = static_cast<WheelGemAction_t>(msg.getByte());
    switch (action) {
        case WheelGemAction_t::Reveal:
            player->wheel().revealGem(static_cast<WheelGemQuality_t>(msg.getByte(true)));
            break;
        case WheelGemAction_t::ImproveGrade: {
            const auto fragmentType = static_cast<WheelFragmentType_t>(msg.getByte(true) != 0 ? 1 : 0);
            const auto position = msg.getByte(true);
            player->wheel().improveGemGrade(fragmentType, position);
            break;
        }
        default: break;
    }
}
"""

GAME = r"""
void Game::playerWheelGemAction(uint32_t playerId, NetworkMessage &msg) {
    const auto action = msg.getByte();
    const auto param = msg.getByte();
    uint8_t pos = 0;
    switch (static_cast<WheelGemAction_t>(action)) {
        case WheelGemAction_t::Reveal:
            player->wheel().revealGem(static_cast<WheelGemQuality_t>(param));
            break;
        case WheelGemAction_t::ImproveGrade:
            pos = msg.getByte();
            player->wheel().improveGemGrade(static_cast<WheelFragmentType_t>(param), pos);
            break;
        default: break;
    }
}
"""

PLAYER_CPP = r"""
void PlayerWheel::revealGem(WheelGemQuality_t quality) {
    if (!g_game().removeMoney(m_player.getPlayer(), getGemRevealCost(quality), 0, true)) return;
    m_revealedGems.emplace_back(PlayerWheelGem{});
}
void PlayerWheel::improveGemGrade(WheelFragmentType_t type, uint8_t pos) {
    const auto grade = type == WheelFragmentType_t::Lesser ? m_basicGrades[pos] : m_supremeGrades[pos];
}
"""

PLAYER_HPP = r"""
std::array<uint8_t, 49> m_basicGrades = { 0 };
std::array<uint8_t, 95> m_supremeGrades = { 0 };
"""


class WheelProtocolValidationTests(unittest.TestCase):
    def test_detects_both_unguarded_profiles(self) -> None:
        report = audit_sources(PROTOCOL, GAME, PLAYER_CPP, PLAYER_HPP)
        self.assertFalse(report["ok"])
        self.assertEqual(report["summary"]["profiles"], ["current", "legacy"])
        self.assertEqual(report["summary"]["findingCount"], 2)
        by_code = {item["code"]: item for item in report["findings"]}
        self.assertEqual(
            by_code["revealed-gem-cap-unenforced-all-profiles"]["evidence"]["unguardedProfiles"],
            ["current", "legacy"],
        )
        self.assertEqual(
            by_code["grade-position-unvalidated-all-profiles"]["evidence"]["unguardedProfiles"],
            ["current", "legacy"],
        )
        self.assertEqual(report["summary"]["basicGradeArraySize"], 49)
        self.assertEqual(report["summary"]["supremeGradeArraySize"], 95)

    def test_accepts_central_runtime_guards(self) -> None:
        guarded_cpp = PLAYER_CPP.replace(
            "if (!g_game().removeMoney",
            "if (m_revealedGems.size() >= 225) return;\n    if (!g_game().removeMoney",
        ).replace(
            "const auto grade =",
            "if (pos >= (type == WheelFragmentType_t::Lesser ? m_basicGrades.size() : m_supremeGrades.size())) return;\n    const auto grade =",
        )
        report = audit_sources(PROTOCOL, GAME, guarded_cpp, PLAYER_HPP)
        self.assertTrue(report["ok"])
        self.assertEqual(report["summary"]["findingCount"], 0)


if __name__ == "__main__":
    unittest.main()
