local RESULT_PATH = 'e2e-result.txt'
local CLIENT_VERSION = tonumber(os.getenv('CYCLOPEDIA_E2E_CLIENT_VERSION') or '1525')
local ACCOUNT = 'test1@example.com'
local PASSWORD = os.getenv('CYCLOPEDIA_E2E_PASSWORD') or 'test'
local CHARACTER = os.getenv('CYCLOPEDIA_E2E_CHARACTER') or 'Knight 1'
local HOST = os.getenv('CYCLOPEDIA_E2E_HOST') or '127.0.0.1'
local LOGIN_PORT = tonumber(os.getenv('CYCLOPEDIA_E2E_LOGIN_PORT') or '7171')

local phase = 1
local phaseComplete = false
local received = {}
local finished = false
local protocolLogin
local sessionKey
local characters
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

local function closeLoginProtocol()
    if protocolLogin then
        protocolLogin:cancelLogin()
        protocolLogin = nil
    end
end

local function finishFailure(message)
    if finished then
        return
    end
    finished = true
    closeLoginProtocol()
    appendResult('e2e', 'failure')
    appendResult('error', message)
    scheduleEvent(function()
        g_app.exit()
    end, 250)
end

local function findCharacter(list)
    for _, character in ipairs(list or {}) do
        if character.name == CHARACTER then
            return character
        end
    end
    return nil
end

local function maybeEnterWorld()
    if finished or enteringWorld or not sessionKey or not characters then
        return
    end

    local selected = findCharacter(characters)
    if not selected then
        finishFailure('character not present in login-server response: ' .. CHARACTER)
        return
    end

    if not selected.worldIp or not selected.worldPort or not selected.worldName then
        finishFailure('selected character has incomplete world connection data')
        return
    end

    enteringWorld = true
    appendResult('session_key_' .. phase, #sessionKey)
    appendResult('character_list_' .. phase, valueCount(characters))
    appendResult(
        'game_login_attempt_' .. phase,
        string.format('%s:%d/%s/%s', tostring(selected.worldIp), tonumber(selected.worldPort), selected.worldName, selected.name)
    )

    g_game.loginWorld(
        ACCOUNT,
        PASSWORD,
        selected.worldName,
        selected.worldIp,
        selected.worldPort,
        selected.name,
        '',
        sessionKey,
        ''
    )
end

local function startLogin()
    closeLoginProtocol()
    sessionKey = nil
    characters = nil
    enteringWorld = false

    appendResult('login_server_attempt_' .. phase, string.format('%s:%d/v%d', HOST, LOGIN_PORT, CLIENT_VERSION))

    g_game.setClientVersion(CLIENT_VERSION)
    g_game.setProtocolVersion(g_game.getClientProtocolVersion(CLIENT_VERSION))
    g_game.chooseRsa(HOST)

    protocolLogin = ProtocolLogin.create()
    protocolLogin.onLoginError = function(_, message, errorCode)
        finishFailure(string.format('login server error %s: %s', tostring(errorCode), tostring(message)))
    end
    protocolLogin.onSessionKey = function(_, key)
        sessionKey = key
        appendResult('login_server_session_' .. phase, #key)
        maybeEnterWorld()
    end
    protocolLogin.onCharacterList = function(_, list, account)
        characters = list
        appendResult('login_server_characters_' .. phase, valueCount(list))
        appendResult('login_server_account_' .. phase, account and 'received' or 'missing')
        maybeEnterWorld()
    end
    protocolLogin.onUpdateNeeded = function(_, signature)
        finishFailure('login server requested client update: ' .. tostring(signature))
    end

    protocolLogin:login(HOST, LOGIN_PORT, ACCOUNT, PASSWORD, '', false)
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
        if type(toggle) == 'function' then
            toggle('bestiary')
        else
            g_game.requestBestiary()
        end
    end, 500)

    scheduleEvent(function()
        if type(showCharms) == 'function' then
            showCharms()
        else
            g_game.requestBestiary()
        end
    end, 1800)

    scheduleEvent(function()
        if type(showBosstiary) == 'function' then
            showBosstiary()
        else
            g_game.requestBosstiaryInfo()
        end
    end, 3200)
end

connect(g_game, {
    onGameStart = function()
        closeLoginProtocol()
        appendResult('login_' .. phase, 'success')
        requestCyclopediaSurfaces()
    end,
    onGameEnd = function()
        appendResult('logout_' .. phase, 'complete')
        if phase == 1 and phaseComplete and not finished then
            phase = 2
            scheduleEvent(startLogin, 1500)
        end
    end,
    onLoginError = function(message)
        finishFailure('game login error: ' .. tostring(message))
    end,
    onConnectionError = function(message, code)
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
