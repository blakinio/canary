#!/usr/bin/env python3
"""Apply the bounded F-020/F-021 Forge transaction-safety patch."""

from pathlib import Path


def marked(text: str) -> str:
    lines = text.strip("\n").splitlines()
    result: list[str] = []
    for line in lines:
        if not line.startswith("|"):
            raise RuntimeError(f"marked line missing prefix: {line!r}")
        result.append(line[1:])
    return "\n".join(result) + "\n"


def replace_once(path: str, old: str, new: str) -> None:
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one anchor, found {count}: {old!r}")
    file_path.write_text(text.replace(old, new), encoding="utf-8")


def replace_between(path: str, start: str, end: str, replacement: str) -> None:
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8")
    if text.count(start) != 1 or text.count(end) != 1:
        raise RuntimeError(
            f"{path}: expected unique boundaries, got start={text.count(start)} end={text.count(end)}"
        )
    start_index = text.index(start)
    end_index = text.index(end, start_index)
    file_path.write_text(
        text[:start_index] + replacement.rstrip() + "\n\n" + text[end_index:],
        encoding="utf-8",
    )


player = "src/creatures/players/player.cpp"
replace_once(
    player,
    '#include "game/functions/forge_fusion_policy.hpp"\n#include "game/functions/forge_transfer_policy.hpp"\n',
    '#include "game/functions/forge_fusion_policy.hpp"\n#include "game/functions/forge_transaction.hpp"\n#include "game/functions/forge_transfer_policy.hpp"\n',
)

