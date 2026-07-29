from __future__ import annotations

import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import tibia_client_reference_drift as drift

REVISION = "a" * 40


def write(path: Path, value: object) -> str:
    data = json.dumps(value, indent=2, sort_keys=True).encode() + b"\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return hashlib.sha256(data).hexdigest()


def selected(version: str) -> list[dict[str, object]]:
    return [
        {"id": "package-metadata", "path": "package.json", "sizeBytes": 10, "sha256": hashlib.sha256(f"pkg-{version}".encode()).hexdigest()},
        {"id": "staticdata", "path": "assets/staticdata.dat", "sizeBytes": 20, "sha256": hashlib.sha256(f"static-{version}".encode()).hexdigest()},
        {"id": "staticmapdata", "path": "assets/staticmapdata.dat", "sizeBytes": 30, "sha256": hashlib.sha256(b"map-same").hexdigest()},
        {"id": "proficiencies", "path": "assets/proficiencies.json", "sizeBytes": 40, "sha256": hashlib.sha256(f"prof-{version}".encode()).hexdigest()},
    ]


def manifest(reference: str, inputs: list[dict[str, object]], generated: list[dict[str, str]]) -> dict[str, object]:
    return {
        "format": drift.MANIFEST_FORMAT,
        "schemaVersion": 1,
        "referenceId": reference,
        "packageRootLabel": reference,
        "sourceRole": "test",
        "observedAt": "2026-07-29T00:00:00Z",
        "clientBuild": {"evidence": "declared", "value": reference, "conflictingValues": []},
        "parserRevision": REVISION,
        "selectedInputs": inputs,
        "generatedIndexes": generated,
        "packageMetadata": {},
        "summary": {"selectedInputCount": len(inputs), "selectedInputBytes": sum(int(x["sizeBytes"]) for x in inputs), "generatedIndexCount": len(generated)},
        "policy": {"explicitSelectionOnly": True, "recursiveDiscovery": False, "executesSelectedContent": False, "packageRootTrustedAsVersionProof": False, "maxSelectedFileBytes": 1000},
    }


def source(reference: str, bootstrap_sha: str, row: dict[str, object]) -> dict[str, object]:
    return {
        "manifestFormat": drift.MANIFEST_FORMAT,
        "manifestSha256": bootstrap_sha,
        "referenceId": reference,
        "inputId": row["id"],
        "manifestPath": row["path"],
        "sizeBytes": row["sizeBytes"],
        "sha256": row["sha256"],
        "encoding": "raw",
        "decodedSizeBytes": row["sizeBytes"],
    }


def make_snapshot(root: Path, name: str, *, family: str = "legacy", profs: list[dict[str, object]] | None = None, houses: list[dict[str, object]] | None = None, static_records: list[dict[str, object]] | None = None) -> drift.SnapshotPaths:
    folder = root / name
    inputs = selected(name)
    by_id = {str(row["id"]): row for row in inputs}
    bootstrap_path = folder / "manifest.bootstrap.json"
    bootstrap = manifest(name, inputs, [])
    bootstrap_sha = write(bootstrap_path, bootstrap)

    staticdata = {
        "format": "canary-tibia-staticdata-index-v1", "schemaVersion": 2,
        "source": source(name, bootstrap_sha, by_id["staticdata"]) | {"schemaFamily": family, "schemaEvidence": ["test"], "houseFieldOrder": "unresolved", "houseFieldOrderEvidence": {"state": "unresolved"}},
        "categories": {"houses": {"sourceCategory": "houses", "sourceSchema": family, "count": len(static_records or []), "records": static_records or []}},
        "findings": {}, "summary": {}, "policy": {},
    }
    staticmap = {
        "format": "canary-tibia-staticmapdata-index-v1", "schemaVersion": 1,
        "source": source(name, bootstrap_sha, by_id["staticmapdata"]),
        "objectIdNamespace": {}, "houses": houses or [], "findings": {}, "summary": {}, "policy": {},
    }
    proficiency = {
        "format": "canary-tibia-proficiency-index-v1", "schemaVersion": 2,
        "source": source(name, bootstrap_sha, by_id["proficiencies"]),
        "identifierNamespaces": {}, "proficiencies": profs or [], "findings": {}, "summary": {}, "policy": {},
    }
    paths = {
        "staticdata": folder / "staticdata.json",
        "staticmapdata": folder / "staticmapdata.json",
        "proficiencies": folder / "proficiencies.json",
    }
    hashes = {
        "staticdata": write(paths["staticdata"], staticdata),
        "staticmapdata": write(paths["staticmapdata"], staticmap),
        "proficiencies": write(paths["proficiencies"], proficiency),
    }
    final = manifest(name, inputs, [{"id": key, "sha256": hashes[key]} for key in sorted(hashes)])
    manifest_path = folder / "manifest.json"
    write(manifest_path, final)
    return drift.SnapshotPaths(manifest_path, bootstrap_path, paths["staticdata"], paths["staticmapdata"], paths["proficiencies"])


