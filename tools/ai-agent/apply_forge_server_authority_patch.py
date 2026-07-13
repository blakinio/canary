#!/usr/bin/env python3
"""Apply the bounded F-003/F-004/F-005 Forge server-authority patch.

This temporary task-local runner exists because the execution environment cannot
clone GitHub. Every edit is anchored and the script stops on source drift.
"""

from pathlib import Path
from textwrap import dedent


def replace_once(path: str, old: str, new: str) -> None:
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(
            f"{path}: expected exactly one anchor, found {count}: {old!r}"
        )
    file_path.write_text(text.replace(old, new), encoding="utf-8")


def block(text: str) -> str:
    return dedent(text).lstrip("\n")


player_path = Path("src/creatures/players/player.cpp")
if '#include "game/functions/forge_fusion_policy.hpp"' in player_path.read_text(
    encoding="utf-8"
):
    print("Forge server-authority patch is already applied; nothing to do.")
    raise SystemExit(0)

replace_once(
    "src/creatures/players/player.cpp",
    '#include "creatures/players/player.hpp"\n#include "game/functions/forge_transfer_policy.hpp"\n',
    '#include "creatures/players/player.hpp"\n#include "game/functions/forge_fusion_policy.hpp"\n#include "game/functions/forge_transfer_policy.hpp"\n',
)

fusion_anchor = block(
    """
    \tconst auto &secondForgingItem = getForgeItemFromId(secondItemId, tier, firstForgingItem);
    \tif (!secondForgingItem) {
    \t\tg_logger().error("[Log 2] Player with name {} failed to fuse item with id {}", getName(), secondItemId);
    \t\tsendForgeError(RETURNVALUE_CONTACTADMINISTRATOR);
    \t\treturn;
    \t}
    """
)
fusion_authority = fusion_anchor + block(
    """

    \tauto normalizeForgeSlot = [](uint32_t slotPosition) {
    \t\treturn (slotPosition & SLOTP_TWO_HAND) != 0 ? static_cast<uint32_t>(SLOTP_HAND) : slotPosition;
    \t};
    \tconst bool sameForgeSlot = normalizeForgeSlot(firstForgingItem->getSlotPosition()) == normalizeForgeSlot(secondForgingItem->getSlotPosition());
    \tif (!ForgeFusionPolicy::isValid(
    \t\t\tfirstItemId,
    \t\t\tsecondItemId,
    \t\t\tfirstForgingItem->getClassification(),
    \t\t\tsecondForgingItem->getClassification(),
    \t\t\tsameForgeSlot,
    \t\t\tconvergence)) {
    \t\tg_logger().warn(
    \t\t\t"[{}] Rejected invalid fusion for player {}: first item {}, second item {}, first class {}, second class {}, tier {}, same slot {}, convergence {}",
    \t\t\t__FUNCTION__,
    \t\t\tgetName(),
    \t\t\tfirstItemId,
    \t\t\tsecondItemId,
    \t\t\tfirstForgingItem->getClassification(),
    \t\t\tsecondForgingItem->getClassification(),
    \t\t\ttier,
    \t\t\tsameForgeSlot,
    \t\t\tconvergence
    \t\t);
    \t\tsendForgeError(RETURNVALUE_NOTPOSSIBLE);
    \t\treturn;
    \t}
    """
)
replace_once("src/creatures/players/player.cpp", fusion_anchor, fusion_authority)

replace_once(
    "src/creatures/players/player.cpp",
    "\tif (!ForgeTransferPolicy::isValidDonorTier(donorItem->getTier(), convergence) || !ForgeTransferPolicy::hasMatchingClassification(donorClassification, receiveClassification)) {",
    "\tif (!ForgeTransferPolicy::isValidTransfer(donorClassification, receiveClassification, donorItem->getTier(), convergence)) {",
)

