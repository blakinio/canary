from __future__ import annotations

import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path

from otbm_storage_graph import (
    QUEST_EVIDENCE_FORMAT,
    REPORT_FORMAT,
    StorageGraphError,
    build_storage_graph,
    write_report,
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class StorageGraphTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def evidence(self, sources: dict[str, str], *, unresolved=None, extra_evidence=None) -> Path:
        files = []
        for rel, text in sources.items():
            path = self.root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
            files.append({"path": rel, "sha256": sha(path), "evidenceCount": 0, "unresolvedCount": 0})
        payload = {
            "format": QUEST_EVIDENCE_FORMAT,
            "ok": True,
            "selectors": {"repositoryRoot": ".", "sourceRoots": ["data"], "includes": ["data/**/*.lua"], "excludes": []},
            "sourceDigest": "a" * 64,
            "summary": {"filesScanned": len(files), "evidenceCount": len(extra_evidence or []), "unresolvedCount": len(unresolved or []), "byKind": {}, "byRole": {}},
            "files": files,
            "evidence": extra_evidence or [],
            "unresolved": unresolved or [],
        }
        path = self.root / "evidence.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def build(self, sources: dict[str, str], **kwargs):
        evidence = self.evidence(sources, unresolved=kwargs.pop("unresolved", None), extra_evidence=kwargs.pop("extra_evidence", None))
        return build_storage_graph(repository_root=self.root, quest_evidence_path=evidence, **kwargs)

    def test_literal_transition_and_context(self) -> None:
        rel = "data/quest.lua"
        evidence_entry = {
            "id": "1" * 20,
            "kind": "actionId",
            "value": 45001,
            "role": "registration",
            "confidence": "high",
            "source": {"path": rel, "line": 1, "context": "action:aid(45001)"},
            "details": {"eventType": "Action", "handler": "onUse"},
        }
        report = self.build(
            {
                rel: """
local stage = Storage.Quest.Test.Stage
local action = Action()
function action.onUse(player)
    if player:getStorageValue(stage) == 1 then
        player:setStorageValue(stage, 2)
    end
end
action:aid(45001)
action:register()
"""
            },
            extra_evidence=[evidence_entry],
        )
        self.assertEqual(report["format"], REPORT_FORMAT)
        self.assertEqual(report["summary"]["transitions"], 1)
        edge = report["transitions"][0]
        self.assertEqual(edge["namespace"], "player-storage")
        self.assertEqual(edge["key"], "Storage.Quest.Test.Stage")
        self.assertEqual(edge["prerequisite"]["value"], 1)
        self.assertEqual(edge["result"]["value"], 2)
        self.assertEqual(edge["handlerContext"][0]["eventType"], "Action")
        self.assertFalse(report["policy"]["executionOrderInferred"])

    def test_increment_from_same_key_read(self) -> None:
        report = self.build(
            {
                "data/inc.lua": """
local key = Storage.Quest.Test.Counter
function advance(player)
    if player:getStorageValue(key) == 3 then
        player:setStorageValue(key, player:getStorageValue(key) + 1)
    end
end
"""
            }
        )
        self.assertEqual(report["summary"]["transitions"], 1)
        edge = report["transitions"][0]
        self.assertEqual(edge["result"]["kind"], "delta")
        self.assertEqual(edge["result"]["delta"], 1)
        self.assertEqual(edge["result"]["value"], 4)
        self.assertIn("increment", report["summary"]["byOperation"])

    def test_increment_from_unique_read_variable(self) -> None:
        report = self.build(
            {
                "data/inc.lua": """
local key = Storage.Quest.Test.Counter
local current = player:getStorageValue(key)
if current == 7 then
    player:setStorageValue(key, current - 2)
end
"""
            }
        )
        edge = report["transitions"][0]
        self.assertEqual(edge["result"]["value"], 5)
        self.assertIn("backward-literal-transition", edge["issues"])
        self.assertEqual(report["summary"]["findingsByCode"]["storage_backward_literal_transition"], 1)

    def test_conflicting_writers_same_prerequisite(self) -> None:
        report = self.build(
            {
                "data/a.lua": "if player:getStorageValue(100) == 1 then\n player:setStorageValue(100, 2)\nend\n",
                "data/b.lua": "if player:getStorageValue(100) == 1 then\n player:setStorageValue(100, 3)\nend\n",
            }
        )
        self.assertEqual(report["summary"]["findingsByCode"]["storage_conflicting_literal_writers"], 1)

    def test_non_exact_condition_does_not_form_transition(self) -> None:
        report = self.build(
            {"data/a.lua": "if player:getStorageValue(100) >= 1 then\n player:setStorageValue(100, 2)\nend\n"}
        )
        self.assertEqual(report["summary"]["transitions"], 0)

    def test_else_branch_does_not_invert_condition(self) -> None:
        report = self.build(
            {"data/a.lua": "if player:getStorageValue(100) == 1 then\n return true\nelse\n player:setStorageValue(100, 2)\nend\n"}
        )
        self.assertEqual(report["summary"]["transitions"], 0)

    def test_namespaces_are_separate(self) -> None:
        report = self.build(
            {
                "data/ns.lua": """
local key = 9
player:getStorageValue(key)
player:getAccountStorage(key)
player:kv():get("quest")
player:accountKV():set("quest", 1)
Game.getStorageValue(key)
Game.setStorageValue(key, 2)
GlobalKV.set("world", true)
db.storeQuery("SELECT `value` FROM `player_storage` WHERE `key` = 9")
"""
            }
        )
        namespaces = set(report["summary"]["byNamespace"])
        self.assertEqual(
            namespaces,
            {"player-storage", "account-storage", "player-kv", "account-kv", "global-storage", "global-kv", "database"},
        )

    def test_scoped_kv_key(self) -> None:
        report = self.build({"data/kv.lua": 'player:kv():scoped("quest"):set("stage", 2)\n'})
        keys = {(op["namespace"], op["key"]) for op in report["operations"]}
        self.assertIn(("player-kv", "quest/stage"), keys)

    def test_dynamic_key_and_value_are_unresolved(self) -> None:
        report = self.build(
            {"data/dyn.lua": "player:getStorageValue(keys[index])\nplayer:setStorageValue(Storage.Quest.X, value())\n"}
        )
        kinds = {entry["kind"] for entry in report["unresolved"]}
        self.assertIn("storage-key", kinds)
        self.assertIn("storage-value", kinds)
        self.assertFalse(report["complete"])

    def test_phase2_unresolved_is_preserved(self) -> None:
        unresolved = [
            {
                "id": "2" * 20,
                "kind": "storage",
                "expression": "storages[index]",
                "source": {"path": "data/a.lua", "line": 1, "context": ""},
                "reason": "dynamic",
            }
        ]
        report = self.build({"data/a.lua": "return true\n"}, unresolved=unresolved)
        self.assertTrue(any(entry["id"].startswith("phase2-") for entry in report["unresolved"]))

    def test_selected_hash_mismatch_fails_closed(self) -> None:
        evidence = self.evidence({"data/a.lua": "return true\n"})
        (self.root / "data/a.lua").write_text("changed\n", encoding="utf-8")
        with self.assertRaisesRegex(StorageGraphError, "hash mismatch"):
            build_storage_graph(repository_root=self.root, quest_evidence_path=evidence)

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unsupported")
    def test_selected_symlink_fails_closed(self) -> None:
        real = self.root / "real.lua"
        real.write_text("return true\n", encoding="utf-8")
        link = self.root / "data/a.lua"
        link.parent.mkdir(parents=True)
        link.symlink_to(real)
        payload = {
            "format": QUEST_EVIDENCE_FORMAT,
            "ok": True,
            "selectors": {"repositoryRoot": ".", "sourceRoots": ["data"], "includes": ["data/*.lua"], "excludes": []},
            "sourceDigest": "a" * 64,
            "summary": {"filesScanned": 1, "evidenceCount": 0, "unresolvedCount": 0, "byKind": {}, "byRole": {}},
            "files": [{"path": "data/a.lua", "sha256": sha(real), "evidenceCount": 0, "unresolvedCount": 0}],
            "evidence": [],
            "unresolved": [],
        }
        evidence = self.root / "evidence.json"
        evidence.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(StorageGraphError, "symlink"):
            build_storage_graph(repository_root=self.root, quest_evidence_path=evidence)

    def test_deterministic_report(self) -> None:
        sources = {"data/a.lua": "if player:getStorageValue(1) == 0 then\nplayer:setStorageValue(1, 1)\nend\n"}
        evidence = self.evidence(sources)
        first = build_storage_graph(repository_root=self.root, quest_evidence_path=evidence)
        second = build_storage_graph(repository_root=self.root, quest_evidence_path=evidence)
        self.assertEqual(first, second)

    def test_reverse_comparison_forms_transition(self) -> None:
        report = self.build(
            {"data/reverse.lua": "if 4 == player:getStorageValue(100) then\n player:setStorageValue(100, 5)\nend\n"}
        )
        self.assertEqual(report["transitions"][0]["prerequisite"]["value"], 4)

    def test_nested_branch_keeps_exact_prerequisite(self) -> None:
        report = self.build(
            {
                "data/nested.lua": """
function run(player)
    if player:getStorageValue(100) == 2 then
        if player:getLevel() > 20 then
            player:setStorageValue(100, 3)
        end
    end
end
"""
            }
        )
        self.assertEqual(report["summary"]["transitions"], 1)
        self.assertEqual(report["transitions"][0]["result"]["value"], 3)

    def test_optional_phase4_actor_context(self) -> None:
        rel = "data/npc/test.lua"
        evidence = self.evidence({rel: "player:getStorageValue(100)\n"})
        spawn = {
            "format": "canary-otbm-spawn-npc-evidence-v1",
            "schemaVersion": 1,
            "ok": True,
            "activeDatapack": {"rootName": "data", "sourceManifestSha256": "a" * 64},
            "policy": {},
            "sources": {},
            "summary": {},
            "definitions": [{"kind": "npc", "name": "Test", "canonicalName": "test", "source": rel, "line": 1, "sourceSha256": "b" * 64, "rewardBossLiteral": False, "spawnBossLiteral": False}],
            "spawnGroups": [],
            "placements": [],
            "dynamicCreations": [],
            "findings": [],
        }
        spawn_path = self.root / "spawn.json"
        spawn_path.write_text(json.dumps(spawn), encoding="utf-8")
        report = build_storage_graph(repository_root=self.root, quest_evidence_path=evidence, spawn_evidence_path=spawn_path)
        self.assertEqual(report["operations"][0]["actorContext"]["definitions"][0]["name"], "Test")
        self.assertTrue(report["correlation"]["spawnNpcEvidenceProvided"])

    def test_mismatched_quest_validation_digest_fails(self) -> None:
        evidence = self.evidence({"data/a.lua": "player:getStorageValue(1)\n"})
        validation = {
            "format": "canary-quest-map-validation-v1",
            "sources": {"evidenceDigest": "b" * 64},
            "findings": [],
        }
        validation_path = self.root / "validation.json"
        validation_path.write_text(json.dumps(validation), encoding="utf-8")
        with self.assertRaisesRegex(StorageGraphError, "digest does not match"):
            build_storage_graph(repository_root=self.root, quest_evidence_path=evidence, quest_validation_path=validation_path)

    def test_atomic_output_requires_overwrite(self) -> None:
        report = self.build({"data/a.lua": "player:getStorageValue(1)\n"})
        output = self.root / "report.json"
        write_report(output, report)
        with self.assertRaisesRegex(StorageGraphError, "already exists"):
            write_report(output, report)
        write_report(output, report, overwrite=True)
        self.assertEqual(json.loads(output.read_text())["format"], REPORT_FORMAT)

    @unittest.skipUnless(hasattr(os, "symlink"), "symlinks unsupported")
    def test_output_symlink_rejected(self) -> None:
        report = self.build({"data/a.lua": "player:getStorageValue(1)\n"})
        target = self.root / "real.json"
        target.write_text("{}", encoding="utf-8")
        link = self.root / "link.json"
        link.symlink_to(target)
        with self.assertRaisesRegex(StorageGraphError, "symlink"):
            write_report(link, report, overwrite=True)


if __name__ == "__main__":
    unittest.main()
