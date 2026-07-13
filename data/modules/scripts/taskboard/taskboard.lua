local ClientPackets = {
	Taskboard = 0x5F,
}

local ServerPackets = {
	Taskboard = 0x5B,
}

local OutboundWindow = {
	Bounty = 0x00,
	Weekly = 0x01,
	Shop = 0x02,
}

local ClientAction = {
	Bounty = 0x00,
	Weekly = 0x01,
	BountyDifficulty = 0x02,
	BountyReroll = 0x03,
	ClaimDailyReroll = 0x04,
	BountySelect = 0x05,
	BountyClaimReward = 0x06,
	TalismanUpgrade = 0x07,
	WeeklyDelivery = 0x08,
	WeeklyDifficulty = 0x09,
	Shop = 0x0A,
	ShopBuy = 0x0B,
	UnlockPreferenceSlot = 0x0C,
	ClearPreferred = 0x0D,
	ClearUnwanted = 0x0E,
	AssignPreferred = 0x0F,
	AssignUnwanted = 0x10,
}

local OneBytePayloadActions = {
	[ClientAction.BountyDifficulty] = true,
	[ClientAction.BountySelect] = true,
	[ClientAction.TalismanUpgrade] = true,
	[ClientAction.WeeklyDelivery] = true,
	[ClientAction.WeeklyDifficulty] = true,
}

local OneU16PayloadActions = {
	[ClientAction.ShopBuy] = true,
	[ClientAction.UnlockPreferenceSlot] = true,
	[ClientAction.ClearPreferred] = true,
	[ClientAction.ClearUnwanted] = true,
}

local TwoU16PayloadActions = {
	[ClientAction.AssignPreferred] = true,
	[ClientAction.AssignUnwanted] = true,
}

local BountyResponseActions = {
	[ClientAction.Bounty] = true,
	[ClientAction.BountyDifficulty] = true,
	[ClientAction.BountyReroll] = true,
	[ClientAction.ClaimDailyReroll] = true,
	[ClientAction.BountySelect] = true,
	[ClientAction.BountyClaimReward] = true,
	[ClientAction.TalismanUpgrade] = true,
	[ClientAction.UnlockPreferenceSlot] = true,
	[ClientAction.ClearPreferred] = true,
	[ClientAction.ClearUnwanted] = true,
	[ClientAction.AssignPreferred] = true,
	[ClientAction.AssignUnwanted] = true,
}

local WeeklyResponseActions = {
	[ClientAction.Weekly] = true,
	[ClientAction.WeeklyDelivery] = true,
	[ClientAction.WeeklyDifficulty] = true,
}

local ShopResponseActions = {
	[ClientAction.Shop] = true,
	[ClientAction.ShopBuy] = true,
}

local ShopOfferType = {
	BonusPromotion = 0x04,
}

local ShopStatus = {
	Available = 0x00,
	NotEnoughPoints = 0x02,
	Bought = 0x04,
}

local BonusPromotion = {
	OfferId = 0,
	MaxPoints = 50,
	KvScope = "wheel-of-destiny",
	KvKey = "hunting-task-shop-points",
}

-- Official-client packet implementation for 15.25 Taskboard traffic.
-- Bounty and Weekly remain structurally valid empty windows. The Hunting
-- Task Shop exposes the retail Bonus Promotion offer and persists only the
-- purchased Wheel points, never the player's complete Hunting Task balance.

local function readU8(msg)
	if msg:getUnreadBytes() < 1 then
		return nil
	end

	return msg:getByte()
end

local function readU16(msg)
	if msg:getUnreadBytes() < 2 then
		return nil
	end

	return msg:getU16()
end

local function consumeU8(msg)
	return readU8(msg) ~= nil
end

local function consumeU16(msg)
	return readU16(msg) ~= nil
end

local function addEmptyBountyTalismanLine(msg)
	msg:addU16(0)
	msg:addByte(0)
	msg:addU16(0)
end

local function sendBountyWindow(player)
	local msg = NetworkMessage()
	msg:addByte(ServerPackets.Taskboard)
	msg:addByte(OutboundWindow.Bounty)
	msg:addByte(0) -- bounty task count
	msg:addByte(0) -- daily rerolls
	msg:addByte(0) -- reroll state
	msg:addByte(0) -- current difficulty
	addEmptyBountyTalismanLine(msg)
	addEmptyBountyTalismanLine(msg)
	addEmptyBountyTalismanLine(msg)
	addEmptyBountyTalismanLine(msg)
	msg:addByte(0) -- preferred/unwanted slot count
	msg:sendToPlayer(player)
end

local function sendWeeklyWindow(player)
	local msg = NetworkMessage()
	msg:addByte(ServerPackets.Taskboard)
	msg:addByte(OutboundWindow.Weekly)
	msg:addU16(0) -- any creature required amount
	msg:addU16(0) -- any creature current amount
	msg:addByte(0) -- weekly kill task count
	msg:addByte(0) -- weekly item task count
	msg:addByte(0) -- current difficulty
	msg:addU32(0) -- kill experience reward
	msg:addU32(0) -- item delivery experience reward
	msg:addByte(0) -- completed kill tasks
	msg:addByte(0) -- completed item tasks
	msg:addByte(0) -- difficulty selection available
	msg:addByte(0) -- suggested difficulty
	msg:addU32(0) -- next reset timestamp
	msg:addByte(0) -- third weekly slot unlocked
	msg:addU32(0) -- task hunting points reward
	msg:addU32(0) -- soulseals reward tail for current official clients
	msg:sendToPlayer(player)
