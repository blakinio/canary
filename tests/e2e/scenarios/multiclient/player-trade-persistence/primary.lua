local CLIENT_VERSION = tonumber(os.getenv("AGENT_E2E_CLIENT_VERSION") or "1525")
local ACCOUNT = os.getenv("AGENT_E2E_ACCOUNT") or "@test15"
local PASSWORD = os.getenv("AGENT_E2E_PASSWORD") or ""
local CHARACTER = os.getenv("AGENT_E2E_CHARACTER") or "Paladin 15"
local WORLD = os.getenv("AGENT_E2E_WORLD") or "Canary E2E"
local HOST = os.getenv("AGENT_E2E_HOST") or "127.0.0.1"
local GAME_PORT = tonumber(os.getenv("AGENT_E2E_GAME_PORT") or "7172")
local ARTIFACT_DIR = os.getenv("AGENT_E2E_ARTIFACT_DIR") or "../artifacts"
local GLOBAL_TIMEOUT_SECONDS = tonumber(os.getenv("AGENT_E2E_GLOBAL_TIMEOUT_SECONDS") or "180")
local RELOG_DELAY_MS = tonumber(os.getenv("AGENT_E2E_RELOG_DELAY_MS") or "1500")
local SCENARIO_KEY = os.getenv("AGENT_E2E_SCENARIO_KEY") or "multiclient/player-trade-persistence"
local OTCLIENT_ROOT = os.getenv("AGENT_E2E_OTCLIENT_ROOT") or ""
local OTCLIENT_BIN = os.getenv("OTCLIENT_BIN") or ""

local BACKPACK_SLOT = 3
local RESOURCE_ITEM_ID = 3043
local EVENTS_PATH = ARTIFACT_DIR .. "/client-events.tsv"
local INTERNAL_LOG_PATH = ARTIFACT_DIR .. "/otclient.internal.log"
local MANIFEST_PATH = ARTIFACT_DIR .. "/scenario-manifest.json"
local SECONDARY_ENV_PATH = ARTIFACT_DIR .. "/multi-client-secondary.env"
local RELOG_SIGNAL_PATH = ARTIFACT_DIR .. "/trade-relog-go"

local phase = 1
local phaseStarted = false
local logoutRequested = false
local enteringWorld = false
local finished = false
local secondaryStarted = false
local secondaryEnv = nil
local secondaryArtifactDir = nil
local secondaryEventsPath = nil
local multiClient = nil
local primaryOfferObserved = false
local primaryTradeClosed = false
local lastSuccessfulStep = "bootstrap"
local startedAt = os.time()

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
	g_logger.info(string.format("[agent-e2e-trade-primary] %s=%s", tostring(key), tostring(value)))
end

local function markStep(step)
	lastSuccessfulStep = step
	appendEvent("trade_last_successful_step", step)
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

local function writeFile(path, content)
	local file, err = io.open(path, "w")
	if not file then
		return false, err
	end
	file:write(content)
	file:close()
	return true, nil
end

local function integerFile(path)
	return tonumber((readFile(path) or ""):match("%-?%d+"))
end

local function readEventValue(path, key)
	local content = readFile(path)
	if not content then
		return nil
	end
	local latest = nil
	for line in content:gmatch("[^\r\n]+") do
		local _, eventKey, value = line:match("^(.-)\t(.-)\t(.*)$")
		if eventKey == key then
			latest = value
		end
	end
	return latest
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
	if multiClient and secondaryArtifactDir then
		multiClient.stopSecondary(secondaryArtifactDir)
	end
	appendEvent("failure_actor", CHARACTER)
	appendEvent("failure_client", "primary")
	appendEvent("failure_last_successful_step", lastSuccessfulStep)
	appendEvent("failure_first_failed_step", step)
	appendEvent("failure_expected", expected)
	appendEvent("failure_observed", observed)
	appendEvent("failure_primary_position", localPositionString())
	appendEvent("failure_secondary_position", readEventValue(secondaryEventsPath or "", "trade_position_secondary") or "unavailable")
	appendEvent("e2e", "failure")
	appendEvent("error", string.format("%s expected=%s observed=%s", step, expected, observed))
	if g_game.isOnline() then
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

