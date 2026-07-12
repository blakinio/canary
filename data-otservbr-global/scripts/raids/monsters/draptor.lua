local zone = Zone("farmine.draptor")
zone:addArea(Position(33195, 31160, 7), Position(33286, 31247, 7))

local raid = Raid("farmine.draptor", {
	zone = zone,
	allowedDays = { "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday" },
	minActivePlayers = 2,
	initialChance = 0.02,
	targetChancePerDay = 0.02,
	maxChancePerCheck = 0.6,
	minGapBetween = "12h",
	timeToSpawnMonsters = "1s",
})

raid:addBroadcast("The dragons of the Dragonblaze Mountains have  descended to Zao to protect the lizardkin!"):autoAdvance("30s")

local dragonWaves = { 20, 20, 20, 10, 20, 20, 20, 20 }
for _, amount in ipairs(dragonWaves) do
	raid
		:addSpawnMonsters({
			{
				name = "Dragon",
				amount = amount,
			},
		})
		:autoAdvance("2s")
end

for i = 1, 8 do
	raid
		:addSpawnMonsters({
			{
				name = "Draptor",
				amount = 1,
			},
		})
		:autoAdvance("10s")
end

raid
	:addSpawnMonsters({
		{
			name = "Grand Mother Foulscale",
			amount = 1,
		},
	})
	:autoAdvance("10s")

raid:register()
