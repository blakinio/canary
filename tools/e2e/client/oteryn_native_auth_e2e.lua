local CLIENT_VERSION = tonumber(os.getenv("AGENT_E2E_CLIENT_VERSION") or "1525")
local CHARACTER = os.getenv("AGENT_E2E_CHARACTER") or "Knight 1"
local WORLD = os.getenv("AGENT_E2E_WORLD") or "Canary E2E"
local HOST = os.getenv("AGENT_E2E_HOST") or "127.0.0.1"
local GAME_PORT = tonumber(os.getenv("AGENT_E2E_GAME_PORT") or "7172")
local GATEWAY_BASE_URL = os.getenv("AGENT_E2E_GATEWAY_BASE_URL") or ""
local GAME_LOGIN_TICKET = os.getenv("AGENT_E2E_GAME_LOGIN_TICKET") or ""
local ARTIFACT_DIR = os.getenv("AGENT_E2E_ARTIFACT_DIR") or "../artifacts"
local GLOBAL_TIMEOUT_SECONDS = tonumber(os.getenv("AGENT_E2E_GLOBAL_TIMEOUT_SECONDS") or "180")
local SESSION_HOLD_MS = tonumber(os.getenv("AGENT_E2E_SESSION_HOLD_MS") or "5000")
local REPLAY_DELAY_MS = tonumber(os.getenv("AGENT_E2E_RELOG_DELAY_MS") or "1500")
local SCENARIO_KEY = os.getenv("AGENT_E2E_SCENARIO_KEY") or "login/oteryn-native-auth"

local EVENTS_PATH = ARTIFACT_DIR .. "/client-events.tsv"
local INTERNAL_LOG_PATH = ARTIFACT_DIR .. "/otclient.internal.log"

local phase = 0
local successfulEntries = 0
local firstSessionStarted = false
local logoutRequested = false
local firstLogoutCompleted = false
local replayStartRetries = 0
local replayAttempted = false
local replayEntered = false
local replayCredential = nil
local finished = false
local gatewayOperation = nil
local startedAt = os.time()

local function sanitize(value)
    return tostring(value):gsub("[\t\r\n]", " ")
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

local function succeedReplayRejection(source)
    if finished or not replayAttempted or replayEntered then
        return
    end
    if successfulEntries ~= 1 then
        fail("expected exactly one successful world entry before replay rejection")
        return
    end
    finished = true
    replayCredential = nil
    appendEvent("replay_rejected", source)
    appendEvent("successful_world_entries", successfulEntries)
    appendEvent("duration_seconds", os.time() - startedAt)
    appendEvent("e2e", "success")
    exitSoon()
end

local function safeJsonDecode(value)
    if type(value) == "table" then
        return value
    end
    if type(value) ~= "string" or value == "" then
        return nil
    end
    local ok, decoded = pcall(json.decode, value)
    return ok and decoded or nil
end

local function disableStartupModule(name)
    local module = g_modules.getModule(name)
    if not module or not module:isLoaded() then
        return
    end
    local ok, err = pcall(function()
        module:unload()
    end)
    if not ok then
        fail("failed to disable startup module " .. name .. ": " .. tostring(err))
    end
end

local function installStartupProfile()
    for _, name in ipairs({
        "game_quickloot",
        "game_imbuementtracker",
        "game_shop",
        "client_locales",
        "game_proficiency",
        "game_questlog",
    }) do
        disableStartupModule(name)
        if finished then
            return
        end
    end
end

local function configureGameProtocol()
    g_game.setClientVersion(CLIENT_VERSION)
    g_game.setProtocolVersion(g_game.getClientProtocolVersion(CLIENT_VERSION))
    g_game.disableFeature(GameClientPing)
    g_game.disableFeature(GameExtendedClientPing)
    if not g_game.getFeature(GameSessionKey) then
        fail("maintained client profile does not expose GameSessionKey")
        return false
    end
    g_game.chooseRsa(HOST)
    return true
end

local function loginWithCredential(credential, isReplay)
    if finished then
        return
    end
    if type(credential) ~= "string" or credential == "" then
        fail("Game Session credential is missing")
        return
    end
    if not configureGameProtocol() then
        return
    end

    if isReplay then
        phase = 2
        replayAttempted = true
        appendEvent("replay_attempt", "started")
    else
        phase = 1
        appendEvent("gateway_session", "received")
    end

    -- Never log or persist the opaque credential. Game::loginWorld synchronously
    -- copies it into ProtocolGame before the asynchronous connection starts.
    g_game.loginWorld("", "", WORLD, HOST, GAME_PORT, CHARACTER, "", credential)
end

local function startReplay()
    if finished then
        return
    end
    if g_game.isOnline() then
        replayStartRetries = replayStartRetries + 1
        if replayStartRetries > 20 then
            fail("cannot start replay while the first session is still online")
            return
        end
        scheduleEvent(startReplay, 250)
        return
    end
    local credential = replayCredential
    loginWithCredential(credential, true)
end

