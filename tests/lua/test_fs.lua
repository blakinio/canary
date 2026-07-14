-- Runtime-independent contract tests for data/libs/functions/fs.lua
-- Run: luajit tests/lua/test_fs.lua

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

local calls = {}
fs = {
	createDirectory = function(path)
		table.insert(calls, { method = "createDirectory", path = path })
		return true
	end,
	createDirectories = function(path)
		table.insert(calls, { method = "createDirectories", path = path })
		return true
	end,
}

local originalExecute = os.execute
os.execute = function()
	error("FS helpers must not execute a shell", 2)
end
dofile("data/libs/functions/fs.lua")

test("mkdir delegates hostile paths literally to the native binding", function()
	local hostile = 'reports/unsafe" & echo injected > marker & echo "'
	assert_equal(FS.mkdir(hostile), true)
	assert_equal(calls[#calls].method, "createDirectory")
	assert_equal(calls[#calls].path, hostile)
end)

test("mkdir_p delegates recursive creation without path splitting", function()
	local path = "reports/bugs/Player Name/child"
	assert_equal(FS.mkdir_p(path), true)
	assert_equal(calls[#calls].method, "createDirectories")
	assert_equal(calls[#calls].path, path)
end)

test("mkdir_p preserves the empty-path success contract", function()
	local before = #calls
	assert_equal(FS.mkdir_p(""), true)
	assert_equal(#calls, before)
end)

os.execute = originalExecute

print(string.format("\n%d passed, %d failed", passed, failed))
if #errors > 0 then
	print("\nFailed tests:")
	for _, entry in ipairs(errors) do
		print(string.format("  FAIL: %s\n        %s", entry.name, entry.err))
	end
	os.exit(1)
end
