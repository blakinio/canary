-- Runtime-independent contract tests for data/scripts/lib/register_achievements.lua
-- Run: luajit tests/lua/test_achievement_helpers.lua

local passed, failed, errors = 0, 0, {}

local function test(name, fn)
	local ok, err = pcall(fn)
	if ok then
		passed = passed + 1
	else
		failed = failed + 1
		table.insert(errors, { name = name, err = err })
	end
end

local function assert_equal(actual, expected, message)
	if actual ~= expected then
		error(message or string.format("expected %s, got %s", tostring(expected), tostring(actual)), 2)
	end
end

local function assert_array_equal(actual, expected, message)
	assert_equal(#actual, #expected, message or "array lengths differ")
	for index = 1, #expected do
		assert_equal(actual[index], expected[index], (message or "arrays differ") .. " at index " .. index)
	end
end

local logErrors = {}
logger = {
	trace = function() end,
	debug = function() end,
	error = function(message, ...)
		table.insert(logErrors, { message = message, args = { ... } })
	end,
}

function isNumber(value)
	return type(value) == "number"
end

local registeredById, registeredByName = {}, {}
Game = {}
function Game.registerAchievement(id, name, description, secret, grade, points)
	local achievement = {
		id = id,
		name = name,
		description = description,
		secret = secret,
		grade = grade,
		points = points,
	}
	registeredById[id] = achievement
	registeredByName[name] = achievement
end

function Game.getAchievementInfoById(id)
	return registeredById[id]
end

function Game.getAchievementInfoByName(name)
	return registeredByName[name]
end

Player = {}
dofile("data/scripts/lib/register_achievements.lua")

local achievementIds = {}
for id in pairs(ACHIEVEMENTS) do
	if type(id) == "number" then
		achievementIds[#achievementIds + 1] = id
	end
end
table.sort(achievementIds)

local function makePlayer(unlocked)
	local player = { unlocked = unlocked or {}, added = {}, removed = {} }
	setmetatable(player, { __index = Player })

	function player:hasAchievement(id)
		return self.unlocked[id] == true
	end

	function player:addAchievement(id, denyMsg)
		self.added[#self.added + 1] = { id = id, denyMsg = denyMsg }
		return true
	end

	function player:removeAchievement(id)
		self.removed[#self.removed + 1] = id
		return true
	end

	return player
end

test("registers every numeric definition and exposes real bounds", function()
	local registeredCount = 0
	for _ in pairs(registeredById) do
		registeredCount = registeredCount + 1
	end
	assert_equal(registeredCount, #achievementIds)
	assert_equal(ACHIEVEMENT_FIRST, achievementIds[1])
	assert_equal(ACHIEVEMENT_LAST, achievementIds[#achievementIds])
	assert_equal(registeredById[achievementIds[#achievementIds]].id, achievementIds[#achievementIds])
end)

test("enumerates unlocked achievements across sparse gaps in ascending order", function()
	local middle = achievementIds[math.floor(#achievementIds / 2)]
	local expected = { achievementIds[1], middle, achievementIds[#achievementIds] }
	local unlocked = {}
	for _, id in ipairs(expected) do
		unlocked[id] = true
	end
	assert_array_equal(makePlayer(unlocked):getAchievements(), expected)
end)

test("bulk add and remove visit every registered ID deterministically", function()
	local player = makePlayer()
	player:addAllAchievements(false)
	player:removeAllAchievements()
	assert_equal(#player.added, #achievementIds)
	assert_equal(#player.removed, #achievementIds)
	for index, id in ipairs(achievementIds) do
		assert_equal(player.added[index].id, id)
		assert_equal(player.added[index].denyMsg, false)
		assert_equal(player.removed[index], id)
	end
end)

test("public and secret enumeration use registered IDs in ascending order", function()
	local unlocked, expectedPublic, expectedSecret = {}, {}, {}
	for _, id in ipairs(achievementIds) do
		unlocked[id] = true
		if ACHIEVEMENTS[id].secret then
			expectedSecret[#expectedSecret + 1] = id
		else
			expectedPublic[#expectedPublic + 1] = id
		end
	end
	local player = makePlayer(unlocked)
	assert_array_equal(player:getPublicAchievements(), expectedPublic)
	assert_array_equal(player:getSecretAchievements(), expectedSecret)
end)

test("secret lookup resolves ID and name metadata", function()
	local publicId, secretId
	for _, id in ipairs(achievementIds) do
		if ACHIEVEMENTS[id].secret and not secretId then
			secretId = id
		elseif not ACHIEVEMENTS[id].secret and not publicId then
			publicId = id
		end
		if publicId and secretId then
			break
		end
	end
	assert_equal(Game.isAchievementSecret(publicId), false)
	assert_equal(Game.isAchievementSecret(ACHIEVEMENTS[publicId].name), false)
	assert_equal(Game.isAchievementSecret(secretId), true)
	assert_equal(Game.isAchievementSecret(ACHIEVEMENTS[secretId].name), true)
end)

test("invalid secret lookup logs supplied identifier and returns false", function()
	local before = #logErrors
	assert_equal(Game.isAchievementSecret(99999), false)
	assert_equal(#logErrors, before + 1)
	assert_equal(logErrors[#logErrors].args[1], 99999)
end)

print(string.format("\n%d passed, %d failed", passed, failed))
if #errors > 0 then
	print("\nFailed tests:")
	for _, entry in ipairs(errors) do
		print(string.format("  FAIL: %s\n        %s", entry.name, entry.err))
	end
	os.exit(1)
end