local function completeFirstLogout(source)
    if finished or firstLogoutCompleted then
        return
    end
    if phase ~= 1 or not firstSessionStarted or not logoutRequested then
        fail("first session ended before the controlled safe logout")
        return
    end
    firstLogoutCompleted = true
    appendEvent("logout_1", "complete")
    appendEvent("logout_signal", source)
    scheduleEvent(startReplay, REPLAY_DELAY_MS)
end

local function requestFreshGatewaySession()
    if finished then
        return
    end
    if GATEWAY_BASE_URL == "" or GAME_LOGIN_TICKET == "" then
        fail("native-auth Gateway runtime environment is incomplete")
        return
    end

    appendEvent("gateway_login_request", "started")
    local ticket = GAME_LOGIN_TICKET
    GAME_LOGIN_TICKET = ""
    gatewayOperation = HTTP.postJSON(GATEWAY_BASE_URL .. "/v1/login", {
        protocol_version = 1,
        game_login_ticket = ticket,
    }, function(response, err)
        gatewayOperation = nil
        if finished then
            return
        end
        local decoded = safeJsonDecode(response)
        if err or type(decoded) ~= "table" or decoded.error then
            fail("Gateway login failed")
            return
        end
        if tonumber(decoded.protocol_version) ~= 1 or type(decoded.session) ~= "table" then
            fail("Gateway returned an invalid protocol response")
            return
        end
        local credential = decoded.session.credential
        if type(credential) ~= "string" or credential == "" then
            fail("Gateway returned an empty Game Session credential")
            return
        end
        if type(decoded.worlds) ~= "table" or #decoded.worlds ~= 1 or type(decoded.characters) ~= "table" then
            fail("Gateway returned an invalid world or character set")
            return
        end
        local world = decoded.worlds[1]
        if tostring(world.name) ~= WORLD or tostring(world.host) ~= HOST or tonumber(world.port) ~= GAME_PORT then
            fail("Gateway world routing does not match the expected disposable world")
            return
        end
        local matchedCharacter = false
        for _, character in ipairs(decoded.characters) do
            if tostring(character.name) == CHARACTER and tonumber(character.world_id) == tonumber(world.id) then
                matchedCharacter = true
                break
            end
        end
        if not matchedCharacter then
            fail("Gateway did not authorize the intended character")
            return
        end

        -- Retain one in-memory copy only for the explicit negative replay check.
        -- The value is never written to settings, events, logs, or artifacts.
        replayCredential = credential
        loginWithCredential(credential, false)
    end)

    if type(gatewayOperation) ~= "number" or gatewayOperation < 0 then
        gatewayOperation = nil
        fail("could not queue Gateway login request")
    end
end

connect(g_game, {
    onLogin = function()
        appendEvent("protocol_login_" .. tostring(phase), "received")
    end,
    onGameStart = function()
        successfulEntries = successfulEntries + 1
        if phase == 2 then
            replayEntered = true
            fail("replayed Game Session credential entered the world")
            return
        end
        if phase ~= 1 or firstSessionStarted then
            fail("unexpected successful world-entry state")
            return
        end
        firstSessionStarted = true
        appendEvent("login_1", "success")
        scheduleEvent(function()
            if not finished and phase == 1 and g_game.isOnline() then
                appendEvent("online_stable_1", "confirmed")
            end
        end, 1500)
        scheduleEvent(function()
            if not finished and phase == 1 and g_game.isOnline() then
                logoutRequested = true
                appendEvent("logout_request_1", "safe")
                g_game.safeLogout()
            end
        end, SESSION_HOLD_MS)
    end,
    onGameEnd = function()
        if finished then
            return
        end
        if phase == 1 then
            completeFirstLogout("game_end")
            return
        end
        if phase == 2 and replayAttempted and not replayEntered then
            succeedReplayRejection("connection_closed")
            return
        end
        fail("unexpected game-end transition")
    end,
    onLoginError = function(_message)
        if phase == 2 and replayAttempted and not replayEntered then
            succeedReplayRejection("login_error")
            return
        end
        fail("login error before successful native-auth world entry")
    end,
    onSessionEnd = function(_reason)
        if phase == 1 and firstSessionStarted and logoutRequested then
            completeFirstLogout("session_end")
            return
        end
        if phase == 2 and replayAttempted and not replayEntered then
            succeedReplayRejection("session_end")
            return
        end
        fail("session ended before successful native-auth world entry")
    end,
    onConnectionError = function(_message, _code)
        if phase == 2 and replayAttempted and not replayEntered then
            succeedReplayRejection("connection_error")
            return
        end
        fail("connection error before successful native-auth world entry")
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
appendEvent("driver", "oteryn-native-auth-gateway-v1")
installStartupProfile()

if not finished then
    scheduleEvent(requestFreshGatewaySession, 2500)
end
scheduleEvent(function()
    if not finished then
        fail("global timeout after " .. tostring(GLOBAL_TIMEOUT_SECONDS) .. " seconds")
    end
end, GLOBAL_TIMEOUT_SECONDS * 1000)
