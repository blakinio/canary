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
\t\t.bytesToSkipBeforeRsa = 17,
\t\t.characterListLayout = AccountCharacterListLayout::WorldListWithSessionKey,
\t\t.sendsSessionKey = true,
\t};
"""
new_profile = """\tconstexpr AccountLoginLayout currentAccountLoginLayout {
\t\t.profileId = ProtocolProfileId::Current,
\t\t.clientVersion = CLIENT_VERSION,
\t\t.responseTransport = TransportProfileId::CurrentLogin,
\t\t// OTClient 15.25 sends client version (4), content revision (4), and preview state (1) before RSA.
\t\t.bytesToSkipBeforeRsa = 9,
\t\t.characterListLayout = AccountCharacterListLayout::WorldListWithSessionKey,
\t\t.sendsSessionKey = true,
\t};
"""
if profile.count(old_profile) != 1:
    raise SystemExit("current account-login layout did not match the reviewed precondition")
PROFILE.write_text(profile.replace(old_profile, new_profile, 1), encoding="utf-8")

test = TEST.read_text(encoding="utf-8")
marker = """    def test_boosted_boss_has_single_recoverable_empty_result_branch(self) -> None:
        text = self.read(\"src/io/io_bosstiary.cpp\")
        function = re.search(r\"void IOBosstiary::loadBoostedBoss.*?\\n}\", text, re.S)
        self.assertIsNotNone(function)
        body = function.group(0)
        self.assertEqual(body.count(\"if (!result)\"), 1)
        self.assertIn(\"INSERT INTO `boosted_boss`\", body)
"""
replacement = marker + """

    def test_current_login_prelude_matches_maintained_otclient(self) -> None:
        text = self.read(\"src/server/network/protocol/protocol_profile.cpp\")
        layout = re.search(
            r\"constexpr AccountLoginLayout currentAccountLoginLayout \\{.*?\\n\\t\\};\",
            text,
            re.S,
        )
        self.assertIsNotNone(layout)
        body = layout.group(0)
        self.assertIn(\".bytesToSkipBeforeRsa = 9,\", body)
        self.assertNotIn(\".bytesToSkipBeforeRsa = 17,\", body)
"""
if test.count(marker) != 1:
    raise SystemExit("Cyclopedia runtime contract test marker did not match")
TEST.write_text(test.replace(marker, replacement, 1), encoding="utf-8")
