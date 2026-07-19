local M = {}

local DIRECTIONS = {
	north = North or 0,
	east = East or 1,
	south = South or 2,
	west = West or 3,
	["north-east"] = NorthEast or 4,
	["south-east"] = SouthEast or 5,
	["south-west"] = SouthWest or 6,
	["north-west"] = NorthWest or 7,
}

local MOVEMENT_DIRECTIONS = {
	["0,-1"] = DIRECTIONS.north,
	["1,-1"] = DIRECTIONS["north-east"],
	["1,0"] = DIRECTIONS.east,
	["1,1"] = DIRECTIONS["south-east"],
	["0,1"] = DIRECTIONS.south,
	["-1,1"] = DIRECTIONS["south-west"],
	["-1,0"] = DIRECTIONS.west,
	["-1,-1"] = DIRECTIONS["north-west"],
}

local function position(value)
	if type(value) ~= "table" then
		return nil
	end
	if value.x ~= nil or value.y ~= nil or value.z ~= nil then
		return { x = value.x, y = value.y, z = value.z }
	end
	return { x = value[1], y = value[2], z = value[3] }
end

local function samePosition(a, b)
	return a and b and a.x == b.x and a.y == b.y and a.z == b.z
end

local function positionString(value)
	if not value then
		return "unavailable"
	end
	return string.format("%d,%d,%d", value.x, value.y, value.z)
end

local function localPosition()
	local player = g_game.getLocalPlayer()
	return player and player:getPosition() or nil
end

local function findExactMapItem(targetPosition, itemId)
	local tile = g_map.getTile(targetPosition)
	if not tile then
		return nil, "target tile unavailable at " .. positionString(targetPosition)
	end
	local match = nil
	local count = 0
	for _, item in ipairs(tile:getItems() or {}) do
		if item and item:getId() == itemId then
			match = item
			count = count + 1
		end
	end
	if count == 0 then
		return nil, string.format("target item %d unavailable at %s", itemId, positionString(targetPosition))
	end
	if count > 1 then
		return nil, string.format("target item %d ambiguous at %s matches=%d", itemId, positionString(targetPosition), count)
	end
	return match, nil
end

function M.walkEdge(sourceValue, destinationValue, timeoutMs, callbacks)
	local source = position(sourceValue)
	local destination = position(destinationValue)
	local actual = localPosition()
	if not source or not destination then
		callbacks.onFailure("MOVEMENT_DIVERGENCE", "invalid exact movement edge contract")
		return
	end
	if not samePosition(actual, source) then
		callbacks.onFailure("INITIAL_POSITION_MISMATCH", string.format("source mismatch actual=%s expected=%s", positionString(actual), positionString(source)))
		return
	end
	if source.z ~= destination.z then
		callbacks.onFailure("MOVEMENT_DIVERGENCE", "floor-changing movement edge is unsupported")
		return
	end
	local deltaX = destination.x - source.x
	local deltaY = destination.y - source.y
	local direction = MOVEMENT_DIRECTIONS[string.format("%d,%d", deltaX, deltaY)]
	if direction == nil then
		callbacks.onFailure("MOVEMENT_DIVERGENCE", string.format("invalid adjacent edge delta=%d,%d", deltaX, deltaY))
		return
	end
	if not g_game.walk(direction) then
		callbacks.onFailure("MOVEMENT_DIVERGENCE", "walk request rejected")
		return
	end

	local remainingChecks = math.max(1, math.floor((timeoutMs or 10000) / 100))
	local function check()
		local livePosition = localPosition()
		if not livePosition then
			callbacks.onFailure("MOVEMENT_DIVERGENCE", "local player position unavailable")
			return
		end
		if samePosition(livePosition, destination) then
			callbacks.onSuccess(positionString(livePosition))
			return
		end
		if not samePosition(livePosition, source) then
			callbacks.onFailure("MOVEMENT_DIVERGENCE", string.format("route drift actual=%s expected=%s", positionString(livePosition), positionString(destination)))
			return
		end
		remainingChecks = remainingChecks - 1
		if remainingChecks <= 0 then
			callbacks.onFailure("MOVEMENT_TIMEOUT", string.format("position=%s expected=%s timeout_ms=%d", positionString(livePosition), positionString(destination), timeoutMs or 10000))
			return
		end
		scheduleEvent(check, 100)
	end
	check()