class DriftTests(unittest.TestCase):
    def load_pair(self, root: Path, **current_kwargs: object) -> tuple[drift.LoadedSnapshot, drift.LoadedSnapshot]:
        before_paths = make_snapshot(root, "baseline", family="legacy", profs=[{"sourceOrdinal": 1, "proficiencyId": 1, "name": "One", "levels": []}], houses=[{"sourceOrdinal": 1, "houseId": 10}], static_records=[{"sourceOrdinal": 1, "id": 10, "name": "House"}])
        after_paths = make_snapshot(root, "current", **current_kwargs)
        return drift.load_snapshot(before_paths, label="baseline"), drift.load_snapshot(after_paths, label="current")

    def test_deterministic_and_record_changes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            before, after = self.load_pair(Path(directory), family="legacy", profs=[{"sourceOrdinal": 1, "proficiencyId": 1, "name": "Changed", "levels": []}, {"sourceOrdinal": 2, "proficiencyId": 2, "name": "Added", "levels": []}], houses=[{"sourceOrdinal": 1, "houseId": 11}], static_records=[{"sourceOrdinal": 1, "id": 10, "name": "Changed"}, {"sourceOrdinal": 2, "id": 11, "name": "Added"}])
            first = drift.generate_drift(before, after, parser_revision=REVISION)
            second = drift.generate_drift(before, after, parser_revision=REVISION)
            self.assertEqual(first, second)
            families = {row["family"] for row in first["findings"]}
            self.assertIn("proficiency.definition", families)
            self.assertIn("staticmapdata.house", families)
            self.assertIn("staticdata.houses", families)
            self.assertFalse(first["staleness"]["usesTimestamps"])

    def test_schema_family_change_skips_staticdata_records(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            before, after = self.load_pair(Path(directory), family="newer", profs=[{"sourceOrdinal": 1, "proficiencyId": 1, "name": "One", "levels": []}], houses=[{"sourceOrdinal": 1, "houseId": 10}], static_records=[{"sourceOrdinal": 1, "id": 999, "name": "Different"}])
            result = drift.generate_drift(before, after, parser_revision=REVISION)
            family_rows = [row for row in result["findings"] if row["family"] == "staticdata.schema-family"]
            self.assertEqual(len(family_rows), 1)
            self.assertEqual(family_rows[0]["comparisonState"], "schema-family-changed-record-comparison-skipped")
            self.assertFalse(any(row["family"].startswith("staticdata.") and row["family"] != "staticdata.schema-family" for row in result["findings"]))

    def test_generated_index_hash_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = make_snapshot(Path(directory), "baseline")
            data = json.loads(paths.manifest.read_text())
            data["generatedIndexes"][0]["sha256"] = "0" * 64
            write(paths.manifest, data)
            with self.assertRaisesRegex(drift.DriftError, "generatedIndexes"):
                drift.load_snapshot(paths, label="baseline")

    def test_source_binding_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = make_snapshot(Path(directory), "baseline")
            report = json.loads(paths.staticdata.read_text())
            report["source"]["manifestSha256"] = "0" * 64
            write(paths.staticdata, report)
            final = json.loads(paths.manifest.read_text())
            for row in final["generatedIndexes"]:
                if row["id"] == "staticdata":
                    row["sha256"] = drift.file_sha256(paths.staticdata)
            write(paths.manifest, final)
            with self.assertRaisesRegex(drift.DriftError, "bootstrap manifest"):
                drift.load_snapshot(paths, label="baseline")

    def test_parser_revision_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            before, after = self.load_pair(Path(directory), family="legacy")
            changed = copy.deepcopy(after)
            object.__setattr__(changed, "manifest", dict(after.manifest) | {"parserRevision": "b" * 40})
            with self.assertRaisesRegex(drift.DriftError, "parser revisions differ"):
                drift.validate_compatibility(before, changed)

    def test_report_schema_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            before, after = self.load_pair(Path(directory), family="legacy")
            changed_reports = dict(after.reports)
            changed_reports["staticmapdata"] = dict(changed_reports["staticmapdata"]) | {"schemaVersion": 2}
            changed = copy.copy(after)
            object.__setattr__(changed, "reports", changed_reports)
            with self.assertRaisesRegex(drift.DriftError, "schema versions differ"):
                drift.validate_compatibility(before, changed)

    def test_finding_bound_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            before, after = self.load_pair(Path(directory), family="legacy", profs=[{"sourceOrdinal": i + 1, "proficiencyId": i + 2, "name": str(i), "levels": []} for i in range(5)])
            with self.assertRaisesRegex(drift.DriftError, "finding count exceeds"):
                drift.generate_drift(before, after, parser_revision=REVISION, max_findings=1)

    def test_duplicate_json_key_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.json"
            path.write_text('{"a": 1, "a": 2}', encoding="utf-8")
            with self.assertRaisesRegex(drift.DriftError, "duplicate JSON object key"):
                drift.load_json(path)

    def test_same_reference_id_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            paths = make_snapshot(Path(directory), "same")
            one = drift.load_snapshot(paths, label="one")
            two = drift.load_snapshot(paths, label="two")
            with self.assertRaisesRegex(drift.DriftError, "must be distinct"):
                drift.validate_compatibility(one, two)


if __name__ == "__main__":
    unittest.main()
