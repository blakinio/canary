local CLIENT_VERSION = tonumber(os.getenv("AGENT_E2E_CLIENT_VERSION") or "1525")
local ACCOUNT = os.getenv("AGENT_E2E_ACCOUNT") or "@test1"
local PASSWORD = os.getenv("AGENT_E2E_PASSWORD") or ""
local CHARACTER = os.getenv("AGENT_E2E_CHARACTER") or "Knight 1"
local WORLD = os.getenv("AGENT_E2E_WORLD") or "Canary E2E"
local HOST = os.getenv("AGENT_E2E_HOST") or "127.0.0.1"
local GAME_PORT = tonumber(os.getenv("AGENT_E2E_GAME_PORT") or "7172")
local ARTIFACT_DIR = os.getenv("AGENT_E2E_ARTIFACT_DIR") or "../artifacts"
local GLOBAL_TIMEOUT_SECONDS = tonumber(os.getenv("AGENT_E2E_GLOBAL_TIMEOUT_SECONDS") or "180")
local SESSION_HOLD_MS = tonumber(os.getenv("AGENT_E2E_SESSION_HOLD_MS") or "7000")
local RELOG_DELAY_MS = tonumber(os.getenv("AGENT_E2E_RELOG_DELAY_MS") or "1500")
local SCENARIO_KEY = os.getenv("AGENT_E2E_SCENARIO_KEY") or "unknown"
local STARTUP_PROFILE = os.getenv("AGENT_E2E_STARTUP_PROFILE") or "minimal-transport"
local PING_PROFILE = os.getenv("AGENT_E2E_PING_PROFILE") or "disabled"
local DB_HOST = os.getenv("DB_HOST") or "127.0.0.1"
local DB_PORT = tonumber(os.getenv("DB_PORT") or "3306")
local DB_USER = os.getenv("DB_USER") or "root"
local DB_NAME = os.getenv("DB_NAME") or "agent_e2e"

local EVENTS_PATH = ARTIFACT_DIR .. "/client-events.tsv"
local INTERNAL_LOG_PATH = ARTIFACT_DIR .. "/otclient.internal.log"
local PLAN_PATH = ARTIFACT_DIR .. "/scenario-plan.lua"
local ROUTE_EXECUTOR_PATH = ARTIFACT_DIR .. "/agent-e2e-route.lua"

local phase = 1
local phaseStarted = false
local logoutRequested = false
local enteringWorld = false
local waitingForServerPersistence = false
local finished = false
local startedAt = os.time()
local plan = nil
local routeExecutor = nil
local planIndex = 1
local persistenceIndex = 1
local initialPosition = nil

local DIRECTIONS = {
	north = North or 0,
	east = East or 1,
	south = South or 2,
	west = West or 3,
	northeast = NorthEast or 4,
	southeast = SouthEast or 5,
	southwest = SouthWest or 6,
	northwest = NorthWest or 7,
}

local WALK_EDGE_DIRECTIONS = {
	["0,-1"] = DIRECTIONS.north,
	["1,-1"] = DIRECTIONS.northeast,
	["1,0"] = DIRECTIONS.east,
	["1,1"] = DIRECTIONS.southeast,
	["0,1"] = DIRECTIONS.south,
	["-1,1"] = DIRECTIONS.southwest,
	["-1,0"] = DIRECTIONS.west,
	["-1,-1"] = DIRECTIONS.northwest,
}

local function sanitize(value)
	return tostring(value):gsub("[\t\r\n]", " ")
end

local function shellQuote(value)
	return "'" .. tostring(value):gsub("'", "'\\''") .. "'"
end

local function appendEvent(key, value)
	local file = assert(io.open(EVENTS_PATH, "a"))
	file:write(string.format("%d\t%s\t%s\n", os.time(), sanitize(key), sanitize(value)))
	file:close()
	g_logger.info(string.format("[agent-e2e] %s=%s", tostring(key), tostring(value)))
end

local function exitSoon()
	scheduleEvent(function()
		g_app.exit()
	end, 250)
end

local function fail(message)
	if finished then
		return
	end
	finished = true
	appendEvent("e2e", "failure")
	appendEvent("error", message)
	exitSoon()
end

