-- Account-wide quest system configuration.
-- This file is loaded by scripts/custom/account_quest_system.lua.
-- Restart the server after changing it.

return {
    enabled = true,

    -- When true, an access unlocked by one character is available to every
    -- character on the same account.
    shareAccess = true,

    -- Supported values: "oncePerAccount" and "oncePerCharacter".
    defaultRewardMode = "oncePerAccount",

    -- Self-service reset is disabled by default. Administrators can always use
    -- /questreset Player Name, quest-id
    allowSelfReset = false,

    -- Storage keys listed in progressStorages are reset only for the selected
    -- character. Account access and reward history are deliberately preserved.
    quests = {
        ["the-ape-city"] = {
            rewardMode = "oncePerCharacter",
            progressStorages = {
                40612, -- Started
                40613, -- Questline
                40614, -- DworcDoor
                40615, -- ChorDoor
                40616, -- ParchmentDecyphering
                40617, -- FibulaDoor
                40618, -- WitchesCapSpot
                40619, -- CasksDoor
                40620, -- Casks
                40621, -- HolyApeHair
                40622, -- SnakeDestroyer
                40623, -- ShamanOutfit
                40624, -- TheLargeAmphoras1
                40625, -- TheLargeAmphoras2
                40626, -- TheLargeAmphoras3
                40627, -- TheLargeAmphoras4
                40628, -- TheLargeAmphorasCooldown
            },
        },
    },
}
