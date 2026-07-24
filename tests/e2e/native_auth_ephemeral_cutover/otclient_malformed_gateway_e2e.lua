local CLIENT_VERSION = tonumber(os.getenv("REHEARSAL_CLIENT_VERSION") or "1525")
local HOST = os.getenv("REHEARSAL_GAME_HOST") or "canary-game.oteryn.test"
local GAME_PORT = tonumber(os.getenv("REHEARSAL_GAME_PORT") or "7172")
local PLATFORM_BASE_URL = os.getenv("REHEARSAL_PLATFORM_PUBLIC_URL") or ""
local GATEWAY_BASE_URL = os.getenv("REHEARSAL_GATEWAY_PUBLIC_URL") or ""
local CLIENT_ID = os.getenv("REHEARSAL_OAUTH_CLIENT_ID") or ""
local ARTIFACT_DIR = os.getenv("REHEARSAL_ARTIFACT_DIR") or "/evidence"
local EVENTS_PATH = ARTIFACT_DIR .. "/malformed-gateway-client-events.tsv"
local INTERNAL_LOG_PATH = ARTIFACT_DIR .. "/otclient.malformed-gateway.internal.log"
local OBSERVATION_MS = tonumber(os.getenv("REHEARSAL_FAILURE_OBSERVATION_MS") or "20000")
local GLOBAL_TIMEOUT_SECONDS = tonumber(os.getenv("REHEARSAL_GLOBAL_TIMEOUT_SECONDS") or "45")

local finished = false
local flowStarted = false
local successfulEntries = 0

local function sanitize(value)
    return tostring(value):gsub("[\t\r\n]", " ")
end

local function appendEvent(key, value)
    local file = assert(io.open(EVENTS_PATH, "a"))
    file:write(string.format("%d\t%s\t%s\n", os.time(), sanitize(key), sanitize(value)))
    file:close()
    g_logger.info(string.format("[malformed-gateway-e2e] %s=%s", tostring(key), tostring(value)))
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

local function succeed()
    if finished then
        return
    end
    if successfulEntries ~= 0 or g_game.isOnline() then
        fail("malformed Gateway response caused a world entry")
        return
    end
    if type(G) == "table" and type(G.sessionKey) == "string" and G.sessionKey ~= "" then
        fail("malformed Gateway response was accepted as a Game Session")
        return
    end
    finished = true
    appendEvent("malformed_gateway_response", "rejected")
    appendEvent("successful_world_entries", successfulEntries)
    appendEvent("e2e", "success")
    exitSoon()
end

local function setWidgetText(widget, value)
    if not widget or not widget.setText then
        return false
    end
    widget:setText(tostring(value))
    return true
end

local function beginNativeFlow()
    if finished or flowStarted then
        return
    end
    if not OterynIdentity or not EnterGame or not Services or not Servers_init then
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
        oterynIdentity = { enabled = true, protocolVersion = 1 }
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
    scheduleEvent(succeed, OBSERVATION_MS)
end

connect(g_game, {
    onGameStart = function()
        successfulEntries = successfulEntries + 1
        fail("malformed Gateway response entered the world")
    end,
})

local previous = io.open(EVENTS_PATH, "w")
if previous then
    previous:write("timestamp\tkey\tvalue\n")
    previous:close()
end

g_logger.setLogFile(INTERNAL_LOG_PATH)
appendEvent("scenario", "native-auth-malformed-gateway-response")
scheduleEvent(beginNativeFlow, 2500)
scheduleEvent(function()
    if not finished then
        fail("global timeout after " .. tostring(GLOBAL_TIMEOUT_SECONDS) .. " seconds")
    end
end, GLOBAL_TIMEOUT_SECONDS * 1000)