Path("src/game/functions/forge_fusion_policy.hpp").write_text(
    block(
        """
        /**
         * Canary - A free and open-source MMORPG server emulator
         * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
         * Repository: https://github.com/opentibiabr/canary
         * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
         * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
         * Website: https://docs.opentibiabr.com/
         */

        #pragma once

        #include <cstdint>

        namespace ForgeFusionPolicy {
        \t[[nodiscard]] constexpr bool isValid(
        \t\tuint16_t firstItemId,
        \t\tuint16_t secondItemId,
        \t\tuint8_t firstClassification,
        \t\tuint8_t secondClassification,
        \t\tbool sameSlot,
        \t\tbool convergence
        \t) {
        \t\tif (firstItemId == 0 || secondItemId == 0 || firstClassification == 0 || secondClassification == 0) {
        \t\t\treturn false;
        \t\t}

        \t\tif (!convergence) {
        \t\t\treturn firstItemId == secondItemId && firstClassification == secondClassification;
        \t\t}

        \t\treturn firstItemId != secondItemId
        \t\t\t&& firstClassification == 4
        \t\t\t&& secondClassification == 4
        \t\t\t&& sameSlot;
        \t}
        } // namespace ForgeFusionPolicy
        """
    ),
    encoding="utf-8",
)

Path("src/game/functions/forge_transfer_policy.hpp").write_text(
    block(
        """
        /**
         * Canary - A free and open-source MMORPG server emulator
         * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
         * Repository: https://github.com/opentibiabr/canary
         * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
         * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
         * Website: https://docs.opentibiabr.com/
         */

        #pragma once

        #include <cstdint>

        namespace ForgeTransferPolicy {
        \t[[nodiscard]] constexpr bool hasMatchingClassification(uint8_t donorClassification, uint8_t receiveClassification) {
        \t\treturn donorClassification > 0 && donorClassification == receiveClassification;
        \t}

        \t[[nodiscard]] constexpr bool isValidDonorTier(uint8_t donorTier, bool convergence) {
        \t\treturn convergence ? donorTier >= 1 : donorTier >= 2;
        \t}

        \t[[nodiscard]] constexpr bool isValidClassification(uint8_t donorClassification, uint8_t receiveClassification, bool convergence) {
        \t\treturn hasMatchingClassification(donorClassification, receiveClassification)
        \t\t\t&& (!convergence || donorClassification == 4);
        \t}

        \t[[nodiscard]] constexpr bool isValidTransfer(uint8_t donorClassification, uint8_t receiveClassification, uint8_t donorTier, bool convergence) {
        \t\treturn isValidDonorTier(donorTier, convergence)
        \t\t\t&& isValidClassification(donorClassification, receiveClassification, convergence);
        \t}

        \t[[nodiscard]] constexpr uint8_t resourceTier(uint8_t donorTier) {
        \t\treturn donorTier;
        \t}

        \t[[nodiscard]] constexpr uint8_t resultTier(uint8_t donorTier, bool convergence) {
        \t\treturn convergence ? donorTier : static_cast<uint8_t>(donorTier - 1);
        \t}
        } // namespace ForgeTransferPolicy
        """
    ),
    encoding="utf-8",
)

replace_once(
    "tests/unit/players/forge_test.cpp",
    '#include "creatures/players/player.hpp"\n#include "game/functions/forge_transfer_policy.hpp"\n',
    '#include "creatures/players/player.hpp"\n#include "game/functions/forge_fusion_policy.hpp"\n#include "game/functions/forge_transfer_policy.hpp"\n',
)

unit_append = block(
    """

    TEST(ForgeTransferPolicyTest, RestrictsConvergenceTransferToClassFour) {
    \tEXPECT_TRUE(ForgeTransferPolicy::isValidTransfer(4, 4, 1, true));
    \tEXPECT_FALSE(ForgeTransferPolicy::isValidTransfer(3, 3, 1, true));
    \tEXPECT_FALSE(ForgeTransferPolicy::isValidTransfer(4, 3, 1, true));
    \tEXPECT_TRUE(ForgeTransferPolicy::isValidTransfer(3, 3, 2, false));
    }

    TEST(ForgeFusionPolicyTest, RegularFusionRequiresIdenticalForgeItems) {
    \tEXPECT_TRUE(ForgeFusionPolicy::isValid(100, 100, 3, 3, true, false));
    \tEXPECT_FALSE(ForgeFusionPolicy::isValid(100, 101, 3, 3, true, false));
    \tEXPECT_FALSE(ForgeFusionPolicy::isValid(100, 100, 0, 0, true, false));
    }

    TEST(ForgeFusionPolicyTest, ConvergenceFusionRequiresDifferentClassFourItemsInSameSlot) {
    \tEXPECT_TRUE(ForgeFusionPolicy::isValid(100, 101, 4, 4, true, true));
    \tEXPECT_FALSE(ForgeFusionPolicy::isValid(100, 100, 4, 4, true, true));
    \tEXPECT_FALSE(ForgeFusionPolicy::isValid(100, 101, 3, 3, true, true));
    \tEXPECT_FALSE(ForgeFusionPolicy::isValid(100, 101, 4, 4, false, true));
    }
    """
)
unit_path = Path("tests/unit/players/forge_test.cpp")
unit_path.write_text(
    unit_path.read_text(encoding="utf-8").rstrip() + unit_append + "\n",
    encoding="utf-8",
)

