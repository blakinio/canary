#!/usr/bin/env python3
"""Apply bounded F-022/F-023/F-024 Forge history corrections."""

from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one anchor, found {count}: {old!r}")
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


player = "src/creatures/players/player.cpp"
replace_once(player, "\t\thistory.gained = 3;\n", "\t\thistory.gained = itemCount;\n")
replace_once(
    player,
    "\t\t} else if (history.actionType == ForgeAction_t::SLIVERSTOCORES) {\n\t\t\thistory.actionType = ForgeAction_t::DUSTTOSLIVERS;\n\t\t\tdetailsResponse << fmt::format(\"Converted {:d} slivers to {:d} exalted core.\", history.cost, history.gained);\n\t\t} else if (history.actionType == ForgeAction_t::INCREASELIMIT) {\n\t\t\thistory.actionType = ForgeAction_t::DUSTTOSLIVERS;\n\t\t\tdetailsResponse << fmt::format(\"Spent {:d} dust to increase the dust limit to {:d}.\", history.cost, history.gained + 1);\n",
    "\t\t} else if (history.actionType == ForgeAction_t::SLIVERSTOCORES) {\n\t\t\tdetailsResponse << fmt::format(\"Converted {:d} slivers to {:d} exalted core.\", history.cost, history.gained);\n\t\t} else if (history.actionType == ForgeAction_t::INCREASELIMIT) {\n\t\t\tdetailsResponse << fmt::format(\"Spent {:d} dust to increase the dust limit to {:d}.\", history.cost, history.gained + 1);\n",
)
replace_once(
    player,
    "\t\t\t\t\"100 dust\"\n",
    "\t\t\t\t\"{:d} dust\"\n",
)
replace_once(
    player,
    "\t\t\t\thistory.coresCost, price\n\t\t\t);\n\t\t}\n\t} else if (history.actionType == ForgeAction_t::TRANSFER)",
    "\t\t\t\thistory.coresCost, history.dustCost, price\n\t\t\t);\n\t\t}\n\t} else if (history.actionType == ForgeAction_t::TRANSFER)",
)

integration = Path("tests/integration/game/forge_it.cpp")
text = integration.read_text(encoding="utf-8").rstrip()
append = r'''

TEST_F(ForgeIntegrationTest, ForgeFailedFusionHistoryUsesRecordedDustCost) {
	const auto &fixture = testState();
	ForgeHistory history;
	history.actionType = ForgeAction_t::FUSION;
	history.success = false;
	history.firstItemId = fixture.firstForgeItemId;
	history.secondItemId = fixture.firstForgeItemId;
	history.firstItemName = Item::items[fixture.firstForgeItemId].name;
	history.secondItemName = Item::items[fixture.firstForgeItemId].name;
	history.tier = 1;
	history.dustCost = 137;
	history.coresCost = 2;
	history.cost = 320;

	const auto before = player->forgeHistory().get().size();
	player->registerForgeHistoryDescription(history);

	const auto &entries = player->forgeHistory().get();
	ASSERT_EQ(before + 1, entries.size());
	const auto &recorded = entries.back();
	EXPECT_EQ(ForgeAction_t::FUSION, recorded.actionType);
	EXPECT_EQ(137, recorded.dustCost);
	EXPECT_NE(std::string::npos, recorded.description.find("137 dust"));
}

TEST_F(ForgeIntegrationTest, ForgeDustToSliversHistoryUsesConfiguredAmountAndAction) {
	ensureBackpack();
	const auto amount = static_cast<uint16_t>(g_configManager().getNumber(FORGE_SLIVER_AMOUNT));
	const auto cost = static_cast<uint16_t>(g_configManager().getNumber(FORGE_COST_ONE_SLIVER) * amount);
	setPlayerResources(cost + 7, 0);
	const auto [sliversBefore, coresBefore] = player->getForgeSliversAndCores();
	const auto historyBefore = player->forgeHistory().get().size();

	player->forgeResourceConversion(ForgeAction_t::DUSTTOSLIVERS);

	const auto [sliversAfter, coresAfter] = player->getForgeSliversAndCores();
	EXPECT_EQ(sliversBefore + amount, sliversAfter);
	EXPECT_EQ(coresBefore, coresAfter);
	EXPECT_EQ(7, player->getForgeDusts());
	const auto &entries = player->forgeHistory().get();
	ASSERT_EQ(historyBefore + 1, entries.size());
	const auto &history = entries.back();
	EXPECT_EQ(ForgeAction_t::DUSTTOSLIVERS, history.actionType);
	EXPECT_EQ(cost, history.cost);
	EXPECT_EQ(amount, history.gained);
	EXPECT_NE(std::string::npos, history.description.find("Converted " + std::to_string(cost) + " dust to " + std::to_string(amount) + " slivers."));
}

TEST_F(ForgeIntegrationTest, ForgeSliversToCoreHistoryPreservesActionAndConfiguredCost) {
	ensureBackpack();
	const auto cost = static_cast<uint16_t>(g_configManager().getNumber(FORGE_CORE_COST));
	const auto &slivers = Item::CreateItem(ITEM_FORGE_SLIVER, cost);
	ASSERT_NE(nullptr, slivers);
	ASSERT_EQ(RETURNVALUE_NOERROR, g_game().internalPlayerAddItem(player, slivers, false, CONST_SLOT_BACKPACK));
	const auto historyBefore = player->forgeHistory().get().size();

	player->forgeResourceConversion(ForgeAction_t::SLIVERSTOCORES);

	const auto &entries = player->forgeHistory().get();
	ASSERT_EQ(historyBefore + 1, entries.size());
	const auto &history = entries.back();
	EXPECT_EQ(ForgeAction_t::SLIVERSTOCORES, history.actionType);
	EXPECT_EQ(cost, history.cost);
	EXPECT_EQ(1, history.gained);
	EXPECT_NE(std::string::npos, history.description.find("Converted " + std::to_string(cost) + " slivers to 1 exalted core."));
}

TEST_F(ForgeIntegrationTest, ForgeIncreaseLimitHistoryPreservesAction) {
	constexpr uint64_t testLimit = 100;
	const auto currentLimit = player->getForgeDustLevel();
	if (currentLimit < testLimit) {
		player->addForgeDustLevel(testLimit - currentLimit);
	} else if (currentLimit > testLimit) {
		player->removeForgeDustLevel(currentLimit - testLimit);
	}
	ASSERT_EQ(testLimit, player->getForgeDustLevel());
	const uint64_t cost = testLimit - 75;
	setPlayerResources(cost, 0);
	const auto historyBefore = player->forgeHistory().get().size();

	player->forgeResourceConversion(ForgeAction_t::INCREASELIMIT);

	EXPECT_EQ(testLimit + 1, player->getForgeDustLevel());
	EXPECT_EQ(0, player->getForgeDusts());
	const auto &entries = player->forgeHistory().get();
	ASSERT_EQ(historyBefore + 1, entries.size());
	const auto &history = entries.back();
	EXPECT_EQ(ForgeAction_t::INCREASELIMIT, history.actionType);
	EXPECT_EQ(cost, history.cost);
	EXPECT_EQ(testLimit, history.gained);
	EXPECT_NE(std::string::npos, history.description.find("Spent 25 dust to increase the dust limit to 101."));
}
'''
integration.write_text(text + append + "\n", encoding="utf-8")

print("Applied bounded Forge history correctness patch.")
