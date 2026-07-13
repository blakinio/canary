#!/usr/bin/env python3
"""Resolve the two expected post-squash conflicts for PR #257."""

from pathlib import Path
import subprocess


def git_show(ref_path: str) -> str:
    return subprocess.check_output(["git", "show", ref_path], text=True)


def extract_function(text: str, signature: str) -> tuple[int, int, str]:
    start = text.index(signature)
    brace = text.index("{", start)
    depth = 0
    i = brace
    while i < len(text):
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                if end < len(text) and text[end] == "\n":
                    end += 1
                return start, end, text[start:end]
        i += 1
    raise RuntimeError(f"unterminated function {signature}")


def replace_function(target: str, source: str, signature: str) -> str:
    start, end, _ = extract_function(target, signature)
    _, _, replacement = extract_function(source, signature)
    return target[:start] + replacement + target[end:]


player_path = Path("src/creatures/players/player.cpp")
branch_player = player_path.read_text(encoding="utf-8")
main_player = git_show("origin/main:src/creatures/players/player.cpp")

# Preserve PR #257 Forge transaction implementation while importing only the
# two effect functions and include introduced by merged PR #267.
branch_player = replace_function(branch_player, main_player, "void Player::triggerMomentum()")
branch_player = replace_function(branch_player, main_player, "void Player::triggerTranscendence()")
if '#include "game/functions/forge_effect_policy.hpp"\n' not in branch_player:
    anchor = '#include "creatures/players/player.hpp"\n'
    if branch_player.count(anchor) != 1:
        raise RuntimeError("unexpected player include anchor")
    branch_player = branch_player.replace(anchor, anchor + '#include "game/functions/forge_effect_policy.hpp"\n', 1)
player_path.write_text(branch_player, encoding="utf-8")

cmake_path = Path("tests/unit/players/CMakeLists.txt")
cmake = git_show("origin/main:tests/unit/players/CMakeLists.txt")
entry = "            forge_transaction_test.cpp\n"
if entry not in cmake:
    candidates = [
        "            forge_effect_policy_test.cpp\n",
        "            forge_test.cpp\n",
    ]
    for anchor in candidates:
        if anchor in cmake:
            cmake = cmake.replace(anchor, anchor + entry, 1)
            break
    else:
        raise RuntimeError("no stable CMake insertion anchor")
cmake_path.write_text(cmake, encoding="utf-8")

print("Resolved expected PR #257 conflicts against current main.")
