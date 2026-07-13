from __future__ import annotations

import unittest
from pathlib import Path

from wheel_task_shop_validation import audit_sources


TASKBOARD = r"""
-- Official-client packet shim for 15.25 Taskboard traffic.
-- Full task state, rewards, shop contents and Soulpit behavior should be added.
local function sendShopWindow(player)
    local msg = NetworkMessage()
    msg:addByte(0) -- offer count
    msg:sendToPlayer(player)
end
function onRecvbyte(player, msg, byte)
    local action = msg:getByte()
    if ShopResponseActions[action] then
        sendWindow(player, OutboundWindow.Shop)
    end
    logger.debug("handled by minimal official packet shim")
end
"""

PLAYER_WHEEL = r"""
uint16_t PlayerWheel::getExtraPoints() const {
    uint16_t totalBonus = 0;
    for (const auto &scroll : m_unlockedScrolls) totalBonus += scroll.extraPoints;
    return totalBonus;
}
"""


class WheelTaskShopValidationTests(unittest.TestCase):
    def test_detects_empty_shop_and_missing_point_path(self) -> None:
        report = audit_sources(TASKBOARD, PLAYER_WHEEL)
        self.assertFalse(report["ok"])
        self.assertEqual(report["summary"]["findingCount"], 1)
        self.assertEqual(report["findings"][0]["code"], "hunting-task-shop-wheel-points-missing")

    def test_repository_implements_bounded_persistent_promotion_offer(self) -> None:
        root = Path(__file__).resolve().parents[2]
        taskboard = (root / "data/modules/scripts/taskboard/taskboard.lua").read_text(encoding="utf-8")
        player_wheel = (root / "src/creatures/players/components/wheel/player_wheel.cpp").read_text(encoding="utf-8")
        report = audit_sources(taskboard, player_wheel)
        self.assertTrue(report["ok"], report["findings"])
        self.assertIn("MaxPoints = 50", taskboard)
        self.assertIn("100 * (1 + math.floor((pointNumber * (pointNumber - 1)) / 2))", taskboard)
        self.assertIn("player:removeTaskHuntingPoints(cost)", taskboard)
        self.assertIn('KvKey = "hunting-task-shop-points"', taskboard)
        self.assertIn("totalBonus += getHuntingTaskShopPoints();", player_wheel)
        self.assertIn("return m_huntingTaskShopPoints;", player_wheel)
        self.assertIn("msg.add<uint16_t>(getHuntingTaskShopPoints());", player_wheel)

    def test_accepts_implemented_shop_and_point_path(self) -> None:
        taskboard = TASKBOARD.replace("msg:addByte(0) -- offer count", "msg:addByte(1) -- offer count").replace(
            "sendWindow(player, OutboundWindow.Shop)",
            "player:useTaskHuntingPoints(1000)\n        player:addWheelPromotionPoint()",
        )
        player_wheel = PLAYER_WHEEL.replace(
            "return totalBonus;",
            "totalBonus += m_huntingTaskPromotionPoints;\n    return totalBonus;",
        )
        report = audit_sources(taskboard, player_wheel)
        self.assertTrue(report["ok"])
        self.assertEqual(report["summary"]["findingCount"], 0)


if __name__ == "__main__":
    unittest.main()
