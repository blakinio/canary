FS = {}

function FS.exists(path)
	local file = io.open(path, "r")
	if file then
		file:close()
		return true
	end
	return false
end

function FS.mkdir(path)
	return FileSystem.createDirectory(path)
end

function FS.mkdir_p(path)
	if path == "" then
		return true
	end
	return FileSystem.createDirectories(path)
end
