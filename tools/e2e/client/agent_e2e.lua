local CLIENT_VERSION = tonumber(os.getenv('AGENT_E2E_CLIENT_VERSION') or '1525')
local ACCOUNT = os.getenv('AGENT_E2E_ACCOUNT') or '@test1'
local PASSWORD = os.getenv('AGENT_E2E_PASSWORD') or ''
local CHARACTER = os.getenv('AGENT_E2E_CHARACTER') or 'Knight 1'
local WORLD = os.getenv('AGENT_E2E_WORLD') or 'Canary E2E'
local HOST = os.getenv('AGENT_E2E_HOST') or '127.0.0.1'
local GAME_PORT = tonumber(os.getenv('AGENT_E2E_GAME_PORT') or '7172')
local ARTIFACT_DIR = os.getenv('AGENT_E2E_ARTIFACT_DIR') or '../artifacts'
local GLOBAL_TIMEOUT_SECONDS = tonumber(os.getenv('AGENT_E2E_GLOBAL_TIMEOUT_SECONDS') or '180')
local SESSION_HOLD_MS = tonumber(os.getenv('AGENT_E2E_SESSION_HOLD_MS') or '7000')
local SCENARIO_KEY = os.getenv('AGENT_E2E_SCENARIO_KEY') or 'login/relog'
local STARTUP_PROFILE = os.getenv('AGENT_E2E_STARTUP_PROFILE') or 'minimal-transport'
local PING_PROFILE = os.getenv('AGENT_E2E_PING_PROFILE') or 'disabled'
local DB_HOST = os.getenv('DB_HOST') or '127.0.0.1'
local DB_PORT = tonumber(os.getenv('DB_PORT') or '3306')
local DB_USER = os.getenv('DB_USER') or 'root'
local DB_NAME = os.getenv('DB_NAME') or 'agent_e2e'

local EVENTS_PATH = ARTIFACT_DIR .. '/client-events.tsv'
local INTERNAL_LOG_PATH = ARTIFACT_DIR .. '/otclient.internal.log'

local phase = 1
local phaseStarted = false
local logoutRequested = false
local enteringWorld = false
local waitingForServerPersistence = false
local finished = false
local startedAt = os.time()

local function sanitize(value)
    return tostring(value):gsub('[\t\r\n]', ' ')
end

local function shellQuote(value)
    return "'" .. tostring(value):gsub("'", "'\\''") .. "'"
end

local function appendEvent(key, value)
    local file = assert(io.open(EVENTS_PATH, 'a'))
    file:write(string.format('%d\t%s\t%s\n', os.time(), sanitize(key), sanitize(value)))
    file:close()
    g_logger.info(string.format('[agent-e2e] %s=%s', tostring(key), tostring(value)))
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
    appendEvent('e2e', 'failure')
    appendEvent('error', message)
    exitSoon()
end

local function disableStartupModule(name)
    local module = g_modules.getModule(name)
    if not module or not module:isLoaded() then
        appendEvent('startup_module_' .. name, 'not-loaded')
        return
    end

    local ok, err = pcall(function()
        module:unload()
    end)
    if ok then
        appendEvent('startup_module_' .. name, 'disabled')
    else
        fail('failed to disable startup module ' .. name .. ': ' .. tostring(err))
    end
end

local function installStartupProfile()
    appendEvent('startup_profile', STARTUP_PROFILE)
    if STARTUP_PROFILE == 'full' then
        return
    end
    if STARTUP_PROFILE ~= 'minimal-transport' then
        fail('unknown startup profile: ' .. tostring(STARTUP_PROFILE))
        return
    end

    local modules = {
        'game_quickloot',
        'game_imbuementtracker',
        'game_shop',
        'client_locales',
        'game_proficiency',
        'game_questlog',
    }
    for _, name in ipairs(modules) do
        disableStartupModule(name)
        if finished then
            return
        end
    end
end

local function configureTransportFeatures()
    if PING_PROFILE == 'default' then
        appendEvent('ping_features_' .. phase, 'default')
        return true
    end
    if PING_PROFILE ~= 'disabled' then
        fail('unknown ping profile: ' .. tostring(PING_PROFILE))
        return false
    end

    g_game.disableFeature(GameClientPing)
    g_game.disableFeature(GameExtendedClientPing)
    appendEvent('ping_features_' .. phase, 'disabled')
    return true
end

local function requestLogout(expectedPhase)
    if finished or expectedPhase ~= phase or not phaseStarted or logoutRequested then
        return
    end

    logoutRequested = true
    appendEvent('logout_request_' .. phase, 'safe')
    g_game.safeLogout()
end

local function startLogin()
    if finished or enteringWorld or phaseStarted then
        return
    end
    if PASSWORD == '' then
        fail('AGENT_E2E_PASSWORD is empty')
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

    local sessionKey = ACCOUNT .. '\n' .. PASSWORD
    local packetRecord = string.format('%s/session-%d.record', ARTIFACT_DIR, phase)
    appendEvent('login_request_' .. phase, string.format('%s:%d/%s/%s/v%d', HOST, GAME_PORT, WORLD, CHARACTER, CLIENT_VERSION))
    appendEvent('packet_record_' .. phase, packetRecord)

    g_game.loginWorld(
        ACCOUNT,
        PASSWORD,
        WORLD,
        HOST,
        GAME_PORT,
        CHARACTER,
        '',
        sessionKey,
        packetRecord
    )
