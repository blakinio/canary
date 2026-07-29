from __future__ import annotations

import copy
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).with_name("real_tibia_evidence.py")
SPEC = importlib.util.spec_from_file_location("real_tibia_evidence", MODULE_PATH)
assert SPEC and SPEC.loader
cli = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cli)
Corpus, EvidenceError, write_generated = cli.Corpus, cli.EvidenceError, cli.write_generated
AS_OF = cli.dt.date(2026, 7, 29)
COMMIT = "93413bd53e9a40f0ff3c4f55986036b10be44e0f"
SHA256 = "a" * 64
AXES = (
    "official_tibia_release", "official_client_build", "protocol_profile", "canary_commit",
    "maintained_otclient_commit", "map_sha256", "datapack_revision",
    "appearances_items_revision", "spawn_npc_sidecar_revision", "database_schema_revision",
)


def dump(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def axes(**values: str | None) -> dict[str, str | None]:
    result = {axis: None for axis in AXES}
    result.update(values)
    return result


def marker(mode: str = "UNKNOWN", ref: str | None = None, **values: str) -> dict[str, object]:
    exact = axes(**values) if mode == "EXACT" else None
    return {
        "mode": mode, "exact": exact, "lower_bound": None, "upper_bound": None,
        "evidence_refs": [ref] if ref else [], "notes": [] if ref else ["Exact version is not proven."],
    }


def history() -> dict[str, object]:
    return {
        "format": "canary-real-tibia-version-history-v1", "schema_version": 1, "module_id": "combat",
        "entries": [{
            "history_id": "RTVH-COMBAT-0001", "claim_refs": ["RT-COMBAT-0001"],
            "lifecycle": {
                "announced_in": marker(), "introduced_in": marker(),
                "observed_in": [marker("EXACT", "RT-COMBAT-0001", canary_commit=COMMIT)],
                "changed_in": [], "deprecated_in": marker(), "removed_in": marker(),
                "effective_from": marker(), "effective_until": marker(),
            },
            "confidence": "proven-observation", "statement": "Observed at the pinned Canary commit.",
            "evidence_refs": ["RT-COMBAT-0001"], "proves": ["Exact Canary observation."],
            "does_not_prove": ["No official Tibia introduction version."], "supersedes": [], "superseded_by": [],
        }],
    }


class EvidenceTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo = Path(__file__).resolve().parents[2]
        cls.record_template = json.loads((cls.repo / "docs/agents/templates/REAL_TIBIA_EVIDENCE_RECORD.yaml").read_text())
        cls.request_template = json.loads((cls.repo / "docs/agents/templates/REAL_TIBIA_EVIDENCE_REQUEST.yaml").read_text())

    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        registry = self.root / "docs/agents/real-tibia/registry/modules"
        for module in ("combat", "protocol"):
            dump(registry / f"{module}.yaml", {"schema_version": 1, "module_id": module})
        evidence = self.root / "docs/agents/real-tibia/evidence"
        (evidence / "generated").mkdir(parents=True)
        (evidence / "README.md").write_text("test\n", encoding="utf-8")
        shutil.copytree(self.repo / "docs/agents/real-tibia/evidence/schemas", evidence / "schemas")
        self.refresh()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def record(self, evidence_id: str = "RT-COMBAT-0001", module: str = "combat") -> dict[str, object]:
        value = copy.deepcopy(self.record_template)
        value["evidence_id"], value["module_id"] = evidence_id, module
        value["claim_key"] = f"claim-{evidence_id[-4:]}"
        return value

    def request(self, request_id: str = "RTREQ-E2E-COMBAT-0001") -> dict[str, object]:
        value = copy.deepcopy(self.request_template)
        value["request_id"] = request_id
        value["claim_refs"] = ["RT-COMBAT-0001"]
        value["available_inputs"]["source_claims"] = ["RT-COMBAT-0001"]
        value["coordination"]["collector_task"] = "CAN-TEST"
        value["coordination"]["coordination_id"] = request_id
        return value

    def write_record(self, value: dict[str, object], *, module_dir: str | None = None) -> None:
        module = module_dir or str(value["module_id"])
        dump(self.root / f"docs/agents/real-tibia/evidence/modules/{module}/records/{value['evidence_id']}.yaml", value)

    def write_request(self, value: dict[str, object], folder: str = "e2e") -> None:
        dump(self.root / f"docs/agents/real-tibia/evidence/requests/{folder}/{value['request_id']}.yaml", value)

    def refresh(self) -> None:
        write_generated(Corpus.load(self.root), check=False, as_of=AS_OF)

    def codes(self, refresh: bool = True) -> set[str]:
        if refresh:
            self.refresh()
        return {item.code for item in Corpus.load(self.root).validate(AS_OF).errors}
