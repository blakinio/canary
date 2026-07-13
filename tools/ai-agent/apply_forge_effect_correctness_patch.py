#!/usr/bin/env python3
"""Apply the bounded F-011/F-012 Forge effect-correctness patch."""

from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one anchor, found {count}: {old!r}")
    file_path.write_text(text.replace(old, new), encoding="utf-8")


player = "src/creatures/players/player.cpp"
replace_once(
    player,
    '#include "creatures/players/player.hpp"\n#include "game/functions/forge_fusion_policy.hpp"\n',
    '#include "creatures/players/player.hpp"\n#include "game/functions/forge_effect_policy.hpp"\n#include "game/functions/forge_fusion_policy.hpp"\n',
)

momentum_old = """\t\t\tconst int32_t ticks = condItem->getTicks();
\t\t\tconst int32_t newTicks = (ticks <= 2000) ? 0 : ticks - 2000;
\t\t\ttriggered = true;
\t\t\tif (type == CONDITION_SPELLCOOLDOWN || (type == CONDITION_SPELLGROUPCOOLDOWN && spellId > SPELLGROUP_SUPPORT)) {
\t\t\t\tcondItem->setTicks(newTicks);
\t\t\t\ttype == CONDITION_SPELLGROUPCOOLDOWN ? sendSpellGroupCooldown(static_cast<SpellGroup_t>(spellId), newTicks) : sendSpellCooldown(spellId, newTicks);
\t\t\t}
"""
momentum_new = """\t\t\tconst bool isSpellCooldown = type == CONDITION_SPELLCOOLDOWN;
\t\t\tconst bool isSpellGroupCooldown = type == CONDITION_SPELLGROUPCOOLDOWN;
\t\t\tif (!ForgeEffectPolicy::isMomentumCooldownEligible(isSpellCooldown, isSpellGroupCooldown, spellId, SPELLGROUP_SUPPORT)) {
\t\t\t\t++it;
\t\t\t\tcontinue;
\t\t\t}

\t\t\tconst int32_t ticks = condItem->getTicks();
\t\t\tconst int32_t newTicks = (ticks <= 2000) ? 0 : ticks - 2000;
\t\t\tcondItem->setTicks(newTicks);
\t\t\tisSpellGroupCooldown ? sendSpellGroupCooldown(static_cast<SpellGroup_t>(spellId), newTicks) : sendSpellCooldown(spellId, newTicks);
\t\t\ttriggered = true;
"""
replace_once(player, momentum_old, momentum_new)

avatar_old = """void Player::triggerTranscendence() {
\tif (wheel().getOnThinkTimer(WheelOnThink_t::AVATAR_FORGE) > OTSYS_TIME()) {
\t\treturn;
\t}
"""
avatar_new = """void Player::triggerTranscendence() {
\tconst uint64_t now = OTSYS_TIME();
\tif (ForgeEffectPolicy::isAvatarActive(
\t\t\twheel().getOnThinkTimer(WheelOnThink_t::AVATAR_FORGE),
\t\t\twheel().getOnThinkTimer(WheelOnThink_t::AVATAR_SPELL),
\t\t\tnow
\t\t)) {
\t\treturn;
\t}
"""
replace_once(player, avatar_old, avatar_new)

print("Applied Forge effect-correctness patch.")