helpers_and_fusion = marked(
    r'''
|namespace {
|	struct ForgeItemSnapshot {
|		std::shared_ptr<Item> item;
|		std::shared_ptr<Cylinder> parent;
|		int32_t index = INDEX_WHEREEVER;
|	};
|
|	ForgeItemSnapshot captureForgeItem(const std::shared_ptr<Item> &item) {
|		ForgeItemSnapshot snapshot;
|		snapshot.item = item;
|		if (!item) {
|			return snapshot;
|		}
|
|		snapshot.parent = item->getParent();
|		if (snapshot.parent) {
|			snapshot.index = snapshot.parent->getThingIndex(item);
|		}
|		return snapshot;
|	}
|
|	void restoreForgeItem(const ForgeItemSnapshot &snapshot, const std::string &playerName) {
|		if (!snapshot.item || !snapshot.parent) {
|			g_logger().error("[ForgeTransaction] Cannot restore an item for player {} because its snapshot is incomplete", playerName);
|			return;
|		}
|
|		if (snapshot.parent->getThingIndex(snapshot.item) >= 0) {
|			return;
|		}
|
|		const auto returnValue = g_game().internalAddItem(snapshot.parent, snapshot.item, snapshot.index, FLAG_NOLIMIT);
|		if (returnValue != RETURNVALUE_NOERROR) {
|			g_logger().error("[ForgeTransaction] Failed to restore item {} for player {}: {}", snapshot.item->getID(), playerName, getReturnMessage(returnValue));
|		}
|	}
|
|	uint32_t getForgeStackableCount(Player &player, uint16_t itemId) {
|		const auto &[sliverCount, coreCount] = player.getForgeSliversAndCores();
|		if (itemId == ITEM_FORGE_SLIVER) {
|			return sliverCount;
|		}
|		if (itemId == ITEM_FORGE_CORE) {
|			return coreCount;
|		}
|		return player.getItemTypeCount(itemId);
|	}
|
|	void restoreForgeStackable(const std::shared_ptr<Player> &player, uint16_t itemId, uint32_t expectedCount) {
|		const uint32_t currentCount = getForgeStackableCount(*player, itemId);
|		if (currentCount == expectedCount) {
|			return;
|		}
|
|		if (currentCount < expectedCount) {
|			const auto &replacement = Item::CreateItem(itemId, expectedCount - currentCount);
|			if (!replacement || g_game().internalAddItem(player, replacement, INDEX_WHEREEVER, FLAG_NOLIMIT) != RETURNVALUE_NOERROR) {
|				g_logger().error("[ForgeTransaction] Failed to restore {} units of item {} for player {}", expectedCount - currentCount, itemId, player->getName());
|			}
|			return;
|		}
|
|		if (!player->removeItemCountById(itemId, currentCount - expectedCount)) {
|			g_logger().error("[ForgeTransaction] Failed to remove {} excess units of item {} for player {}", currentCount - expectedCount, itemId, player->getName());
|		}
|	}
|
|	void restoreForgeMoney(const std::shared_ptr<Player> &player, uint64_t expectedInventoryMoney, uint64_t expectedBankBalance) {
|		const uint64_t currentInventoryMoney = player->getMoney();
|		if (currentInventoryMoney < expectedInventoryMoney) {
|			const auto [remainder, returnValue] = g_game().addMoney(player, expectedInventoryMoney - currentInventoryMoney, FLAG_NOLIMIT);
|			if (returnValue != RETURNVALUE_NOERROR || remainder != 0) {
|				g_logger().error("[ForgeTransaction] Failed to restore inventory money for player {}", player->getName());
|			}
|		} else if (currentInventoryMoney > expectedInventoryMoney) {
|			if (!g_game().removeMoney(player, currentInventoryMoney - expectedInventoryMoney, FLAG_NOLIMIT, false)) {
|				g_logger().error("[ForgeTransaction] Failed to remove excess inventory money for player {}", player->getName());
|			}
|		}
|
|		player->setBankBalance(expectedBankBalance);
|	}
|
|	void removePreparedForgeChest(const std::shared_ptr<Container> &container, const std::string &playerName) {
|		if (!container || !container->getParent()) {
|			return;
|		}
|
|		const auto returnValue = g_game().internalRemoveItem(container, 1, false, 0, true);
|		if (returnValue != RETURNVALUE_NOERROR) {
|			g_logger().error("[ForgeTransaction] Failed to roll back Exaltation Chest for player {}", playerName);
|		}
|	}
|} // namespace
|
|// Forge system
|void Player::forgeFuseItems(ForgeAction_t actionType, uint16_t firstItemId, uint8_t tier, uint16_t secondItemId, bool success, bool reduceTierLoss, bool convergence, uint8_t bonus, uint8_t coreCount) {
|	if (getFreeBackpackSlots() == 0) {
|		sendCancelMessage(RETURNVALUE_NOTENOUGHROOM);
|		return;
|	}
|
|	ForgeHistory history;
|	history.actionType = actionType;
|	history.tier = tier;
|	history.success = success;
|	history.tierLoss = reduceTierLoss;
|
|	const auto &firstForgingItem = getForgeItemFromId(firstItemId, tier);
|	if (!firstForgingItem) {
|		g_logger().error("[Log 1] Player with name {} failed to fuse item with id {}", getName(), firstItemId);
|		sendForgeError(RETURNVALUE_CONTACTADMINISTRATOR);
|		return;
|	}
|	const auto &secondForgingItem = getForgeItemFromId(secondItemId, tier, firstForgingItem);
|	if (!secondForgingItem) {
|		g_logger().error("[Log 2] Player with name {} failed to fuse item with id {}", getName(), secondItemId);
|		sendForgeError(RETURNVALUE_CONTACTADMINISTRATOR);
|		return;
|	}
|
|	auto normalizeForgeSlot = [](uint32_t slotPosition) {
|		return (slotPosition & SLOTP_TWO_HAND) != 0 ? static_cast<uint32_t>(SLOTP_HAND) : slotPosition;
|	};
|	const bool sameForgeSlot = normalizeForgeSlot(firstForgingItem->getSlotPosition()) == normalizeForgeSlot(secondForgingItem->getSlotPosition());
|	if (!ForgeFusionPolicy::isValid(
|			firstItemId,
|			secondItemId,
|			firstForgingItem->getClassification(),
|			secondForgingItem->getClassification(),
|			sameForgeSlot,
|			convergence
|		)) {
|		g_logger().warn(
|			"[{}] Rejected invalid fusion for player {}: first item {}, second item {}, first class {}, second class {}, tier {}, same slot {}, convergence {}",
|			__FUNCTION__,
|			getName(),
|			firstItemId,
|			secondItemId,
|			firstForgingItem->getClassification(),
|			secondForgingItem->getClassification(),
|			tier,
|			sameForgeSlot,
|			convergence
|		);
|		sendForgeError(RETURNVALUE_NOTPOSSIBLE);
|		return;
|	}
|
|	const auto player = static_self_cast<Player>();
|	const uint64_t dustCost = static_cast<uint64_t>(g_configManager().getNumber(convergence ? FORGE_CONVERGENCE_FUSION_DUST_COST : FORGE_FUSION_DUST_COST));
|	const bool chargeDust = convergence || !success || bonus != 1;
|	const bool chargeCores = !convergence && coreCount != 0 && (!success || bonus != 2);
|	const bool chargeGold = convergence || !success || bonus != 3;
|
|	if (chargeDust && getForgeDusts() < dustCost) {
|		g_logger().error("[{}] Not enough dust to forge for player {}", __FUNCTION__, getName());
|		sendForgeError(RETURNVALUE_CONTACTADMINISTRATOR);
|		return;
|	}
|	if (chargeCores && !hasItemCountById(ITEM_FORGE_CORE, coreCount, true)) {
|		g_logger().error("[{}] Not enough forge cores for player {}", __FUNCTION__, getName());
|		sendForgeError(RETURNVALUE_CONTACTADMINISTRATOR);
|		return;
|	}
|
|	uint64_t goldCost = 0;
|	if (chargeGold) {
|		bool hasMatchingClassification = false;
|		for (const auto* itemClassification : g_game().getItemsClassifications()) {
|			if (!itemClassification || itemClassification->id != firstForgingItem->getClassification()) {
|				continue;
|			}
|
|			hasMatchingClassification = true;
|			if (!itemClassification->tiers.contains(tier + 1)) {
|				g_logger().error("[{}] Tier {} not found in classification {} for player {}", __FUNCTION__, tier + 1, itemClassification->id, getName());
|				sendForgeError(RETURNVALUE_CONTACTADMINISTRATOR);
|				return;
|			}
|			const auto &tierPrices = itemClassification->tiers.at(tier + 1);
|			goldCost = convergence ? tierPrices.convergenceFusionPrice : tierPrices.regularPrice;
|			break;
|		}
|		if (!hasMatchingClassification) {
|			g_logger().error("[{}] Failed to find classification {} for player {}", __FUNCTION__, firstForgingItem->getClassification(), getName());
|			sendForgeError(RETURNVALUE_CONTACTADMINISTRATOR);
|			return;
|		}
|		if (getMoney() + getBankBalance() < goldCost) {
|			g_logger().error("[{}] Not enough money to forge for player {}", __FUNCTION__, getName());
|			sendForgeError(RETURNVALUE_CONTACTADMINISTRATOR);
|			return;
|		}
|	}
|
|	uint8_t resultBonus = bonus;
|	uint8_t firstResultTier = tier;
|	uint8_t secondResultTier = tier;
|	bool keepSecondOutput = false;
|	if (convergence) {
|		firstResultTier = tier + 1;
|	} else if (success) {
|		firstResultTier = tier + 1;
|		if (bonus == 4) {
|			keepSecondOutput = true;
|			secondResultTier = tier > 0 ? tier - 1 : tier;
|		} else if (bonus == 5 || bonus == 8) {
|			keepSecondOutput = true;
|		} else if (bonus == 6) {
|			keepSecondOutput = true;
|			secondResultTier = tier + 1;
|		} else if (bonus == 7 && tier + 2 <= firstForgingItem->getClassification()) {
|			firstResultTier = tier + 2;
|		}
|	} else {
|		const bool isTierLost = uniform_random(1, 100) <= (reduceTierLoss ? g_configManager().getNumber(FORGE_TIER_LOSS_REDUCTION) : 100);
|		resultBonus = isTierLost ? 0 : 8;
|		if (isTierLost) {
|			if (tier >= 1) {
|				keepSecondOutput = true;
|				secondResultTier = tier - 1;
|			}
|		} else {
|			keepSecondOutput = true;
|		}
|	}
|
|	const auto &exaltationChest = Item::CreateItem(ITEM_EXALTATION_CHEST, 1);
|	const auto &exaltationContainer = exaltationChest ? exaltationChest->getContainer() : nullptr;
|	if (!exaltationContainer) {
|		g_logger().error("[{}] Failed to prepare Exaltation Chest for player {}", __FUNCTION__, getName());
|		sendForgeError(RETURNVALUE_CONTACTADMINISTRATOR);
|		return;
|	}
|
|	const auto &firstForgedItem = Item::CreateItem(firstItemId, 1);
|	if (!firstForgedItem) {
|		g_logger().error("[{}] Failed to prepare result item {} for player {}", __FUNCTION__, firstItemId, getName());
|		sendForgeError(RETURNVALUE_CONTACTADMINISTRATOR);
|		return;
|	}
|	firstForgedItem->setTier(firstResultTier);
|	if (g_game().internalAddItem(exaltationContainer, firstForgedItem, INDEX_WHEREEVER, FLAG_NOLIMIT) != RETURNVALUE_NOERROR) {
|		g_logger().error("[{}] Failed to stage result item {} for player {}", __FUNCTION__, firstItemId, getName());
|		sendForgeError(RETURNVALUE_CONTACTADMINISTRATOR);
|		return;
|	}
|
|	if (keepSecondOutput) {
|		const auto &secondForgedItem = Item::CreateItem(secondItemId, 1);
|		if (!secondForgedItem) {
|			g_logger().error("[{}] Failed to prepare second result item {} for player {}", __FUNCTION__, secondItemId, getName());
|			sendForgeError(RETURNVALUE_CONTACTADMINISTRATOR);
|			return;
|		}
|		secondForgedItem->setTier(secondResultTier);
|		if (g_game().internalAddItem(exaltationContainer, secondForgedItem, INDEX_WHEREEVER, FLAG_NOLIMIT) != RETURNVALUE_NOERROR) {
|			g_logger().error("[{}] Failed to stage second result item {} for player {}", __FUNCTION__, secondItemId, getName());
|			sendForgeError(RETURNVALUE_CONTACTADMINISTRATOR);
|			return;
|		}
|	}
|
|	if (g_game().internalAddItem(player, exaltationContainer, INDEX_WHEREEVER, 0, true) != RETURNVALUE_NOERROR
|	    || g_game().internalRemoveItem(firstForgingItem, 1, true) != RETURNVALUE_NOERROR
|	    || g_game().internalRemoveItem(secondForgingItem, 1, true) != RETURNVALUE_NOERROR) {
|		g_logger().error("[{}] Forge inventory preflight failed for player {}", __FUNCTION__, getName());
|		sendForgeError(RETURNVALUE_CONTACTADMINISTRATOR);
|		return;
|	}
|
|	const auto firstSnapshot = captureForgeItem(firstForgingItem);
|	const auto secondSnapshot = captureForgeItem(secondForgingItem);
|	const auto [sliversBefore, coresBefore] = getForgeSliversAndCores();
|	const uint64_t inventoryMoneyBefore = getMoney();
|	const uint64_t bankBalanceBefore = getBankBalance();
|
|	ForgeTransaction transaction;
|	transaction.stage(
|		[firstForgingItem] { return g_game().internalRemoveItem(firstForgingItem, 1) == RETURNVALUE_NOERROR; },
|		[firstSnapshot, playerName = getName()] { restoreForgeItem(firstSnapshot, playerName); }
|	);
|	transaction.stage(
|		[secondForgingItem] { return g_game().internalRemoveItem(secondForgingItem, 1) == RETURNVALUE_NOERROR; },
|		[secondSnapshot, playerName = getName()] { restoreForgeItem(secondSnapshot, playerName); }
|	);
|	if (chargeCores) {
|		transaction.stage(
|			[player, coreCount] { return player->removeItemCountById(ITEM_FORGE_CORE, coreCount); },
|			[player, coresBefore] { restoreForgeStackable(player, ITEM_FORGE_CORE, coresBefore); }
|		);
|	}
|	if (chargeGold) {
|		transaction.stage(
|			[player, goldCost] { return g_game().removeMoney(player, goldCost, 0, true); },
|			[player, inventoryMoneyBefore, bankBalanceBefore] { restoreForgeMoney(player, inventoryMoneyBefore, bankBalanceBefore); }
|		);
|	}
|	transaction.stage(
|		[player, exaltationContainer] { return g_game().internalAddItem(player, exaltationContainer, INDEX_WHEREEVER) == RETURNVALUE_NOERROR; },
|		[exaltationContainer, playerName = getName()] { removePreparedForgeChest(exaltationContainer, playerName); }
|	);
|
|	if (!transaction.commit()) {
|		g_logger().error("[{}] Forge transaction rolled back for player {}", __FUNCTION__, getName());
|		sendForgeError(RETURNVALUE_CONTACTADMINISTRATOR);
|		return;
|	}
|
|	if (chargeDust) {
|		setForgeDusts(getForgeDusts() - dustCost);
|		history.dustCost = dustCost;
|	}
|	if (chargeCores) {
|		history.coresCost = coreCount;
|	}
|	if (chargeGold) {
|		history.cost = goldCost;
|		g_metrics().addCounter("balance_decrease", goldCost, { { "player", getName() }, { "context", convergence ? "forge_convergence_fuse" : "forge_fuse" } });
|	}
|
|	history.firstItemId = firstItemId;
|	history.secondItemId = secondItemId;
|	history.firstItemName = firstForgingItem->getName();
|	history.secondItemName = secondForgingItem->getName();
|	history.bonus = resultBonus;
|	history.createdAt = getTimeMsNow();
|	history.convergence = convergence;
|	registerForgeHistoryDescription(history);
|
|	sendForgeResult(actionType, firstItemId, tier, secondItemId, tier + 1, success, resultBonus, coreCount, convergence);
|}
'''
)
replace_between(
    player,
    "// Forge system\nvoid Player::forgeFuseItems(",
    "void Player::forgeTransferItemTier(",
    helpers_and_fusion,
)

