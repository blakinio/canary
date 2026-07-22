local CLIENT_VERSION = tonumber(os.getenv("AGENT_E2E_CLIENT_VERSION") or "1525")
local ACCOUNT = os.getenv("AGENT_E2E_ACCOUNT") or ""
local PASSWORD_ENV = os.getenv("AGENT_E2E_PASSWORD_ENV") or ""
local PASSWORD = PASSWORD_ENV ~= "" and (os.getenv(PASSWORD_ENV) or "") or ""
local CHARACTER = os.getenv("AGENT_E2E_CHARACTER") or ""
local PRIMARY_CHARACTER = os.getenv("AGENT_E2E_PRIMARY_CHARACTER") or ""
local WORLD = os.getenv("AGENT_E2E_WORLD") or "Canary E2E"
local HOST = os.getenv("AGENT_E2E_HOST") or "127.0.0.1"
local GAME_PORT = tonumber(os.getenv("AGENT_E2E_GAME_PORT") or "7172")
local ARTIFACT_DIR = os.getenv("AGENT_E2E_ARTIFACT_DIR") or "../artifacts/secondary"
local RELEASE_FILE = os.getenv("AGENT_E2E_SECONDARY_RELEASE_FILE") or ""
local SCENARIO_KEY = os.getenv("AGENT_E2E_SCENARIO_KEY") or "unknown#secondary"
local GLOBAL_TIMEOUT_SECONDS = 90

local EVENTS_PATH = ARTIFACT_DIR .. "/client-events.tsv"
local INTERNAL_LOG_PATH = ARTIFACT_DIR .. "/otclient.internal.log"
local PACKET_RECORD = ARTIFACT_DIR .. "/session-1.record"

local finished = false
local online = false
local logoutRequested = false

local function sanitize(value)
	return tostring(value):gsub("[\t\r\n]", " ")
end

local function appendEvent(key, value)
	local file = assert(io.open(EVENTS_PATH, "a"))
	file:write(string.format("%d\t%s\t%s\n", os.time(), sanitize(key), sanitize(value)))
	file:close()
	g_logger.info(string.format("[agent-e2e-secondary] %s=%s", tostring(key), tostring(value)))
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
	if online then
		g_game.safeLogout()
	end
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

local function releaseReady()
	if RELEASE_FILE == "" then
		return false
	end
	local file = io.open(RELEASE_FILE, "r")
	if not file then
		return false
	end
	file:close()
	return true
end

local function waitForRelease()
	local checks = 300
	local function poll()
		if finished or not online then
			return
		end
		if releaseReady() then
			appendEvent("release", "received")
			logoutRequested = true
			appendEvent("logout_request_1", "safe")
			g_game.safeLogout()
			return
		end
		checks = checks - 1
		if checks <= 0 then
			fail("secondary release timeout")
			return
		end
		scheduleEvent(poll, 100)
	end
	poll()
end

local function waitForPrimary()
	local checks = 200
	local function poll()
		if finished or not online then
			return
		end
		if findVisibleCreature(PRIMARY_CHARACTER) then
			appendEvent("peer_visible", PRIMARY_CHARACTER)
			waitForRelease()
			return
		end
		checks = checks - 1
		if checks <= 0 then
			fail("primary character not visible: " .. tostring(PRIMARY_CHARACTER))
			return
		end
		scheduleEvent(poll, 100)
	end
	poll()
end

local function startLogin()
	if ACCOUNT == "" or PASSWORD_ENV == "" or PASSWORD == "" or CHARACTER == "" or PRIMARY_CHARACTER == "" then
		fail("secondary actor environment is incomplete")
		return
	end
	g_game.setClientVersion(CLIENT_VERSION)
	g_game.setProtocolVersion(g_game.getClientProtocolVersion(CLIENT_VERSION))
	g_game.disableFeature(GameClientPing)
	g_game.disableFeature(GameExtendedClientPing)
	g_game.chooseRsa(HOST)
	local sessionKey = ACCOUNT .. "\n" .. PASSWORD
	appendEvent("login_request_1", string.format("%s:%d/%s/%s/v%d", HOST, GAME_PORT, WORLD, CHARACTER, CLIENT_VERSION))
	appendEvent("packet_record_1", PACKET_RECORD)
	g_game.loginWorld(ACCOUNT, PASSWORD, WORLD, HOST, GAME_PORT, CHARACTER, "", sessionKey, PACKET_RECORD)
end

connect(g_game, {
	onGameStart = function()
		online = true
		appendEvent("login_1", "success")
		scheduleEvent(function()
			if not finished and online and g_game.isOnline() then
				appendEvent("online_stable_1", "confirmed")
				waitForPrimary()
			end
		end, 1500)
	end,
	onGameEnd = function()
		online = false
		if finished then
			return
		end
		if not logoutRequested then
			fail("secondary game ended before coordinated safe logout")
			return
		end
		appendEvent("logout_1", "complete")
		appendEvent("transport_closed_1", "confirmed")
		finished = true
		appendEvent("e2e", "success")
		exitSoon()
	end,
	onLoginError = function(message)
		fail("secondary login error: " .. tostring(message))
	end,
	onConnectionError = function(message, code)
		fail(string.format("secondary connection error (%s): %s", tostring(code), tostring(message)))
	end,
})

os.execute("mkdir -p '" .. ARTIFACT_DIR:gsub("'", "'\\''") .. "'")
local previous = io.open(EVENTS_PATH, "w")
if previous then
	previous:write("timestamp\tkey\tvalue\n")
	previous:close()
end

g_logger.setLogFile(INTERNAL_LOG_PATH)
appendEvent("scenario", SCENARIO_KEY)
appendEvent("actor", os.getenv("AGENT_E2E_ACTOR_ID") or "secondary")
appendEvent("driver", "bounded-multi-client-secondary-v1")
scheduleEvent(startLogin, 1500)
scheduleEvent(function()
	if not finished then
		fail("secondary global timeout after " .. tostring(GLOBAL_TIMEOUT_SECONDS) .. " seconds")
	end
end, GLOBAL_TIMEOUT_SECONDS * 1000)
