local function assertEqual(actual, expected, message)
	if actual ~= expected then
		error(string.format("%s: expected %s, got %s", message or "assertion failed", tostring(expected), tostring(actual)), 2)
	end
end

local function assertTrue(value, message)
	assertEqual(value == true, true, message)
end

local realDofile = dofile
local registered = {}
local calls = {
	started = 0,
	stopped = 0,
	damageDealt = {},
	damageReceived = {},
	healing = {},
	mana = {},
	kills = {},
	deaths = {},
	experience = {},
}

local Analytics = {
	config = { trackPvP = false },
}

function Analytics.isEnabled()
	return true
end

function Analytics.startRuntime()
	calls.started = calls.started + 1
	return true
end

function Analytics.stopRuntime()
	calls.stopped = calls.stopped + 1
end

function Analytics.recordDamageDealt(player, target, amount, damageType)
	calls.damageDealt[#calls.damageDealt + 1] = { player = player, target = target, amount = amount, damageType = damageType }
end

function Analytics.recordDamageReceived(player, attacker, amount, damageType)
	calls.damageReceived[#calls.damageReceived + 1] = { player = player, attacker = attacker, amount = amount, damageType = damageType }
end

function Analytics.recordHealing(player, target, effective, overhealing)
	calls.healing[#calls.healing + 1] = { player = player, target = target, effective = effective, overhealing = overhealing }
end

function Analytics.recordManaSpent(player, amount)
	calls.mana[#calls.mana + 1] = { player = player, amount = amount }
end

function Analytics.recordKill(player, target)
	calls.kills[#calls.kills + 1] = { player = player, target = target }
end

function Analytics.recordDeath(player)
	calls.deaths[#calls.deaths + 1] = player
end

function Analytics.recordExperience(player, finalExperience, rawExperience, source)
	calls.experience[#calls.experience + 1] = { player = player, finalExperience = finalExperience, rawExperience = rawExperience, source = source }
end

function Analytics.finish() end
function Analytics.flush()
	return true
end
function Analytics.persistDeadLetters()
	return 0
end
function Analytics.checkSchema()
	return true
end
function Analytics.status()
	return {
		queuedSessions = 0,
		retryingSessions = 0,
		deadLetterQueueSize = 0,
		persistedDeadLetters = 0,
		droppedDeadLetters = 0,
		schemaVersion = 3,
		requiredSchemaVersion = 3,
		schemaReady = true,
		activeSessions = 0,
		retriedSessions = 0,
		successfulFlushes = 0,
		failedFlushes = 0,
		lastFlushDurationMs = 0,
		oldestQueuedAgeSeconds = 0,
		detailLevel = 1,
		detailBatchSize = 250,
		detailBatchQueries = 0,
		detailRowsPersisted = 0,
		contextSamples = 0,
		contextFinalizedSessions = 0,
		dayRollovers = 0,
		discardedNonCombatSessions = 0,
		shortDeathSessionsPersisted = 0,
		lastFlush = 0,
	}
end

function dofile(path)
	if path:find("data%-otservbr%-global/scripts/lib/gameplay_analytics", 1, false) then
		return Analytics
	end
	return realDofile(path)
end

local function eventFactory(name)
	local event = { name = name }
	function event:register()
		registered[name] = self
	end
	return event
end

function GlobalEvent(name)
	return eventFactory(name)
end

function CreatureEvent(name)
	return eventFactory(name)
end

function EventCallback(name)
	return eventFactory(name)
end

function TalkAction(name)
	local action = eventFactory(name)
	function action:separator() end
	function action:groupType() end
	return action
end

ACCOUNT_TYPE_GAMEMASTER = 3
MESSAGE_EVENT_ADVANCE = 1
Game = {
	getPlayers = function()
		return {}
	end,
}

local function player(id, health, maximumHealth)
	local value = {
		id = id,
		health = health or 100,
		maximumHealth = maximumHealth or 100,
		registeredEvents = {},
	}
	function value:isPlayer()
		return true
	end
	function value:isMonster()
		return false
	end
	function value:getMaster()
		return nil
	end
	function value:getHealth()
		return self.health
	end
	function value:getMaxHealth()
		return self.maximumHealth
	end
	function value:registerEvent(name)
		self.registeredEvents[#self.registeredEvents + 1] = name
	end
	return value
end

local function monster(master)
	local value = { master = master }
	function value:isPlayer()
		return false
	end
	function value:isMonster()
		return true
	end
	function value:getMaster()
		return self.master
	end
	return value
end

realDofile("data-otservbr-global/scripts/systems/gameplay_analytics.lua")

for _, name in ipairs({
	"GameplayAnalyticsStartup",
	"GameplayAnalyticsShutdown",
	"GameplayAnalyticsHealth",
	"GameplayAnalyticsMana",
	"GameplayAnalyticsLogin",
	"GameplayAnalyticsLogout",
	"GameplayAnalyticsDeath",
	"GameplayAnalyticsKill",
	"GameplayAnalyticsExperience",
	"GameplayAnalyticsDrainHealth",
	"/analytics",
}) do
	assertTrue(registered[name] ~= nil, "registered hook " .. name)
end

registered.GameplayAnalyticsStartup.onStartup()
registered.GameplayAnalyticsShutdown.onShutdown()
assertEqual(calls.started, 1, "startup delegates once")
assertEqual(calls.stopped, 1, "shutdown delegates once")

local owner = player(1)
local summon = monster(owner)
local targetMonster = monster(nil)
registered.GameplayAnalyticsDrainHealth.creatureOnDrainHealth(targetMonster, summon, 4, 30, 8, 12, 0, 0)
assertEqual(#calls.damageDealt, 2, "summon primary and secondary damage are recorded")
assertEqual(calls.damageDealt[1].player, owner, "summon damage is attributed to player owner")
assertEqual(calls.damageDealt[1].amount, 30, "primary summon damage amount")
assertEqual(calls.damageDealt[1].damageType, 4, "primary summon damage type")
assertEqual(calls.damageDealt[2].amount, 12, "secondary summon damage amount")
assertEqual(calls.damageDealt[2].damageType, 8, "secondary summon damage type")

local attacker = player(2)
local victim = player(3)
registered.GameplayAnalyticsHealth.onHealthChange(victim, attacker, -50, 4, -10, 8, 0)
assertEqual(#calls.damageDealt, 2, "PvP dealt damage is excluded by default")
assertEqual(#calls.damageReceived, 0, "PvP received damage is excluded by default")

local attackerSummon = monster(attacker)
registered.GameplayAnalyticsHealth.onHealthChange(victim, attackerSummon, -20, 4, 0, 0, 0)
assertEqual(#calls.damageDealt, 2, "player-summon PvP dealt damage is excluded")
assertEqual(#calls.damageReceived, 0, "player-summon PvP received damage is excluded")

local victimSummon = monster(victim)
registered.GameplayAnalyticsDrainHealth.creatureOnDrainHealth(victimSummon, attacker, 4, 25, 0, 0, 0, 0)
assertEqual(#calls.damageDealt, 2, "damage to a player-owned summon is excluded as PvP")

local hostileMonster = monster(nil)
registered.GameplayAnalyticsHealth.onHealthChange(victim, hostileMonster, -40, 4, -5, 8, 0)
assertEqual(#calls.damageReceived, 2, "monster primary and secondary damage are received")
assertEqual(calls.damageReceived[1].player, victim, "incoming monster damage targets the player")
assertEqual(calls.damageReceived[1].amount, 40, "incoming primary damage amount")
assertEqual(calls.damageReceived[2].damageType, 8, "incoming secondary damage type")

Analytics.config.trackPvP = true
registered.GameplayAnalyticsHealth.onHealthChange(victim, attacker, -9, 4, 0, 0, 0)
assertEqual(#calls.damageDealt, 3, "PvP dealt damage records when enabled")
assertEqual(#calls.damageReceived, 3, "PvP received damage records when enabled")
Analytics.config.trackPvP = false

registered.GameplayAnalyticsMana.onManaChange(owner, nil, -20, 0, -5, 0, 0)
registered.GameplayAnalyticsMana.onManaChange(owner, nil, 10, 0, 5, 0, 0)
assertEqual(#calls.mana, 1, "one mana record per negative mana callback")
assertEqual(calls.mana[1].player, owner, "mana spend owner")
assertEqual(calls.mana[1].amount, 25, "primary and secondary negative mana are summed")

local healer = player(4)
local wounded = player(5, 50, 100)
registered.GameplayAnalyticsHealth.onHealthChange(wounded, healer, 80, 0, 0, 0, 0)
assertEqual(#calls.healing, 1, "healing callback records once")
assertEqual(calls.healing[1].effective, 50, "healing is capped by missing health")
assertEqual(calls.healing[1].overhealing, 30, "overhealing is retained")

registered.GameplayAnalyticsExperience.playerOnGainExperience(owner, targetMonster, 150, 100)
assertEqual(#calls.experience, 1, "experience hook records once")
assertEqual(calls.experience[1].source, targetMonster, "experience source is retained")

registered.GameplayAnalyticsKill.onKill(owner, targetMonster)
registered.GameplayAnalyticsDeath.onDeath(owner, nil, nil, nil, false, false)
assertEqual(#calls.kills, 1, "kill hook records once")
assertEqual(#calls.deaths, 1, "death hook records once")

registered.GameplayAnalyticsLogin.onLogin(owner)
assertEqual(#owner.registeredEvents, 4, "login registers all player creature events")

-- Restore the global loader for any test runner that executes multiple files in one process.
dofile = realDofile
print("gameplay analytics runtime hook dry-run test passed")
