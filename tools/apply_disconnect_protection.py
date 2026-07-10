from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    file = Path(path)
    text = file.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"Anchor not found in {path}")
    file.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_once(
    "src/config/config_enums.hpp",
    "\tDEPOTCHEST,\n\tDISABLE_LEGACY_RAIDS,",
    "\tDEPOTCHEST,\n\tDISCONNECT_PROTECTION_COOLDOWN,\n\tDISCONNECT_PROTECTION_DETECTION_TIME,\n\tDISCONNECT_PROTECTION_DURATION,\n\tDISCONNECT_PROTECTION_ENABLED,\n\tDISCONNECT_PROTECTION_IN_PVP,\n\tDISCONNECT_PROTECTION_LOG_ENABLED,\n\tDISABLE_LEGACY_RAIDS,",
)

replace_once(
    "src/config/configmanager.cpp",
    '\tloadBoolConfig(L, DISCORD_SEND_FOOTER, "discordSendFooter", true);',
    '\tloadBoolConfig(L, DISCONNECT_PROTECTION_ENABLED, "disconnectProtectionEnabled", false);\n'
    '\tloadBoolConfig(L, DISCONNECT_PROTECTION_IN_PVP, "disconnectProtectionInPvp", false);\n'
    '\tloadBoolConfig(L, DISCONNECT_PROTECTION_LOG_ENABLED, "disconnectProtectionLogEnabled", true);\n'
    '\tloadBoolConfig(L, DISCORD_SEND_FOOTER, "discordSendFooter", true);',
)

replace_once(
    "src/config/configmanager.cpp",
    '\tloadIntConfig(L, DEPOT_BOXES, "depotBoxes", 20);',
    '\tloadIntConfig(L, DISCONNECT_PROTECTION_COOLDOWN, "disconnectProtectionCooldown", 30 * 60 * 1000);\n'
    '\tloadIntConfig(L, DISCONNECT_PROTECTION_DETECTION_TIME, "disconnectProtectionDetectionTime", 10 * 1000);\n'
    '\tloadIntConfig(L, DISCONNECT_PROTECTION_DURATION, "disconnectProtectionDuration", 30 * 1000);\n'
    '\tloadIntConfig(L, DEPOT_BOXES, "depotBoxes", 20);',
)

replace_once(
    "src/creatures/players/player.hpp",
    "\tvoid sendPing();",
    "\tvoid sendPing();\n\tvoid activateDisconnectProtection();\n\tvoid clearDisconnectProtection();\n\tvoid consumeDisconnectProtection();\n\t[[nodiscard]] bool hasActiveDisconnectProtection() const;",
)

replace_once(
    "src/creatures/players/player.hpp",
    "\tbool shouldForceLogout = true;",
    "\tbool shouldForceLogout = true;\n\tbool disconnectProtectionActive = false;\n\tint64_t disconnectProtectionActivatedAt = 0;\n\tint64_t disconnectProtectionCooldownUntil = 0;",
)

replace_once(
    "src/creatures/players/player.cpp",
    "\tconst int64_t noPongTime = timeNow - lastPong;\n\tconst auto &attackedCreature = getAttackedCreature();\n\tif ((hasLostConnection || noPongTime >= 10000) && attackedCreature) {\n\t\tsetAttackedCreature(nullptr);\n\t}",
    "\tconst int64_t noPongTime = timeNow - lastPong;\n\tconst int64_t detectionTime = std::max<int64_t>(1000, g_configManager().getNumber(DISCONNECT_PROTECTION_DETECTION_TIME));\n\tconst bool connectionTimedOut = hasLostConnection || noPongTime >= detectionTime;\n\tconst auto &attackedCreature = getAttackedCreature();\n\tif (connectionTimedOut && attackedCreature) {\n\t\tsetAttackedCreature(nullptr);\n\t}\n\n\tif (connectionTimedOut) {\n\t\tactivateDisconnectProtection();\n\t}",
)

replace_once(
    "src/creatures/players/player.cpp",
    "void Player::receivePing() {\n\tlastPong = OTSYS_TIME();\n}",
    "void Player::receivePing() {\n\tlastPong = OTSYS_TIME();\n\tclearDisconnectProtection();\n}",
)

