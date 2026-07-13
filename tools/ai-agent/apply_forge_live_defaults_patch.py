#!/usr/bin/env python3
"""Apply the bounded F-001/F-002 Forge live-default patch."""

from pathlib import Path


def replace_once(path: str, old: str, new: str) -> None:
    file_path = Path(path)
    text = file_path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one anchor, found {count}: {old!r}")
    file_path.write_text(text.replace(old, new), encoding="utf-8")


replace_once(
    "src/config/configmanager.cpp",
    '#include "config/configmanager.hpp"\n',
    '#include "config/configmanager.hpp"\n#include "config/forge_config_defaults.hpp"\n',
)
replace_once(
    "src/config/configmanager.cpp",
    'loadIntConfig(L, FORGE_FIENDISH_CREATURES_LIMIT, "forgeFiendishLimit", 3);',
    'loadIntConfig(L, FORGE_FIENDISH_CREATURES_LIMIT, "forgeFiendishLimit", ForgeConfigDefaults::fiendishCreaturesLimit);',
)
replace_once(
    "src/config/configmanager.cpp",
    'loadIntConfig(L, FORGE_MAX_DUST, "forgeMaxDust", 225);',
    'loadIntConfig(L, FORGE_MAX_DUST, "forgeMaxDust", ForgeConfigDefaults::maxDust);',
)
replace_once(
    "config.lua.dist",
    "forgeMaxDust = 225",
    "forgeMaxDust = 325",
)

print("Applied Forge live-default patch.")
