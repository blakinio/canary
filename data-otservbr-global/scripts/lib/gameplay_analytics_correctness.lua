local Analytics = GameplayAnalytics
if not Analytics then
	error("GameplayAnalytics must be loaded before gameplay_analytics_correctness.lua")
end

if Analytics.correctnessInstalled then
	return Analytics
end

Analytics.correctnessInstalled = true
Analytics.correctnessStats = Analytics.correctnessStats or {
	dayRollovers = 0,
	discardedNonCombatSessions = 0,
	expiredNonCombatSessions = 0,
	shortDeathSessionsPersisted = 0,
	shortRolloverSessionsPersisted = 0,
}

local originalGet = Analytics.get
local originalFinish = Analytics.finish
local originalEnqueue = Analytics.enqueue
local originalExpireInactive = Analytics.expireInactive
local originalStatus = Analytics.status

local function now()
	return os.time()
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

local function utcDay(timestamp)
	return math.floor(math.max(0, tonumber(timestamp) or 0) / 86400)
end

local function hasCombatOrDeath(session)
	return (tonumber(session and session.lastCombatAt) or 0) > 0 or (tonumber(session and session.deaths) or 0) > 0
end

local function callFinishWithMinimum(player, reason, minimum)
	local configuredMinimum = Analytics.config.minimumSessionSeconds
	Analytics.config.minimumSessionSeconds = minimum
	local ok, resultValue = pcall(originalFinish, player, reason)
	Analytics.config.minimumSessionSeconds = configuredMinimum
	if not ok then
		error(resultValue, 0)
	end
	return resultValue
end

function Analytics.get(player)
	if not player then
		return originalGet(player)
	end

	local timestamp = now()
	local playerGuid = player:getGuid()
	local current = Analytics.sessions[playerGuid]
	if current and utcDay(current.startedAt) < utcDay(timestamp) then
		Analytics.correctnessStats.dayRollovers = Analytics.correctnessStats.dayRollovers + 1
		Analytics.finish(player, "utc-day-rollover")
	end

	local session = originalGet(player)
	if session then
		session.lastActivityAt = timestamp
	end
	return session
end

function Analytics.enqueue(session)
	if not hasCombatOrDeath(session) then
		Analytics.correctnessStats.discardedNonCombatSessions = Analytics.correctnessStats.discardedNonCombatSessions + 1
		return true
	end
	return originalEnqueue(session)
end

function Analytics.finish(player, reason)
	if not player then
		return originalFinish(player, reason)
	end

	local session = Analytics.sessions[player:getGuid()]
	if not session then
		return originalFinish(player, reason)
	end

	session.lastActivityAt = now()
	local duration = math.max(0, session.lastActivityAt - (tonumber(session.startedAt) or session.lastActivityAt))
	local minimum = clampInteger(Analytics.config.minimumSessionSeconds, 0, nil, 60)
	local forceShortSession = reason == "death" or reason == "utc-day-rollover"
	if forceShortSession and duration < minimum then
		local resultValue = callFinishWithMinimum(player, reason, 0)
		if reason == "death" then
			Analytics.correctnessStats.shortDeathSessionsPersisted = Analytics.correctnessStats.shortDeathSessionsPersisted + 1
		else
			Analytics.correctnessStats.shortRolloverSessionsPersisted = Analytics.correctnessStats.shortRolloverSessionsPersisted + 1
		end
		return resultValue
	end

	return originalFinish(player, reason)
end

function Analytics.expireInactive()
	originalExpireInactive()

	local timestamp = now()
	local timeout = clampInteger(Analytics.config.combatTimeoutSeconds, 10, nil, 120)
	local expired = {}
	for playerGuid, session in pairs(Analytics.sessions) do
		if (tonumber(session.lastCombatAt) or 0) == 0 then
			local lastActivityAt = tonumber(session.lastActivityAt) or tonumber(session.startedAt) or timestamp
			if timestamp - lastActivityAt >= timeout then
				expired[#expired + 1] = { playerGuid = playerGuid, session = session }
			end
		end
	end

	for _, entry in ipairs(expired) do
		Analytics.correctnessStats.expiredNonCombatSessions = Analytics.correctnessStats.expiredNonCombatSessions + 1
		local player = nil
		if type(Player) == "function" and entry.session.runtimeId then
			player = Player(entry.session.runtimeId)
		end
		if player then
			callFinishWithMinimum(player, "activity-timeout", 0)
		else
			Analytics.sessions[entry.playerGuid] = nil
			Analytics.correctnessStats.discardedNonCombatSessions = Analytics.correctnessStats.discardedNonCombatSessions + 1
		end
	end
end

function Analytics.status()
	local status = originalStatus()
	for key, value in pairs(Analytics.correctnessStats) do
		status[key] = value
	end
	return status
end

return Analytics
