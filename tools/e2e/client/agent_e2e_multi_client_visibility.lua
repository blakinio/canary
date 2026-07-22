local CLIENT_VERSION = tonumber(os.getenv("AGENT_E2E_CLIENT_VERSION") or "1525")
local ACCOUNT = os.getenv("AGENT_E2E_ACCOUNT") or "@test1"
local PASSWORD = os.getenv("AGENT_E2E_PASSWORD") or ""
local CHARACTER = os.getenv("AGENT_E2E_CHARACTER") or "Knight 1"
local WORLD = os.getenv("AGENT_E2E_WORLD") or "Canary E2E"
local HOST = os.getenv("AGENT_E2E_HOST") or "127.0.0.1"
local GAME_PORT = tonumber(os.getenv("AGENT_E2E_GAME_PORT") or "7172")
local ARTIFACT_DIR = os.getenv("AGENT_E2E_ARTIFACT_DIR") or "../artifacts"
local GLOBAL_TIMEOUT_SECONDS = tonumber(os.getenv("AGENT_E2E_GLOBAL_TIMEOUT_SECONDS") or "180")
local RELOG_DELAY_MS = tonumber(os.getenv("AGENT_E2E_RELOG_DELAY_MS") or "1500")
local SCENARIO_KEY = os.getenv("AGENT_E2E_SCENARIO_KEY") or "multiclient/shared-world-visibility"
local OTCLIENT_ROOT = os.getenv("AGENT_E2E_OTCLIENT_ROOT") or ""
local OTCLIENT_BIN = os.getenv("OTCLIENT_BIN") or ""
local DB_HOST = os.getenv("DB_HOST") or "127.0.0.1"
local DB_PORT = tonumber(os.getenv("DB_PORT") or "3306")
local DB_USER = os.getenv("DB_USER") or "root"
local DB_NAME = os.getenv("DB_NAME") or "agent_e2e"

local EVENTS_PATH = ARTIFACT_DIR .. "/client-events.tsv"
local INTERNAL_LOG_PATH = ARTIFACT_DIR .. "/otclient.internal.log"
local MANIFEST_PATH = ARTIFACT_DIR .. "/scenario-manifest.json"
local SECONDARY_ENV_PATH = ARTIFACT_DIR .. "/multi-client-secondary.env"

local phase = 1
local phaseStarted = false
local logoutRequested = false
local enteringWorld = false
local waitingForServerPersistence = false
local finished = false
local secondaryStarted = false
local secondaryReleased = false
local secondaryEnv = nil
local secondaryArtifactDir = nil
local startedAt = os.time()
local multiClient = nil

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
	g_logger.info(string.format("[agent-e2e-multiclient] %s=%s", tostring(key), tostring(value)))
end

local function exitSoon()
	scheduleEvent(function()
		g_app.exit()
	end, 250)
end

local function readFile(path)
	local file = io.open(path, "r")
	if not file then
		return nil
	end
	local content = file:read("*a") or ""
	file:close()
	return content
end

local function integerFile(path)
	return tonumber((readFile(path) or ""):match("%-?%d+"))
end

local function loadHostLuaModule(path, label)
	local source = readFile(path)
	if not source then
		return nil, "failed to open " .. label
	end
	local chunk, compileError = load(source, "@" .. path)
	if not chunk then
		return nil, "failed to compile " .. label .. ": " .. tostring(compileError)
	end
	local ok, loaded = pcall(chunk)
	if not ok then
		return nil, "failed to execute " .. label .. ": " .. tostring(loaded)
	end
	return loaded, nil
end

local function fail(message)
	if finished then
		return
	end
	finished = true
	if multiClient and secondaryArtifactDir then
		multiClient.stopSecondary(secondaryArtifactDir)
	end
	appendEvent("e2e", "failure")
	appendEvent("error", message)
	exitSoon()
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

local function configureTransportFeatures()
	g_game.disableFeature(GameClientPing)
	g_game.disableFeature(GameExtendedClientPing)
	appendEvent("ping_features_" .. phase, "disabled")
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
	configureTransportFeatures()
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

