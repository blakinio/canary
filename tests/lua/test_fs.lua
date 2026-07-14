-- Run: luajit tests/lua/test_fs.lua

local calls = {}
local shellCalled = false
local realExecute = os.execute

os.execute = function()
	shellCalled = true
	error("FS helpers must not invoke os.execute")
end

FileSystem = {
	createDirectory = function(path)
		table.insert(calls, { method = "createDirectory", path = path })
		return true
	end,
	createDirectories = function(path)
		table.insert(calls, { method = "createDirectories", path = path })
		return true
	end,
}

dofile("data/libs/functions/fs.lua")

local function assertEqual(actual, expected, message)
	if actual ~= expected then
		error(string.format("%s: expected %s, got %s", message, tostring(expected), tostring(actual)))
	end
end

assertEqual(FS.mkdir("reports/player $(touch marker)"), true, "single directory result")
assertEqual(calls[1].method, "createDirectory", "single directory method")
assertEqual(calls[1].path, "reports/player $(touch marker)", "single directory path")

assertEqual(FS.mkdir_p("reports/bugs/player name"), true, "recursive directory result")
assertEqual(calls[2].method, "createDirectories", "recursive directory method")
assertEqual(calls[2].path, "reports/bugs/player name", "recursive directory path")

local beforeEmpty = #calls
assertEqual(FS.mkdir_p(""), true, "empty recursive path")
assertEqual(#calls, beforeEmpty, "empty recursive path must not call native binding")

FileSystem.createDirectory = function(path)
	return false, "denied: " .. path
end
local success, err = FS.mkdir("blocked")
assertEqual(success, false, "error success flag")
assertEqual(err, "denied: blocked", "error message passthrough")
assertEqual(shellCalled, false, "shell execution")

os.execute = realExecute
print("FS shell-free wrapper tests passed")