local function findResourceItem()
	local player = g_game.getLocalPlayer()
	if not player then
		return nil
	end
	for slot = 1, 10 do
		local item = player:getInventoryItem(slot)
		if item and item:getId() == RESOURCE_ITEM_ID then
			return item
		end
	end
	return g_game.findItemInContainers(RESOURCE_ITEM_ID, -1, 0)
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
	if PASSWORD == "" then
		fail("login_" .. tostring(phase), "non-empty AGENT_E2E_PASSWORD", "empty")
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

local function prepareSecondary()
	if secondaryStarted then
		return true
	end
	if OTCLIENT_ROOT == "" or OTCLIENT_BIN == "" then
		fail("secondary_start", "configured OTClient root and binary", "missing runtime path")
		return false
	end
	local repoRoot = OTCLIENT_ROOT:match("^(.*)/[^/]+$")
	if not repoRoot or repoRoot == "" then
		fail("secondary_start", "repository root derived from AGENT_E2E_OTCLIENT_ROOT", OTCLIENT_ROOT)
		return false
	end
	local materializer = repoRoot .. "/tools/e2e/multi_client_orchestration.py"
	local helperPath = repoRoot .. "/tools/e2e/client/agent_e2e_multi_client.lua"
	local secondaryAutomation = repoRoot .. "/tests/e2e/scenarios/multiclient/player-trade-persistence/secondary.lua"
	local command = string.format("python3 %s --manifest %s --artifact-dir %s", shellQuote(materializer), shellQuote(MANIFEST_PATH), shellQuote(ARTIFACT_DIR))
	local result = os.execute(command)
	if result ~= true and result ~= 0 then
		fail("secondary_materialization", "existing bounded two-client materializer succeeds", tostring(result))
		return false
	end
	local loaded, loadError = loadHostLuaModule(helperPath, "multi-client helper")
	if type(loaded) ~= "table" or type(loaded.spawnSecondary) ~= "function" or type(loaded.hasEvent) ~= "function" or type(loaded.writeRelease) ~= "function" then
		fail("secondary_helper", "valid canary-universal-e2e-two-client-orchestration-v1 helper", loadError or "invalid helper")
		return false
	end
	multiClient = loaded
	local values, envError = multiClient.readEnvFile(SECONDARY_ENV_PATH)
	if not values then
		fail("secondary_environment", "materialized secondary environment", envError or "missing")
		return false
	end
	secondaryEnv = values
	secondaryArtifactDir = secondaryEnv.AGENT_E2E_ARTIFACT_DIR
	secondaryEventsPath = secondaryArtifactDir .. "/client-events.tsv"
	secondaryEnv.AGENT_E2E_CLIENT_VERSION = tostring(CLIENT_VERSION)
	secondaryEnv.AGENT_E2E_WORLD = WORLD
	secondaryEnv.AGENT_E2E_HOST = HOST
	secondaryEnv.AGENT_E2E_GAME_PORT = tostring(GAME_PORT)
	secondaryEnv.AGENT_E2E_OTCLIENT_ROOT = OTCLIENT_ROOT
	secondaryEnv.AGENT_E2E_PRIMARY_ARTIFACT_DIR = ARTIFACT_DIR
	secondaryEnv.AGENT_E2E_RELOG_DELAY_MS = tostring(RELOG_DELAY_MS)
	secondaryEnv.AGENT_E2E_GLOBAL_TIMEOUT_SECONDS = tostring(math.min(GLOBAL_TIMEOUT_SECONDS, 110))
	local ok, spawnError = multiClient.spawnSecondary({
		otclientRoot = OTCLIENT_ROOT,
		otclientBin = OTCLIENT_BIN,
		automationSource = secondaryAutomation,
		artifactDir = secondaryArtifactDir,
		env = secondaryEnv,
		timeoutSeconds = math.min(GLOBAL_TIMEOUT_SECONDS, 120),
	})
	if not ok then
		fail("secondary_start", "secondary controlled OTClient starts", spawnError or "launch failed")
		return false
	end
	secondaryStarted = true
	appendEvent("multi_client_secondary_started", secondaryEnv.AGENT_E2E_ACTOR_ID)
	markStep("secondary_started")
	return true