local function disableStartupModule(name)
	local module = g_modules.getModule(name)
	if not module or not module:isLoaded() then
		appendEvent("startup_module_" .. name, "not-loaded")
		return
	end
	local ok, err = pcall(function()
		module:unload()
	end)
	if ok then
		appendEvent("startup_module_" .. name, "disabled")
	else
		fail("failed to disable startup module " .. name .. ": " .. tostring(err))
	end
end

local function installStartupProfile()
	appendEvent("startup_profile", STARTUP_PROFILE)
	if STARTUP_PROFILE == "full" then
		return
	end
	if STARTUP_PROFILE ~= "minimal-transport" then
		fail("unknown startup profile: " .. tostring(STARTUP_PROFILE))
		return
	end
	local modules = {
		"game_quickloot",
		"game_imbuementtracker",
		"game_shop",
		"client_locales",
		"game_proficiency",
		"game_questlog",
	}
	for _, name in ipairs(modules) do
		disableStartupModule(name)
		if finished then
			return
		end
	end
end

local function configureTransportFeatures()
	if PING_PROFILE == "default" then
		appendEvent("ping_features_" .. phase, "default")
		return true
	end
	if PING_PROFILE ~= "disabled" then
		fail("unknown ping profile: " .. tostring(PING_PROFILE))
		return false
	end
	g_game.disableFeature(GameClientPing)
	g_game.disableFeature(GameExtendedClientPing)
	appendEvent("ping_features_" .. phase, "disabled")
	return true
end

local function requestLogout(expectedPhase)
	if finished or expectedPhase ~= phase or not phaseStarted or logoutRequested then
		return
	end
	logoutRequested = true
	appendEvent("logout_request_" .. phase, "safe")
	g_game.safeLogout()
end

local function startLogin()
	if finished or enteringWorld or phaseStarted then
		return
	end
	if PASSWORD == "" then
		fail("AGENT_E2E_PASSWORD is empty")
		return
	end
	enteringWorld = true
	logoutRequested = false
	g_game.setClientVersion(CLIENT_VERSION)
	g_game.setProtocolVersion(g_game.getClientProtocolVersion(CLIENT_VERSION))
	if not configureTransportFeatures() then
		return
	end
	g_game.chooseRsa(HOST)
	local sessionKey = ACCOUNT .. "\n" .. PASSWORD
	local packetRecord = string.format("%s/session-%d.record", ARTIFACT_DIR, phase)
	appendEvent("login_request_" .. phase, string.format("%s:%d/%s/%s/v%d", HOST, GAME_PORT, WORLD, CHARACTER, CLIENT_VERSION))
	appendEvent("packet_record_" .. phase, packetRecord)
	g_game.loginWorld(ACCOUNT, PASSWORD, WORLD, HOST, GAME_PORT, CHARACTER, "", sessionKey, packetRecord)
end

local function serverPersistenceReady()
	local query = string.format("SELECT IF(lastlogin > 0 AND lastlogout > 0, 1, 0) FROM players WHERE name=%s;", shellQuote(CHARACTER))
	local command = string.format("mariadb -N -s -h %s -P %d -u %s %s -e %s 2>/dev/null", shellQuote(DB_HOST), DB_PORT, shellQuote(DB_USER), shellQuote(DB_NAME), shellQuote(query))
	local pipe = io.popen(command, "r")
	if not pipe then
		return false
	end
	local output = pipe:read("*a") or ""
	local ok = pipe:close()
	return ok and output:match("^%s*1%s*$") ~= nil
end

local function waitForServerPersistence()
	if finished or phase ~= 2 or not waitingForServerPersistence then
		return
	end
	if serverPersistenceReady() then
		waitingForServerPersistence = false
		appendEvent("server_persistence_1", "confirmed")
		scheduleEvent(startLogin, RELOG_DELAY_MS)
		return
	end
	scheduleEvent(waitForServerPersistence, 250)
end

local function samePosition(a, b)
	return a and b and a.x == b.x and a.y == b.y and a.z == b.z
end

local function positionString(position)
	if not position then
		return "unavailable"
	end
	return string.format("%d,%d,%d", position.x, position.y, position.z)
end

local function findVisibleCreature(name)
	local player = g_game.getLocalPlayer()
	if not player then
		return nil
	end
	for _, creature in ipairs(g_map.getSpectators(player:getPosition(), false)) do
		if creature and creature:getName() == name then
			return creature
		end
	end
	return nil
end

