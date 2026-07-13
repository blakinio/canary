-- Instanced Test Arena (docs/architecture/instanced-test-arena.md): the
-- only player-facing entry point into InstanceArenaService. "leave" just
-- teleports back without releasing the reserved region; only "close"
-- evacuates and releases it, so the arena can be left and re-closed later.
local instanceArena = TalkAction("/instancearena")

function instanceArena.onSay(player, words, param)
	-- create log
	logCommand(player, words, param)

	if param == "create" then
		local position, errorMessage = Game.createInstanceArena(player)
		if not position then
			player:sendCancelMessage(errorMessage)
			return true
		end

		player:teleportTo(position)
		if not player:isInGhostMode() then
			position:sendMagicEffect(CONST_ME_TELEPORT)
		end
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Instance arena created. Use /instancearena leave to step out, or /instancearena close when done.")
	elseif param == "leave" then
		local position, errorMessage = Game.leaveInstanceArena(player)
		if not position then
			player:sendCancelMessage(errorMessage)
			return true
		end

		player:teleportTo(position)
		if not player:isInGhostMode() then
			position:sendMagicEffect(CONST_ME_TELEPORT)
		end
	elseif param == "close" then
		local position, errorMessage = Game.closeInstanceArena(player)
		if not position then
			player:sendCancelMessage(errorMessage)
			return true
		end

		player:teleportTo(position)
		if not player:isInGhostMode() then
			position:sendMagicEffect(CONST_ME_TELEPORT)
		end
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Instance arena closed.")
	else
		player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "Usage: /instancearena create|leave|close")
	end
	return true
end

instanceArena:separator(" ")
instanceArena:groupType("gamemaster")
instanceArena:register()
