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
local PRIMARY_ARTIFACT_DIR = os.getenv("AGENT_E2E_PRIMARY_ARTIFACT_DIR") or ""
local RELEASE_FILE = os.getenv("AGENT_E2E_SECONDARY_RELEASE_FILE") or ""
local SCENARIO_KEY = os.getenv("AGENT_E2E_SCENARIO_KEY") or "unknown#secondary"
local GLOBAL_TIMEOUT_SECONDS = tonumber(os.getenv("AGENT_E2E_GLOBAL_TIMEOUT_SECONDS") or "110")
local RELOG_DELAY_MS = tonumber(os.getenv("AGENT_E2E_RELOG_DELAY_MS") or "1500")

local BACKPACK_SLOT = 3
local RESOURCE_ITEM_ID = 3043
local EVENTS_PATH = ARTIFACT_DIR .. "/client-events.tsv"
local INTERNAL_LOG_PATH = ARTIFACT_DIR .. "/otclient.internal.log"
local RELOG_SIGNAL_PATH = PRIMARY_ARTIFACT_DIR .. "/trade-relog-go"

local phase = 1
local phaseStarted = false
local enteringWorld = false
local logoutRequested = false
local finished = false
local readyForTrade = false
local tradeOfferObserved = false
local tradeClosed = false
local immediateCheckStarted = false
local lastSuccessfulStep = "bootstrap"
local startedAt = os.time()

local function sanitize(value)
	return tostring(value):gsub("[\t\r\n]", " ")
end

local function appendEvent(key, value)
	local file = assert(io.open(EVENTS_PATH, "a"))
	file:write(string.format("%d\t%s\t%s\n", os.time(), sanitize(key), sanitize(value)))
	file:close()
	g_logger.info(string.format("[agent-e2e-trade-secondary] %s=%s", tostring(key), tostring(value)))
end

local function markStep(step)
	lastSuccessfulStep = step
	appendEvent("trade_last_successful_step", step)
end

local function fileExists(path)
	if path == "" then
		return false
	end
	local file = io.open(path, "r")
	if not file then
		return false
	end
	file:close()
	return true
end

local function positionString(creature)
	if not creature then
		return "unavailable"
	end
	local position = creature:getPosition()
	if not position then
		return "unavailable"
	end
	return string.format("%d,%d,%d", position.x, position.y, position.z)
end

local function localPositionString()
	return positionString(g_game.getLocalPlayer())
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

local function exitSoon()
	scheduleEvent(function()
		g_app.exit()
	end, 250)
end

local function fail(step, expected, observed)
	if finished then
		return
	end
	finished = true
	appendEvent("failure_actor", CHARACTER)
	appendEvent("failure_client", "secondary")
	appendEvent("failure_last_successful_step", lastSuccessfulStep)
	appendEvent("failure_first_failed_step", step)
	appendEvent("failure_expected", expected)
	appendEvent("failure_observed", observed)
	appendEvent("failure_secondary_position", localPositionString())
	appendEvent("failure_primary_position", positionString(findVisibleCreature(PRIMARY_CHARACTER)))
	appendEvent("e2e", "failure")
	appendEvent("error", string.format("%s expected=%s observed=%s", step, expected, observed))
	if g_game.isOnline() then
		g_game.safeLogout()
	end
	exitSoon()
end

local function resourceCount()
	local player = g_game.getLocalPlayer()
	if not player then
		return -1
	end
	local total = 0
	for slot = 1, 10 do
		local item = player:getInventoryItem(slot)
		if item and item:getId() == RESOURCE_ITEM_ID then
			total = total + item:getCount()
		end
	end
	for _, container in pairs(g_game.getContainers()) do
		if container then
			for _, item in ipairs(container:getItems()) do
				if item and item:getId() == RESOURCE_ITEM_ID then
					total = total + item:getCount()
				end
			end
		end
	end
	return total
end

local function openStarterBackpack(onReady)
	local player = g_game.getLocalPlayer()
	local backpack = player and player:getInventoryItem(BACKPACK_SLOT) or nil
	if not backpack then
		fail("starter_backpack", "starter backpack in inventory slot 3", "missing")
		return
	end
	local containerId = g_game.open(backpack, nil)
	if containerId == nil or containerId < 0 then
		fail("starter_backpack_open", "starter backpack open request accepted", tostring(containerId))
		return
	end
	local checks = 100
	local function poll()
		if finished or not phaseStarted then
			return
		end
		if g_game.getContainer(containerId) then
			appendEvent("trade_backpack_open_" .. phase, "confirmed")
			onReady()
			return
		end
		checks = checks - 1
		if checks <= 0 then
			fail("starter_backpack_open", "opened starter backpack visible to controlled client", "timeout")
			return
		end
		scheduleEvent(poll, 100)
	end
	poll()
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
	if ACCOUNT == "" or PASSWORD_ENV == "" or PASSWORD == "" or CHARACTER == "" or PRIMARY_CHARACTER == "" or PRIMARY_ARTIFACT_DIR == "" then
		fail("secondary_environment", "complete bounded secondary actor environment", "missing required field")
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

local function waitForFinalRelease()
	local checks = 300
	local function poll()
		if finished or phase ~= 2 or not phaseStarted then
			return
		end
		if fileExists(RELEASE_FILE) then
			appendEvent("release", "received")
			markStep("final_release_received")
			requestLogout(2)
			return
		end
		checks = checks - 1
		if checks <= 0 then
			fail("final_release", "primary releases secondary after relog assertions", "timeout")
			return
		end
		scheduleEvent(poll, 100)
	end
	poll()
