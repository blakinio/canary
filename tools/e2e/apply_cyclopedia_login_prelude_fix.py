#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROFILE = ROOT / "src/server/network/protocol/protocol_profile.cpp"
TEST = ROOT / "tools/ai-agent/test_cyclopedia_runtime_fix_contracts.py"

profile = PROFILE.read_text(encoding="utf-8")
old_profile = """\tconstexpr AccountLoginLayout currentAccountLoginLayout {
\t\t.profileId = ProtocolProfileId::Current,
\t\t.clientVersion = CLIENT_VERSION,
\t\t.responseTransport = TransportProfileId::CurrentLogin,
\t\t// OTClient 15.25 sends client version (4), content revision (4), and preview state (1) before RSA.
\t\t.bytesToSkipBeforeRsa = 9,
\t\t.characterListLayout = AccountCharacterListLayout::WorldListWithSessionKey,
\t\t.sendsSessionKey = true,
\t};
"""
new_profile = """\tconstexpr AccountLoginLayout currentAccountLoginLayout {
\t\t.profileId = ProtocolProfileId::Current,
\t\t.clientVersion = CLIENT_VERSION,
\t\t.responseTransport = TransportProfileId::CurrentLogin,
\t\t.bytesToSkipBeforeRsa = 17,
\t\t.characterListLayout = AccountCharacterListLayout::WorldListWithSessionKey,
\t\t.sendsSessionKey = true,
\t};
"""
if profile.count(old_profile) != 1:
    raise SystemExit("current account-login layout revert precondition did not match")
PROFILE.write_text(profile.replace(old_profile, new_profile, 1), encoding="utf-8")

test = TEST.read_text(encoding="utf-8")n