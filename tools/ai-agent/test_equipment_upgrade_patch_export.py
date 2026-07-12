from __future__ import annotations

import hashlib
import json
import os
import shutil
import unittest
from pathlib import Path


class EquipmentUpgradePatchExportTest(unittest.TestCase):
    """Temporary CI-only exporter; removed from the final validation branch."""

    def test_export_verified_patch(self) -> None:
        if os.environ.get("GITHUB_ACTIONS") != "true" or os.environ.get("GITHUB_HEAD_REF") != "validation/equipment-upgrade":
            self.skipTest("Equipment Upgrade patch export runs only on the validation PR")

        root = Path.cwd()

        def replace_once(path: str, old: str, new: str) -> None:
            file_path = root / path
            text = file_path.read_text(encoding="utf-8")
            count = text.count(old)
            self.assertEqual(count, 1, f"{path}: expected one occurrence of {old!r}, found {count}")
            file_path.write_text(text.replace(old, new), encoding="utf-8")

        replace_once("config.lua.dist", "forgeMaxDust = 225", "forgeMaxDust = 325")
        replace_once(
            "src/config/configmanager.cpp",
            'loadIntConfig(L, FORGE_FIENDISH_CREATURES_LIMIT, "forgeFiendishLimit", 3);',
            'loadIntConfig(L, FORGE_FIENDISH_CREATURES_LIMIT, "forgeFiendishLimit", 4);',
        )
        replace_once(
            "src/config/configmanager.cpp",
            'loadIntConfig(L, FORGE_MAX_DUST, "forgeMaxDust", 225);',
            'loadIntConfig(L, FORGE_MAX_DUST, "forgeMaxDust", 325);',
        )
        replace_once(
            "src/creatures/players/player.cpp",
            '#include "game/functions/forge_transfer_policy.hpp"\n',
            '#include "game/functions/forge_fusion_policy.hpp"\n#include "game/functions/forge_transfer_policy.hpp"\n',
        )

        fusion_anchor = '''\tconst auto &secondForgingItem = getForgeItemFromId(secondItemId, tier, firstForgingItem);
\tif (!secondForgingItem) {
\t\tg_logger().error("[Log 2] Player with name {} failed to fuse item with id {}", getName(), secondItemId);
\t\tsendForgeError(RETURNVALUE_CONTACTADMINISTRATOR);
\t\treturn;
\t}
'''
        fusion_validation = fusion_anchor + '''
\tauto normalizeForgeSlot = [](uint32_t slotPosition) {
\t\treturn (slotPosition & SLOTP_TWO_HAND) != 0 ? static_cast<uint32_t>(SLOTP_HAND) : slotPosition;
\t};
\tconst bool sameForgeSlot = normalizeForgeSlot(firstForgingItem->getSlotPosition()) == normalizeForgeSlot(secondForgingItem->getSlotPosition());
\tif (!ForgeFusionPolicy::isValid(
\t\t\tfirstItemId,
\t\t\tsecondItemId,
\t\t\tfirstForgingItem->getClassification(),
\t\t\tsecondForgingItem->getClassification(),
\t\t\tsameForgeSlot,
\t\t\tconvergence)) {
\t\tg_logger().warn(
\t\t\t"[{}] Rejected invalid fusion for player {}: first item {}, second item {}, first class {}, second class {}, tier {}, same slot {}, convergence {}",
\t\t\t__FUNCTION__,
\t\t\tgetName(),
\t\t\tfirstItemId,
\t\t\tsecondItemId,
\t\t\tfirstForgingItem->getClassification(),
\t\t\tsecondForgingItem->getClassification(),
\t\t\ttier,
\t\t\tsameForgeSlot,
\t\t\tconvergence
\t\t);
\t\tsendForgeError(RETURNVALUE_NOTPOSSIBLE);
\t\treturn;
\t}
'''
        replace_once("src/creatures/players/player.cpp", fusion_anchor, fusion_validation)
        replace_once(
            "src/creatures/players/player.cpp",
            '''\tif (!ForgeTransferPolicy::isValidDonorTier(donorItem->getTier(), convergence) || !ForgeTransferPolicy::hasMatchingClassification(donorClassification, receiveClassification)) {''',
            '''\tif (!ForgeTransferPolicy::isValidTransfer(donorClassification, receiveClassification, donorItem->getTier(), convergence)) {''',
        )

        fusion_policy = root / "src/game/functions/forge_fusion_policy.hpp"
        fusion_policy.write_text(
            '''/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#pragma once

#include <cstdint>

namespace ForgeFusionPolicy {
\t[[nodiscard]] constexpr bool isValid(
\t\tuint16_t firstItemId,
\t\tuint16_t secondItemId,
\t\tuint8_t firstClassification,
\t\tuint8_t secondClassification,
\t\tbool sameSlot,
\t\tbool convergence
\t) {
\t\tif (firstItemId == 0 || secondItemId == 0 || firstClassification == 0 || secondClassification == 0) {
\t\t\treturn false;
\t\t}

\t\tif (!convergence) {
\t\t\treturn firstItemId == secondItemId && firstClassification == secondClassification;
\t\t}

\t\treturn firstItemId != secondItemId
\t\t\t&& firstClassification == 4
\t\t\t&& secondClassification == 4
\t\t\t&& sameSlot;
\t}
} // namespace ForgeFusionPolicy
''',
            encoding="utf-8",
        )

        transfer_policy = root / "src/game/functions/forge_transfer_policy.hpp"
        transfer_policy.write_text(
            '''/**
 * Canary - A free and open-source MMORPG server emulator
 * Copyright (©) 2019–present OpenTibiaBR <opentibiabr@outlook.com>
 * Repository: https://github.com/opentibiabr/canary
 * License: https://github.com/opentibiabr/canary/blob/main/LICENSE
 * Contributors: https://github.com/opentibiabr/canary/graphs/contributors
 * Website: https://docs.opentibiabr.com/
 */

#pragma once

#include <cstdint>

namespace ForgeTransferPolicy {
\t[[nodiscard]] constexpr bool hasMatchingClassification(uint8_t donorClassification, uint8_t receiveClassification) {
\t\treturn donorClassification > 0 && donorClassification == receiveClassification;
\t}

\t[[nodiscard]] constexpr bool isValidDonorTier(uint8_t donorTier, bool convergence) {
\t\treturn convergence ? donorTier >= 1 : donorTier >= 2;
\t}

\t[[nodiscard]] constexpr bool isValidClassification(uint8_t donorClassification, uint8_t receiveClassification, bool convergence) {
\t\treturn hasMatchingClassification(donorClassification, receiveClassification)
\t\t\t&& (!convergence || donorClassification == 4);
\t}

\t[[nodiscard]] constexpr bool isValidTransfer(uint8_t donorClassification, uint8_t receiveClassification, uint8_t donorTier, bool convergence) {
\t\treturn isValidDonorTier(donorTier, convergence)
\t\t\t&& isValidClassification(donorClassification, receiveClassification, convergence);
\t}

\t[[nodiscard]] constexpr uint8_t resourceTier(uint8_t donorTier) {
\t\treturn donorTier;
\t}

\t[[nodiscard]] constexpr uint8_t resultTier(uint8_t donorTier, bool convergence) {
\t\treturn convergence ? donorTier : static_cast<uint8_t>(donorTier - 1);
\t}
} // namespace ForgeTransferPolicy
''',
            encoding="utf-8",
        )

        replace_once(
            "tests/unit/players/forge_test.cpp",
            '#include "creatures/players/player.hpp"\n#include "game/functions/forge_transfer_policy.hpp"\n',
            '#include "creatures/players/player.hpp"\n#include "game/functions/forge_fusion_policy.hpp"\n#include "game/functions/forge_transfer_policy.hpp"\n',
        )
        tests_path = root / "tests/unit/players/forge_test.cpp"
        tests_path.write_text(
            tests_path.read_text(encoding="utf-8").rstrip()
            + '''

TEST(ForgeTransferPolicyTest, RestrictsConvergenceTransferToClassFour) {
\tEXPECT_TRUE(ForgeTransferPolicy::isValidTransfer(4, 4, 1, true));
\tEXPECT_FALSE(ForgeTransferPolicy::isValidTransfer(3, 3, 1, true));
\tEXPECT_FALSE(ForgeTransferPolicy::isValidTransfer(4, 3, 1, true));
\tEXPECT_TRUE(ForgeTransferPolicy::isValidTransfer(3, 3, 2, false));
}

TEST(ForgeFusionPolicyTest, RegularFusionRequiresIdenticalForgeItems) {
\tEXPECT_TRUE(ForgeFusionPolicy::isValid(100, 100, 3, 3, true, false));
\tEXPECT_FALSE(ForgeFusionPolicy::isValid(100, 101, 3, 3, true, false));
\tEXPECT_FALSE(ForgeFusionPolicy::isValid(100, 100, 0, 0, true, false));
}

TEST(ForgeFusionPolicyTest, ConvergenceFusionRequiresDifferentClassFourItemsInSameSlot) {
\tEXPECT_TRUE(ForgeFusionPolicy::isValid(100, 101, 4, 4, true, true));
\tEXPECT_FALSE(ForgeFusionPolicy::isValid(100, 100, 4, 4, true, true));
\tEXPECT_FALSE(ForgeFusionPolicy::isValid(100, 101, 3, 3, true, true));
\tEXPECT_FALSE(ForgeFusionPolicy::isValid(100, 101, 4, 4, false, true));
}
'''
            + "\n",
            encoding="utf-8",
        )

        doc_path = root / "docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_VALIDATION.md"
        doc = doc_path.read_text(encoding="utf-8")
        doc = doc.replace(
            "> **Current phase:** inventory and evidence collection",
            "> **Current phase:** static/semantic validation and evidence-backed remediation",
        )
        replacements = {
            "| Eligibility | Forge equipment cannot be imbued during the process | not started |": "| Eligibility | Forge equipment cannot be imbued during the process | confirmed statically: UI and server lookup reject imbued items |",
            "| Dust capacity | Starts at 100; upgrade cost is current limit minus 75; maximum 325 | not started |": "| Dust capacity | Starts at 100; upgrade cost is current limit minus 75; maximum 325 | mismatch fixed: configured/fallback maximum 225 -> 325; runtime test pending |",
            "| Dust conversion | 60 Dust creates 3 Slivers | not started |": "| Dust conversion | 60 Dust creates 3 Slivers | confirmed statically; runtime test pending |",
            "| Core conversion | 50 Slivers creates 1 Exalted Core | not started |": "| Core conversion | 50 Slivers creates 1 Exalted Core | confirmed statically; failure-path test pending |",
            "| Influenced creatures | 1–5 stacks; stack-dependent HP/damage/XP/Dust | not started |": "| Influenced creatures | 1–5 stacks; stack-dependent HP/damage/XP/Dust | HP and damage formulas confirmed statically; XP/Dust runtime path pending |",
            "| Fiendish creatures | Equivalent strength/reward to 15 stacks; world cap and lifecycle rules | not started |": "| Fiendish creatures | Equivalent strength/reward to 15 stacks; world cap and lifecycle rules | stack 15, HP/damage and cap 4 confirmed statically; lifecycle/rewards pending |",
            "| Fusion | Two identical items of equal tier; base success 50%; optional core raises to 65% | not started |": "| Fusion | Two identical items of equal tier; base success 50%; optional core raises to 65% | server eligibility mismatch fixed; probability path confirmed statically; outcome tests pending |",
            "| Convergence Fusion | Class 4 only; different items in same body slot and equal tier; guaranteed; no bonus | not started |": "| Convergence Fusion | Class 4 only; different items in same body slot and equal tier; guaranteed; no bonus | server eligibility mismatch fixed; resource/outcome tests pending |",
            "| Convergence Transfer | Class 4 only; no tier loss; may cross body slots; source destroyed | not started |": "| Convergence Transfer | Class 4 only; no tier loss; may cross body slots; source destroyed | class restriction mismatch fixed; full integration test pending |",
        }
        for old, new in replacements.items():
            self.assertIn(old, doc)
            doc = doc.replace(old, new)

        anchor = "No production code was changed in this step.\n"
        self.assertIn(anchor, doc)
        doc = doc.replace(
            anchor,
            '''No production code was changed in this step.

### 2026-07-12 — first semantic findings and fixes

- Opened draft PR #171 for the validation stream.
- Confirmed `forge_dust_level` starts at 100 in the database schema.
- Confirmed the Dust-limit upgrade formula is `current limit - 75`.
- Confirmed Dust-to-Slivers is 60 Dust for 3 Slivers and Slivers-to-Core is 50 Slivers for 1 Core.
- Confirmed imbued equipment is filtered both from the Forge window and from the server-side item lookup.
- Confirmed the runtime pricing table matches the documented regular/convergence Fusion and Transfer tables.
- Confirmed influenced/fiendish HP and damage formulas match stacks 1-5 and 15; XP, Dust and Premium paths remain open.
- Fixed stale maximum Dust values: `config.lua.dist` and the `ConfigManager` fallback used 225 instead of 325.
- Aligned the fallback Fiendish world limit with the configured/documented limit of 4 (fallback was 3).
- Fixed a server-authority gap where regular Fusion accepted different item IDs when a crafted packet bypassed the client list.
- Fixed server-authority gaps where Convergence Fusion and Convergence Transfer could be requested for upgrade classes 1-3.
- Added pure policy helpers and unit tests for regular Fusion identity, Convergence Fusion class/slot/identity rules, and Convergence Transfer class-4 enforcement.
- Added server-side rejection before any Forge inventory/resource mutation.
- Used a temporary CI artifact exporter because the connector exposes full-file writes but not textual patch application; the exporter and workflow scaffolding are excluded from the final branch state.

Files changed in this remediation:

- `config.lua.dist`;
- `src/config/configmanager.cpp`;
- `src/creatures/players/player.cpp`;
- `src/game/functions/forge_fusion_policy.hpp`;
- `src/game/functions/forge_transfer_policy.hpp`;
- `tests/unit/players/forge_test.cpp`;
- this validation document.

Evidence level after this step: static/semantic **B-C** for the listed rules; regression **F** is pending CI execution and runtime/gameplay **D-E** remain open.
''',
        )
        old_next = '''1. inventory every Forge-related source/config/test file;
2. reconstruct the exact cost/probability/classification tables used at runtime;
3. compare Fusion and both Convergence flows first, because normal Transfer already has focused baseline coverage;
4. inspect mutation ordering and rollback guarantees;
5. add failing tests before behavioural fixes;
6. continue with influenced/fiendish creatures and item effects;
7. perform runtime and protocol validation after static/semantic issues are resolved.'''
        new_next = '''1. run the focused Forge unit/integration suites and inspect CI;
2. add integration coverage proving malformed Fusion/Convergence packets do not mutate items, Dust, cores or gold;
3. validate all eight Fusion bonus outcomes and their history/result packets;
4. inspect mutation ordering and rollback guarantees for late failures;
5. validate influenced/fiendish XP, Dust, Premium restrictions and lifecycle;
6. validate Onslaught, Ruse, Momentum, Transcendence and Amplification formulas;
7. perform runtime and protocol gameplay validation after static/semantic issues are resolved.'''
        self.assertIn(old_next, doc)
        doc = doc.replace(old_next, new_next)
        doc = doc.replace(
            "No claim of full Equipment Upgrade parity has been made yet. The current work is at evidence-inventory stage.",
            "No claim of full Equipment Upgrade parity has been made yet. Static server-authority fixes are present, but CI, runtime/gameplay validation, bonus outcomes, monster rewards/lifecycle and effect formulas remain open.",
        )
        doc_path.write_text(doc, encoding="utf-8")

        paths = [
            "config.lua.dist",
            "src/config/configmanager.cpp",
            "src/creatures/players/player.cpp",
            "src/game/functions/forge_fusion_policy.hpp",
            "src/game/functions/forge_transfer_policy.hpp",
            "tests/unit/players/forge_test.cpp",
            "docs/ai-agent/OTS_AI_EQUIPMENT_UPGRADE_VALIDATION.md",
        ]
        export_root = root / "artifacts/first-real-content-pack/generated-content/equipment-upgrade-patch"
        manifest: dict[str, str] = {}
        for relative in paths:
            source = root / relative
            target = export_root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            manifest[relative] = hashlib.sha256(source.read_bytes()).hexdigest()

        (export_root / "MANIFEST.json").write_text(
            json.dumps({"files": manifest}, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        self.assertEqual(set(manifest), set(paths))


if __name__ == "__main__":
    unittest.main()
