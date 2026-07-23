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
local SCENARIO_KEY = os.getenv("AGENT_E2E_SCENARIO_KEY") or "recovery/client-disconnect-recovery"

local EVENTS_PATH = ARTIFACT_DIR .. "/client-events.tsv"
local INTERNAL_LOG_PATH = ARTIFACT_DIR .. "/otclient.internal.log"

local phase = 1
local phaseStarted = false
local enteringWorld = false
local safeLogoutRequested = false
local injectedDisconnectPending = false
local injectedDisconnectObserved = false
local finished = false
local startedAt = os.time()

local function sanitize(value)
	return tostring(value):gsub("[\t\r\n]", " ")
end

local function appendEvent(key, value)
	local file = assert(io.open(EVENTS_PATH, "a"))
	file:write(string.format("%d\t%s\t%s\n", os.time(), sanitize(key), sanitize(value)))
	file:close()
	g_logger.info(string.format("[agent-e2e-recovery] %s=%s", tostring(key), tostring(value)))
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
	if g_game.isOnline() then
		g_game.forceLogout()
	end
	exitSoon()
end

local function configureTransportFeatures()
	g_game.disableFeature(GameClientPing)
	g_game.disableFeature(GameExtendedClientPing)
	appendEvent("ping_features_" .. phase, "disabled")
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
	safeLogoutRequested = false
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

local function injectClientDisconnect()
	if finished or phase ~= 1 or not phaseStarted or not g_game.isOnline() or injectedDisconnectPending or injectedDisconnectObserved then
		return
	end
	injectedDisconnectPending = true
	appendEvent("fault_injection", "client_force_logout")
	appendEvent("fault_expected", "client_disconnect")
	g_game.forceLogout()
end

local function requestRecoveryCleanup()
	if finished or phase ~= 2 or not phaseStarted or safeLogoutRequested then
		return
	end
	safeLogoutRequested = true
	appendEvent("logout_request_2", "safe")
	g_game.safeLogout()
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
				appendEvent("recovery_baseline", "confirmed")
				scheduleEvent(injectClientDisconnect, 500)
			else
				if not injectedDisconnectObserved then
					fail("recovery login started without observing the injected disconnect")
					return
				end
				appendEvent("recovery_login", "success")
				appendEvent("recovery_online", "confirmed")
				scheduleEvent(requestRecoveryCleanup, 1500)
			end
		end, 1500)
	end,
	onGameEnd = function()
		enteringWorld = false
		if not phaseStarted then
			fail("game ended before phase " .. tostring(phase) .. " entered the world")
			return
		end

		if phase == 1 and injectedDisconnectPending then
			injectedDisconnectPending = false
			injectedDisconnectObserved = true
			phaseStarted = false
			appendEvent("fault_observed", "client_disconnect")
			appendEvent("fault_classification", "expected_injected_failure")
			phase = 2
			appendEvent("recovery_state", "relogin_pending")
			scheduleEvent(startLogin, RELOG_DELAY_MS)
			return
		end

		if phase == 2 and safeLogoutRequested then
			appendEvent("logout_2", "complete")
			appendEvent("cleanup", "safe_logout_complete")
			phaseStarted = false
			safeLogoutRequested = false
			finished = true
			appendEvent("duration_seconds", os.time() - startedAt)
			appendEvent("e2e", "success")
			exitSoon()
			return
		end

		fail("unexpected disconnect in phase " .. tostring(phase))
	end,
	onLoginError = function(message)
		enteringWorld = false
		fail("login error in phase " .. tostring(phase) .. ": " .. tostring(message))
	end,
	onConnectionError = function(message, code)
		enteringWorld = false
		if phase == 1 and injectedDisconnectPending then
			appendEvent("fault_transport_signal", string.format("%s:%s", tostring(code), tostring(message)))
			return
		end
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
appendEvent("driver", "bounded-client-disconnect-recovery-v1")
scheduleEvent(startLogin, 2500)
scheduleEvent(function()
	if not finished then
		fail("global timeout after " .. tostring(GLOBAL_TIMEOUT_SECONDS) .. " seconds")
	end
end, GLOBAL_TIMEOUT_SECONDS * 1000)