transfer = marked(
    r'''
|void Player::forgeTransferItemTier(ForgeAction_t actionType, uint16_t donorItemId, uint8_t tier, uint16_t receiveItemId, bool convergence) {
|	if (getFreeBackpackSlots() == 0) {
|		sendCancelMessage(RETURNVALUE_NOTENOUGHROOM);
|		return;
|	}
|
|	ForgeHistory history;
|	history.actionType = actionType;
|	history.tier = tier;
|	history.success = true;
|
|	const auto &donorItem = getForgeItemFromId(donorItemId, tier);
|	if (!donorItem) {
|		g_logger().error("[Log 1] Player with name {} failed to transfer item with id {}", getName(), donorItemId);
|		sendForgeError(RETURNVALUE_CONTACTADMINISTRATOR);
|		return;
|	}
|	const auto &receiveItem = getForgeItemFromId(receiveItemId, 0, donorItem);
|	if (!receiveItem) {
|		g_logger().error("[Log 2] Player with name {} failed to transfer item with id {}", getName(), receiveItemId);
|		sendForgeError(RETURNVALUE_CONTACTADMINISTRATOR);
|		return;
|	}
|
|	const uint8_t donorClassification = donorItem->getClassification();
|	const uint8_t receiveClassification = receiveItem->getClassification();
|	if (!ForgeTransferPolicy::isValidTransfer(donorClassification, receiveClassification, donorItem->getTier(), convergence)) {
|		g_logger().warn("[{}] Rejected invalid transfer for player {}: donor class {}, receiver class {}, donor tier {}, convergence {}", __FUNCTION__, getName(), donorClassification, receiveClassification, donorItem->getTier(), convergence);
|		sendForgeError(RETURNVALUE_NOTPOSSIBLE);
|		return;
|	}
|
|	const uint64_t dustCost = static_cast<uint64_t>(g_configManager().getNumber(convergence ? FORGE_CONVERGENCE_TRANSFER_DUST_COST : FORGE_TRANSFER_DUST_COST));
|	if (getForgeDusts() < dustCost) {
|		g_logger().error("[{}] Insufficient transfer dust for player with name {}", __FUNCTION__, getName());
|		sendForgeError(RETURNVALUE_CONTACTADMINISTRATOR);
|		return;
|	}
|
|	uint8_t coresAmount = 0;
|	uint64_t goldCost = 0;
|	bool hasMatchingClassification = false;
|	const uint8_t resourceTier = ForgeTransferPolicy::resourceTier(donorItem->getTier());
|	for (const auto* itemClassification : g_game().getItemsClassifications()) {
|		if (!itemClassification || itemClassification->id != donorClassification) {
|			continue;
|		}
|		hasMatchingClassification = true;
|		if (!itemClassification->tiers.contains(resourceTier)) {
|			g_logger().error("[{}] Failed to find tier {} for item {} in classification {}", __FUNCTION__, resourceTier, donorClassification, itemClassification->id);
|			sendForgeError(RETURNVALUE_CONTACTADMINISTRATOR);
|			return;
|		}
|		const auto &tierPrices = itemClassification->tiers.at(resourceTier);
|		goldCost = convergence ? tierPrices.convergenceTransferPrice : tierPrices.regularPrice;
|		coresAmount = tierPrices.corePrice;
|		break;
|	}
|	if (!hasMatchingClassification || !hasItemCountById(ITEM_FORGE_CORE, coresAmount, true) || getMoney() + getBankBalance() < goldCost) {
|		g_logger().error("[{}] Transfer resource preflight failed for player {}", __FUNCTION__, getName());
|		sendForgeError(RETURNVALUE_CONTACTADMINISTRATOR);
|		return;
|	}
|
|	const uint8_t resultTier = ForgeTransferPolicy::resultTier(donorItem->getTier(), convergence);
|	const auto &exaltationChest = Item::CreateItem(ITEM_EXALTATION_CHEST, 1);
|	const auto &exaltationContainer = exaltationChest ? exaltationChest->getContainer() : nullptr;
|	const auto &newReceiveItem = Item::CreateItem(receiveItemId, 1);
|	if (!exaltationContainer || !newReceiveItem) {
|		g_logger().error("[{}] Failed to prepare Transfer output for player {}", __FUNCTION__, getName());
|		sendForgeError(RETURNVALUE_CONTACTADMINISTRATOR);
|		return;
|	}
|	newReceiveItem->setTier(resultTier);
|	if (g_game().internalAddItem(exaltationContainer, newReceiveItem, INDEX_WHEREEVER, FLAG_NOLIMIT) != RETURNVALUE_NOERROR) {
|		g_logger().error("[{}] Failed to stage Transfer output for player {}", __FUNCTION__, getName());
|		sendForgeError(RETURNVALUE_CONTACTADMINISTRATOR);
|		return;
|	}
|
|	const auto player = static_self_cast<Player>();
|	if (g_game().internalAddItem(player, exaltationContainer, INDEX_WHEREEVER, 0, true) != RETURNVALUE_NOERROR
|	    || g_game().internalRemoveItem(donorItem, 1, true) != RETURNVALUE_NOERROR
|	    || g_game().internalRemoveItem(receiveItem, 1, true) != RETURNVALUE_NOERROR) {
|		g_logger().error("[{}] Transfer inventory preflight failed for player {}", __FUNCTION__, getName());
|		sendForgeError(RETURNVALUE_CONTACTADMINISTRATOR);
|		return;
|	}
|
|	const auto donorSnapshot = captureForgeItem(donorItem);
|	const auto receiveSnapshot = captureForgeItem(receiveItem);
|	const auto [sliversBefore, coresBefore] = getForgeSliversAndCores();
|	const uint64_t inventoryMoneyBefore = getMoney();
|	const uint64_t bankBalanceBefore = getBankBalance();
|
|	ForgeTransaction transaction;
|	transaction.stage(
|		[donorItem] { return g_game().internalRemoveItem(donorItem, 1) == RETURNVALUE_NOERROR; },
|		[donorSnapshot, playerName = getName()] { restoreForgeItem(donorSnapshot, playerName); }
|	);
|	transaction.stage(
|		[receiveItem] { return g_game().internalRemoveItem(receiveItem, 1) == RETURNVALUE_NOERROR; },
|		[receiveSnapshot, playerName = getName()] { restoreForgeItem(receiveSnapshot, playerName); }
|	);
|	if (coresAmount != 0) {
|		transaction.stage(
|			[player, coresAmount] { return player->removeItemCountById(ITEM_FORGE_CORE, coresAmount); },
|			[player, coresBefore] { restoreForgeStackable(player, ITEM_FORGE_CORE, coresBefore); }
|		);
|	}
|	if (goldCost != 0) {
|		transaction.stage(
|			[player, goldCost] { return g_game().removeMoney(player, goldCost, 0, true); },
|			[player, inventoryMoneyBefore, bankBalanceBefore] { restoreForgeMoney(player, inventoryMoneyBefore, bankBalanceBefore); }
|		);
|	}
|	transaction.stage(
|		[player, exaltationContainer] { return g_game().internalAddItem(player, exaltationContainer, INDEX_WHEREEVER) == RETURNVALUE_NOERROR; },
|		[exaltationContainer, playerName = getName()] { removePreparedForgeChest(exaltationContainer, playerName); }
|	);
|
|	if (!transaction.commit()) {
|		g_logger().error("[{}] Transfer transaction rolled back for player {}", __FUNCTION__, getName());
|		sendForgeError(RETURNVALUE_CONTACTADMINISTRATOR);
|		return;
|	}
|
|	setForgeDusts(getForgeDusts() - dustCost);
|	history.cost = goldCost;
|	history.coresCost = coresAmount;
|	history.dustCost = dustCost;
|	if (goldCost != 0) {
|		g_metrics().addCounter("balance_decrease", goldCost, { { "player", getName() }, { "context", "forge_transfer" } });
|	}
|
|	history.firstItemId = donorItemId;
|	history.secondItemId = receiveItemId;
|	history.firstItemName = donorItem->getName();
|	history.secondItemName = newReceiveItem->getName();
|	history.createdAt = getTimeMsNow();
|	history.convergence = convergence;
|	registerForgeHistoryDescription(history);
|
|	sendForgeResult(actionType, donorItemId, tier, receiveItemId, resultTier, true, 0, 0, convergence);
|}
'''
)
replace_between(
    player,
    "void Player::forgeTransferItemTier(",
    "void Player::forgeResourceConversion(",
    transfer,
)

