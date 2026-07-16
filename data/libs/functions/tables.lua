table.append = table.insert
table.empty = function(t)
	return next(t) == nil
end

table.find = function(table, value)
	for i, v in pairs(table) do
		if v == value then
			return i
		end
	end

	return nil
end

table.contains = function(array, value)
	for _, targetColumn in pairs(array) do
		if targetColumn == value then
			return true
		end
	end
	return false
end

table.count = function(table, item)
	local count = 0
	for i, n in pairs(table) do
		if item == n then
			count = count + 1
		end
	end

	return count
end
table.countElements = table.count

table.getCombinations = function(table, num)
	local a, number, select, newlist = {}, #table, num, {}
	for i = 1, select do
		a[#a + 1] = i
	end

	local newthing = {}
	while true do
		local newrow = {}
		for i = 1, select do
			newrow[#newrow + 1] = table[a[i]]
		end

		newlist[#newlist + 1] = newrow
		i = select
		while a[i] == (number - select + i) do
			i = i - 1
		end

		if i < 1 then
			break
		end

		a[i] = a[i] + 1
		for j = i, select do
			a[j] = a[i] + j - i
		end
	end

	return newlist
end

function table.serialize(x, recur)
	local t = type(x)
	recur = recur or {}

	if t == nil then
		return "nil"
	elseif t == "string" then
		return string.format("%q", x)
	elseif t == "number" then
		return tostring(x)
	elseif t == "boolean" then
		return t and "true" or "false"
	elseif getmetatable(x) then
		error("Can not serialize a table that has a metatable associated with it.")
	elseif t == "table" then
		if table.find(recur, x) then
			error("Can not serialize recursive tables.")
		end
		table.append(recur, x)

		local s = "{"
		for k, v in pairs(x) do
			s = s .. "[" .. table.serialize(k, recur) .. "]"
			s = s .. " = " .. table.serialize(v, recur) .. ","
		end
		s = s .. "}"
		return s
	else
		error("Can not serialize value of type '" .. t .. "'.")
	end
end

local TABLE_UNSERIALIZE_MAX_BYTES = 1024 * 1024
local TABLE_UNSERIALIZE_MAX_DEPTH = 64
local TABLE_UNSERIALIZE_MAX_VALUES = 100000

local TABLE_UNSERIALIZE_ESCAPES = {
	a = string.char(7),
	b = string.char(8),
	f = string.char(12),
	n = "\n",
	r = "\r",
	t = "\t",
	v = string.char(11),
	["\\"] = "\\",
	['"'] = '"',
	["'"] = "'",
}

local function tableUnserializeError(parser, message)
	return false, nil, string.format("%s at byte %d", message, parser.index)
end

local function tableUnserializeSkipWhitespace(parser)
	while parser.index <= parser.length and parser.source:sub(parser.index, parser.index):match("%s") do
		parser.index = parser.index + 1
	end
end

local function tableUnserializeIsDigit(char)
	return char ~= "" and char >= "0" and char <= "9"
end

local function tableUnserializeParseString(parser)
	local quote = parser.source:sub(parser.index, parser.index)
	parser.index = parser.index + 1
	local output = {}

	while parser.index <= parser.length do
		local char = parser.source:sub(parser.index, parser.index)
		if char == quote then
			parser.index = parser.index + 1
			return true, table.concat(output)
		elseif char == "\\" then
			parser.index = parser.index + 1
			if parser.index > parser.length then
				return tableUnserializeError(parser, "unterminated escape sequence")
			end

			local escaped = parser.source:sub(parser.index, parser.index)
			local replacement = TABLE_UNSERIALIZE_ESCAPES[escaped]
			if replacement ~= nil then
				output[#output + 1] = replacement
				parser.index = parser.index + 1
			elseif tableUnserializeIsDigit(escaped) then
				local value = 0
				local digits = 0
				while digits < 3 and tableUnserializeIsDigit(parser.source:sub(parser.index, parser.index)) do
					value = value * 10 + tonumber(parser.source:sub(parser.index, parser.index))
					parser.index = parser.index + 1
					digits = digits + 1
				end
				if value > 255 then
					return tableUnserializeError(parser, "decimal escape exceeds one byte")
				end
				output[#output + 1] = string.char(value)
			elseif escaped == "x" then
				local hexadecimal = parser.source:sub(parser.index + 1, parser.index + 2)
				if not hexadecimal:match("^%x%x$") then
					return tableUnserializeError(parser, "invalid hexadecimal escape")
				end
				output[#output + 1] = string.char(tonumber(hexadecimal, 16))
				parser.index = parser.index + 3
			elseif escaped == "\n" then
				output[#output + 1] = "\n"
				parser.index = parser.index + 1
			elseif escaped == "\r" then
				if parser.source:sub(parser.index + 1, parser.index + 1) == "\n" then
					parser.index = parser.index + 1
				end
				output[#output + 1] = "\n"
				parser.index = parser.index + 1
			else
				return tableUnserializeError(parser, "unsupported escape sequence")
			end
		elseif char == "\n" or char == "\r" then
			return tableUnserializeError(parser, "unescaped newline in string")
		else
			output[#output + 1] = char
			parser.index = parser.index + 1
		end
	end

	return tableUnserializeError(parser, "unterminated string")
end

local function tableUnserializeParseNumber(parser)
	local start = parser.index
	local char = parser.source:sub(parser.index, parser.index)
	if char == "+" or char == "-" then
		parser.index = parser.index + 1
	end

	local digits = 0
	while tableUnserializeIsDigit(parser.source:sub(parser.index, parser.index)) do
		parser.index = parser.index + 1
		digits = digits + 1
	end

	if parser.source:sub(parser.index, parser.index) == "." then
		parser.index = parser.index + 1
		while tableUnserializeIsDigit(parser.source:sub(parser.index, parser.index)) do
			parser.index = parser.index + 1
			digits = digits + 1
		end
	end

	if digits == 0 then
		return tableUnserializeError(parser, "invalid number")
	end

	char = parser.source:sub(parser.index, parser.index)
	if char == "e" or char == "E" then
		parser.index = parser.index + 1
		char = parser.source:sub(parser.index, parser.index)
		if char == "+" or char == "-" then
			parser.index = parser.index + 1
		end
		local exponentDigits = 0
		while tableUnserializeIsDigit(parser.source:sub(parser.index, parser.index)) do
			parser.index = parser.index + 1
			exponentDigits = exponentDigits + 1
		end
		if exponentDigits == 0 then
			return tableUnserializeError(parser, "invalid number exponent")
		end
	end

	local value = tonumber(parser.source:sub(start, parser.index - 1))
	if value == nil or value ~= value or value == math.huge or value == -math.huge then
		return tableUnserializeError(parser, "invalid finite number")
	end
	return true, value
end

local tableUnserializeParseValue

local function tableUnserializeParseTable(parser, depth)
	if depth > TABLE_UNSERIALIZE_MAX_DEPTH then
		return tableUnserializeError(parser, "maximum table depth exceeded")
	end

	parser.index = parser.index + 1
	local result = {}
	local implicitIndex = 1
	tableUnserializeSkipWhitespace(parser)
	if parser.source:sub(parser.index, parser.index) == "}" then
		parser.index = parser.index + 1
		return true, result
	end

	while parser.index <= parser.length do
		tableUnserializeSkipWhitespace(parser)
		local key
		local value
		local ok
		local err

		if parser.source:sub(parser.index, parser.index) == "[" then
			parser.index = parser.index + 1
			ok, key, err = tableUnserializeParseValue(parser, depth)
			if not ok then
				return false, nil, err
			end
			if key == nil then
				return tableUnserializeError(parser, "nil table key")
			end
			tableUnserializeSkipWhitespace(parser)
			if parser.source:sub(parser.index, parser.index) ~= "]" then
				return tableUnserializeError(parser, "expected closing key bracket")
			end
			parser.index = parser.index + 1
			tableUnserializeSkipWhitespace(parser)
			if parser.source:sub(parser.index, parser.index) ~= "=" then
				return tableUnserializeError(parser, "expected key assignment")
			end
			parser.index = parser.index + 1
		else
			key = implicitIndex
			implicitIndex = implicitIndex + 1
		end

		ok, value, err = tableUnserializeParseValue(parser, depth)
		if not ok then
			return false, nil, err
		end
		result[key] = value

		tableUnserializeSkipWhitespace(parser)
		local separator = parser.source:sub(parser.index, parser.index)
		if separator == "," or separator == ";" then
			parser.index = parser.index + 1
			tableUnserializeSkipWhitespace(parser)
			if parser.source:sub(parser.index, parser.index) == "}" then
				parser.index = parser.index + 1
				return true, result
			end
		elseif separator == "}" then
			parser.index = parser.index + 1
			return true, result
		else
			return tableUnserializeError(parser, "expected table separator or closing brace")
		end
	end

	return tableUnserializeError(parser, "unterminated table")
end

tableUnserializeParseValue = function(parser, depth)
	tableUnserializeSkipWhitespace(parser)
	parser.values = parser.values + 1
	if parser.values > TABLE_UNSERIALIZE_MAX_VALUES then
		return tableUnserializeError(parser, "maximum value count exceeded")
	end

	local char = parser.source:sub(parser.index, parser.index)
	if char == "" then
		return tableUnserializeError(parser, "expected a value")
	elseif char == '"' or char == "'" then
		return tableUnserializeParseString(parser)
	elseif char == "{" then
		return tableUnserializeParseTable(parser, depth + 1)
	elseif tableUnserializeIsDigit(char) or char == "+" or char == "-" or char == "." then
		return tableUnserializeParseNumber(parser)
	end

	local keywords = {
		["nil"] = nil,
		["true"] = true,
		["false"] = false,
	}
	for _, keyword in ipairs({ "nil", "true", "false" }) do
		if parser.source:sub(parser.index, parser.index + #keyword - 1) == keyword then
			local following = parser.source:sub(parser.index + #keyword, parser.index + #keyword)
			if following == "" or not following:match("[%w_]") then
				parser.index = parser.index + #keyword
				return true, keywords[keyword]
			end
		end
	end

	return tableUnserializeError(parser, "unsupported value")
end

function table.unserialize(str)
	if type(str) ~= "string" then
		return nil, "serialized value must be a string"
	end
	if #str > TABLE_UNSERIALIZE_MAX_BYTES then
		return nil, "serialized value is too large"
	end

	local parser = {
		source = str,
		length = #str,
		index = 1,
		values = 0,
	}
	local ok, value, err = tableUnserializeParseValue(parser, 0)
	if not ok then
		return nil, err
	end
	tableUnserializeSkipWhitespace(parser)
	if parser.index <= parser.length then
		return nil, string.format("trailing data at byte %d", parser.index)
	end
	return value
end

function table.shallowCopy(oldTable)
	local newTable = {}
	for k, v in pairs(oldTable) do
		newTable[k] = v
	end
	return newTable
end

function pairsByKeys(t, f)
	local a = {}
	for n in pairs(t) do
		table.insert(a, n)
	end
	table.sort(a, f)
	local i = 0 -- iterator variable
	local iter = function() -- iterator function
		i = i + 1
		if a[i] == nil then
			return nil
		else
			return a[i], t[a[i]]
		end
	end
	return iter
end