different_id_success = block(
    """
    TEST_F(ForgeIntegrationTest, ForgeFuseItemsViaGameFlowAddsExaltationChestAndConsumesInputs) {
    \tensureBackpack();
    \tconst auto &fixture = testState();

    \tseedGameRng(1337);
    \tconst uint64_t dustCost = g_configManager().getNumber(FORGE_FUSION_DUST_COST);
    \tconst uint64_t goldCost = fixture.fusionCostForTier(2);
    \tsetPlayerResources(dustCost + 5, goldCost + 7);
    \taddPlayerItemBackpack(fixture.firstForgeItemId, 1);
    \taddPlayerItemBackpack(fixture.secondForgeItemId, 1);

    \tconst auto startDust = player->getForgeDusts();
    \tconst auto startBalance = player->getBankBalance();
    \tconst auto startChest = countItem(*player, ITEM_EXALTATION_CHEST, 0);
    \tconst auto startFirstTier = countItem(*player, fixture.firstForgeItemId, 1);
    \tconst auto startSecondTier = countItem(*player, fixture.secondForgeItemId, 1);

    \tplayer->forgeFuseItems(ForgeAction_t::FUSION, fixture.firstForgeItemId, 1, fixture.secondForgeItemId, true, false, false, 0, 0);

    \tEXPECT_EQ(player->getForgeDusts(), startDust - dustCost);
    \tEXPECT_EQ(player->getBankBalance(), startBalance - goldCost);
    \tEXPECT_GT(countItem(*player, ITEM_EXALTATION_CHEST, 0), startChest);
    \tEXPECT_EQ(countItem(*player, fixture.firstForgeItemId, 1), startFirstTier - 1u);
    \tEXPECT_EQ(countItem(*player, fixture.secondForgeItemId, 1), startSecondTier - 1u);
    }
    """
)
different_id_rejection = block(
    """
    TEST_F(ForgeIntegrationTest, ForgeFuseItemsRejectsDifferentItemIdsBeforeMutating) {
    \tensureBackpack();
    \tconst auto &fixture = testState();

    \tconst uint64_t dustCost = g_configManager().getNumber(FORGE_FUSION_DUST_COST);
    \tconst uint64_t goldCost = fixture.fusionCostForTier(2);
    \tsetPlayerResources(dustCost + 5, goldCost + 7);
    \taddPlayerItemBackpack(fixture.firstForgeItemId, 1);
    \taddPlayerItemBackpack(fixture.secondForgeItemId, 1);
    \tconst auto &forgeCore = Item::CreateItem(ITEM_FORGE_CORE, 1);
    \tASSERT_NE(nullptr, forgeCore);
    \tASSERT_EQ(RETURNVALUE_NOERROR, g_game().internalPlayerAddItem(player, forgeCore, false, CONST_SLOT_BACKPACK));

    \tconst auto startDust = player->getForgeDusts();
    \tconst auto startBalance = player->getBankBalance();
    \tconst auto startChest = countItem(*player, ITEM_EXALTATION_CHEST, 0);
    \tconst auto startFirstTier = countItem(*player, fixture.firstForgeItemId, 1);
    \tconst auto startSecondTier = countItem(*player, fixture.secondForgeItemId, 1);
    \tconst auto startCore = countItem(*player, ITEM_FORGE_CORE, 0);
    \tconst auto startHistory = player->forgeHistory().get().size();

    \tplayer->forgeFuseItems(ForgeAction_t::FUSION, fixture.firstForgeItemId, 1, fixture.secondForgeItemId, true, false, false, 0, 1);

    \tEXPECT_EQ(startDust, player->getForgeDusts());
    \tEXPECT_EQ(startBalance, player->getBankBalance());
    \tEXPECT_EQ(startChest, countItem(*player, ITEM_EXALTATION_CHEST, 0));
    \tEXPECT_EQ(startFirstTier, countItem(*player, fixture.firstForgeItemId, 1));
    \tEXPECT_EQ(startSecondTier, countItem(*player, fixture.secondForgeItemId, 1));
    \tEXPECT_EQ(startCore, countItem(*player, ITEM_FORGE_CORE, 0));
    \tEXPECT_EQ(startHistory, player->forgeHistory().get().size());
    }
    """
)
replace_once(
    "tests/integration/game/forge_it.cpp",
    different_id_success,
    different_id_rejection,
)