end

local function getBonusPromotionKV(player)
	return player:kv():scoped(BonusPromotion.KvScope)
end

local function getPurchasedBonusPromotionPoints(player)
	local stored = getBonusPromotionKV(player):get(BonusPromotion.KvKey)
	local points = math.floor(tonumber(stored) or 0)
	return math.max(0, math.min(BonusPromotion.MaxPoints, points))
end

local function getBonusPromotionPointCost(pointNumber)
	if pointNumber < 1 or pointNumber > BonusPromotion.MaxPoints then
		return 0
	end

	return 100 * (1 + math.floor((pointNumber * (pointNumber - 1)) / 2))
end

local function getBonusPromotionStatus(player, purchasedPoints, nextCost)
	if purchasedPoints >= BonusPromotion.MaxPoints then
		return ShopStatus.Bought
	end
	if player:getTaskHuntingPoints() < nextCost then
		return ShopStatus.NotEnoughPoints
	end
	return ShopStatus.Available
end

local function sendShopWindow(player)
	local purchasedPoints = getPurchasedBonusPromotionPoints(player)
	local nextPoint = purchasedPoints + 1
	local nextCost = getBonusPromotionPointCost(nextPoint)

	local msg = NetworkMessage()
	msg:addByte(ServerPackets.Taskboard)
	msg:addByte(OutboundWindow.Shop)
	msg:addByte(1) -- offer count
	msg:addByte(ShopOfferType.BonusPromotion)
	msg:addU16(nextPoint) -- client derives purchased count as value - 1
	msg:addU32(nextCost)
	msg:addByte(getBonusPromotionStatus(player, purchasedPoints, nextCost))
	msg:sendToPlayer(player)
end

local function purchaseBonusPromotionPoint(player, offerId)
	if offerId ~= BonusPromotion.OfferId then
		logger.debug("[Taskboard] player='{}' requested unknown shop offer {}", player:getName(), offerId)
		return false
	end

	local purchasedPoints = getPurchasedBonusPromotionPoints(player)
	if purchasedPoints >= BonusPromotion.MaxPoints then
		return false
	end

	local cost = getBonusPromotionPointCost(purchasedPoints + 1)
	if cost <= 0 or player:getTaskHuntingPoints() < cost then
		return false
	end

	player:removeTaskHuntingPoints(cost)
	getBonusPromotionKV(player):set(BonusPromotion.KvKey, purchasedPoints + 1)
	player:setWheelHuntingTaskShopPoints(purchasedPoints + 1)
	logger.info("[Taskboard] player='{}' bought Wheel Promotion Point {} for {} Hunting Task Points", player:getName(), purchasedPoints + 1, cost)
	return true
end

local function sendWindow(player, window)
	if window == OutboundWindow.Weekly then
		sendWeeklyWindow(player)
	elseif window == OutboundWindow.Shop then
		sendShopWindow(player)
	else
		sendBountyWindow(player)
	end
end

local function readActionPayload(msg, action)
	if OneBytePayloadActions[action] then
		local value = readU8(msg)
		return value ~= nil, value
	end

	if OneU16PayloadActions[action] then
		local value = readU16(msg)
		return value ~= nil, value
	end

	if TwoU16PayloadActions[action] then
		local first = readU16(msg)
		local second = readU16(msg)
		return first ~= nil and second ~= nil, first, second
	end

	return true
end

function onRecvbyte(player, msg, byte)
	if byte ~= ClientPackets.Taskboard then
		return
	end

	local action = readU8(msg)
	if not action then
		logger.debug("[Taskboard] ignored malformed 0x5F packet from player='{}': missing action", player:getName())
		return
	end

	local payloadValid, firstPayload = readActionPayload(msg, action)
	if not payloadValid then
		logger.debug("[Taskboard] ignored malformed 0x5F packet from player='{}': incomplete action {}", player:getName(), action)
		return
	end

	local trailingBytes = msg:getUnreadBytes()
	if trailingBytes > 0 then
		logger.debug("[Taskboard] ignored malformed 0x5F packet from player='{}': action={} unexpected trailing bytes={}", player:getName(), action, trailingBytes)
		return
	end

	if action == ClientAction.ShopBuy then
		purchaseBonusPromotionPoint(player, firstPayload)
		sendWindow(player, OutboundWindow.Shop)
	elseif BountyResponseActions[action] then
		sendWindow(player, OutboundWindow.Bounty)
	elseif WeeklyResponseActions[action] then
		sendWindow(player, OutboundWindow.Weekly)
	elseif ShopResponseActions[action] then
		sendWindow(player, OutboundWindow.Shop)
	else
		sendWindow(player, OutboundWindow.Bounty)
	end

	logger.debug("[Taskboard] player='{}' action={} handled.", player:getName(), action)
end