end

local function waitForSecondaryCompletion()
	local checks = 400
	local exitPath = secondaryArtifactDir .. "/otclient-exit-code.txt"
	local function poll()
		if finished then
			return
		end
		if multiClient.hasEvent(secondaryEventsPath, "e2e", "failure") then
			fail("secondary_completion", "secondary e2e=success", "secondary e2e=failure")
			return
		end
		if multiClient.hasEvent(secondaryEventsPath, "e2e", "success") then
			local exitCode = integerFile(exitPath)
			if exitCode == nil then
				scheduleEvent(poll, 100)
				return
			end
			if exitCode ~= 0 then
				fail("secondary_completion", "secondary exit code 0", tostring(exitCode))
				return
			end
			appendEvent("multi_client_secondary_exit", "clean")
			markStep("secondary_cleanup_complete")
			requestLogout(2)
			return
		end
		checks = checks - 1
		if checks <= 0 then
			fail("secondary_completion", "secondary safe logout and clean exit", "timeout")
			return
		end
		scheduleEvent(poll, 100)
	end
	poll()
end

local function waitForRelogAssertions()
	local checks = 300
	local function poll()
		if finished or phase ~= 2 or not phaseStarted then
			return
		end
		local primaryCount = resourceCount()
		local secondaryReady = multiClient.hasEvent(secondaryEventsPath, "trade_relog_secondary", "1")
		if primaryCount == 0 and secondaryReady then
			appendEvent("trade_relog_primary", "0")
			appendEvent("trade_relog_secondary", "1")
			appendEvent("trade_relog_conservation", "1")
			appendEvent("trade_position_primary", localPositionString())
			appendEvent("trade_position_secondary", readEventValue(secondaryEventsPath, "trade_position_secondary") or "unavailable")
			markStep("relog_conservation_confirmed")
			local ok, releaseError = multiClient.writeRelease(secondaryEnv.AGENT_E2E_SECONDARY_RELEASE_FILE)
			if not ok then
				fail("secondary_release", "release file written", releaseError or "write failed")
				return
			end
			appendEvent("multi_client_secondary_release", "sent")
			waitForSecondaryCompletion()
			return
		end
		if multiClient.hasEvent(secondaryEventsPath, "e2e", "failure") then
			fail("relog_persistence", "primary=0 secondary=1 conservation=1", "secondary failed")
			return
		end
		checks = checks - 1
		if checks <= 0 then
			fail("relog_persistence", "primary=0 secondary=1 conservation=1", string.format("primary=%d secondaryReady=%s", primaryCount, tostring(secondaryReady)))
			return
		end
		scheduleEvent(poll, 100)
	end
	poll()
end

