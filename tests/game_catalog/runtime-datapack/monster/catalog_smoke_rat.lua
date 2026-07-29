local mType = Game.createMonsterType("Catalog Smoke Rat")
local monster = {}

monster.description = "a catalog smoke rat"
monster.experience = 5
monster.outfit = {
	lookType = 21,
}

monster.health = 20
monster.maxHealth = 20
monster.race = "blood"
monster.corpse = 5964
monster.speed = 100
monster.changeTarget = {
	interval = 4000,
	chance = 0,
}

monster.flags = {
	summonable = false,
	attackable = true,
	hostile = true,
	convinceable = false,
	pushable = true,
	rewardBoss = false,
	illusionable = false,
	canPushItems = false,
	canPushCreatures = false,
	staticAttackChance = 95,
	targetDistance = 1,
	runHealth = 0,
	healthHidden = false,
	isBlockable = false,
	canWalkOnEnergy = true,
	canWalkOnFire = true,
	canWalkOnPoison = true,
}

monster.light = {
	level = 0,
	color = 0,
}

monster.voices = {
	interval = 5000,
	chance = 0,
}

monster.loot = {
	{ id = 3031, chance = 100000, maxCount = 1 },
}

monster.attacks = {
	{ name = "melee", interval = 2000, chance = 100, minDamage = 0, maxDamage = -5 },
}

monster.defenses = {
	defense = 5,
	armor = 5,
}

monster.elements = {}
monster.immunities = {}

mType:register(monster)
