local CLIENT_VERSION = tonumber(os.getenv("REHEARSAL_CLIENT_VERSION") or "1525")
local CHARACTER = os.getenv("REHEARSAL_CHARACTER") or "Knight 1"
local WORLD = os.getenv("REHEARSAL_WORLD") or "Canary E2E"
local HOST = os.getenv("REHEARSAL_GAME_HOST") or "canary-game.oteryn.test"
local GAME_PORT = tonumber(os.getenv("REHEARSAL_GAME_PORT") or "7172")
local PLATFORM_BASE_URL = os.getenv("REHEARSAL_PLATFORM_PUBLIC_URL") or ""
local GATEWAY_BASE_URL = os.getenv("REHEARSAL_GATEWAY_PUBLIC_URL") or ""
local CLIENT_ID = os.getenv("REHEARSAL_OAUTH_CLIENT_ID") or ""
local ARTIFACT_DIR = os.getenv("REHEARSAL_ARTIFACT_DIR") or "/evidence"
local SESSION_HOLD_MS = tonumber(os.getenv("REHEARSAL_SESSION_HOLD_MS") or "5000")
local REPLAY_DELAY_MS = tonumber(os.getenv("REHEARSAL_REPLAY_DELAY_MS") or "1500")
local GLOBAL_TIMEOUT_SECONDS = tonumber(os.getenv("REHEARSAL_GLOBAL_TIMEOUT_SECONDS") or "180")

local EVENTS_PATH = ARTIFACT_DIR .. "/client-events.tsv"
local INTERNAL_LOG_PATH = ARTIFACT_DIR .. "/otclient.internal.log"

local phase = 0
local successfulEntries = 0
local firstSessionStarted = false
local logoutRequested = false
local firstLogoutCompleted = false
local replayAttempted = false
local replayEntered = false
local replayCredential = nil
local finished = false
local startedAt = os.time()
local flowStarted = false
local characterLoginStarted = false

local function sanitize(value)
    return tostring(value):gsub("[\t\r\n]", " ")
end

local function appendEvent(key, value)
    local file = assert(io.open(EVENTS_PATH, "a"))
    file:write(string.format("%d\t%s\t%s\n", os.time(), sanitize(key), sanitize(value)))
    file:close()
    g_logger.info(string.format("[native-auth-rehearsal] %s=%s", tostring(key), tostring(value)))
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
    replayCredential = nil
    appendEvent("e2e", "failure")
    appendEvent("error", message)
    exitSoon()
end

local function succeedReplayRejection(source)
    if finished or not replayAttempted or replayEntered then
        return
    end
    if successfulEntries ~= 1 then
        fail("expected exactly one successful world entry")
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

local function configureReplayProtocol()
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

local function startReplay()
    if finished then
        return
    end
    if g_game.isOnline() then
        scheduleEvent(startReplay, 250)
        return
    end
    if type(replayCredential) ~= "string" or replayCredential == "" then
        fail("replay credential was not retained in memory")
        return
    end
    if not configureReplayProtocol() then
        return
    end
    phase = 2
    replayAttempted = true
    appendEvent("replay_attempt", "started")
    local credential = replayCredential
    g_game.loginWorld("", "", WORLD, HOST, GAME_PORT, CHARACTER, "", credential)
end

local function completeFirstLogout(source)
    if finished or firstLogoutCompleted then
        return
    end
    if phase ~= 1 or not firstSessionStarted or not logoutRequested then
        fail("first session ended before controlled safe logout")
        return
    end
    firstLogoutCompleted = true
    appendEvent("logout_1", "complete")
    appendEvent("logout_signal", source)
    scheduleEvent(startReplay, REPLAY_DELAY_MS)
end

local function tryCharacterLogin()
    if finished or characterLoginStarted then
        return
    end
    if type(G) ~= "table" or type(G.characters) ~= "table" or #G.characters == 0 or
       type(G.sessionKey) ~= "string" or G.sessionKey == "" or not CharacterList then
        scheduleEvent(tryCharacterLogin, 100)
        return
    end

    local matched = false
    for _, character in ipairs(G.characters) do
        if tostring(character.name) == CHARACTER and tostring(character.worldName) == WORLD and
           tostring(character.worldIp) == HOST and tonumber(character.worldPort) == GAME_PORT then
            matched = true
            break
        end
    end
    if not matched then
        fail("Gateway did not return the expected authorized character/world route")
        return
    end

    replayCredential = G.sessionKey
    characterLoginStarted = true
    phase = 1
    appendEvent("gateway_session", "received")
    appendEvent("character_authorization", "matched")
    CharacterList.doLogin()
end

local function setWidgetText(widget, value)
    if not widget then
        return false
    end
    if widget.setText then
        widget:setText(tostring(value))
        return true
    end
    return false
end

local function beginNativeFlow()
    if finished or flowStarted then
        return
    end
    if not OterynIdentity or not EnterGame or not CharacterList or not Services or not Servers_init then
        scheduleEvent(beginNativeFlow, 100)
        return
    end
    if PLATFORM_BASE_URL == "" or GATEWAY_BASE_URL == "" or CLIENT_ID == "" then
        fail("native-auth endpoint configuration is incomplete")
        return
    end

    Services.oterynIdentity = {
        enabled = true,
        authorizationEndpoint = PLATFORM_BASE_URL .. "/oauth/authorize",
        tokenEndpoint = PLATFORM_BASE_URL .. "/oauth/token",
        ticketEndpoint = PLATFORM_BASE_URL .. "/api/v1/game-auth/tickets",
        gatewayLoginEndpoint = GATEWAY_BASE_URL .. "/v1/login",
        clientId = CLIENT_ID,
        scope = "game:ticket",
        callbackTimeoutMillis = 120000,
        maxGameTicketTtlSeconds = 60,
        allowInsecureLoopback = false
    }
    Servers_init[HOST] = {
        port = GAME_PORT,
        protocol = CLIENT_VERSION,
        httpLogin = false,
        authMode = "oteryn_identity",
        legacyAuthEnabled = true,
        oterynIdentity = {
            enabled = true,
            protocolVersion = 1
        }
    }

    local enterGame = rootWidget:recursiveGetChildById("enterGame")
    if not enterGame then
        scheduleEvent(beginNativeFlow, 100)
        return
    end
    local hostWidget = enterGame:getChildById("serverHostTextEdit")
    local portWidget = enterGame:getChildById("serverPortTextEdit")
    local clientWidget = enterGame:getChildById("clientComboBox")
    if not setWidgetText(hostWidget, HOST) or not setWidgetText(portWidget, GAME_PORT) then
        fail("could not configure native-auth server widgets")
        return
    end
    if clientWidget and clientWidget.setCurrentOption then
        clientWidget:setCurrentOption(tostring(CLIENT_VERSION))
    elseif not setWidgetText(clientWidget, CLIENT_VERSION) then
        fail("could not configure client version widget")
        return
    end

    flowStarted = true
    appendEvent("native_flow", "started")
    OterynIdentity.updateUi()
    OterynIdentity.start()
    scheduleEvent(tryCharacterLogin, 100)
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
        if finished then return end
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
appendEvent("scenario", "native-auth-ephemeral-cutover")
appendEvent("client_version", CLIENT_VERSION)
appendEvent("driver", "otclient-native-oauth-pkce")
scheduleEvent(beginNativeFlow, 2500)
scheduleEvent(function()
    if not finished then
        fail("global timeout after " .. tostring(GLOBAL_TIMEOUT_SECONDS) .. " seconds")
    end
end, GLOBAL_TIMEOUT_SECONDS * 1000)
