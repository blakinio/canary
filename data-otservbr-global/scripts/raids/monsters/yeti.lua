local zone = Zone("folda.yeti")
zone:addArea(Position(31991, 31580, 7), Position(32044, 31616, 7))

local raid = Raid("folda.yeti", {
	zone = zone,
	allowedDays = { "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday" },
	minActivePlayers = 2,
	initialChance = 0.02,
	targetChancePerDay = 0.02,
	maxChancePerCheck = 0.6,
	minGapBetween = "48h",
	timeToSpawnMonsters = "1s",
})

raid:addBroadcast("Something is moving to the icy grounds of Folda."):autoAdvance("30s")
raid:addBroadcast("Many Yetis are emerging from the icy mountains of Folda."):autoAdvance("30s")
raid:addBroadcast("Numerous Yetis are dominating Folda, beware!"):autoAdvance("60s")

local yetiWaves = { 20, 20, 20 }
for _, amount in ipairs(yetiWaves) do
	raid
		:addSpawnMonsters({
			{
				name = "Yeti",
				amount = amount,
			},
		})
		:autoAdvance("2s")
end

raid:register()