integration_append = block(
    """

    TEST_F(ForgeIntegrationTest, ForgeConvergenceFusionRejectsNonClassFourBeforeMutating) {
    \tensureBackpack();
    \tconst auto &fixture = testState();
    \tASSERT_NE(4, fixture.classificationId);
    \tsetPlayerResources(1000, 1000000);
    \taddPlayerItemBackpack(fixture.firstForgeItemId, 1);
    \taddPlayerItemBackpack(fixture.secondForgeItemId, 1);

    \tconst auto startDust = player->getForgeDusts();
    \tconst auto startBalance = player->getBankBalance();
    \tconst auto startChest = countItem(*player, ITEM_EXALTATION_CHEST, 0);
    \tconst auto startFirst = countItem(*player, fixture.firstForgeItemId, 1);
    \tconst auto startSecond = countItem(*player, fixture.secondForgeItemId, 1);
    \tconst auto startHistory = player->forgeHistory().get().size();

    \tplayer->forgeFuseItems(ForgeAction_t::FUSION, fixture.firstForgeItemId, 1, fixture.secondForgeItemId, true, false, true, 0, 0);

    \tEXPECT_EQ(startDust, player->getForgeDusts());
    \tEXPECT_EQ(startBalance, player->getBankBalance());
    \tEXPECT_EQ(startChest, countItem(*player, ITEM_EXALTATION_CHEST, 0));
    \tEXPECT_EQ(startFirst, countItem(*player, fixture.firstForgeItemId, 1));
    \tEXPECT_EQ(startSecond, countItem(*player, fixture.secondForgeItemId, 1));
    \tEXPECT_EQ(startHistory, player->forgeHistory().get().size());
    }

    TEST_F(ForgeIntegrationTest, ForgeConvergenceFusionRejectsSameItemIdBeforeMutating) {
    \tensureBackpack();
    \tconst auto &fixture = testState();
    \tauto &itemType = Item::items.getItemType(fixture.firstForgeItemId);
    \tconst auto originalClassification = itemType.upgradeClassification;
    \tconst auto originalSlot = itemType.slotPosition;
    \titemType.upgradeClassification = 4;
    \titemType.slotPosition = SLOTP_HAND;

    \tsetPlayerResources(1000, 1000000);
    \taddPlayerItemBackpack(fixture.firstForgeItemId, 1, 2);
    \tconst auto startDust = player->getForgeDusts();
    \tconst auto startBalance = player->getBankBalance();
    \tconst auto startChest = countItem(*player, ITEM_EXALTATION_CHEST, 0);
    \tconst auto startItems = countItem(*player, fixture.firstForgeItemId, 1);
    \tconst auto startHistory = player->forgeHistory().get().size();

    \tplayer->forgeFuseItems(ForgeAction_t::FUSION, fixture.firstForgeItemId, 1, fixture.firstForgeItemId, true, false, true, 0, 0);

    \titemType.upgradeClassification = originalClassification;
    \titemType.slotPosition = originalSlot;
    \tEXPECT_EQ(startDust, player->getForgeDusts());
    \tEXPECT_EQ(startBalance, player->getBankBalance());
    \tEXPECT_EQ(startChest, countItem(*player, ITEM_EXALTATION_CHEST, 0));
    \tEXPECT_EQ(startItems, countItem(*player, fixture.firstForgeItemId, 1));
    \tEXPECT_EQ(startHistory, player->forgeHistory().get().size());
    }

    TEST_F(ForgeIntegrationTest, ForgeConvergenceFusionRejectsDifferentSlotsBeforeMutating) {
    \tensureBackpack();
    \tconst auto &fixture = testState();
    \tauto &firstType = Item::items.getItemType(fixture.firstForgeItemId);
    \tauto &secondType = Item::items.getItemType(fixture.secondForgeItemId);
    \tconst auto originalFirstClassification = firstType.upgradeClassification;
    \tconst auto originalSecondClassification = secondType.upgradeClassification;
    \tconst auto originalFirstSlot = firstType.slotPosition;
    \tconst auto originalSecondSlot = secondType.slotPosition;
    \tfirstType.upgradeClassification = 4;
    \tsecondType.upgradeClassification = 4;
    \tfirstType.slotPosition = SLOTP_HAND;
    \tsecondType.slotPosition = SLOTP_ARMOR;

    \tsetPlayerResources(1000, 1000000);
    \taddPlayerItemBackpack(fixture.firstForgeItemId, 1);
    \taddPlayerItemBackpack(fixture.secondForgeItemId, 1);
    \tconst auto startDust = player->getForgeDusts();
    \tconst auto startBalance = player->getBankBalance();
    \tconst auto startChest = countItem(*player, ITEM_EXALTATION_CHEST, 0);
    \tconst auto startFirst = countItem(*player, fixture.firstForgeItemId, 1);
    \tconst auto startSecond = countItem(*player, fixture.secondForgeItemId, 1);
    \tconst auto startHistory = player->forgeHistory().get().size();

    \tplayer->forgeFuseItems(ForgeAction_t::FUSION, fixture.firstForgeItemId, 1, fixture.secondForgeItemId, true, false, true, 0, 0);

    \tfirstType.upgradeClassification = originalFirstClassification;
    \tsecondType.upgradeClassification = originalSecondClassification;
    \tfirstType.slotPosition = originalFirstSlot;
    \tsecondType.slotPosition = originalSecondSlot;
    \tEXPECT_EQ(startDust, player->getForgeDusts());
    \tEXPECT_EQ(startBalance, player->getBankBalance());
    \tEXPECT_EQ(startChest, countItem(*player, ITEM_EXALTATION_CHEST, 0));
    \tEXPECT_EQ(startFirst, countItem(*player, fixture.firstForgeItemId, 1));
    \tEXPECT_EQ(startSecond, countItem(*player, fixture.secondForgeItemId, 1));
    \tEXPECT_EQ(startHistory, player->forgeHistory().get().size());
    }

    TEST_F(ForgeIntegrationTest, ForgeConvergenceTransferRejectsNonClassFourBeforeMutating) {
    \tensureBackpack();
    \tconst auto &fixture = testState();
    \tASSERT_NE(4, fixture.classificationId);
    \tsetPlayerResources(1000, 1000000);
    \taddPlayerItemBackpack(fixture.donorItemId, 1);
    \taddPlayerItemBackpack(fixture.receiveItemId, 0);
    \tconst auto &forgeCore = Item::CreateItem(ITEM_FORGE_CORE, 1);
    \tASSERT_NE(nullptr, forgeCore);
    \tASSERT_EQ(RETURNVALUE_NOERROR, g_game().internalPlayerAddItem(player, forgeCore, false, CONST_SLOT_BACKPACK));

    \tconst auto startDust = player->getForgeDusts();
    \tconst auto startBalance = player->getBankBalance();
    \tconst auto startChest = countItem(*player, ITEM_EXALTATION_CHEST, 0);
    \tconst auto startDonor = countItem(*player, fixture.donorItemId, 1);
    \tconst auto startReceive = countItem(*player, fixture.receiveItemId, 0);
    \tconst auto startCore = countItem(*player, ITEM_FORGE_CORE, 0);
    \tconst auto startHistory = player->forgeHistory().get().size();

    \tplayer->forgeTransferItemTier(ForgeAction_t::TRANSFER, fixture.donorItemId, 1, fixture.receiveItemId, true);

    \tEXPECT_EQ(startDust, player->getForgeDusts());
    \tEXPECT_EQ(startBalance, player->getBankBalance());
    \tEXPECT_EQ(startChest, countItem(*player, ITEM_EXALTATION_CHEST, 0));
    \tEXPECT_EQ(startDonor, countItem(*player, fixture.donorItemId, 1));
    \tEXPECT_EQ(startReceive, countItem(*player, fixture.receiveItemId, 0));
    \tEXPECT_EQ(startCore, countItem(*player, ITEM_FORGE_CORE, 0));
    \tEXPECT_EQ(startHistory, player->forgeHistory().get().size());
    }
    """
)
integration_path = Path("tests/integration/game/forge_it.cpp")
integration_path.write_text(
    integration_path.read_text(encoding="utf-8").rstrip()
    + integration_append
    + "\n",
    encoding="utf-8",
)

print("Applied bounded Forge server-authority patch.")