local function waitForImmediateAssertions()
	local checks = 300
	local function poll()
		if finished or phase ~= 1 or not phaseStarted then
			return
		end
		local primaryCount = resourceCount()
		local secondaryReady = multiClient.hasEvent(secondaryEventsPath, "trade_immediate_secondary", "1")
		local secondaryClosed = multiClient.hasEvent(secondaryEventsPath, "trade_close_secondary", "observed")
		if primaryTradeClosed and secondaryClosed and primaryCount == 0 and secondaryReady then
			appendEvent("trade_close_secondary", "observed")
			appendEvent("trade_immediate_primary", "0")
			appendEvent("trade_immediate_secondary", "1")
			appendEvent("trade_immediate_conservation", "1")
			appendEvent("trade_position_primary", localPositionString())
			appendEvent("trade_position_secondary", readEventValue(secondaryEventsPath, "trade_position_secondary") or "unavailable")
			markStep("immediate_conservation_confirmed")
			local ok, writeError = writeFile(RELOG_SIGNAL_PATH, "relog\n")
			if not ok then
				fail("relog_signal", "coordination signal written", writeError or "write failed")
				return
			end
			requestLogout(1)
			return
		end
		if multiClient.hasEvent(secondaryEventsPath, "e2e", "failure") then
			fail("immediate_conservation", "primary=0 secondary=1 conservation=1", "secondary failed")
			return
		end
		checks = checks - 1
		if checks <= 0 then
			fail("immediate_conservation", "closed trades and primary=0 secondary=1 conservation=1", string.format("primaryClosed=%s secondaryClosed=%s primary=%d secondaryReady=%s", tostring(primaryTradeClosed), tostring(secondaryClosed), primaryCount, tostring(secondaryReady)))
			return
		end
		scheduleEvent(poll, 100)
	end
	poll()
end

local function waitForSecondaryAccept()
	local checks = 200
	local function poll()
		if finished or phase ~= 1 or not phaseStarted then
			return
		end
		if multiClient.hasEvent(secondaryEventsPath, "trade_accept_secondary", "sent") then
			appendEvent("trade_accept_secondary", "sent")
			g_game.acceptTrade()
			appendEvent("trade_accept_primary", "sent")
			markStep("bilateral_trade_accept_sent")
			waitForImmediateAssertions()
			return
		end
		if multiClient.hasEvent(secondaryEventsPath, "e2e", "failure") then
			fail("trade_accept_secondary", "secondary acceptance", "secondary failed")
			return
		end
		checks = checks - 1
		if checks <= 0 then
			fail("trade_accept_secondary", "trade_accept_secondary=sent", "timeout")
			return
		end
		scheduleEvent(poll, 100)
	end
	poll()
end

local function waitForTradeOffers()
	local checks = 200
	local function poll()
		if finished or phase ~= 1 or not phaseStarted then
			return
		end
		local secondaryOffer = multiClient.hasEvent(secondaryEventsPath, "trade_offer_secondary", "observed")
		if primaryOfferObserved and secondaryOffer then
			appendEvent("trade_offer_secondary", "observed")
			markStep("bilateral_trade_offer_observed")
			waitForSecondaryAccept()
			return
		end
		if multiClient.hasEvent(secondaryEventsPath, "e2e", "failure") then
			fail("trade_offer", "both controlled clients observe trade", "secondary failed")
			return
		end
		checks = checks - 1
		if checks <= 0 then
			fail("trade_offer", "primary and secondary trade offers observed", string.format("primary=%s secondary=%s", tostring(primaryOfferObserved), tostring(secondaryOffer)))
			return
		end
		scheduleEvent(poll, 100)
	end
	poll()
end

local function initiateTrade()
	local secondaryCharacter = secondaryEnv.AGENT_E2E_CHARACTER
	local peer = findVisibleCreature(secondaryCharacter)
	local item = findResourceItem()
	local count = resourceCount()
	if not peer or not item or count ~= 1 then
		fail("trade_request", "visible secondary and exactly one item 3043 in Player A inventory", string.format("peer=%s item=%s count=%d", tostring(peer ~= nil), tostring(item ~= nil), count))
		return
	end
	appendEvent("trade_position_primary", localPositionString())
	g_game.requestTrade(item, peer)
	appendEvent("trade_request", "sent")
	markStep("trade_request_sent")
	waitForTradeOffers()
end

local function createFixture()
	g_game.talk("/i 3043, 1")
	local checks = 100
	local function poll()
		if finished or phase ~= 1 or not phaseStarted then
			return
		end
		local count = resourceCount()
		local item = findResourceItem()
		if count == 1 and item then
			appendEvent("trade_fixture_created", "item-3043")
			markStep("fixture_created")
			initiateTrade()
			return
		end
		checks = checks - 1
		if checks <= 0 then
			fail("fixture_creation", "exactly one item 3043 visible in Player A inventory", string.format("count=%d item=%s", count, tostring(item ~= nil)))
			return
		end
		scheduleEvent(poll, 100)
	end
	poll()
