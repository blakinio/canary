#!/usr/bin/env python3
"""Apply bounded F-006 Premium Dust remediation to current main."""

from pathlib import Path
import json


def replace_once(path: str, old: str, new: str) -> None:
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one anchor, found {count}: {old!r}")
    p.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_once(
    "data/libs/systems/exaltation_forge.lua",
    "\tif amount <= 0 then\n\t\treturn 0\n\tend\n\n\tlocal totalDusts = player:getForgeDusts()\n",
    "\tif amount <= 0 then\n\t\treturn 0\n\tend\n\n\tif not player:isPremium() then\n\t\tplayer:sendTextMessage(MESSAGE_EVENT_ADVANCE, \"You did not receive \" .. amount .. \" dust for the Exaltation Forge because a Premium Account is required.\")\n\t\treturn 0\n\tend\n\n\tlocal totalDusts = player:getForgeDusts()\n",
)

replace_once(
    "src/lua/functions/creatures/player/player_functions.cpp",
    "\tLua::registerMethod(L, \"Player\", \"getPremiumDays\", PlayerFunctions::luaPlayerGetPremiumDays);\n",
    "\tLua::registerMethod(L, \"Player\", \"isPremium\", PlayerFunctions::luaPlayerIsPremium);\n\tLua::registerMethod(L, \"Player\", \"getPremiumDays\", PlayerFunctions::luaPlayerGetPremiumDays);\n",
)
replace_once(
    "src/lua/functions/creatures/player/player_functions.cpp",
    "int PlayerFunctions::luaPlayerGetPremiumDays(lua_State* L) {\n",
    "int PlayerFunctions::luaPlayerIsPremium(lua_State* L) {\n\t// player:isPremium()\n\tconst auto &player = Lua::getUserdataShared<Player>(L, 1, \"Player\");\n\tif (player) {\n\t\tLua::pushBoolean(L, player->isPremium());\n\t} else {\n\t\tlua_pushnil(L);\n\t}\n\treturn 1;\n}\n\nint PlayerFunctions::luaPlayerGetPremiumDays(lua_State* L) {\n",
)
replace_once(
    "src/lua/functions/creatures/player/player_functions.hpp",
    "\tstatic int luaPlayerGetPremiumDays(lua_State* L);\n",
    "\tstatic int luaPlayerIsPremium(lua_State* L);\n\tstatic int luaPlayerGetPremiumDays(lua_State* L);\n",
)

api_path = Path("docs/lua-api/lua_api.json")
api = json.loads(api_path.read_text(encoding="utf-8"))
player_methods = None
for entry in api:
    if isinstance(entry, dict) and entry.get("name") == "Player" and isinstance(entry.get("methods"), list):
        player_methods = entry["methods"]
        break
if player_methods is None:
    raise RuntimeError("Player methods array not found in Lua API JSON")
if any(method.get("name") == "isPremium" for method in player_methods):
    raise RuntimeError("Player:isPremium already exists")
insert_at = next((i for i, method in enumerate(player_methods) if method.get("name") == "isPromoted"), None)
if insert_at is None:
    raise RuntimeError("isPromoted API anchor not found")
