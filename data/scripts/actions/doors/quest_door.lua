local doorIds = {}
for index, value in ipairs(QuestDoorTable) do
	if not table.contains(doorIds, value.openDoor) then
		table.insert(doorIds, value.openDoor)
	end

	if not table.contains(doorIds, value.closedDoor) then
		table.insert(doorIds, value.closedDoor)
	end
end

local accountQuestDoors = {}
local accountQuestUnlockDoors = {}
local function addAccountQuestDoor(storageId, questId, unlockOnUse, shareAccess)
	if not storageId then
		return
	end

	if shareAccess ~= false then
		accountQuestDoors[storageId] = questId
	end
	if unlockOnUse then
		accountQuestUnlockDoors[storageId] = questId
	end
end

local theApeCity = Storage.Quest.U7_6 and Storage.Quest.U7_6.TheApeCity or {}
addAccountQuestDoor(theApeCity.DworcDoor, "the-ape-city")
addAccountQuestDoor(theApeCity.ChorDoor, "the-ape-city")
addAccountQuestDoor(theApeCity.FibulaDoor, "the-ape-city")
addAccountQuestDoor(theApeCity.CasksDoor, "the-ape-city")

local secretService = Storage.Quest.U8_1 and Storage.Quest.U8_1.SecretService or {}
addAccountQuestDoor(secretService.CGBMission01, "secret-service")
addAccountQuestDoor(secretService.TBIMission02, "secret-service")
addAccountQuestDoor(secretService.AVINMission02, "secret-service")
addAccountQuestDoor(secretService.CGBMission02, "secret-service")
addAccountQuestDoor(secretService.TBIMission03, "secret-service")
addAccountQuestDoor(secretService.TBIMission04, "secret-service")
addAccountQuestDoor(secretService.CGBMission04, "secret-service")
addAccountQuestDoor(secretService.AVINMission05, "secret-service")
addAccountQuestDoor(secretService.CGBMission05, "secret-service")
addAccountQuestDoor(secretService.Mission07, "secret-service", true)
addAccountQuestDoor(secretService.CGBMission06, "secret-service")

local yalahar = Storage.Quest.U8_4 and Storage.Quest.U8_4.InServiceOfYalahar or {}
addAccountQuestDoor(yalahar.Mission03, "in-service-of-yalahar")
addAccountQuestDoor(yalahar.AlchemistFormula, "in-service-of-yalahar")
addAccountQuestDoor(yalahar.TamerinStatus, "in-service-of-yalahar")
addAccountQuestDoor(yalahar.MorikSummon, "in-service-of-yalahar")
addAccountQuestDoor(yalahar.NotesPalimuth, "in-service-of-yalahar")
addAccountQuestDoor(yalahar.DoorToAzerus, "in-service-of-yalahar")
addAccountQuestDoor(yalahar.DoorToBog, "in-service-of-yalahar")
addAccountQuestDoor(yalahar.DoorToMatrix, "in-service-of-yalahar")
addAccountQuestDoor(yalahar.DoorToQuara, "in-service-of-yalahar")
-- The reward-room door is a completion gate only. It records account access
-- without granting alternate characters access to the final reward room.
addAccountQuestDoor(yalahar.DoorToReward, "in-service-of-yalahar", true, false)

local newFrontier = Storage.Quest.U8_54 and Storage.Quest.U8_54.TheNewFrontier or {}
addAccountQuestDoor(newFrontier.Mission01, "the-new-frontier")
addAccountQuestDoor(newFrontier.Mission04, "the-new-frontier")
addAccountQuestDoor(newFrontier.Mission07 and newFrontier.Mission07[1], "the-new-frontier")
addAccountQuestDoor(newFrontier.Mission09 and newFrontier.Mission09.ArenaDoor, "the-new-frontier")
-- RewardDoor stays per character. MagicCarpetDoor is awarded only after the
-- final report to Ongulf and is therefore the completion gate.
addAccountQuestDoor(newFrontier.Mission10 and newFrontier.Mission10.MagicCarpetDoor, "the-new-frontier", true)

local wrath = Storage.Quest.U8_6 and Storage.Quest.U8_6.WrathOfTheEmperor or {}
addAccountQuestDoor(wrath.Mission02, "wrath-of-the-emperor")
addAccountQuestDoor(wrath.Mission06, "wrath-of-the-emperor")
addAccountQuestDoor(wrath.Mission07, "wrath-of-the-emperor")
addAccountQuestDoor(wrath.Mission08, "wrath-of-the-emperor")
addAccountQuestDoor(wrath.Mission09, "wrath-of-the-emperor")
-- Mission 12 is the wardrobe/reward stage. Use it only to record completion.
addAccountQuestDoor(wrath.Mission12, "wrath-of-the-emperor", true, false)

local questDoor = Action()
function questDoor.onUse(player, item, fromPosition, target, toPosition, isHotkey)
	for index, value in ipairs(QuestDoorTable) do
		if value.closedDoor == item.itemid then
			local hasCharacterAccess = item.actionid > 0 and player:getStorageValue(item.actionid) ~= -1
			local accountQuestId = accountQuestDoors[item.actionid]
			local hasAccountAccess = accountQuestId and player:hasAccountQuestAccess(accountQuestId) or false
			local completionQuestId = accountQuestUnlockDoors[item.actionid]

			if hasCharacterAccess and completionQuestId then
				player:unlockAccountQuestAccess(completionQuestId)
			end

			if hasCharacterAccess or hasAccountAccess then
				item:transform(value.openDoor)
				item:getPosition():sendSingleSoundEffect(SOUND_EFFECT_TYPE_ACTION_OPEN_DOOR)
				player:teleportTo(toPosition, true)
				return true
			else
				player:sendTextMessage(MESSAGE_EVENT_ADVANCE, "The door seems to be sealed against unwanted intruders.")
				return true
			end
		end
	end

	if Creature.checkCreatureInsideDoor(player, toPosition) then
		return true
	end
	return true
end

for index, value in ipairs(doorIds) do
	questDoor:id(value)
end

questDoor:register()
