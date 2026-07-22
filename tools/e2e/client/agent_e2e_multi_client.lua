local M = {}

local function sanitize(value)
	return tostring(value):gsub("[\t\r\n]", " ")
end

local function shellQuote(value)
	return "'" .. tostring(value):gsub("'", "'\\''") .. "'"
end

local function readFile(path)
	local file = io.open(path, "r")
	if not file then
		return nil
	end
	local content = file:read("*a") or ""
	file:close()
	return content
end

local function writeFile(path, content)
	local file, err = io.open(path, "w")
	if not file then
		return false, err
	end
	file:write(content)
	file:close()
	return true
end

local function copyFile(source, target)
	local content = readFile(source)
	if not content then
		return false, "cannot read " .. tostring(source)
	end
	return writeFile(target, content)
end

local function selfPid()
	local stat = readFile("/proc/self/stat")
	if not stat then
		return nil
	end
	return tonumber(stat:match("^(%d+)%s"))
end

function M.readEnvFile(path)
	local content = readFile(path)
	if not content then
		return nil, "cannot read environment file " .. tostring(path)
	end
	local values = {}
	for line in content:gmatch("[^\r\n]+") do
		local key, value = line:match("^([A-Z_][A-Z0-9_]*)=(.*)$")
		if not key then
			return nil, "invalid environment line: " .. sanitize(line)
		end
		if value:find("[\r\n%z]") then
			return nil, "invalid control data for " .. key
		end
		values[key] = value
	end
	return values, nil
end

function M.hasEvent(path, key, value)
	local content = readFile(path)
	if not content then
		return false
	end
	local expected = "\t" .. tostring(key) .. "\t" .. tostring(value)
	for line in content:gmatch("[^\r\n]+") do
		if line:find(expected, 1, true) then
			return true
		end
	end
	return false
end

function M.writeRelease(path)
	return writeFile(path, "release\n")
end

function M.spawnSecondary(options)
	if type(options) ~= "table" then
		return false, "options must be a table"
	end
	local otclientRoot = options.otclientRoot
	local otclientBin = options.otclientBin
	local automationSource = options.automationSource
	local artifactDir = options.artifactDir
	local env = options.env
	local timeoutSeconds = tonumber(options.timeoutSeconds or 90)
	if type(otclientRoot) ~= "string" or otclientRoot == "" then
		return false, "otclientRoot is required"
	end
	if type(otclientBin) ~= "string" or otclientBin == "" then
		return false, "otclientBin is required"
	end
	if type(automationSource) ~= "string" or automationSource == "" then
		return false, "automationSource is required"
	end
	if type(artifactDir) ~= "string" or artifactDir == "" then
		return false, "artifactDir is required"
	end
	if type(env) ~= "table" then
		return false, "env is required"
	end
	if not timeoutSeconds or timeoutSeconds < 10 or timeoutSeconds > 300 then
		return false, "timeoutSeconds must be between 10 and 300"
	end
	local parentPid = selfPid()
	if not parentPid then
		return false, "cannot resolve primary OTClient pid"
	end

	local ok, err = copyFile(automationSource, otclientRoot .. "/otclientrc.lua")
	if not ok then
		return false, err
	end
	os.execute("mkdir -p " .. shellQuote(artifactDir))

	local keys = {}
	for key, value in pairs(env) do
		if type(key) ~= "string" or not key:match("^[A-Z_][A-Z0-9_]*$") then
			return false, "unsafe environment key"
		end
		if type(value) ~= "string" or value:find("[\r\n%z]") then
			return false, "unsafe environment value for " .. key
		end
		table.insert(keys, key)
	end
	table.sort(keys)
	local assignments = {}
	for _, key in ipairs(keys) do
		table.insert(assignments, key .. "=" .. shellQuote(env[key]))
	end

	local pidFile = artifactDir .. "/otclient.pid"
	local exitFile = artifactDir .. "/otclient-exit-code.txt"
	local stdoutFile = artifactDir .. "/otclient.stdout.log"
	local stderrFile = artifactDir .. "/otclient.stderr.log"
	local script = table.concat({
		"set +e",
		"cd " .. shellQuote(otclientRoot),
		"env " .. table.concat(assignments, " ") .. " timeout --signal=TERM " .. tostring(timeoutSeconds) .. " " .. shellQuote(otclientBin) .. " >" .. shellQuote(stdoutFile) .. " 2>" .. shellQuote(stderrFile) .. " &",
		"child=$!",
		"printf '%s\\n' \"$child\" >" .. shellQuote(pidFile),
		"while kill -0 \"$child\" 2>/dev/null; do",
		"  if ! kill -0 " .. tostring(parentPid) .. " 2>/dev/null; then kill \"$child\" 2>/dev/null || true; break; fi",
		"  sleep 1",
		"done",
		"wait \"$child\"",
		"status=$?",
		"printf '%s\\n' \"$status\" >" .. shellQuote(exitFile),
		"exit 0",
	}, "\n")
	local command = "sh -c " .. shellQuote(script) .. " >/dev/null 2>&1 &"
	local result = os.execute(command)
	if result ~= true and result ~= 0 then
		return false, "failed to launch secondary OTClient watchdog"
	end
	return true, tostring(parentPid)
end

function M.stopSecondary(artifactDir)
	local pid = tonumber((readFile(artifactDir .. "/otclient.pid") or ""):match("(%d+)"))
	if not pid then
		return false
	end
	os.execute("kill " .. tostring(pid) .. " >/dev/null 2>&1 || true")
	return true
end

return M