end

local function waitForMutualVisibilityAndPrecondition()
	local checks = 250
	local secondaryCharacter = secondaryEnv.AGENT_E2E_CHARACTER
	local function poll()
		if finished or phase ~= 1 or not phaseStarted then
			return
		end
		local peer = findVisibleCreature(secondaryCharacter)
		local secondarySeesPrimary = multiClient.hasEvent(secondaryEventsPath, "trade_secondary_peer_visible", CHARACTER)
		local secondaryEmpty = multiClient.hasEvent(secondaryEventsPath, "trade_fixture_precondition_secondary", "empty")
		if peer and secondarySeesPrimary and secondaryEmpty then
			local primaryCount = resourceCount()
			if primaryCount ~= 0 then
				fail("fixture_precondition", "Player A has zero item 3043 before fixture creation", tostring(primaryCount))
				return
			end
			appendEvent("trade_primary_peer_visible", secondaryCharacter)
			appendEvent("trade_secondary_peer_visible", CHARACTER)
			appendEvent("trade_mutual_visibility", "confirmed")
			appendEvent("trade_fixture_precondition", "empty")
			appendEvent("trade_position_primary", localPositionString())
			appendEvent("trade_position_secondary", readEventValue(secondaryEventsPath, "trade_position_secondary") or "unavailable")
			markStep("mutual_visibility_and_empty_resource_precondition")
			createFixture()
			return
		end
		if multiClient.hasEvent(secondaryEventsPath, "e2e", "failure") then
			fail("mutual_visibility", "both players visible with zero item 3043", "secondary failed")
			return
		end
		checks = checks - 1
		if checks <= 0 then
			fail("mutual_visibility", "both players visible with zero item 3043", string.format("primarySeesSecondary=%s secondarySeesPrimary=%s secondaryEmpty=%s", tostring(peer ~= nil), tostring(secondarySeesPrimary), tostring(secondaryEmpty)))
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
					appendEvent("trade_primary_online", "confirmed")
					markStep("primary_online_with_backpack_open")
					if prepareSecondary() then
						waitForMutualVisibilityAndPrecondition()
					end
				else
					markStep("primary_relogged_with_backpack_open")
					waitForRelogAssertions()
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
			markStep("primary_phase_one_logout_complete")
			scheduleEvent(startLogin, RELOG_DELAY_MS)
			return
		end
		finished = true
		appendEvent("duration_seconds", os.time() - startedAt)
		appendEvent("e2e", "success")
		exitSoon()
	end,
	onOwnTrade = function()
		if phase == 1 and not primaryOfferObserved then
			primaryOfferObserved = true
			appendEvent("trade_offer_primary", "observed")
		end
	end,
	onCounterTrade = function()
		if phase == 1 and not primaryOfferObserved then
			primaryOfferObserved = true
			appendEvent("trade_offer_primary", "observed")
		end
	end,
	onCloseTrade = function()
		if phase == 1 and not primaryTradeClosed then
			primaryTradeClosed = true
			appendEvent("trade_close_primary", "observed")
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

local previous = io.open(EVENTS_PATH, "w")
if previous then
	previous:write("timestamp\tkey\tvalue\n")
	previous:close()
end

g_logger.setLogFile(INTERNAL_LOG_PATH)
appendEvent("scenario", SCENARIO_KEY)
appendEvent("driver", "e2e-qri-001-trade-primary-v2")
scheduleEvent(startLogin, 2500)
scheduleEvent(function()
	if not finished then
		fail("global_timeout", "scenario completes within bounded timeout", tostring(GLOBAL_TIMEOUT_SECONDS) .. " seconds elapsed")
	end
end, GLOBAL_TIMEOUT_SECONDS * 1000)
