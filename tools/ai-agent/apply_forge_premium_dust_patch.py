#!/usr/bin/env python3
"""Apply the bounded F-006 Premium Dust eligibility patch."""

import json
from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one anchor, found {count}: {old!r}")
    file_path.write_text(text.replace(old, new), encoding="utf-8")


replace_once(
    "src/lua/functions/creatures/player/player_functions.hpp",
    "\tstatic int luaPlayerGetPremiumDays(lua_State* L);\n",
    "\tstatic int luaPlayerIsPremium(lua_State* L);\n\tstatic int luaPlayerGetPremiumDays(lua_State* L);\n",
)

replace_once(
    "src/lua/functions/creatures/player/player_functions.cpp",
    '\tLua::registerMethod(L, "Player", "getPremiumDays", PlayerFunctions::luaPlayerGetPremiumDays);\n',
    '\tLua::registerMethod(L, "Player", "isPremium", PlayerFunctions::luaPlayerIsPremium);\n\tLua::registerMethod(L, "Player", "getPremiumDays", PlayerFunctions::luaPlayerGetPremiumDays);\n',
)

premium_days_definition = """int PlayerFunctions::luaPlayerGetPremiumDays(lua_State* L) {
\t// player:getPremiumDays()
"""
is_premium_definition = """int PlayerFunctions::luaPlayerIsPremium(lua_State* L) {
\t// player:isPremium()
\tconst auto &player = Lua::getUserdataShared<Player>(L, 1, "Player");
\tif (player) {
\t\tLua::pushBoolean(L, player->isPremium());
\t} else {
\t\tlua_pushnil(L);
\t}
\treturn 1;
}

""" + premium_days_definition
replace_once(
    "src/lua/functions/creatures/player/player_functions.cpp",
    premium_days_definition,
    is_premium_definition,
)

replace_once(
    "data/libs/systems/exaltation_forge.lua",
    """function ForgeMonster:creditDust(player, amount)
\tif not player then
\t\treturn 0
\tend

\tlocal totalDusts = player:getForgeDusts()
""",
    """function ForgeMonster:creditDust(player, amount)
\tif not player then
\t\treturn 0
\tend

\tif not player:isPremium() then
\t\tplayer:sendTextMessage(MESSAGE_EVENT_ADVANCE, "You did not receive " .. amount .. " dust for the Exaltation Forge because a Premium Account is required.")
\t\treturn 0
\tend

\tlocal totalDusts = player:getForgeDusts()
""",
)

api_path = Path("docs/lua-api/lua_api.json")
api = json.loads(api_path.read_text(encoding="utf-8"))
player_methods = api.setdefault("classes", {}).setdefault("Player", [])
if any(method.get("name") == "isPremium" for method in player_methods):
    raise RuntimeError("Player:isPremium documentation already exists")
player_methods.append(
    {
        "name": "isPremium",
        "params": [],
        "return": "boolean",
        "source": "src/lua/functions/creatures/player/player_functions.cpp",
    }
)
player_methods.sort(key=lambda method: method.get("name", "").lower())
api_path.write_text(json.dumps(api, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

print("Applied Forge Premium Dust eligibility patch.")
