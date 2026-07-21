local ARTIFACT_DIR = os.getenv("AGENT_E2E_ARTIFACT_DIR") or "../artifacts"
local EVENTS_PATH = ARTIFACT_DIR .. "/client-events.tsv"
local DATAPACK_PATH = assert(os.getenv("AGENT_E2E_SERVER_DATAPACK_PATH"), "AGENT_E2E_SERVER_DATAPACK_PATH is required")
local REPO_ROOT = assert(DATAPACK_PATH:match("^(.*)/[^/]+$"), "unable to resolve Canary repository root")
local GENERIC_DRIVER_PATH = REPO_ROOT .. "/tools/e2e/client/agent_e2e_scenario.lua"

local expectedResponses = {
	{
		marker = "quentin_greeting",
		contains = "Welcome, young",
		nextMessage = "adventurer stone",
		sentMarker = "quentin_request_stone_sent",
	},
	{
		marker = "quentin_free_stone_offer",
		contains = "replace your adventurer's stone for free",
		nextMessage = "yes",
		sentMarker = "quentin_accept_stone_sent",
	},
	{
		marker = "quentin_reward_response",
		contains = "Here you are. Take care.",
	},
}
local expectedIndex = 1

local function sanitize(value)
	return tostring(value):gsub("[\t\r\n]", " ")
end

local function appendEvent(key, value)
	local file = assert(io.open(EVENTS_PATH, "a"))
	file:write(string.format("%d\t%s\t%s\n", os.time(), sanitize(key), sanitize(value)))
	file:close()
	g_logger.info(string.format("[quentin-e2e] %s=%s", tostring(key), tostring(value)))
end

local function sendNpcMessage(marker, text)
	g_game.talkPrivate(MessageModes.NpcTo, "Quentin", text)
	appendEvent(marker, "private_npc")
end

local function runCanonicalDriver()
	local file = assert(io.open(GENERIC_DRIVER_PATH, "r"))
	local source = file:read("*a")
	file:close()
	local chunk, loadError = loadstring(source, "@" .. GENERIC_DRIVER_PATH)
	assert(chunk, loadError)
	return chunk()
end

connect(g_game, {
	onTalk = function(name, _, _, text)
		if name ~= "Quentin" then
			return
		end
		appendEvent("quentin_talk_received", text)
		local expected = expectedResponses[expectedIndex]
		if not expected or not text:find(expected.contains, 1, true) then
			return
		end
		appendEvent(expected.marker, "confirmed")
		expectedIndex = expectedIndex + 1
		if expected.nextMessage then
			scheduleEvent(function()
				sendNpcMessage(expected.sentMarker, expected.nextMessage)
			end, 100)
		end
	end,
})

-- Preserve the canonical Generic Physical E2E lifecycle without duplicating it.
-- This feature adapter adds only the response-driven NPC-private dialogue that
-- the focused Canary NPC handler requires after the initial greeting.
runCanonicalDriver()