local function completeStep(step, detail)
	appendEvent("step_" .. step.id, "success")
	if detail then
		appendEvent("step_" .. step.id .. "_detail", detail)
	end
	planIndex = planIndex + 1
	scheduleEvent(function()
		if not finished then
			runNextStep()
		end
	end, 100)
end

local function failStep(step, message)
	fail(string.format("step %s (%s) failed: %s", tostring(step.id), tostring(step.action), tostring(message)))
end

local function pollUntil(step, timeoutMs, predicate, onSuccess)
	local remainingChecks = math.max(1, math.floor(timeoutMs / 100))
	local function check()
		if finished then
			return
		end
		local ok, detail = predicate()
		if ok then
			onSuccess(detail)
			return
		end
		remainingChecks = remainingChecks - 1
		if remainingChecks <= 0 then
			failStep(step, detail or "timeout")
			return
		end
		scheduleEvent(check, 100)
	end
	check()
end

function runNextStep()
	if finished or phase ~= 1 or not phaseStarted then
		return
	end
	if not plan or type(plan.steps) ~= "table" then
		fail("scenario plan is unavailable")
		return
	end
	if planIndex > #plan.steps then
		appendEvent("plan", "success")
		scheduleEvent(function()
			requestLogout(1)
		end, 250)
		return
	end
	local step = plan.steps[planIndex]
	if type(step) ~= "table" or type(step.id) ~= "string" or type(step.action) ~= "string" then
		fail("invalid runtime scenario step")
		return
	end
	appendEvent("step_" .. step.id, "start")
	if step.action == "wait" then
		scheduleEvent(function()
			completeStep(step, tostring(step.ms))
		end, step.ms)
		return
	end
	if step.action == "walk" then
		local direction = DIRECTIONS[step.direction]
		if direction == nil then
			failStep(step, "unknown direction")
			return
		end
		local remaining = step.count or 1
		local interval = step.interval_ms or 250
		local function walkOnce()
			if finished then
				return
			end
			if remaining <= 0 then
				completeStep(step, step.direction)
				return
			end
			if not g_game.walk(direction) then
				failStep(step, "walk request rejected")
				return
			end
			remaining = remaining - 1
			scheduleEvent(walkOnce, interval)
		end
		walkOnce()
		return
	end
	if step.action == "walk_edge" then
		local player = g_game.getLocalPlayer()
		if not player then
			failStep(step, "local player unavailable")
			return
		end
		local source = { x = step.from_x, y = step.from_y, z = step.from_z }
		local destination = { x = step.to_x, y = step.to_y, z = step.to_z }
		local current = player:getPosition()
		if not samePosition(current, source) then
			failStep(step, string.format("source mismatch actual=%s expected=%s", positionString(current), positionString(source)))
			return
		end
		if source.z ~= destination.z then
			failStep(step, "floor-changing movement edge is unsupported")
			return
		end
		local deltaX = destination.x - source.x
		local deltaY = destination.y - source.y
		local direction = WALK_EDGE_DIRECTIONS[string.format("%d,%d", deltaX, deltaY)]
		if direction == nil then
			failStep(step, string.format("invalid adjacent edge delta=%d,%d", deltaX, deltaY))
			return
		end
		if not g_game.walk(direction) then
			failStep(step, "walk request rejected")
			return
		end
		pollUntil(step, step.timeout_ms or 10000, function()
			local livePlayer = g_game.getLocalPlayer()
			local livePosition = livePlayer and livePlayer:getPosition() or nil
			if not livePosition then
				return false, "local player position unavailable"
			end
			if samePosition(livePosition, destination) then
				return true, positionString(livePosition)
			end
			if not samePosition(livePosition, source) then
				failStep(step, string.format("route drift actual=%s expected=%s", positionString(livePosition), positionString(destination)))
				return false, "route drift"
			end
			return false, string.format("position=%s expected=%s", positionString(livePosition), positionString(destination))
		end, function(detail)
			completeStep(step, detail)
		end)
		return
	end
	if step.action == "follow_route" then
		if not routeExecutor or type(routeExecutor.execute) ~= "function" then
			failStep(step, "route executor unavailable")
			return
		end
		local route = plan.routes and plan.routes[step.route] or nil
		if type(route) ~= "table" then
			failStep(step, "route plan unavailable for logical id " .. tostring(step.route))
			return
		end
		routeExecutor.execute(step, route, {
			appendEvent = appendEvent,
			failStep = failStep,
			completeStep = completeStep,
		})
		return
	end
	if step.action == "talk" then
		g_game.talk(step.text)
		scheduleEvent(function()
			completeStep(step, step.text)
		end, 150)
		return
	end
	if step.action == "attack_visible" then
		pollUntil(step, step.timeout_ms or 10000, function()
			local target = findVisibleCreature(step.creature)
			if not target then
				return false, "creature not visible"
			end
			g_game.attack(target)
			local attacking = g_game.getAttackingCreature()
			if attacking and attacking:getId() == target:getId() then
				return true, tostring(target:getId())
			end
			return false, "attack target not confirmed"
		end, function(detail)
			completeStep(step, detail)
		end)
		return
	end
	if step.action == "use_inventory_item" then
		local player = g_game.getLocalPlayer()
		if not player or player:getInventoryCount(step.item_id, 0) <= 0 then
			failStep(step, "inventory item unavailable")
			return
		end
		g_game.useInventoryItem(step.item_id)
		scheduleEvent(function()
			completeStep(step, tostring(step.item_id))
		end, 200)
		return
	end
	if step.action == "request_quest_log" then
		g_game.requestQuestLog()
		scheduleEvent(function()
			completeStep(step)
		end, 200)
		return
	end
	if step.action == "request_channels" then
		g_game.requestChannels()
		scheduleEvent(function()
			completeStep(step)
		end, 200)
		return
	end
	if step.action == "observe_online" then
		local actual = g_game.isOnline()
		if actual ~= step.expected then
			failStep(step, string.format("online=%s expected=%s", tostring(actual), tostring(step.expected)))
			return
		end
		completeStep(step, tostring(actual))
		return
	end
	if step.action == "observe_position_changed" then
		local player = g_game.getLocalPlayer()
		if not player or not initialPosition then
			failStep(step, "position baseline unavailable")
			return
		end
		local current = player:getPosition()
		if samePosition(current, initialPosition) then
			failStep(step, "position did not change")
			return
		end
		completeStep(step, string.format("%d,%d,%d", current.x, current.y, current.z))
		return
	end
	if step.action == "observe_floor_delta" then
		local player = g_game.getLocalPlayer()
		if not player or not initialPosition then
			failStep(step, "position baseline unavailable")
			return
		end
		local current = player:getPosition()
		local delta = current.z - initialPosition.z
		if delta ~= step.delta then
			failStep(step, string.format("floor delta=%d expected=%d", delta, step.delta))
			return
		end
		completeStep(step, tostring(delta))
		return
	end
	if step.action == "observe_health_percent_below" then
		local player = g_game.getLocalPlayer()
		if not player or player:getMaxHealth() <= 0 then
			failStep(step, "health unavailable")
			return
		end
		local percent = math.floor((player:getHealth() * 100) / player:getMaxHealth())
		if percent >= step.percent then
			failStep(step, string.format("health percent=%d threshold=%d", percent, step.percent))
			return
		end
		completeStep(step, tostring(percent))
		return
	end
	if step.action == "observe_inventory_count_at_least" then
		local player = g_game.getLocalPlayer()
		if not player then
			failStep(step, "local player unavailable")
			return
		end
		local count = player:getInventoryCount(step.item_id, step.tier or 0)
		if count < step.count then
			failStep(step, string.format("count=%d expected-at-least=%d", count, step.count))
			return
		end
		completeStep(step, tostring(count))
		return
	end
	if step.action == "wait_creature" then
		pollUntil(step, step.timeout_ms or 10000, function()
			local present = findVisibleCreature(step.creature) ~= nil
			if present == step.present then
				return true, tostring(present)
			end
			return false, string.format("present=%s expected=%s", tostring(present), tostring(step.present))
		end, function(detail)
			completeStep(step, detail)
		end)
		return
	end
	if step.action == "observe_attacking" then
		local actual = g_game.getAttackingCreature() ~= nil
		if actual ~= step.expected then
			failStep(step, string.format("attacking=%s expected=%s", tostring(actual), tostring(step.expected)))
			return
		end
		completeStep(step, tostring(actual))
		return
	end
	failStep(step, "unsupported runtime action")
