local function assertEqual(actual, expected, message)
	if actual ~= expected then
		error(string.format("%s: expected %s, got %s", message or "assertion failed", tostring(expected), tostring(actual)), 2)
	end
end

local function assertTrue(value, message)
	assertEqual(value == true, true, message)
end

local realTime = os.time
local clock = 0
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

local finishShouldError = false
local originalExpireCalls = 0

GameplayAnalytics = {
	config = {
		minimumSessionSeconds = 60,
		combatTimeoutSeconds = 120,
	},
	sessions = {},
	queue = {},
}

function GameplayAnalytics.get(subject)
	if not subject then
		return nil
	end
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
	if finishShouldError then
		error("simulated finish failure")
	end
	if not subject then
		return false
	end
	local guid = subject:getGuid()
	local session = GameplayAnalytics.sessions[guid]
	if not session then
		return false
	end
	GameplayAnalytics.sessions[guid] = nil
	session.endedAt = clock
	session.finishReason = reason
	local duration = session.endedAt - session.startedAt
	if session.hasData and duration >= GameplayAnalytics.config.minimumSessionSeconds then
		return GameplayAnalytics.enqueue(session)
	end
	return false
end

function GameplayAnalytics.expireInactive()
	originalExpireCalls = originalExpireCalls + 1
end

function GameplayAnalytics.status()
	return {
		queuedSessions = #GameplayAnalytics.queue,
	}
end

local Analytics = dofile("data-otservbr-global/scripts/lib/gameplay_analytics_correctness.lua")

local function reset()
	clock = 0
	playersByRuntimeId = {}
	finishShouldError = false
	originalExpireCalls = 0
	Analytics.config.minimumSessionSeconds = 60
	Analytics.config.combatTimeoutSeconds = 120
	Analytics.sessions = {}
	Analytics.queue = {}
	for key in pairs(Analytics.correctnessStats) do
		Analytics.correctnessStats[key] = 0
	end
end

local function markCombat(session, timestamp)
	session.hasData = true
	session.lastCombatAt = timestamp
end

-- Loading the final wrapper twice must not install a second layer.
reset()
local secondLoad = dofile("data-otservbr-global/scripts/lib/gameplay_analytics_correctness.lua")
assertEqual(secondLoad, Analytics, "correctness wrapper is idempotent")