methods = '''void Player::activateDisconnectProtection() {
\tif (!g_configManager().getBoolean(DISCONNECT_PROTECTION_ENABLED)) {
\t\treturn;
\t}

\tconst int64_t now = OTSYS_TIME();
\tif (disconnectProtectionActive || now < disconnectProtectionCooldownUntil) {
\t\treturn;
\t}

\tdisconnectProtectionActive = true;
\tdisconnectProtectionActivatedAt = now;
\tif (g_configManager().getBoolean(DISCONNECT_PROTECTION_LOG_ENABLED)) {
\t\tg_logger().info("Disconnect protection activated for player {}.", getName());
\t}
}

void Player::clearDisconnectProtection() {
\tdisconnectProtectionActive = false;
\tdisconnectProtectionActivatedAt = 0;
}

void Player::consumeDisconnectProtection() {
\tclearDisconnectProtection();
\tdisconnectProtectionCooldownUntil = OTSYS_TIME() + std::max<int64_t>(0, g_configManager().getNumber(DISCONNECT_PROTECTION_COOLDOWN));
}

bool Player::hasActiveDisconnectProtection() const {
\tif (!g_configManager().getBoolean(DISCONNECT_PROTECTION_ENABLED) || !disconnectProtectionActive) {
\t\treturn false;
\t}

\tconst int64_t duration = std::max<int64_t>(0, g_configManager().getNumber(DISCONNECT_PROTECTION_DURATION));
\treturn duration > 0 && OTSYS_TIME() - disconnectProtectionActivatedAt <= duration;
}

'''
replace_once(
    "src/creatures/players/player.cpp",
    "void Player::sendPingBack() const {",
    methods + "void Player::sendPingBack() const {",
)

replace_once(
    "src/creatures/players/player.cpp",
    "\t\tuint8_t unfairFightReduction = 100;",
    "\t\tconst bool disconnectDeathProtected = hasActiveDisconnectProtection()\n\t\t\t&& (!pvpDeath || g_configManager().getBoolean(DISCONNECT_PROTECTION_IN_PVP));\n\t\tif (disconnectDeathProtected) {\n\t\t\tif (g_configManager().getBoolean(DISCONNECT_PROTECTION_LOG_ENABLED)) {\n\t\t\t\tg_logger().info(\"Death penalty prevented by disconnect protection for player {} (PvP: {}).\", getName(), pvpDeath);\n\t\t\t}\n\t\t\tconsumeDisconnectProtection();\n\t\t}\n\n\t\tuint8_t unfairFightReduction = 100;",
)

replace_once(
    "src/creatures/players/player.cpp",
    "\t\tdouble deathLossPercent = getLostPercent() * (unfairFightReduction / 100.);",
    "\t\tdouble deathLossPercent = disconnectDeathProtected ? 0.0 : getLostPercent() * (unfairFightReduction / 100.);",
)

replace_once(
    "src/creatures/players/player.cpp",
    "\t\tauto willNotLoseBless = getLevel() < adventurerBlessingLevel && getVocationId() > VOCATION_NONE;",
    "\t\tauto willNotLoseBless = disconnectDeathProtected || (getLevel() < adventurerBlessingLevel && getVocationId() > VOCATION_NONE);",
)

replace_once(
    "src/creatures/players/player.cpp",
    "\t\tif (willNotLoseBless) {\n\t\t\tblessOutput << fmt::format(\"You still have adventurer's blessings for being level lower than {}!\", adventurerBlessingLevel);",
    "\t\tif (willNotLoseBless) {\n\t\t\tif (disconnectDeathProtected) {\n\t\t\t\tblessOutput << \"Your death penalty and blessings were preserved because the server detected a lost connection.\";\n\t\t\t} else {\n\t\t\t\tblessOutput << fmt::format(\"You still have adventurer's blessings for being level lower than {}!\", adventurerBlessingLevel);\n\t\t\t}",
)

replace_once(
    "config.lua.dist",
    "replaceKickOnLogin = true\n",
    "replaceKickOnLogin = true\n\n-- Disconnect death protection\n-- Disabled by default to preserve existing server behavior.\ndisconnectProtectionEnabled = false\ndisconnectProtectionDetectionTime = 10 * 1000\ndisconnectProtectionDuration = 30 * 1000\ndisconnectProtectionCooldown = 30 * 60 * 1000\ndisconnectProtectionInPvp = false\ndisconnectProtectionLogEnabled = true\n",
)

print("Disconnect protection changes applied.")