end

local function waitForRelogSignal()
	local checks = 300
	local function poll()
		if finished or phase ~= 1 or not phaseStarted then
			return
		end
		if fileExists(RELOG_SIGNAL_PATH) then
			markStep("relog_signal_received")
			requestLogout(1)
			return
		end
		checks = checks - 1
		if checks <= 0 then
			fail("relog_signal", "primary confirms immediate conservation and requests relog", "timeout")
			return
		end
		scheduleEvent(poll, 100)
	end
	poll()
end

local function waitForImmediateOwnership()
	if immediateCheckStarted then
		return
	end
	immediateCheckStarted = true
	local checks = 200
	local function poll()
		if finished or phase ~= 1 or not phaseStarted then
			return
		end
		local count = resourceCount()
		if tradeClosed and count == 1 then
			appendEvent("trade_immediate_secondary", "1")
			appendEvent("trade_position_secondary", localPositionString())
			markStep("immediate_secondary_ownership_confirmed")
			waitForRelogSignal()
			return
		end
		checks = checks - 1
		if checks <= 0 then
			fail("immediate_secondary_ownership", "closed trade and exactly one item 3043 in Player B inventory", string.format("tradeClosed=%s count=%d", tostring(tradeClosed), count))
			return
		end
		scheduleEvent(poll, 100)
	end
	poll()
end

local function observeTradeOffer()
	if phase ~= 1 or not readyForTrade or tradeOfferObserved then
		return
	end
	tradeOfferObserved = true
	appendEvent("trade_offer_secondary", "observed")
	appendEvent("trade_position_secondary", localPositionString())
	markStep("trade_offer_observed")
	scheduleEvent(function()
		if finished or phase ~= 1 or not phaseStarted then
			return
		end
		g_game.acceptTrade()
		appendEvent("trade_accept_secondary", "sent")
		markStep("trade_accept_sent")
	end, 100)
end

local function waitForPrimaryVisibilityAndPrecondition()
	local checks = 250
	local function poll()
		if finished or phase ~= 1 or not phaseStarted then
			return
		end
		local primary = findVisibleCreature(PRIMARY_CHARACTER)
		local count = resourceCount()
		if primary and count == 0 then
			readyForTrade = true
			appendEvent("trade_secondary_peer_visible", PRIMARY_CHARACTER)
			appendEvent("trade_fixture_precondition_secondary", "empty")
			appendEvent("trade_position_secondary", localPositionString())
			markStep("primary_visible_and_empty_resource_precondition")
			return
		end
		if count > 0 then
			fail("fixture_precondition", "Player B has zero item 3043 before trade", tostring(count))
			return
		end
		checks = checks - 1
		if checks <= 0 then
			fail("primary_visibility", "primary player visible with zero item 3043", string.format("visible=%s count=%d", tostring(primary ~= nil), count))
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
			openStarterBackpack(function()
				if phase == 1 then
					markStep("secondary_online_with_backpack_open")
					waitForPrimaryVisibilityAndPrecondition()
				else
					local count = resourceCount()
					if count ~= 1 then
						fail("relog_secondary_ownership", "exactly one item 3043 after relog", tostring(count))
						return
					end
					appendEvent("trade_relog_secondary", "1")
					appendEvent("trade_position_secondary", localPositionString())
					markStep("secondary_relog_ownership_confirmed")
					waitForFinalRelease()
				end
			end)
		end, 1500)
	end,
	onGameEnd = function()
		enteringWorld = false
		if not phaseStarted then
			fail("logout_" .. tostring(phase), "active game session before logout", "game ended before phase start")
			return
		end
		if not logoutRequested then
			fail("logout_" .. tostring(phase), "coordinated safe logout", "unexpected disconnect")
			return
		end
		appendEvent("logout_" .. phase, "complete")
		appendEvent("transport_closed_" .. phase, "confirmed")
		phaseStarted = false
		logoutRequested = false
		if phase == 1 then
			phase = 2
			markStep("secondary_phase_one_logout_complete")
			scheduleEvent(startLogin, RELOG_DELAY_MS)
			return
		end
		finished = true
		appendEvent("duration_seconds", os.time() - startedAt)
		appendEvent("e2e", "success")
		exitSoon()
	end,
	onOwnTrade = function()
		observeTradeOffer()
	end,
	onCounterTrade = function()
		observeTradeOffer()
	end,
	onCloseTrade = function()
		if phase == 1 and not tradeClosed then
			tradeClosed = true
			appendEvent("trade_close_secondary", "observed")
			markStep("trade_close_observed")
			waitForImmediateOwnership()
		end
	end,
	onLoginError = function(message)
		enteringWorld = false
		fail("login_" .. tostring(phase), "successful login", tostring(message))
	end,
	onConnectionError = function(message, code)
		enteringWorld = false
		fail("connection_" .. tostring(phase), "stable controlled connection", string.format("%s: %s", tostring(code), tostring(message)))
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
appendEvent("actor", os.getenv("AGENT_E2E_ACTOR_ID") or "trade-b")
appendEvent("driver", "e2e-qri-001-trade-secondary-v2")
scheduleEvent(startLogin, 1500)
scheduleEvent(function()
	if not finished then
		fail("global_timeout", "secondary completes within bounded timeout", tostring(GLOBAL_TIMEOUT_SECONDS) .. " seconds elapsed")
	end
end, GLOBAL_TIMEOUT_SECONDS * 1000)
