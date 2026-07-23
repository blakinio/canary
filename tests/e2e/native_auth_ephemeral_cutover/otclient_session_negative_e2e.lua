local CLIENT_VERSION = tonumber(os.getenv("REHEARSAL_CLIENT_VERSION") or "1525")
local WORLD = os.getenv("REHEARSAL_WORLD") or "Canary E2E"
local HOST = os.getenv("REHEARSAL_GAME_HOST") or "canary-game.oteryn.test"
local GAME_PORT = tonumber(os.getenv("REHEARSAL_GAME_PORT") or "7172")
local CREDENTIAL = os.getenv("REHEARSAL_SESSION_CREDENTIAL") or ""
local MODE = os.getenv("REHEARSAL_NEGATIVE_MODE") or "invalid_session"
local AUTHORIZED_CHARACTER = os.getenv("REHEARSAL_AUTHORIZED_CHARACTER") or "Knight 1"
local UNAUTHORIZED_CHARACTER = os.getenv("REHEARSAL_UNAUTHORIZED_CHARACTER") or "Knight 2"
local ARTIFACT_DIR = os.getenv("REHEARSAL_ARTIFACT_DIR") or "/evidence"
local EVENTS_PATH = ARTIFACT_DIR .. "/session-negative-events.tsv"
local INTERNAL_LOG_PATH = ARTIFACT_DIR .. "/otclient.session-negative.internal.log"
local GLOBAL_TIMEOUT_SECONDS = tonumber(os.getenv("REHEARSAL_GLOBAL_TIMEOUT_SECONDS") or "45")

local phase = 0
local successfulEntries = 0
local finished = false
local phaseTransitioned = false

local function sanitize(value)
    return tostring(value):gsub("[\t\r\n]", " ")
end

local function appendEvent(key, value)
    local file = assert(io.open(EVENTS_PATH, "a"))
    file:write(string.format("%d\t%s\t%s\n", os.time(), sanitize(key), sanitize(value)))
    file:close()
    g_logger.info(string.format("[native-auth-negative] %s=%s", tostring(key), tostring(value)))
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

local function succeed(marker)
    if finished then
        return
    end
    if successfulEntries ~= 0 then
        fail("negative Game Session scenario entered the world")
        return
    end
    finished = true
    appendEvent("negative_result", marker)
    appendEvent("successful_world_entries", successfulEntries)
    appendEvent("e2e", "success")
    exitSoon()
end

local function configureProtocol()
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

local function loginCharacter(character)
    if finished then
        return
    end
    if not configureProtocol() then
        return
    end
    appendEvent("attempt", MODE .. ":phase" .. tostring(phase) .. ":" .. character)
    g_game.loginWorld("", "", WORLD, HOST, GAME_PORT, character, "", CREDENTIAL)
end

local function startBurnVerification()
    if finished or phaseTransitioned then
        return
    end
    phaseTransitioned = true
    phase = 2
    scheduleEvent(function()
        phaseTransitioned = false
        loginCharacter(AUTHORIZED_CHARACTER)
    end, 750)
end

local function rejection(source)
    if finished then
        return
    end
    appendEvent("rejection_phase_" .. tostring(phase), source)
    if MODE == "unauthorized_character_burn" and phase == 1 then
        startBurnVerification()
        return
    end
    if MODE == "unauthorized_character_burn" and phase == 2 then
        succeed("unauthorized_character_rejected_and_session_burned")
        return
    end
    if MODE == "invalid_session" and phase == 1 then
        succeed("invalid_session_rejected")
        return
    end
    fail("unexpected rejection state")
end

connect(g_game, {
    onGameStart = function()
        successfulEntries = successfulEntries + 1
        fail("negative Game Session credential entered the world")
    end,
    onLoginError = function(_message)
        rejection("login_error")
    end,
    onSessionEnd = function(_reason)
        rejection("session_end")
    end,
    onConnectionError = function(_message, _code)
        rejection("connection_error")
    end,
    onGameEnd = function()
        rejection("game_end")
    end,
})

local previous = io.open(EVENTS_PATH, "w")
if previous then
    previous:write("timestamp\tkey\tvalue\n")
    previous:close()
end

g_logger.setLogFile(INTERNAL_LOG_PATH)
appendEvent("scenario", "native-auth-session-negative")
appendEvent("mode", MODE)

scheduleEvent(function()
    if CREDENTIAL == "" then
        fail("missing negative scenario credential")
        return
    end
    phase = 1
    if MODE == "unauthorized_character_burn" then
        loginCharacter(UNAUTHORIZED_CHARACTER)
    elseif MODE == "invalid_session" then
        loginCharacter(AUTHORIZED_CHARACTER)
    else
        fail("unsupported negative mode")
    end
end, 2500)

scheduleEvent(function()
    if not finished then
        fail("global timeout after " .. tostring(GLOBAL_TIMEOUT_SECONDS) .. " seconds")
    end
end, GLOBAL_TIMEOUT_SECONDS * 1000)