end

local function persistencePlayerFieldValue(field)
	local player = g_game.getLocalPlayer()
	if not player then
		return nil, "local player unavailable"
	end
	if field == "level" then
		return player:getLevel(), nil
	end
	if field == "vocation" then
		return player:getVocation(), nil
	end
	if field == "experience" then
		return player:getExperience(), nil
	end
	return nil, "unsupported player field"
end

local function failPersistenceCheck(check, message)
	fail(string.format("persistence check %s (%s) failed: %s", tostring(check.id), tostring(check.field), tostring(message)))
end

local function completePersistenceCheck(check, actual)
	appendEvent("persistence_check_" .. check.id, "success")
	appendEvent("persistence_check_" .. check.id .. "_detail", tostring(actual))
	persistenceIndex = persistenceIndex + 1
	scheduleEvent(function()
		if not finished then
			runNextPersistenceCheck()
		end
	end, 100)
end

function runNextPersistenceCheck()
	if finished or phase ~= 2 or not phaseStarted then
		return
	end
	if not plan or type(plan.persistence_checks) ~= "table" then
		fail("persistence plan is unavailable")
		return
	end
	if persistenceIndex > #plan.persistence_checks then
		appendEvent("persistence_plan", "success")
		scheduleEvent(function()
			requestLogout(2)
		end, 250)
		return
	end

	local check = plan.persistence_checks[persistenceIndex]
	if type(check) ~= "table" or type(check.id) ~= "string" or check.type ~= "player_field" or type(check.field) ~= "string" or type(check.equals) ~= "number" then
		fail("invalid runtime persistence check")
		return
	end
	appendEvent("persistence_check_" .. check.id, "start")

	local remainingChecks = 50
	local function verify()
		if finished or phase ~= 2 or not phaseStarted then
			return
		end
		local actual, readError = persistencePlayerFieldValue(check.field)
		if actual ~= nil and actual == check.equals then
			completePersistenceCheck(check, actual)
			return
		end
		remainingChecks = remainingChecks - 1
		if remainingChecks <= 0 then
			if readError then
				failPersistenceCheck(check, readError)
			else
				failPersistenceCheck(check, string.format("actual=%s expected=%s", tostring(actual), tostring(check.equals)))
			end
			return
		end
		scheduleEvent(verify, 100)
	end
	verify()
