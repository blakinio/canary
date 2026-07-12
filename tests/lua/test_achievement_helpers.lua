-- Runtime-independent contract tests for data/scripts/lib/register_achievements.lua
-- Run: luajit tests/lua/test_achievement_helpers.lua

local passed, failed, errors = 0, 0, {}

local function test(name, fn)
\tlocal ok, err = pcall(fn)
\tif ok then
\t\tpassed = passed + 1
\telse
\t\tfailed = failed + 1
\t\ttable.insert(errors, { name = name, err = err })
\tend
end

local function assert_equal(actual, expected, message)
\tif actual ~= expected then
\t\terror(message or string.format("expected %s, got %s", tostring(expected), tostring(actual)), 2)
\tend
end

local function assert_array_equal(actual, expected, message)
\tassert_equal(#actual, #expected, message or "array lengths differ")
\tfor index = 1, #expected do
\t\tassert_equal(actual[index], expected[index], (message or "arrays differ") .. " at index " .. index)
\tend
end

local logErrors = {}
logger = {
\ttrace = function() end,
\tdebug = function() end,
\terror = function(message, ...)
\t\ttable.insert(logErrors, { message = message, args = { ... } })
\tend,
}

function isNumber(value)
\treturn type(value) == "number"
end

local registeredById, registeredByName = {}, {}
Game = {}
function Game.registerAchievement(id, name, description, secret, grade, points)
\tlocal achievement = {
\t\tid = id,
\t\tname = name,
\t\tdescription = description,
\t\tsecret = secret,
\t\tgrade = grade,
\t\tpoints = points,
\t}
\tregisteredById[id] = achievement
\tregisteredByName[name] = achievement
end

function Game.getAchievementInfoById(id)
\treturn registeredById[id]
end

function Game.getAchievementInfoByName(name)
\treturn registeredByName[name]
end

Player = {}
dofile("data/scripts/lib/register_achievements.lua")

local achievementIds = {}
for id in pairs(ACHIEVEMENTS) do
\tif type(id) == "number" then
\t\tachievementIds[#achievementIds + 1] = id
\tend
end
table.sort(achievementIds)

local function makePlayer(unlocked)
\tlocal player = { unlocked = unlocked or {}, added = {}, removed = {} }
\tsetmetatable(player, { __index = Player })

\tfunction player:hasAchievement(id)
\t\treturn self.unlocked[id] == true
\tend

\tfunction player:addAchievement(id, denyMsg)
\t\tself.added[#self.added + 1] = { id = id, denyMsg = denyMsg }
\t\treturn true
\tend

\tfunction player:removeAchievement(id)
\t\tself.removed[#self.removed + 1] = id
\t\treturn true
\tend

\treturn player
end

test("registers every numeric definition and exposes real bounds", function()
\tlocal registeredCount = 0
\tfor _ in pairs(registeredById) do
\t\tregisteredCount = registeredCount + 1
\tend
\tassert_equal(registeredCount, #achievementIds)
\tassert_equal(ACHIEVEMENT_FIRST, achievementIds[1])
\tassert_equal(ACHIEVEMENT_LAST, achievementIds[#achievementIds])
\tassert_equal(registeredById[achievementIds[#achievementIds]].id, achievementIds[#achievementIds])
end)

test("enumerates unlocked achievements across sparse gaps in ascending order", function()
\tlocal middle = achievementIds[math.floor(#achievementIds / 2)]
\tlocal expected = { achievementIds[1], middle, achievementIds[#achievementIds] }
\tlocal unlocked = {}
\tfor _, id in ipairs(expected) do
\t\tunlocked[id] = true
\tend
\tassert_array_equal(makePlayer(unlocked):getAchievements(), expected)
end)

test("bulk add and remove visit every registered ID deterministically", function()
\tlocal player = makePlayer()
\tplayer:addAllAchievements(false)
\tplayer:removeAllAchievements()
\tassert_equal(#player.added, #achievementIds)
\tassert_equal(#player.removed, #achievementIds)
\tfor index, id in ipairs(achievementIds) do
\t\tassert_equal(player.added[index].id, id)
\t\tassert_equal(player.added[index].denyMsg, false)
\t\tassert_equal(player.removed[index], id)
\tend
end)

test("public and secret enumeration use registered IDs in ascending order", function()
\tlocal unlocked, expectedPublic, expectedSecret = {}, {}, {}
\tfor _, id in ipairs(achievementIds) do
\t\tunlocked[id] = true
\t\tif ACHIEVEMENTS[id].secret then
\t\t\texpectedSecret[#expectedSecret + 1] = id
\t\telse
\t\t\texpectedPublic[#expectedPublic + 1] = id
\t\tend
\tend
\tlocal player = makePlayer(unlocked)
\tassert_array_equal(player:getPublicAchievements(), expectedPublic)
\tassert_array_equal(player:getSecretAchievements(), expectedSecret)
end)

test("secret lookup resolves ID and name metadata", function()
\tlocal publicId, secretId
\tfor _, id in ipairs(achievementIds) do
\t\tif ACHIEVEMENTS[id].secret and not secretId then
\t\t\tsecretId = id
\t\telseif not ACHIEVEMENTS[id].secret and not publicId then
\t\t\tpublicId = id
\t\tend
\t\tif publicId and secretId then
\t\t\tbreak
\t\tend
\tend
\tassert_equal(Game.isAchievementSecret(publicId), false)
\tassert_equal(Game.isAchievementSecret(ACHIEVEMENTS[publicId].name), false)
\tassert_equal(Game.isAchievementSecret(secretId), true)
\tassert_equal(Game.isAchievementSecret(ACHIEVEMENTS[secretId].name), true)
end)

test("invalid secret lookup logs supplied identifier and returns false", function()
\tlocal before = #logErrors
\tassert_equal(Game.isAchievementSecret(99999), false)
\tassert_equal(#logErrors, before + 1)
\tassert_equal(logErrors[#logErrors].args[1], 99999)
end)

print(string.format("\n%d passed, %d failed", passed, failed))
if #errors > 0 then
\tprint("\nFailed tests:")
\tfor _, entry in ipairs(errors) do
\t\tprint(string.format("  FAIL: %s\n        %s", entry.name, entry.err))
\tend
\tos.exit(1)
end