local function prepareSecondary()
	if secondaryStarted then
		return true
	end
	if OTCLIENT_ROOT == "" or OTCLIENT_BIN == "" then
		fail("multi-client runtime requires AGENT_E2E_OTCLIENT_ROOT and OTCLIENT_BIN")
		return false
	end
	local repoRoot = OTCLIENT_ROOT:match("^(.*)/[^/]+$")
	if not repoRoot or repoRoot == "" then
		fail("cannot derive repository root from AGENT_E2E_OTCLIENT_ROOT")
		return false
	end
	local materializer = repoRoot .. "/tools/e2e/multi_client_orchestration.py"
	local helperPath = repoRoot .. "/tools/e2e/client/agent_e2e_multi_client.lua"
	local secondaryAutomation = repoRoot .. "/tools/e2e/client/agent_e2e_multi_client_secondary.lua"
	local command = string.format("python3 %s --manifest %s --artifact-dir %s", shellQuote(materializer), shellQuote(MANIFEST_PATH), shellQuote(ARTIFACT_DIR))
	local result = os.execute(command)
	if result ~= true and result ~= 0 then
		fail("multi-client actor materialization failed")
		return false
	end
	local loaded, loadError = loadHostLuaModule(helperPath, "multi-client helper")
	if type(loaded) ~= "table" or type(loaded.spawnSecondary) ~= "function" or type(loaded.hasEvent) ~= "function" or type(loaded.writeRelease) ~= "function" then
		fail(loadError or "invalid multi-client helper contract")
		return false
	end
	multiClient = loaded
	local values, envError = multiClient.readEnvFile(SECONDARY_ENV_PATH)
	if not values then
		fail(envError or "cannot load secondary actor environment")
		return false
	end
	secondaryEnv = values
	secondaryArtifactDir = secondaryEnv.AGENT_E2E_ARTIFACT_DIR
	secondaryEnv.AGENT_E2E_CLIENT_VERSION = tostring(CLIENT_VERSION)
	secondaryEnv.AGENT_E2E_WORLD = WORLD
	secondaryEnv.AGENT_E2E_HOST = HOST
	secondaryEnv.AGENT_E2E_GAME_PORT = tostring(GAME_PORT)
	secondaryEnv.AGENT_E2E_OTCLIENT_ROOT = OTCLIENT_ROOT
	local ok, spawnError = multiClient.spawnSecondary({
		otclientRoot = OTCLIENT_ROOT,
		otclientBin = OTCLIENT_BIN,
		automationSource = secondaryAutomation,
		artifactDir = secondaryArtifactDir,
		env = secondaryEnv,
		timeoutSeconds = math.min(GLOBAL_TIMEOUT_SECONDS, 120),
	})
	if not ok then
		fail(spawnError or "secondary OTClient launch failed")
		return false
	end
	secondaryStarted = true
	appendEvent("multi_client_secondary_started", secondaryEnv.AGENT_E2E_ACTOR_ID)
	return true
end

local function waitForSecondaryCompletion()
	local checks = 300
	local eventsPath = secondaryArtifactDir .. "/client-events.tsv"
	local exitPath = secondaryArtifactDir .. "/otclient-exit-code.txt"
	local function poll()
		if finished then
			return
		end
		if multiClient.hasEvent(eventsPath, "e2e", "failure") then
			fail("secondary actor reported failure")
			return
		end
		if multiClient.hasEvent(eventsPath, "e2e", "success") then
			local exitCode = integerFile(exitPath)
			if exitCode == nil then
				scheduleEvent(poll, 100)
				return
			end
			if exitCode ~= 0 then
				fail("secondary actor exit code=" .. tostring(exitCode))
				return
			end
			appendEvent("multi_client_secondary_exit", "clean")
			requestLogout(1)
			return
		end
		checks = checks - 1
		if checks <= 0 then
			fail("secondary actor completion timeout")
			return
		end
		scheduleEvent(poll, 100)
	end
	poll()
end

local function waitForMutualVisibility()
	local checks = 200
	local secondaryCharacter = secondaryEnv.AGENT_E2E_CHARACTER
	local secondaryEvents = secondaryArtifactDir .. "/client-events.tsv"
	local function poll()
		if finished then
			return
		end
		local primarySeesSecondary = findVisibleCreature(secondaryCharacter) ~= nil
		local secondarySeesPrimary = multiClient.hasEvent(secondaryEvents, "peer_visible", CHARACTER)
		if primarySeesSecondary and secondarySeesPrimary then
			appendEvent("multi_client_primary_peer_visible", secondaryCharacter)
			appendEvent("multi_client_secondary_peer_visible", CHARACTER)
			appendEvent("multi_client_mutual_visibility", "confirmed")
			local ok, releaseError = multiClient.writeRelease(secondaryEnv.AGENT_E2E_SECONDARY_RELEASE_FILE)
			if not ok then
				fail(releaseError or "failed to release secondary actor")
				return
			end
			secondaryReleased = true
			appendEvent("multi_client_secondary_release", "sent")
			waitForSecondaryCompletion()
			return
		end
		if multiClient.hasEvent(secondaryEvents, "e2e", "failure") then
			fail("secondary actor failed before mutual visibility")
			return
		end
		checks = checks - 1
		if checks <= 0 then
			fail(string.format("mutual visibility timeout primarySeesSecondary=%s secondarySeesPrimary=%s", tostring(primarySeesSecondary), tostring(secondarySeesPrimary)))
			return
		end
		scheduleEvent(poll, 100)
	end
	poll()
end

connect(g_game, {
	onLogin = function()
		appendEvent("protocol_login_" .. phase, "received")
	end,
	onGameStart = function()
		enteringWorld = false
		phaseStarted = true
		appendEvent("login_" .. phase, "success")
		local expectedPhase = phase
		scheduleEvent(function()
			if finished or expectedPhase ~= phase or not phaseStarted or not g_game.isOnline() then
				return
			end
			appendEvent("online_stable_" .. phase, "confirmed")
			if phase == 1 then
				appendEvent("multi_client_primary_online", "confirmed")
				if prepareSecondary() then
					waitForMutualVisibility()
				end
			else
				scheduleEvent(function()
					requestLogout(2)
				end, 1500)
			end
		end, 1500)
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
			if not secondaryStarted or not secondaryReleased then
				fail("primary phase one ended before secondary lifecycle completed")
				return
			end
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
appendEvent("driver", "bounded-multi-client-primary-v1")
scheduleEvent(startLogin, 2500)
scheduleEvent(function()
	if not finished then
		fail("global timeout after " .. tostring(GLOBAL_TIMEOUT_SECONDS) .. " seconds")
	end
end, GLOBAL_TIMEOUT_SECONDS * 1000)