player_methods.insert(insert_at, {
    "name": "isPremium",
    "params": [],
    "return": "boolean",
    "source": "src/lua/functions/creatures/player/player_functions.cpp",
})
api_path.write_text(json.dumps(api, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

Path("tests/lua/test_exaltation_forge_premium.lua").write_text('''FORGE_NORMAL_MONSTER = 0
FORGE_INFLUENCED_MONSTER = 1
FORGE_FIENDISH_MONSTER = 2
MESSAGE_EVENT_ADVANCE = 19

local function fail(message)
\tio.stderr:write(message .. "\\n")
\tos.exit(1)
end

local function expectEqual(expected, actual, label)
\tif expected ~= actual then
\t\tfail(label .. ": expected " .. tostring(expected) .. ", got " .. tostring(actual))
\tend
end

local function expectContains(text, needle, label)
\tif not string.find(text, needle, 1, true) then
\t\tfail(label .. ": expected '" .. text .. "' to contain '" .. needle .. "'")
\tend
end

local function newPlayer(premium, dust, limit)
\tlocal messages = {}
\tlocal player = {}

\tfunction player:isPremium()
\t\treturn premium
\tend

\tfunction player:getForgeDusts()
\t\treturn dust
\tend

\tfunction player:getForgeDustLevel()
\t\treturn limit
\tend

\tfunction player:addForgeDusts(amount)
\t\tdust = dust + amount
\tend

\tfunction player:sendTextMessage(messageType, text)
\t\ttable.insert(messages, { messageType = messageType, text = text })
\tend

\tfunction player:state()
\t\treturn dust, messages
\tend

\treturn player
end

dofile("data/libs/systems/exaltation_forge.lua")

local freePlayer = newPlayer(false, 10, 100)
expectEqual(0, ForgeMonster:creditDust(freePlayer, 5), "non-Premium credit")
local freeDust, freeMessages = freePlayer:state()
expectEqual(10, freeDust, "non-Premium Dust remains unchanged")
expectEqual(1, #freeMessages, "non-Premium message count")
expectContains(freeMessages[1].text, "Premium Account", "non-Premium message")

local premiumPlayer = newPlayer(true, 10, 100)
expectEqual(5, ForgeMonster:creditDust(premiumPlayer, 5), "Premium credit")
local premiumDust, premiumMessages = premiumPlayer:state()
expectEqual(15, premiumDust, "Premium Dust credit")
expectEqual(1, #premiumMessages, "Premium message count")

local cappedPlayer = newPlayer(true, 98, 100)
expectEqual(2, ForgeMonster:creditDust(cappedPlayer, 5), "cap-aware credit")
local cappedDust = cappedPlayer:state()
expectEqual(100, cappedDust, "cap-aware Dust total")

print("Exaltation Forge Premium Dust tests passed")
''', encoding="utf-8")

Path("docs/agents/tasks/active/CAN-20260713-forge-premium-dust.md").write_text('''---
task_id: CAN-20260713-forge-premium-dust
program_id: CAN-PROGRAM-EQUIPMENT-UPGRADE-PARITY
coordination_id: ""
status: in_progress
agent: "GPT-5.6 Thinking"
branch: fix/forge-premium-dust
base_branch: main
created: 2026-07-13T16:44:00+02:00
updated: 2026-07-13T21:10:00+02:00
last_verified_commit: "d4e8933b78587445afd9347a6d05b6e715c6c0e4"
risk: medium
related_issue: ""
related_pr: "#262"
depends_on:
  - PR #259 merged as 444aa8ae13edc01c6e77b03139a43d386b437308
blocks: []
owned_paths:
  exclusive:
    - src/lua/functions/creatures/player/player_functions.hpp
    - src/lua/functions/creatures/player/player_functions.cpp
    - docs/lua-api/lua_api.json
    - data/libs/systems/exaltation_forge.lua
    - tests/lua/test_exaltation_forge_premium.lua
    - docs/agents/tasks/active/CAN-20260713-forge-premium-dust.md
  shared: []
  read_only:
    - src/creatures/players/player.hpp
    - src/creatures/players/player.cpp
modules_touched:
  - Player Lua API
  - Exaltation Forge Dust eligibility
  - Lua API documentation
  - Lua reward regressions
reuses:
  - exact C++ `Player::isPremium()` semantics
  - PR #177 capped Dust credit and single party roll
  - PR #259 Forge Lua baseline
public_interfaces:
  - `Player:isPremium() -> boolean`
cross_repo_tasks: []
---

# Goal

Resolve F-006 by requiring exact Canary Premium eligibility before any player receives Exaltation Forge Dust.

# Acceptance criteria

- [x] Lua exposes `Player:isPremium()` as a direct delegation to `Player::isPremium()`.
- [x] The binding is documented in `docs/lua-api/lua_api.json`.
- [x] `ForgeMonster:creditDust` returns zero without Dust mutation for non-Premium players.
- [x] Free Premium, Always Premium and account-time semantics remain inherited from C++.
- [x] PR #177 cap-aware actual credit remains unchanged for eligible players.
- [x] Focused Lua tests cover rejection, eligible credit and cap truncation.
- [ ] Full clean-head CI passes before merge.

# Evidence boundary

The binding delegates to the existing C++ predicate. No Premium semantics are reconstructed in Lua. Repository CI and focused Lua tests are required; physical-client gameplay remains separate evidence.

# Completion

- Final status: in_progress
- PR: #262
- Merge commit:
- Archived at:
''', encoding="utf-8")

print("Applied clean F-006 Premium Dust patch.")
