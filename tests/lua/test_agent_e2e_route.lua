North = 0
East = 1
South = 2
West = 3
NorthEast = 4
SouthEast = 5
SouthWest = 6
NorthWest = 7

local scheduled = {}
local currentPosition = nil
local walkHandler = nil
local walkCalls = 0
local useCalls = 0
local useInventoryCalls = 0
local inventory = {}
local tiles = {}

local function copyPosition(value)
	return { x = value.x, y = value.y, z = value.z }
end

local function positionKey(value)
	return string.format("%d,%d,%d", value.x, value.y, value.z)
end

local function assertEqual(actual, expected, label)
	if actual ~= expected then
		error(string.format("%s: expected=%s actual=%s", label, tostring(expected), tostring(actual)))
	end
end

local function assertContains(value, expected, label)
	if not tostring(value):find(expected, 1, true) then
		error(string.format("%s: expected substring=%s actual=%s", label, expected, tostring(value)))
	end
end

function scheduleEvent(callback, _)
	table.insert(scheduled, callback)
end

local player = {}

function player:getPosition()
	return currentPosition and copyPosition(currentPosition) or nil
end

function player:getInventoryCount(itemId, _)
	return inventory[itemId] or 0
end

g_game = {
	getLocalPlayer = function()
		return player
	end,
	walk = function(direction)
		walkCalls = walkCalls + 1
		if walkHandler then
			return walkHandler(direction)
		end
		return false
	end,
	use = function(_)
		useCalls = useCalls + 1
	end,
	useInventoryItemWith = function(_, _)
		useInventoryCalls = useInventoryCalls + 1
	end,
}

g_map = {
	getTile = function(position)
		return tiles[positionKey(position)]
	end,
}

local routeExecutor = dofile("tools/e2e/client/agent_e2e_route.lua")

local function drainEvents(limit)
	limit = limit or 100
	local count = 0
	while #scheduled > 0 do
		count = count + 1
		if count > limit then
			error("scheduled event queue did not drain")
		end
		local callback = table.remove(scheduled, 1)
		callback()
	end
end

local function reset(position)
	scheduled = {}
	currentPosition = copyPosition(position)
	walkHandler = nil
	walkCalls = 0
	useCalls = 0
	useInventoryCalls = 0
	inventory = {}
	tiles = {}
end

local function item(id)
	return {
		getId = function()
			return id
		end,
	}
end

local function tile(items)
	return {
		getItems = function()
			return items
		end,
	}
end

local function callbacks()
	local result = {
		events = {},
		failure = nil,
		completed = nil,
	}
	return result, {
		appendEvent = function(key, value)
			table.insert(result.events, key .. "=" .. tostring(value))
		end,
		failStep = function(_, message)
			result.failure = message
		end,
		completeStep = function(_, detail)
			result.completed = detail
		end,
	}
end

local function hasEvent(result, expected)
	for _, value in ipairs(result.events) do
		if value == expected then
			return true
		end
	end
	return false
end

local function testWalkEdgeSuccess()
	reset({ x = 100, y = 100, z = 7 })
	walkHandler = function(direction)
		assertEqual(direction, East, "walk direction")
		currentPosition = { x = 101, y = 100, z = 7 }
		return true
	end
	local success = nil
	local failure = nil
	routeExecutor.walkEdge({ 100, 100, 7 }, { 101, 100, 7 }, 500, {
		onSuccess = function(detail)
			success = detail
		end,
		onFailure = function(code, detail)
			failure = code .. ":" .. detail
		end,
	})
	drainEvents()
	assertEqual(walkCalls, 1, "exact movement request count")
	assertEqual(success, "101,100,7", "exact movement destination")
	assertEqual(failure, nil, "movement success failure state")
end

local function testWalkEdgeDivergenceFailsFirstMismatch()
	reset({ x = 100, y = 100, z = 7 })
	walkHandler = function(_)
		currentPosition = { x = 102, y = 100, z = 7 }
		return true
	end
	local failureCode = nil
	local failureDetail = nil
	routeExecutor.walkEdge({ 100, 100, 7 }, { 101, 100, 7 }, 500, {
		onSuccess = function(_)
			error("divergent movement unexpectedly succeeded")
		end,
		onFailure = function(code, detail)
			failureCode = code
			failureDetail = detail
		end,
	})
	assertEqual(walkCalls, 1, "divergent movement request count")
	assertEqual(failureCode, "MOVEMENT_DIVERGENCE", "divergence code")
	assertContains(failureDetail, "actual=102,100,7", "divergence actual position")
	assertContains(failureDetail, "expected=101,100,7", "divergence expected position")
end

local function testWalkEdgeTimeoutIsBounded()
	reset({ x = 100, y = 100, z = 7 })
	walkHandler = function(_)
		return true
	end
	local failureCode = nil
	routeExecutor.walkEdge({ 100, 100, 7 }, { 101, 100, 7 }, 200, {
		onSuccess = function(_)
			error("timed-out movement unexpectedly succeeded")
		end,
		onFailure = function(code, _)
			failureCode = code
		end,
	})
	drainEvents()
	assertEqual(failureCode, "MOVEMENT_TIMEOUT", "movement timeout code")
	assertEqual(walkCalls, 1, "timed-out movement request count")
end