end

local function waitForInitialPositionAndStartPlan()
	local remainingChecks = 50
	local function check()
		if finished or phase ~= 1 or not phaseStarted then
			return
		end
		local player = g_game.getLocalPlayer()
		local position = player and player:getPosition() or nil
		if position and position.x and position.y and position.z then
			initialPosition = { x = position.x, y = position.y, z = position.z }
			appendEvent("initial_position", string.format("%d,%d,%d", initialPosition.x, initialPosition.y, initialPosition.z))
			scheduleEvent(function()
				if not finished and phase == 1 and phaseStarted then
					runNextStep()
				end
			end, 1800)
			return
		end
		remainingChecks = remainingChecks - 1
		if remainingChecks <= 0 then
			fail("local player position unavailable after game start")
			return
		end
		scheduleEvent(check, 100)
	end
	check()
end

local function loadHostLuaModule(path, label)
	local file, openError = io.open(path, "r")
	if not file then
		fail("failed to open " .. label .. ": " .. tostring(openError))
		return nil
	end
	local source = file:read("*a") or ""
	file:close()
	local chunk, compileError = load(source, "@" .. path)
	if not chunk then
		fail("failed to compile " .. label .. ": " .. tostring(compileError))
		return nil
	end
	local ok, loaded = pcall(chunk)
	if not ok then
		fail("failed to execute " .. label .. ": " .. tostring(loaded))
		return nil
	end
	return loaded
end

