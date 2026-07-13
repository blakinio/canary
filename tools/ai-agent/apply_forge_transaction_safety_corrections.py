#!/usr/bin/env python3
"""Apply bounded corrections after materializing the Forge transaction patch."""

from pathlib import Path


def replace_exact(path: str, old: str, new: str, expected: int = 1) -> None:
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != expected:
        raise RuntimeError(f"{path}: expected {expected} anchors, found {count}: {old!r}")
    file_path.write_text(text.replace(old, new), encoding="utf-8")


player = "src/creatures/players/player.cpp"
replace_exact(
    player,
    "\tconst auto [sliversBefore, coresBefore] = getForgeSliversAndCores();\n",
    "\tconst auto coresBefore = getForgeSliversAndCores().second;\n",
    expected=2,
)

core_anchor = """\t\tconst auto &core = Item::CreateItem(ITEM_FORGE_CORE, 1);
\t\tif (!core) {
\t\t\tg_logger().error(\"[{}] Failed to create Forge Core for player {}\", __FUNCTION__, getName());
\t\t\tsendForgeError(RETURNVALUE_CONTACTADMINISTRATOR);
\t\t\treturn;
\t\t}

\t\tForgeTransaction transaction;
"""
core_replacement = """\t\tconst auto &core = Item::CreateItem(ITEM_FORGE_CORE, 1);
\t\tif (!core) {
\t\t\tg_logger().error(\"[{}] Failed to create Forge Core for player {}\", __FUNCTION__, getName());
\t\t\tsendForgeError(RETURNVALUE_CONTACTADMINISTRATOR);
\t\t\treturn;
\t\t}
\t\tif (g_game().internalAddItem(player, core, INDEX_WHEREEVER, 0, true) != RETURNVALUE_NOERROR) {
\t\t\tg_logger().error(\"[{}] No inventory capacity for a Forge Core for player {}\", __FUNCTION__, getName());
\t\t\tsendForgeError(RETURNVALUE_NOTENOUGHROOM);
\t\t\treturn;
\t\t}

\t\tForgeTransaction transaction;
"""
replace_exact(player, core_anchor, core_replacement)
replace_exact(
    player,
    "\t\t\t[player, core] { return g_game().internalPlayerAddItem(player, core) == RETURNVALUE_NOERROR; },\n",
    "\t\t\t[player, core] { return g_game().internalPlayerAddItem(player, core, false) == RETURNVALUE_NOERROR; },\n",
)

integration_path = Path("tests/integration/game/forge_it.cpp")
integration = integration_path.read_text(encoding="utf-8").rstrip()
if "ForgeSliverToCoreConversionRejectsFullBackpackWithoutMutation" in integration:
    raise RuntimeError("full-backpack conversion regression already exists")
integration += """

TEST_F(ForgeIntegrationTest, ForgeSliverToCoreConversionRejectsFullBackpackWithoutMutation) {
\tensureBackpack();
\tconst auto &fixture = testState();
\tconst auto cost = static_cast<uint16_t>(g_configManager().getNumber(FORGE_CORE_COST));
\tconst auto &slivers = Item::CreateItem(ITEM_FORGE_SLIVER, cost);
\tASSERT_NE(nullptr, slivers);
\tASSERT_EQ(RETURNVALUE_NOERROR, g_game().internalPlayerAddItem(player, slivers, false, CONST_SLOT_BACKPACK));
\tfillBackpackWithCopies(fixture.receiveItemId);
\tASSERT_EQ(0u, player->getFreeBackpackSlots());

\tconst auto [sliversBefore, coresBefore] = player->getForgeSliversAndCores();
\tconst auto historyBefore = player->forgeHistory().get().size();

\tplayer->forgeResourceConversion(ForgeAction_t::SLIVERSTOCORES);

\tconst auto [sliversAfter, coresAfter] = player->getForgeSliversAndCores();
\tEXPECT_EQ(sliversBefore, sliversAfter);
\tEXPECT_EQ(coresBefore, coresAfter);
\tEXPECT_EQ(historyBefore, player->forgeHistory().get().size());
}
"""
integration_path.write_text(integration.rstrip() + "\n", encoding="utf-8")

print("Applied Forge transaction-safety corrections.")