-- Activity within the same UTC day must retain the same session.
reset()
clock = 1000
local sameDayPlayer = player(1, 101)
local sameDaySession = Analytics.get(sameDayPlayer)
markCombat(sameDaySession, clock)
clock = 80000
assertEqual(Analytics.get(sameDayPlayer), sameDaySession, "same UTC day keeps the active session")
assertEqual(#Analytics.queue, 0, "same-day access does not queue a rollover")
assertEqual(Analytics.correctnessStats.dayRollovers, 0, "same-day access does not increment rollover counter")

-- The exact first second of the next UTC day must split the session once.
reset()
clock = 86399
local boundaryPlayer = player(2, 102)
local boundarySession = Analytics.get(boundaryPlayer)
markCombat(boundarySession, clock)
clock = 86400
local boundaryNext = Analytics.get(boundaryPlayer)
assertTrue(boundaryNext ~= boundarySession, "midnight creates a new session")
assertEqual(boundaryNext.startedAt, 86400, "new session starts at exact UTC boundary")
assertEqual(#Analytics.queue, 1, "pre-midnight combat fragment is queued")
assertEqual(Analytics.queue[1].finishReason, "utc-day-rollover", "rollover reason is retained")
assertEqual(Analytics.correctnessStats.dayRollovers, 1, "midnight increments rollover once")
assertEqual(Analytics.correctnessStats.shortRolloverSessionsPersisted, 1, "short rollover fragment is retained")

-- A multi-day gap still closes only the one active session and starts one replacement.
reset()
clock = 1
local gapPlayer = player(3, 103)
local gapSession = Analytics.get(gapPlayer)
markCombat(gapSession, clock)
clock = 172800
local gapNext = Analytics.get(gapPlayer)
assertTrue(gapNext ~= gapSession, "multi-day gap creates one replacement session")
assertEqual(#Analytics.queue, 1, "multi-day gap queues only the previous active session")
assertEqual(Analytics.correctnessStats.dayRollovers, 1, "multi-day gap records one rollover")

-- Timeout values below ten seconds are clamped, and expiry happens at the boundary.
reset()
Analytics.config.combatTimeoutSeconds = 0
clock = 300
local timeoutPlayer = player(4, 104)
local timeoutSession = Analytics.get(timeoutPlayer)
timeoutSession.hasData = true
timeoutSession.manaSpent = 20
clock = 309
Analytics.expireInactive()
assertTrue(Analytics.sessions[timeoutPlayer:getGuid()] ~= nil, "non-combat session remains before clamped timeout")
clock = 310
Analytics.expireInactive()
assertEqual(Analytics.sessions[timeoutPlayer:getGuid()], nil, "non-combat session expires at clamped timeout")
assertEqual(#Analytics.queue, 0, "expired non-combat session is never queued")
assertEqual(Analytics.correctnessStats.expiredNonCombatSessions, 1, "online expiry counter")
assertEqual(Analytics.correctnessStats.discardedNonCombatSessions, 1, "online non-combat discard counter")
assertEqual(originalExpireCalls, 2, "original combat expiry still runs on each pass")

-- An offline player must not leave an orphaned non-combat session in memory.
reset()
clock = 500
local offlinePlayer = player(5, 105)
local offlineSession = Analytics.get(offlinePlayer)
offlineSession.hasData = true
offlineSession.manaSpent = 10
playersByRuntimeId[offlinePlayer:getId()] = nil
clock = 620
Analytics.expireInactive()
assertEqual(Analytics.sessions[offlinePlayer:getGuid()], nil, "offline non-combat session is removed")
assertEqual(#Analytics.queue, 0, "offline non-combat session is not queued")
assertEqual(Analytics.correctnessStats.expiredNonCombatSessions, 1, "offline expiry counter")
assertEqual(Analytics.correctnessStats.discardedNonCombatSessions, 1, "offline discard counter")

-- A short death must survive the normal minimum duration.
reset()
clock = 1000
local deathPlayer = player(6, 106)
local deathSession = Analytics.get(deathPlayer)
markCombat(deathSession, clock)
deathSession.deaths = 1
clock = 1001
assertTrue(Analytics.finish(deathPlayer, "death"), "short death finish succeeds")
assertEqual(#Analytics.queue, 1, "short death is queued")
assertEqual(Analytics.correctnessStats.shortDeathSessionsPersisted, 1, "short death counter increments")
assertEqual(Analytics.config.minimumSessionSeconds, 60, "minimum duration is restored after short death")

-- An exception in the wrapped finish must restore global configuration and must
-- not claim that the short session was persisted.
reset()
clock = 2000
local failurePlayer = player(7, 107)
local failureSession = Analytics.get(failurePlayer)
markCombat(failureSession, clock)
failureSession.deaths = 1
clock = 2001
finishShouldError = true
local ok, failure = pcall(Analytics.finish, failurePlayer, "death")
assertEqual(ok, false, "simulated finish failure propagates")
assertTrue(tostring(failure):find("simulated finish failure", 1, true) ~= nil, "finish error is preserved")
assertEqual(Analytics.config.minimumSessionSeconds, 60, "minimum duration is restored after finish error")
assertEqual(Analytics.correctnessStats.shortDeathSessionsPersisted, 0, "failed finish is not counted as persisted")
assertEqual(Analytics.sessions[failurePlayer:getGuid()], failureSession, "failed finish leaves the active session available")

-- Direct enqueue calls retain death/combat data and reject utility-only data.
reset()
assertTrue(Analytics.enqueue({ lastCombatAt = 0, deaths = 0 }), "non-combat discard is non-fatal")
assertEqual(#Analytics.queue, 0, "non-combat direct enqueue is discarded")
local deathOnly = { lastCombatAt = 0, deaths = 1 }
assertTrue(Analytics.enqueue(deathOnly), "death-only enqueue succeeds")
assertEqual(Analytics.queue[1], deathOnly, "death-only session reaches the queue")
local combatOnly = { lastCombatAt = 1, deaths = 0 }
assertTrue(Analytics.enqueue(combatOnly), "combat enqueue succeeds")
assertEqual(Analytics.queue[2], combatOnly, "combat session reaches the queue")

-- Nil delegation and status extension remain safe.
assertEqual(Analytics.get(nil), nil, "nil get delegates safely")
assertEqual(Analytics.finish(nil, "test"), false, "nil finish delegates safely")
local status = Analytics.status()
assertEqual(status.discardedNonCombatSessions, 1, "status exposes dry-run discard count")
assertEqual(status.queuedSessions, 2, "status retains original fields")

os.time = realTime
print("gameplay analytics correctness edge-case test passed")
