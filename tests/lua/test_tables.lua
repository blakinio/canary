-- Runtime-independent security and compatibility tests for table.unserialize.
-- Run: luajit tests/lua/test_tables.lua

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

local function assert_truthy(value, message)
	if not value then
		error(message or "expected a truthy value", 2)
	end
end

local function deep_equal(actual, expected, seen)
	if type(actual) ~= type(expected) then
		return false
	end
	if type(actual) ~= "table" then
		return actual == expected
	end
	seen = seen or {}
	if seen[actual] then
		return seen[actual] == expected
	end
	seen[actual] = expected
	for key, value in pairs(actual) do
		if not deep_equal(value, expected[key], seen) then
			return false
		end
	end
	for key in pairs(expected) do
		if actual[key] == nil then
			return false
		end
	end
	return true
end

dofile("data/libs/functions/tables.lua")

local originalLoad = load
local originalLoadstring = loadstring
load = function()
	error("table.unserialize must not call load", 2)
end
loadstring = function()
	error("table.unserialize must not call loadstring", 2)
end

test("round-trips canonical strings without removing whitespace", function()
	local values = {
		"plain text",
		"spaces and\ttabs\nnewlines",
		"quotes: 'single' and \"double\" and \\ slash",
		string.char(0, 1, 7, 9, 10, 13, 31, 127, 255),
	}
	for _, value in ipairs(values) do
		local decoded, err = table.unserialize(table.serialize(value))
		assert_equal(err, nil)
		assert_equal(decoded, value)
	end
end)

test("round-trips canonical numbers and true", function()
	for _, value in ipairs({ 0, -12.5, 1250000, true }) do
		local decoded, err = table.unserialize(table.serialize(value))
		assert_equal(err, nil)
		assert_equal(decoded, value)
	end
end)

test("decodes false independently of the known serializer defect", function()
	local decoded, err = table.unserialize("false")
	assert_equal(err, nil)
	assert_equal(decoded, false)
end)

test("decodes nested tables with mixed key types", function()
	local source = [[
		{
			[1] = "array",
			[3] = false,
			["name"] = "value with spaces",
			[true] = { ["nested"] = "ok", ["number"] = -4.5, },
			[7.25] = "numeric-key",
		}
	]]
	local decoded, err = table.unserialize(source)
	assert_equal(err, nil)
	assert_equal(decoded[1], "array")
	assert_equal(decoded[3], false)
	assert_equal(decoded.name, "value with spaces")
	assert_equal(decoded[true].nested, "ok")
	assert_equal(decoded[true].number, -4.5)
	assert_equal(decoded[7.25], "numeric-key")
end)

test("round-trips a canonical nested table without false values", function()
	local value = {
		[1] = "array",
		name = "value",
		[true] = { nested = "ok", number = -4.5 },
		[7.25] = "numeric-key",
	}
	local decoded, err = table.unserialize(table.serialize(value))
	assert_equal(err, nil)
	assert_truthy(deep_equal(decoded, value))
end)

test("supports bounded implicit array entries", function()
	local decoded, err = table.unserialize('{"one", "two", [4] = "four",}')
	assert_equal(err, nil)
	assert_equal(decoded[1], "one")
	assert_equal(decoded[2], "two")
	assert_equal(decoded[4], "four")
end)

test("returns nil without an error for serialized nil", function()
	local decoded, err = table.unserialize("nil")
	assert_equal(decoded, nil)
	assert_equal(err, nil)
end)

test("rejects arbitrary function execution", function()
	_G.__cs007_executed = false
	local decoded, err = table.unserialize('(function() _G.__cs007_executed = true return { executed = true } end)()')
	assert_equal(decoded, nil)
	assert_truthy(type(err) == "string" and err ~= "")
	assert_equal(_G.__cs007_executed, false)
end)

test("rejects global access and function calls", function()
	for _, source in ipairs({ "os", "os.execute('id')", "setmetatable({}, {})", "function() end" }) do
		local decoded, err = table.unserialize(source)
		assert_equal(decoded, nil)
		assert_truthy(type(err) == "string" and err ~= "")
	end
end)

test("rejects trailing code and comments", function()
	for _, source in ipairs({ "{}; error('boom')", "{} return 1", "{} -- comment", "true false" }) do
		local decoded, err = table.unserialize(source)
		assert_equal(decoded, nil)
		assert_truthy(type(err) == "string" and err ~= "")
	end
end)

test("rejects malformed data without executing anything", function()
	for _, source in ipairs({ "", "{", "{[1]}", "{[nil] = 1}", "{[1] = }", '"unterminated', '"bad\\qescape"' }) do
		local decoded, err = table.unserialize(source)
		assert_equal(decoded, nil)
		assert_truthy(type(err) == "string" and err ~= "")
	end
end)

test("enforces nesting depth", function()
	local source = "0"
	for _ = 1, 65 do
		source = "{[1]=" .. source .. "}"
	end
	local decoded, err = table.unserialize(source)
	assert_equal(decoded, nil)
	assert_truthy(type(err) == "string" and err:find("depth", 1, true) ~= nil)
end)

test("enforces input size", function()
	local decoded, err = table.unserialize(string.rep(" ", 1024 * 1024 + 1))
	assert_equal(decoded, nil)
	assert_truthy(type(err) == "string" and err:find("large", 1, true) ~= nil)
end)

test("rejects non-string input", function()
	local decoded, err = table.unserialize({})
	assert_equal(decoded, nil)
	assert_truthy(type(err) == "string" and err ~= "")
end)

load = originalLoad
loadstring = originalLoadstring

print(string.format("\n%d passed, %d failed", passed, failed))
if #errors > 0 then
	print("\nFailed tests:")
	for _, entry in ipairs(errors) do
		print(string.format("  FAIL: %s\n        %s", entry.name, entry.err))
	end
	os.exit(1)
end