local function testFollowRouteMovementEvidenceAndCompletion()
	reset({ x = 100, y = 100, z = 7 })
	walkHandler = function(_)
		currentPosition = { x = 101, y = 100, z = 7 }
		return true
	end
	local result, routeCallbacks = callbacks()
	routeExecutor.execute(
		{ id = "fixture", action = "follow_route", timeout_ms = 500 },
		{
			origin = { 100, 100, 7 },
			destination = { 101, 100, 7 },
			edges = {
				{
					kind = "movement",
					from = { 100, 100, 7 },
					to = { 101, 100, 7 },
					interactions = {},
				},
			},
		},
		routeCallbacks
	)
	drainEvents()
	assertEqual(result.failure, nil, "follow_route movement failure state")
	assertEqual(result.completed, "101,100,7", "follow_route destination")
	assertEqual(walkCalls, 1, "follow_route exact movement request count")
	assertEqual(hasEvent(result, "route_fixture_edge_1=start"), true, "edge start marker")
	assertEqual(hasEvent(result, "route_fixture_edge_1=success"), true, "edge success marker")
	assertEqual(hasEvent(result, "route_fixture=success"), true, "route success marker")
end

local function testWrongTransitionDestinationFailsWithExpectedActual()
	reset({ x = 100, y = 100, z = 7 })
	walkHandler = function(direction)
		assertEqual(direction, East, "transition direction")
		currentPosition = { x = 999, y = 999, z = 7 }
		return true
	end
	local result, routeCallbacks = callbacks()
	routeExecutor.execute(
		{ id = "transition", action = "follow_route", timeout_ms = 500 },
		{
			origin = { 100, 100, 7 },
			destination = { 200, 200, 8 },
			edges = {
				{
					kind = "transition",
					from = { 100, 100, 7 },
					to = { 200, 200, 8 },
					interactions = {
						{ kind = "walk-direction", direction = "east" },
					},
				},
			},
		},
		routeCallbacks
	)
	assertContains(result.failure, "WRONG_TRANSITION_DESTINATION", "wrong transition failure code")
	assertContains(result.failure, "actual=999,999,7", "wrong transition actual position")
	assertContains(result.failure, "expected=200,200,8", "wrong transition expected position")
	assertEqual(walkCalls, 1, "transition request count")
end

local function testUseMapItemTransitionUsesExactTarget()
	reset({ x = 100, y = 100, z = 7 })
	tiles["100,100,7"] = tile({ item(1387) })
	g_game.use = function(target)
		useCalls = useCalls + 1
		assertEqual(target:getId(), 1387, "use-map exact item id")
		currentPosition = { x = 200, y = 200, z = 8 }
	end
	local result, routeCallbacks = callbacks()
	routeExecutor.execute(
		{ id = "use-map", action = "follow_route", timeout_ms = 500 },
		{
			origin = { 100, 100, 7 },
			destination = { 200, 200, 8 },
			edges = {
				{
					kind = "transition",
					from = { 100, 100, 7 },
					to = { 200, 200, 8 },
					interactions = {
						{
							kind = "use-map-item",
							target_position = { 100, 100, 7 },
							target_item_id = 1387,
						},
					},
				},
			},
		},
		routeCallbacks
	)
	drainEvents()
	assertEqual(useCalls, 1, "use-map request count")
	assertEqual(result.failure, nil, "use-map transition failure state")
	assertEqual(result.completed, "200,200,8", "use-map transition destination")
end

local function testUseInventoryOnMapTransitionUsesVerifiedApiShape()
	reset({ x = 100, y = 100, z = 7 })
	inventory[3147] = 1
	tiles["100,100,7"] = tile({ item(1387) })
	g_game.useInventoryItemWith = function(inventoryItemId, target)
		useInventoryCalls = useInventoryCalls + 1
		assertEqual(inventoryItemId, 3147, "inventory source item id")
		assertEqual(target:getId(), 1387, "inventory-on-map exact target item id")
		currentPosition = { x = 200, y = 200, z = 8 }
	end
	local result, routeCallbacks = callbacks()
	routeExecutor.execute(
		{ id = "inventory-map", action = "follow_route", timeout_ms = 500 },
		{
			origin = { 100, 100, 7 },
			destination = { 200, 200, 8 },
			edges = {
				{
					kind = "transition",
					from = { 100, 100, 7 },
					to = { 200, 200, 8 },
					interactions = {
						{
							kind = "use-inventory-on-map",
							target_position = { 100, 100, 7 },
							target_item_id = 1387,
							inventory_item_id = 3147,
						},
					},
				},
			},
		},
		routeCallbacks
	)
	drainEvents()
	assertEqual(useInventoryCalls, 1, "use-inventory-on-map request count")
	assertEqual(result.failure, nil, "use-inventory-on-map failure state")
	assertEqual(result.completed, "200,200,8", "use-inventory-on-map destination")
end

testWalkEdgeSuccess()
testWalkEdgeDivergenceFailsFirstMismatch()
testWalkEdgeTimeoutIsBounded()
testFollowRouteMovementEvidenceAndCompletion()
testWrongTransitionDestinationFailsWithExpectedActual()
testUseMapItemTransitionUsesExactTarget()
testUseInventoryOnMapTransitionUsesVerifiedApiShape()

local pythonStatus = os.execute(
	"python3 tests/e2e/test_follow_route_execution.py"
		.. " && python3 tests/e2e/test_exact_movement_edges.py"
		.. " && python3 tests/e2e/test_agent_e2e_scenario_plan.py"
)
if pythonStatus ~= 0 and pythonStatus ~= true then
	error("focused Python E2E route contract tests failed with status " .. tostring(pythonStatus))
end

print("agent_e2e_route contract tests passed")