end

local function serverPersistenceReady()
    local query = string.format(
        "SELECT IF(lastlogin > 0 AND lastlogout > 0, 1, 0) FROM players WHERE name=%s;",
        shellQuote(CHARACTER)
    )
    local command = string.format(
        "mariadb -N -s -h %s -P %d -u %s %s -e %s 2>/dev/null",
        shellQuote(DB_HOST),
        DB_PORT,
        shellQuote(DB_USER),
        shellQuote(DB_NAME),
        shellQuote(query)
    )
    local pipe = io.popen(command, 'r')
    if not pipe then
        return false
    end
    local output = pipe:read('*a') or ''
    local ok = pipe:close()
    return ok and output:match('^%s*1%s*$') ~= nil
end

local function waitForServerPersistence()
    if finished or phase ~= 2 or not waitingForServerPersistence then
        return
    end
    if serverPersistenceReady() then
        waitingForServerPersistence = false
        appendEvent('server_persistence_1', 'confirmed')
        -- Game::processGameEnd emits onGameEnd before Game::processDisconnect
        -- clears m_protocolGame. Hand control back to the dispatcher so the
        -- replacement login cannot re-enter loginWorld from inside onGameEnd.
        addEvent(startLogin)
        return
    end
    scheduleEvent(waitForServerPersistence, 250)
end

connect(g_game, {
    onLogin = function()
        appendEvent('protocol_login_' .. phase, 'received')
    end,
    onPendingGame = function()
        appendEvent('pending_game_' .. phase, 'received')
    end,
    onEnterGame = function()
        appendEvent('enter_game_' .. phase, 'received')
    end,
    onGameStart = function()
        enteringWorld = false
        phaseStarted = true
        appendEvent('login_' .. phase, 'success')
        local expectedPhase = phase
        scheduleEvent(function()
            if not finished and expectedPhase == phase and phaseStarted and g_game.isOnline() then
                appendEvent('online_stable_' .. phase, 'confirmed')
            end
        end, 1500)
        scheduleEvent(function()
            requestLogout(expectedPhase)
        end, SESSION_HOLD_MS)
    end,
    onGameEnd = function()
        enteringWorld = false
        if not phaseStarted then
            fail('game ended before phase ' .. tostring(phase) .. ' entered the world')
            return
        end

        if not logoutRequested then
            fail('unexpected disconnect before safe logout in phase ' .. tostring(phase))
            return
        end

        appendEvent('logout_' .. phase, 'complete')
        phaseStarted = false
        logoutRequested = false

        -- The safe logout has already completed when onGameEnd is emitted.
        -- Calling cancelLogin() here schedules a second game-end transition
        -- without session identity; after relog that stale callback can be
        -- misclassified as a phase-two disconnect. Do not mutate transport
        -- state again from the completion callback.
        appendEvent('transport_closed_' .. phase, 'confirmed')

        if phase == 1 then
            phase = 2
            waitingForServerPersistence = true
            appendEvent('server_persistence_1', 'waiting')
            waitForServerPersistence()
            return
        end

        finished = true
        appendEvent('duration_seconds', os.time() - startedAt)
        appendEvent('e2e', 'success')
        exitSoon()
    end,
    onSessionEnd = function(reason)
        appendEvent('session_end_' .. phase, tostring(reason))
    end,
    onLoginAdvice = function(message)
        appendEvent('login_advice_' .. phase, tostring(message))
    end,
    onLoginWait = function(message, time)
        appendEvent('login_wait_' .. phase, string.format('%s/%s', tostring(message), tostring(time)))
    end,
    onUpdateNeeded = function(signature)
        appendEvent('update_needed_' .. phase, tostring(signature))
    end,
    onConnectionFailing = function(failing)
        appendEvent('connection_failing_' .. phase, tostring(failing))
    end,
    onPing = function()
        appendEvent('server_ping_' .. phase, 'received')
    end,
    onPingBack = function()
        appendEvent('server_ping_back_' .. phase, 'received')
    end,
    onLoginError = function(message)
        enteringWorld = false
        fail('login error in phase ' .. tostring(phase) .. ': ' .. tostring(message))
    end,
    onConnectionError = function(message, code)
        enteringWorld = false
        fail(string.format('connection error in phase %d (%s): %s', phase, tostring(code), tostring(message)))
    end
})

local previous = io.open(EVENTS_PATH, 'w')
if previous then
    previous:write('timestamp\tkey\tvalue\n')
    previous:close()
end

g_logger.setLogFile(INTERNAL_LOG_PATH)
appendEvent('scenario', SCENARIO_KEY)
appendEvent('client_version', CLIENT_VERSION)
appendEvent('driver', 'generic-login-relog-v9')
installStartupProfile()

if not finished then
    scheduleEvent(startLogin, 2500)
end
scheduleEvent(function()
    if not finished then
        fail('global timeout after ' .. tostring(GLOBAL_TIMEOUT_SECONDS) .. ' seconds')
    end
end, GLOBAL_TIMEOUT_SECONDS * 1000)