conversion = marked(
    r'''
|void Player::forgeResourceConversion(ForgeAction_t actionType) {
|	ForgeHistory history;
|	history.actionType = actionType;
|	history.success = true;
|
|	ReturnValue returnValue = RETURNVALUE_NOERROR;
|	if (actionType == ForgeAction_t::DUSTTOSLIVERS) {
|		const auto dusts = getForgeDusts();
|		const auto cost = static_cast<uint16_t>(g_configManager().getNumber(FORGE_COST_ONE_SLIVER) * g_configManager().getNumber(FORGE_SLIVER_AMOUNT));
|		if (cost > dusts) {
|			g_logger().error("[{}] Not enough dust", __FUNCTION__);
|			sendForgeError(RETURNVALUE_CONTACTADMINISTRATOR);
|			return;
|		}
|
|		const auto itemCount = static_cast<uint16_t>(g_configManager().getNumber(FORGE_SLIVER_AMOUNT));
|		const auto &item = Item::CreateItem(ITEM_FORGE_SLIVER, itemCount);
|		if (!item) {
|			g_logger().error("[{}] Failed to create {} slivers for player {}", __FUNCTION__, itemCount, getName());
|			sendForgeError(RETURNVALUE_CONTACTADMINISTRATOR);
|			return;
|		}
|		returnValue = g_game().internalPlayerAddItem(static_self_cast<Player>(), item);
|		if (returnValue != RETURNVALUE_NOERROR) {
|			g_logger().error("Failed to add {} slivers to player with name {}", itemCount, getName());
|			sendCancelMessage(getReturnMessage(returnValue));
|			sendForgeError(RETURNVALUE_CONTACTADMINISTRATOR);
|			return;
|		}
|		history.cost = cost;
|		history.gained = 3;
|		setForgeDusts(dusts - cost);
|	} else if (actionType == ForgeAction_t::SLIVERSTOCORES) {
|		const auto player = static_self_cast<Player>();
|		const auto [sliverCount, coreCount] = getForgeSliversAndCores();
|		const auto cost = static_cast<uint16_t>(g_configManager().getNumber(FORGE_CORE_COST));
|		if (cost > sliverCount) {
|			g_logger().error("[{}] Not enough sliver", __FUNCTION__);
|			sendForgeError(RETURNVALUE_CONTACTADMINISTRATOR);
|			return;
|		}
|
|		const auto &core = Item::CreateItem(ITEM_FORGE_CORE, 1);
|		if (!core) {
|			g_logger().error("[{}] Failed to create Forge Core for player {}", __FUNCTION__, getName());
|			sendForgeError(RETURNVALUE_CONTACTADMINISTRATOR);
|			return;
|		}
|
|		ForgeTransaction transaction;
|		transaction.stage(
|			[player, cost] { return player->removeItemCountById(ITEM_FORGE_SLIVER, cost); },
|			[player, sliverCount, coreCount] {
|				restoreForgeStackable(player, ITEM_FORGE_SLIVER, sliverCount);
|				restoreForgeStackable(player, ITEM_FORGE_CORE, coreCount);
|			}
|		);
|		transaction.stage(
|			[player, core] { return g_game().internalPlayerAddItem(player, core) == RETURNVALUE_NOERROR; },
|			[player, sliverCount, coreCount] {
|				restoreForgeStackable(player, ITEM_FORGE_SLIVER, sliverCount);
|				restoreForgeStackable(player, ITEM_FORGE_CORE, coreCount);
|			}
|		);
|
|		if (!transaction.commit()) {
|			g_logger().error("[{}] Sliver-to-Core transaction rolled back for player {}", __FUNCTION__, getName());
|			sendForgeError(RETURNVALUE_CONTACTADMINISTRATOR);
|			return;
|		}
|
|		history.cost = cost;
|		history.gained = 1;
|	} else {
|		const auto dustLevel = getForgeDustLevel();
|		if (dustLevel >= g_configManager().getNumber(FORGE_MAX_DUST)) {
|			g_logger().error("[{}] Maximum level reached", __FUNCTION__);
|			sendForgeError(RETURNVALUE_CONTACTADMINISTRATOR);
|			return;
|		}
|
|		const auto upgradeCost = dustLevel - 75;
|		if (const auto dusts = getForgeDusts(); upgradeCost > dusts) {
|			g_logger().error("[{}] Not enough dust", __FUNCTION__);
|			sendForgeError(RETURNVALUE_CONTACTADMINISTRATOR);
|			return;
|		}
|
|		history.cost = upgradeCost;
|		history.gained = dustLevel;
|		removeForgeDusts(upgradeCost);
|		addForgeDustLevel(1);
|	}
|
|	history.createdAt = getTimeMsNow();
|	registerForgeHistoryDescription(history);
|	sendForgingData();
|}
'''
)
replace_between(
    player,
    "void Player::forgeResourceConversion(",
    "void Player::forgeHistory(",
    conversion,
)