local function loadPlan()
	local loaded = loadHostLuaModule(PLAN_PATH, "scenario plan")
	if not loaded then
		return false
	end
	if type(loaded) ~= "table" or loaded.schema_version ~= 1 or type(loaded.steps) ~= "table" or type(loaded.persistence_checks) ~= "table" then
		fail("invalid scenario plan contract")
		return false
	end
	if loaded.routes == nil then
		loaded.routes = {}
	end
	if type(loaded.routes) ~= "table" then
		fail("invalid route plan contract")
		return false
	end
	if #loaded.steps > 64 then
		fail("scenario plan exceeds runtime step limit")
		return false
	end
	if #loaded.persistence_checks > 32 then
		fail("persistence plan exceeds runtime check limit")
		return false
	end
	local routeCount = 0
	for _ in pairs(loaded.routes) do
		routeCount = routeCount + 1
	end
	if routeCount > 0 then
		routeExecutor = loadHostLuaModule(ROUTE_EXECUTOR_PATH, "route executor")
		if type(routeExecutor) ~= "table" or type(routeExecutor.execute) ~= "function" then
			fail("invalid route executor contract")
			return false
		end
	end
	plan = loaded
	appendEvent("plan_steps", #plan.steps)
	appendEvent("route_plans", routeCount)
	appendEvent("persistence_checks", #plan.persistence_checks)
	return true
end

connect(g_game, {
	onLogin = function()
		appendEvent("protocol_login_" .. phase, "received")
	end,
	onPendingGame = function()
		appendEvent("pending_game_" .. phase, "received")
	end,
	onEnterGame = function()
		appendEvent("enter_game_" .. phase, "received")
	end,
	onGameStart = function()
		enteringWorld = false
		phaseStarted = true
		appendEvent("login_" .. phase, "success")
		local expectedPhase = phase
		scheduleEvent(function()
			if not finished and expectedPhase == phase and phaseStarted and g_game.isOnline() then
				appendEvent("online_stable_" .. phase, "confirmed")
			end
		end, 1500)
		if phase == 1 then
			waitForInitialPositionAndStartPlan()
		elseif plan and #plan.persistence_checks > 0 then
			scheduleEvent(function()
				runNextPersistenceCheck()
			end, 1800)
		else
			scheduleEvent(function()
				requestLogout(expectedPhase)
			end, SESSION_HOLD_MS)
		end
	end,
	onGameEnd = function()
		enteringWorld = false
		if not phaseStarted then
			fail("game ended before phase " .. tostring(phase) .. " entered the world")
			return
		end
		if not logoutRequested then
			fail("unexpected disconnect before safe logout in phase " .. tostring(phase))
			return
		end
		appendEvent("logout_" .. phase, "complete")
		phaseStarted = false
		logoutRequested = false
		appendEvent("transport_closed_" .. phase, "confirmed")
		if phase == 1 then
			phase = 2
			waitingForServerPersistence = true
			appendEvent("server_persistence_1", "waiting")
			waitForServerPersistence()
			return
		end
		finished = true
		appendEvent("duration_seconds", os.time() - startedAt)
		appendEvent("e2e", "success")
		exitSoon()
	end,
	onSessionEnd = function(reason)
		appendEvent("session_end_" .. phase, tostring(reason))
	end,
	onLoginAdvice = function(message)
		appendEvent("login_advice_" .. phase, tostring(message))
	end,
	onLoginWait = function(message, time)
		appendEvent("login_wait_" .. phase, string.format("%s/%s", tostring(message), tostring(time)))
	end,
	onUpdateNeeded = function(signature)
		appendEvent("update_needed_" .. phase, tostring(signature))
	end,
	onConnectionFailing = function(failing)
		appendEvent("connection_failing_" .. phase, tostring(failing))
	end,
	onPing = function()
		appendEvent("server_ping_" .. phase, "received")
	end,
	onPingBack = function()
		appendEvent("server_ping_back_" .. phase, "received")
	end,
	onLoginError = function(message)
		enteringWorld = false
		fail("login error in phase " .. tostring(phase) .. ": " .. tostring(message))
	end,
	onConnectionError = function(message, code)
		enteringWorld = false
		fail(string.format("connection error in phase %d (%s): %s", phase, tostring(code), tostring(message)))
	end,
})

local previous = io.open(EVENTS_PATH, "w")
if previous then
	previous:write("timestamp\tkey\tvalue\n")
	previous:close()
end

g_logger.setLogFile(INTERNAL_LOG_PATH)
appendEvent("scenario", SCENARIO_KEY)
appendEvent("client_version", CLIENT_VERSION)
appendEvent("driver", "generic-gameplay-plan-v3")
installStartupProfile()
if not finished and loadPlan() then
	scheduleEvent(startLogin, 2500)
end
scheduleEvent(function()
	if not finished then
		fail("global timeout after " .. tostring(GLOBAL_TIMEOUT_SECONDS) .. " seconds")
	end
end, GLOBAL_TIMEOUT_SECONDS * 1000)
