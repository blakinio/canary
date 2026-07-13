local RESULT_PATH = 'e2e-result.txt'
local CLIENT_VERSION = tonumber(os.getenv('CYCLOPEDIA_E2E_CLIENT_VERSION') or '1525')
local ACCOUNT = os.getenv('CYCLOPEDIA_E2E_ACCOUNT') or 'test1@example.com'
local PASSWORD = os.getenv('CYCLOPEDIA_E2E_PASSWORD') or 'test'
local CHARACTER = os.getenv('CYCLOPEDIA_E2E_CHARACTER') or 'Knight 1'
local HOST = os.getenv('CYCLOPEDIA_E2E_HOST') or '127.0.0.1'
local GAME_PORT = tonumber(os.getenv('CYCLOPEDIA_E2E_PORT') or '7172')
local WORLD = os.getenv('CYCLOPEDIA_E2E_WORLD') or 'Canary E2E'

local phase = 1
local phaseComplete = false
local received = {}
local finished = false
local enteringWorld = false

local function appendResult(key, value)
    local file = assert(io.open(RESULT_PATH, 'a'))
    file:write(string.format('%s=%s\n', tostring(key), tostring(value)))
    file:close()
    g_logger.info(string.format('[cyclopedia-e2e] %s=%s', tostring(key), tostring(value)))
end

local function valueCount(value)
    if type(value) == 'table' then
        local count = 0
        for _ in pairs(value) do
            count = count + 1
        end
        return count
    end
    return value == nil and 0 or 1
end

local function finishFailure(message)
    if finished then
        return
    end

    finished = true
    appendResult('e2e', 'failure')
    appendResult('error', message)
    scheduleEvent(function()
        g_app.exit()
    end, 250)
end

local function startLogin()
    if finished or enteringWorld then
        return
    end

    enteringWorld = true
    g_game.setClientVersion(CLIENT_VERSION)
    g_game.setProtocolVersion(g_game.getClientProtocolVersion(CLIENT_VERSION))
    g_game.chooseRsa(HOST)

    local sessionKey = ACCOUNT .. '\n' .. PASSWORD
    local recordName = string.format('cyclopedia-session-%d.record', phase)
    appendResult('session_key_mode_' .. phase, 'password')
    appendResult('packet_record_' .. phase, recordName)
    appendResult(
        'direct_game_login_' .. phase,
        string.format('%s:%d/%s/%s/v%d', HOST, GAME_PORT, WORLD, CHARACTER, CLIENT_VERSION)
    )

    g_game.loginWorld(
        ACCOUNT,
        PASSWORD,
        WORLD,
        HOST,
        GAME_PORT,
        CHARACTER,
        '',
        sessionKey,
        recordName
    )
end

local function maybeCompletePhase()
    if phaseComplete or not received.bestiary or not received.charms or not received.bosstiary then
        return
    end

    phaseComplete = true
    appendResult('phase_' .. phase, 'complete')

    if phase == 1 then
        scheduleEvent(function()
            appendResult('logout_request_1', 'safe')
            g_game.safeLogout()
        end, 1200)
        return
    end

    finished = true
    appendResult('e2e', 'success')
    scheduleEvent(function()
        g_game.safeLogout()
        scheduleEvent(function()
            g_app.exit()
        end, 500)
    end, 800)
end

local function requestCyclopediaSurfaces()
    received = {}
    phaseComplete = false

    scheduleEvent(function()
        appendResult('request_bestiary_' .. phase, 'sent')
        if type(toggle) == 'function' then
            toggle('bestiary')
        else
            g_game.requestBestiary()
        end
    end, 500)

    scheduleEvent(function()
        appendResult('request_charms_' .. phase, 'sent')
        if type(showCharms) == 'function' then
            showCharms()
        else
            g_game.requestBestiary()
        end
    end, 1800)

    scheduleEvent(function()
        appendResult('request_bosstiary_' .. phase, 'sent')
        if type(showBosstiary) == 'function' then
            showBosstiary()
        else
            g_game.requestBosstiaryInfo()
        end
    end, 3200)
end

connect(g_game, {
    onLogin = function()
        appendResult('protocol_login_' .. phase, 'received')
    end,
    onPendingGame = function()
        appendResult('pending_game_' .. phase, 'received')
    end,
    onEnterGame = function()
        appendResult('enter_game_' .. phase, 'received')
    end,
    onGameStart = function()
        enteringWorld = false
        appendResult('login_' .. phase, 'success')
        requestCyclopediaSurfaces()
    end,
    onGameEnd = function()
        enteringWorld = false
        appendResult('logout_' .. phase, 'complete')
        if phase == 1 and phaseComplete and not finished then
            phase = 2
            scheduleEvent(startLogin, 1500)
        elseif not phaseComplete and not finished then
            finishFailure('unexpected game end during phase ' .. tostring(phase))
        end
    end,
    onSessionEnd = function(reason)
        appendResult('session_end_' .. phase, tostring(reason))
    end,
    onLoginAdvice = function(message)
        appendResult('login_advice_' .. phase, tostring(message))
    end,
    onLoginWait = function(message, time)
        appendResult('login_wait_' .. phase, string.format('%s/%s', tostring(message), tostring(time)))
    end,
    onUpdateNeeded = function(signature)
        appendResult('update_needed_' .. phase, tostring(signature))
    end,
    onLoginError = function(message)
        enteringWorld = false
        finishFailure('game login error: ' .. tostring(message))
    end,
    onConnectionError = function(message, code)
        enteringWorld = false
        appendResult('connection_error_' .. phase, string.format('%s/%s', tostring(code), tostring(message)))
        finishFailure(string.format('game connection error %s: %s', tostring(code), tostring(message)))
    end,
    onParseBestiaryRaces = function(data)
        received.bestiary = true
        appendResult('bestiary_' .. phase, valueCount(data))
        maybeCompletePhase()
    end,
    onUpdateBestiaryCharmsData = function(data)
        received.charms = true
        appendResult('charms_' .. phase, valueCount(data))
        maybeCompletePhase()
    end,
    onParseSendBosstiary = function(data)
        received.bosstiary = true
        appendResult('bosstiary_' .. phase, valueCount(data))
        maybeCompletePhase()
    end
})

local previous = io.open(RESULT_PATH, 'w')
if previous then
    previous:write('client_version=' .. tostring(CLIENT_VERSION) .. '\n')
    previous:close()
end

scheduleEvent(startLogin, 2500)
scheduleEvent(function()
    if not finished then
        finishFailure('global timeout')
    end
end, 150000)
