-- This file is loaded after gameplay_analytics.lua and replaces only the
-- persistence function. It keeps the public Analytics API unchanged while
-- avoiding a query-handle variable shadowing Canary's global result API.

local Analytics = GameplayAnalytics
if not Analytics then
	logger.error("[GameplayAnalytics] Persistence fix loaded before the analytics library.")
	return
end

local function clampInteger(value, minimum, maximum, fallback)
	value = tonumber(value)
	if not value then
		return fallback
	end
	value = math.floor(value)
	if value < minimum then
		return minimum
	end
	if maximum and value > maximum then
		return maximum
	end
	return value
end

local function escaped(value)
	return db.escapeString(tostring(value or ""))
end

local function sessionInsert(session)
	local nameSql = session.playerName and escaped(session.playerName) or "NULL"
	return string.format(
		[[INSERT INTO `analytics_sessions`
        (`session_uuid`,`player_id`,`player_name`,`vocation_id`,`level_start`,`level_end`,`started_at`,`ended_at`,`duration_seconds`,`combat_seconds`,`experience_raw`,`experience_final`,`damage_dealt`,`damage_received`,`healing_self`,`healing_others`,`overhealing`,`mana_spent`,`monsters_killed`,`deaths`,`loot_value_npc`,`loot_value_market`,`supplies_value`,`party_size`,`shared_experience`,`detail_level`,`analytics_version`)
        VALUES (%s,%d,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d)]],
		escaped(session.uuid),
		session.playerId,
		nameSql,
		session.vocationId,
		session.levelStart,
		session.levelEnd,
		session.startedAt,
		session.endedAt,
		math.max(0, session.endedAt - session.startedAt),
		session.combatSeconds,
		session.experienceRaw,
		session.experienceFinal,
		session.damageDealt,
		session.damageReceived,
		session.healingSelf,
		session.healingOthers,
		session.overhealing,
		session.manaSpent,
		session.monstersKilled,
		session.deaths,
		session.lootNpc,
		session.lootMarket,
		session.suppliesValue,
		session.partySize,
		session.sharedExperience and 1 or 0,
		clampInteger(Analytics.config.detailLevel, 0, 2, 1),
		Analytics.VERSION
	)
end

local function insertDetails(session)
	local queryResult = db.storeQuery("SELECT `id` FROM `analytics_sessions` WHERE `session_uuid` = " .. escaped(session.uuid) .. " LIMIT 1")
	if not queryResult then
		logger.error("[GameplayAnalytics] Could not resolve persisted session {} for detail writes.", session.uuid)
		return false
	end

	local sessionId = result.getNumber(queryResult, "id")
	result.free(queryResult)

	if Analytics.config.trackMonsters then
		for name, data in pairs(session.monsters) do
			db.query(string.format("INSERT INTO `analytics_session_monsters` (`session_id`,`monster_name`,`kills`,`damage_dealt`,`damage_received`,`experience_raw`) VALUES (%d,%s,%d,%d,%d,%d)", sessionId, escaped(name), data.kills, data.damageDealt, data.damageReceived, data.experienceRaw))
		end
	end
	if Analytics.config.trackSpells then
		for name, data in pairs(session.spells) do
			db.query(string.format("INSERT INTO `analytics_session_spells` (`session_id`,`spell_name`,`casts`,`targets_hit`,`damage`,`healing`,`mana_spent`,`critical_hits`) VALUES (%d,%s,%d,%d,%d,%d,%d,%d)", sessionId, escaped(name), data.casts, data.targets, data.damage, data.healing, data.mana, data.critical))
		end
	end
	if Analytics.config.trackDamageTypes then
		for damageType, data in pairs(session.damageTypes) do
			db.query(string.format("INSERT INTO `analytics_session_damage_types` (`session_id`,`damage_type`,`damage_dealt`,`damage_received`) VALUES (%d,%d,%d,%d)", sessionId, damageType, data.dealt, data.received))
		end
	end
	if Analytics.config.trackSupplies then
		for itemId, data in pairs(session.supplies) do
			db.query(string.format("INSERT INTO `analytics_session_supplies` (`session_id`,`item_id`,`amount_used`,`unit_value`,`total_value`) VALUES (%d,%d,%d,%d,%d)", sessionId, itemId, data.amount, data.unitValue, data.totalValue))
		end
	end
	if Analytics.config.trackLoot then
		for itemId, data in pairs(session.loot) do
			db.query(string.format("INSERT INTO `analytics_session_loot` (`session_id`,`item_id`,`amount`,`npc_value`,`market_value`) VALUES (%d,%d,%d,%d,%d)", sessionId, itemId, data.amount, data.npcValue, data.marketValue))
		end
	end

	return true
end

function Analytics.flush()
	if Analytics.config.databaseEnabled ~= true or #Analytics.queue == 0 then
		Analytics.lastFlush = os.time()
		return true
	end

	local pending = Analytics.queue
	Analytics.queue = {}
	for _, session in ipairs(pending) do
		if db.query(sessionInsert(session)) then
			insertDetails(session)
		else
			logger.error("[GameplayAnalytics] Failed to persist session {}", session.uuid)
			if #Analytics.queue < clampInteger(Analytics.config.queueLimit, 100, nil, 10000) then
				Analytics.queue[#Analytics.queue + 1] = session
			end
		end
	end
	Analytics.lastFlush = os.time()
	return true
end