end

function M.execute(step, route, callbacks)
	local timeoutMs = step.timeout_ms or 10000
	local edgeIndex = 1
	local activeMarker = nil

	local function failRoute(code, detail)
		if activeMarker then
			callbacks.appendEvent(activeMarker, "failure")
		end
		callbacks.failStep(step, string.format("%s: %s", code, detail or "unspecified route failure"))
	end

	local function assertCurrent(expected, code, context)
		local actual = localPosition()
		if not samePosition(actual, expected) then
			failRoute(code, string.format("%s actual=%s expected=%s", context, positionString(actual), positionString(expected)))
			return false
		end
		return true
	end

	local function pollExactDestination(source, destination, timeoutCode, divergenceCode, onSuccess)
		local remainingChecks = math.max(1, math.floor(timeoutMs / 100))
		local function check()
			local actual = localPosition()
			if not actual then
				failRoute(divergenceCode, "local player position unavailable")
				return
			end
			if samePosition(actual, destination) then
				onSuccess()
				return
			end
			if not samePosition(actual, source) then
				failRoute(divergenceCode, string.format("actual=%s expected=%s", positionString(actual), positionString(destination)))
				return
			end
			remainingChecks = remainingChecks - 1
			if remainingChecks <= 0 then
				failRoute(timeoutCode, string.format("position=%s expected=%s timeout_ms=%d", positionString(actual), positionString(destination), timeoutMs))
				return
			end
			scheduleEvent(check, 100)
		end
		check()
	end

	local function executeUseInteraction(interaction, marker, onSuccess)
		local targetPosition = position(interaction.target_position)
		local targetItemId = interaction.target_item_id
		if not targetPosition or type(targetItemId) ~= "number" then
			failRoute("INTERACTION_FAILED", "invalid exact map target contract")
			return
		end
		local targetThing, targetError = findExactMapItem(targetPosition, targetItemId)
		if not targetThing then
			failRoute("INTERACTION_FAILED", targetError)
			return
		end
		if interaction.kind == "use-map-item" then
			g_game.use(targetThing)
		elseif interaction.kind == "use-inventory-on-map" then
			local player = g_game.getLocalPlayer()
			local inventoryItemId = interaction.inventory_item_id
			if not player or type(inventoryItemId) ~= "number" or player:getInventoryCount(inventoryItemId, 0) <= 0 then
				failRoute("INTERACTION_FAILED", "inventory item unavailable: " .. tostring(inventoryItemId))
				return
			end
			g_game.useInventoryItemWith(inventoryItemId, targetThing)
		else
			failRoute("INTERACTION_FAILED", "unsupported use interaction kind: " .. tostring(interaction.kind))
			return
		end
		scheduleEvent(function()
			callbacks.appendEvent(marker, "success")
			onSuccess()
		end, 200)
	end

	local executeMovementEdge
	local executeTransitionEdge
	local executeNextEdge

	executeMovementEdge = function(edge, marker)
		local source = position(edge.from)
		local destination = position(edge.to)
		if not assertCurrent(source, "INITIAL_POSITION_MISMATCH", "movement source mismatch") then
			return
		end
		local interactions = edge.interactions or {}
		local interactionIndex = 1

		local function walkOnce()
			activeMarker = marker
			M.walkEdge(edge.from, edge.to, timeoutMs, {
				onSuccess = function(detail)
					callbacks.appendEvent(marker, "success")
					callbacks.appendEvent(marker .. "_detail", detail)
					edgeIndex = edgeIndex + 1
					scheduleEvent(executeNextEdge, 100)
				end,
				onFailure = function(code, detail)
					failRoute(code, detail)
				end,
			})
		end

		local function executeNextInteraction()
			if interactionIndex > #interactions then
				walkOnce()
				return
			end
			local interaction = interactions[interactionIndex]
			local interactionMarker = marker .. "_interaction_" .. tostring(interactionIndex)
			callbacks.appendEvent(interactionMarker, "start")
			if interaction.kind ~= "use-map-item" and interaction.kind ~= "use-inventory-on-map" then
				activeMarker = interactionMarker
				failRoute("INTERACTION_FAILED", "unsupported movement interaction kind: " .. tostring(interaction.kind))
				return
			end
			activeMarker = interactionMarker
			executeUseInteraction(interaction, interactionMarker, function()
				interactionIndex = interactionIndex + 1
				activeMarker = marker
				executeNextInteraction()
			end)
		end

		executeNextInteraction()
	end

	executeTransitionEdge = function(edge, marker)
		local source = position(edge.from)
		local destination = position(edge.to)
		if not assertCurrent(source, "INITIAL_POSITION_MISMATCH", "transition source mismatch") then
			return
		end
		if type(edge.interactions) ~= "table" or #edge.interactions ~= 1 then
			failRoute("INTERACTION_FAILED", "transition requires exactly one interaction")
			return
		end
		local interaction = edge.interactions[1]
		local interactionMarker = marker .. "_interaction_1"
		callbacks.appendEvent(interactionMarker, "start")
		activeMarker = interactionMarker

		local function waitForDestination(timeoutCode, markInteractionOnDestination)
			pollExactDestination(source, destination, timeoutCode, "WRONG_TRANSITION_DESTINATION", function()
				if markInteractionOnDestination then
					callbacks.appendEvent(interactionMarker, "success")
				end
				callbacks.appendEvent(marker, "success")
				callbacks.appendEvent(marker .. "_detail", positionString(destination))
				activeMarker = marker
				edgeIndex = edgeIndex + 1
				scheduleEvent(executeNextEdge, 100)
			end)
		end

		if interaction.kind == "step-on" then
			waitForDestination("TRANSITION_NOT_TRIGGERED", true)
			return
		end
		if interaction.kind == "walk-direction" then
			local direction = DIRECTIONS[interaction.direction]
			if direction == nil or not g_game.walk(direction) then
				failRoute("INTERACTION_FAILED", "transition movement request rejected")
				return
			end
			waitForDestination("TRANSITION_NOT_TRIGGERED", true)
			return
		end
		if interaction.kind == "use-map-item" or interaction.kind == "use-inventory-on-map" then
			executeUseInteraction(interaction, interactionMarker, function()
				activeMarker = marker
				waitForDestination("INTERACTION_TIMEOUT", false)
			end)
			return
		end
		failRoute("INTERACTION_FAILED", "unsupported transition interaction kind: " .. tostring(interaction.kind))
	end

	executeNextEdge = function()
		if edgeIndex > #route.edges then
			local expected = position(route.destination)
			if not assertCurrent(expected, "FINAL_POSITION_MISMATCH", "route destination mismatch") then
				return
			end
			activeMarker = "route_" .. step.id
			callbacks.appendEvent(activeMarker, "success")
			callbacks.completeStep(step, positionString(expected))
			return
		end
		local edge = route.edges[edgeIndex]
		local marker = "route_" .. step.id .. "_edge_" .. tostring(edgeIndex)
		activeMarker = marker
		callbacks.appendEvent(marker, "start")
		if edge.kind == "movement" then
			executeMovementEdge(edge, marker)
		elseif edge.kind == "transition" then
			executeTransitionEdge(edge, marker)
		else
			failRoute("INTERACTION_FAILED", "unsupported route edge kind: " .. tostring(edge.kind))
		end
	end

	if type(route) ~= "table" or type(route.edges) ~= "table" then
		failRoute("INTERACTION_FAILED", "invalid route runtime contract")
		return
	end
	local origin = position(route.origin)
	activeMarker = "route_" .. step.id
	callbacks.appendEvent(activeMarker, "start")
	if not assertCurrent(origin, "INITIAL_POSITION_MISMATCH", "route origin mismatch") then
		return
	end
	executeNextEdge()
end

return M