integration_path = Path("tests/integration/game/forge_it.cpp")
integration = integration_path.read_text(encoding="utf-8").rstrip()
new_test = marked(
    r'''
|TEST_F(ForgeIntegrationTest, ForgeSliverToCoreConversionCommitsBothResourceSides) {
|	ensureBackpack();
|	const auto cost = static_cast<uint16_t>(g_configManager().getNumber(FORGE_CORE_COST));
|	const auto &slivers = Item::CreateItem(ITEM_FORGE_SLIVER, cost);
|	ASSERT_NE(nullptr, slivers);
|	ASSERT_EQ(RETURNVALUE_NOERROR, g_game().internalPlayerAddItem(player, slivers, false, CONST_SLOT_BACKPACK));
|
|	const auto [sliversBefore, coresBefore] = player->getForgeSliversAndCores();
|	const auto historyBefore = player->forgeHistory().get().size();
|
|	player->forgeResourceConversion(ForgeAction_t::SLIVERSTOCORES);
|
|	const auto [sliversAfter, coresAfter] = player->getForgeSliversAndCores();
|	EXPECT_EQ(sliversBefore - cost, sliversAfter);
|	EXPECT_EQ(coresBefore + 1, coresAfter);
|	EXPECT_EQ(historyBefore + 1, player->forgeHistory().get().size());
|}
'''
)
if "ForgeSliverToCoreConversionCommitsBothResourceSides" in integration:
    raise RuntimeError("integration regression already present")
integration_path.write_text(integration + "\n\n" + new_test, encoding="utf-8")

print("Applied Forge transaction-safety implementation and integration regression.")
