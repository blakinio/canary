from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from otbm_world_assurance_campaign import (
    COVERAGE_FORMAT,
    CERTIFICATION_FORMAT,
    EVIDENCE_BUNDLE_FORMAT,
    FRESHNESS_FORMAT,
    MANIFEST_FORMAT,
    WorldAssuranceCampaignError,
    build_campaign_report,
)


def _load(path: Path, expected_format: str, label: str) -> tuple[dict[str, Any], dict[str, Any], Path]:
    source = path.expanduser().resolve()
    if path.is_symlink() or not source.is_file():
        raise WorldAssuranceCampaignError(f"{label} must be an existing non-symlink regular file: {path}")
    raw = source.read_bytes()
    try:
        document = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise WorldAssuranceCampaignError(f"cannot read {label} JSON {source}: {exc}") from exc
    if not isinstance(document, dict) or document.get("format") != expected_format:
        raise WorldAssuranceCampaignError(f"{label} format must be {expected_format}")
    pin = {
        "fileName": source.name,
        "size": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "format": expected_format,
    }
    return document, pin, source


def _physical_artifact_pin(path: Path, label: str) -> tuple[dict[str, Any], Path]:
    source = path.expanduser().resolve()
    if path.is_symlink() or not source.is_file():
        raise WorldAssuranceCampaignError(f"{label} must be an existing non-symlink regular file: {path}")
    raw = source.read_bytes()
    return {
        "fileName": source.name,
        "size": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }, source


def _write(path: Path, payload: dict[str, Any], *, overwrite: bool, inputs: list[Path]) -> None:
    target = path.expanduser().resolve()
    if path.is_symlink() or target.is_symlink():
        raise WorldAssuranceCampaignError(f"output must not be a symlink: {path}")
    for source in inputs:
        if source == target or (target.exists() and os.path.samefile(source, target)):
            raise WorldAssuranceCampaignError(f"output collides with input: {source}")
    if target.exists() and not target.is_file():
        raise WorldAssuranceCampaignError(f"output exists but is not a regular file: {target}")
    if target.exists() and not overwrite:
        raise WorldAssuranceCampaignError(f"output already exists: {target}; pass --overwrite")
    target.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if not overwrite:
        fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text)
        return
    fd, temporary_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=target.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compose reviewed OTBM world-assurance campaign evidence without rerunning canonical QA producers."
    )
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--coverage-dashboard", type=Path)
    parser.add_argument("--certification", type=Path)
    parser.add_argument("--freshness", type=Path)
    parser.add_argument("--evidence-bundle", type=Path, action="append", default=[])
    parser.add_argument("--physical-artifact", type=Path, action="append", default=[])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    try:
        manifest, manifest_pin, manifest_path = _load(args.manifest, MANIFEST_FORMAT, "campaign manifest")
        inputs = [manifest_path]
        pins: dict[str, Any] = {"manifest": manifest_pin, "evidenceBundles": [], "physicalArtifacts": []}

        coverage = certification = freshness = None
        if args.coverage_dashboard:
            coverage, pins["coverageDashboard"], path = _load(
                args.coverage_dashboard, COVERAGE_FORMAT, "QA-005 coverage dashboard"
            )
            inputs.append(path)
        if args.certification:
            certification, pins["certification"], path = _load(
                args.certification, CERTIFICATION_FORMAT, "QA-006 certification report"
            )
            inputs.append(path)
        if args.freshness:
            freshness, pins["freshness"], path = _load(args.freshness, FRESHNESS_FORMAT, "QA-016 freshness report")
            inputs.append(path)

        bundles = []
        for index, path_arg in enumerate(args.evidence_bundle):
            bundle, pin, path = _load(path_arg, EVIDENCE_BUNDLE_FORMAT, f"QA-018 evidence bundle[{index}]")
            bundles.append(bundle)
            pins["evidenceBundles"].append(pin)
            inputs.append(path)

        for index, path_arg in enumerate(args.physical_artifact):
            physical_pin, path = _physical_artifact_pin(path_arg, f"retained Physical E2E artifact[{index}]")
            pins["physicalArtifacts"].append(physical_pin)
            inputs.append(path)

        report = build_campaign_report(
            manifest=manifest,
            coverage_dashboard=coverage,
            certification_report=certification,
            freshness_report=freshness,
            evidence_bundles=bundles,
            input_pins=pins,
        )
        _write(args.output, report, overwrite=args.overwrite, inputs=inputs)
    except (WorldAssuranceCampaignError, OSError, ValueError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
