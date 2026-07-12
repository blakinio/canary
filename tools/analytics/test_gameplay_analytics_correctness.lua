local function assertEqual(actual, expected, message)
	if actual ~= expected then
		error(string.format("%s: expected %s, got %s", message or "assertion failed", tostring(expected), tostring(actual)), 2)
	end
end

local realTime = os.time
local clock = 1000
os.time = function()
	return clock
end

local playersByRuntimeId = {}
function Player(runtimeId)
	return playersByRuntimeId[runtimeId]
end

local function player(guid, runtimeId)
	local value = { guid = guid, runtimeId = runtimeId }
	function value:getGuid()
		return self.guid
	end
	function value:getId()
		return self.runtimeId
	end
	playersByRuntimeId[runtimeId] = value
	return value
end

GameplayAnalytics = {
	config = {
		minimumSessionSeconds = 60,
		combatTimeoutSeconds = 120,
	},
	sessions = {},
	queue = {},
}

function GameplayAnalytics.get(subject)
	local guid = subject:getGuid()
	local session = GameplayAnalytics.sessions[guid]
	if not session then
		session = {
			uuid = string.format("00000000-0000-0000-0000-%012d", guid),
			playerId = guid,
			runtimeId = subject:getId(),
			startedAt = clock,
			endedAt = clock,
			lastCombatAt = 0,
			deaths = 0,
			hasData = false,
		}
		GameplayAnalytics.sessions[guid] = session
	end
	return session
end

function GameplayAnalytics.enqueue(session)
	GameplayAnalytics.queue[#GameplayAnalytics.queue + 1] = session
	return true
end

function GameplayAnalytics.finish(subject, reason)
	local guid = subject:getGuid()
	local session = GameplayAnalytics.sessions[guid]
	if not session then
		return
	end
	GameplayAnalytics.sessions[guid] = nil
	session.endedAt = clock
	session.finishReason = reason
	local duration = session.endedAt - session.startedAt
	if session.hasData and duration >= GameplayAnalytics.config.minimumSessionSeconds then
		GameplayAnalytics.enqueue(session)
	end
end

function GameplayAnalytics.expireInactive() end

function GameplayAnalytics.status()
	return {
		queuedSessions = #GameplayAnalytics.queue,
	}
end

local Analytics = dofile("data-otservbr-global/scripts/lib/gameplay_analytics_correctness.lua")

local manaPlayer = player(1, 101)
local manaSession = Analytics.get(manaPlayer)
manaSession.hasData = true
manaSession.manaSpent = 25
clock = 1119
Analytics.expireInactive()
assertEqual(Analytics.sessions[manaPlayer:getGuid()] ~= nil, true, "non-combat session stays before timeout")
clock = 1120
Analytics.expireInactive()
assertEqual(Analytics.sessions[manaPlayer:getGuid()], nil, "non-combat session expires")
assertEqual(#Analytics.queue, 0, "non-combat session is not persisted")
assertEqual(Analytics.correctnessStats.expiredNonCombatSessions, 1, "expired non-combat counter")
assertEqual(Analytics.correctnessStats.discardedNonCombatSessions, 1, "discarded non-combat counter")

clock = 2000
local deathPlayer = player(2, 102)
local deathSession = Analytics.get(deathPlayer)
deathSession.hasData = true
deathSession.lastCombatAt = clock
deathSession.deaths = 1
clock = 2010
Analytics.finish(deathPlayer, "death")
assertEqual(#Analytics.queue, 1, "short death session persists")
assertEqual(Analytics.queue[1].finishReason, "death", "death finish reason")
assertEqual(Analytics.config.minimumSessionSeconds, 60, "minimum duration restored")
assertEqual(Analytics.correctnessStats.shortDeathSessionsPersisted, 1, "short death counter")

clock = 86390
local rolloverPlayer = player(3, 103)
local rolloverSession = Analytics.get(rolloverPlayer)
rolloverSession.hasData = true
rolloverSession.lastCombatAt = clock
clock = 86410
local newDaySession = Analytics.get(rolloverPlayer)
assertEqual(#Analytics.queue, 2, "short pre-midnight combat session persists")
assertEqual(Analytics.queue[2].finishReason, "utc-day-rollover", "rollover finish reason")
assertEqual(newDaySession ~= rolloverSession, true, "new UTC day starts a new session")
assertEqual(newDaySession.startedAt, 86410, "new session starts at first event of new UTC day")
assertEqual(Analytics.correctnessStats.dayRollovers, 1, "day rollover counter")
assertEqual(Analytics.correctnessStats.shortRolloverSessionsPersisted, 1, "short rollover counter")

local queueBeforeDiscard = #Analytics.queue
assertEqual(Analytics.enqueue({ lastCombatAt = 0, deaths = 0 }), true, "discarding non-combat enqueue is non-fatal")
assertEqual(#Analytics.queue, queueBeforeDiscard, "direct non-combat enqueue is discarded")

local combatSession = { lastCombatAt = 90000, deaths = 0 }
assertEqual(Analytics.enqueue(combatSession), true, "combat enqueue succeeds")
assertEqual(Analytics.queue[#Analytics.queue], combatSession, "combat session reaches wrapped queue")

local status = Analytics.status()
assertEqual(status.dayRollovers, 1, "status exposes day rollovers")
assertEqual(status.discardedNonCombatSessions, 2, "status exposes discarded non-combat sessions")
assertEqual(status.shortDeathSessionsPersisted, 1, "status exposes short death sessions")

os.time = realTime
print("gameplay analytics correctness runtime test passed")
