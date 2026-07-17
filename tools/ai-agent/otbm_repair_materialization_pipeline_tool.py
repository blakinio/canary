#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from otbm_repair_materialization_pipeline import (
    ATTRIBUTE_MODE,
    TILE_AREA_MODE,
    RepairMaterializationPipelineError,
    execute_area_mutation,
    execute_attribute_mutation,
    run_pipeline,
)


def _path(value: str) -> Path:
    return Path(value)


def _sample_limit(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("sample limit must be an integer") from exc
    if not 1 <= parsed <= 10_000:
        raise argparse.ArgumentTypeError("sample limit must be in 1..10000")
    return parsed


def _positive_timeout(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("timeout must be an integer") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError("timeout must be positive")
    return parsed


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--artifact-root", type=_path, required=True)
    parser.add_argument(
        "--output-map",
        type=_path,
        required=True,
        help="Create-new final map path relative to artifact root.",
    )
    parser.add_argument(
        "--evidence-dir",
        type=_path,
        required=True,
        help="Create-new pipeline evidence directory relative to artifact root.",
    )
    parser.add_argument("--geometry", type=_path, required=True, help="Explicit canary-otbm-geometry-audit-v1 report")
    parser.add_argument(
        "--reachability",
        type=_path,
        required=True,
        help="Explicit canary-otbm-reachability-v1 report from the reviewed candidate map.",
    )
    parser.add_argument(
        "--script-resolution",
        type=_path,
        required=True,
        help="Explicit canary-otbm-script-resolution-v1 report from the reviewed candidate map.",
    )
    parser.add_argument("--fail-on-severity", choices=("error", "warning"), default="error")
    parser.add_argument("--fail-on-unresolved", action="store_true")
    parser.add_argument("--sample-limit", type=_sample_limit, default=500)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Finalize one reviewed OTBM fixed-width repair or approved complete TILE_AREA materialization into a "
            "create-new map artifact, then bind it to explicit compatible Map Quality Gate component evidence."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    attribute = subparsers.add_parser(
        "attribute",
        help="Re-run an existing reviewed Phase 8 plan through the existing repair sandbox verifier.",
    )
    _add_common(attribute)
    attribute.add_argument("--source-map", type=_path, required=True)
    attribute.add_argument("--plan", type=_path, required=True, help="Reviewed canary-otbm-bounded-patch-plan-v1")
    attribute.add_argument("--scanner", type=_path, required=True)
    attribute.add_argument("--appearances-index", type=_path, required=True)
    attribute.add_argument("--items-xml", type=_path, required=True)
    attribute.add_argument("--repository-root", type=_path, required=True)
    attribute.add_argument(
        "--script-root",
        action="append",
        dest="script_roots",
        required=True,
        help="Explicit active script root; repeat for every selected active root.",
    )
    attribute.add_argument("--rules", type=_path)
    attribute.add_argument("--review-rules", type=_path)
    attribute.add_argument("--timeout-seconds", type=_positive_timeout, default=3600)

    area = subparsers.add_parser(
        "tile-area",
        help="Re-run an approved zero-translation complete TILE_AREA plan through the existing materializer.",
    )
    _add_common(area)
    area.add_argument("--current-map", type=_path, required=True)
    area.add_argument("--donor-map", type=_path, required=True)
    area.add_argument("--scanner", type=_path, required=True)
    area.add_argument("--plan", type=_path, required=True)
    area.add_argument("--approval", type=_path, required=True)
    area.add_argument("--current-index", type=_path, required=True)
    area.add_argument("--current-manifest", type=_path, required=True)
    area.add_argument("--donor-index", type=_path, required=True)
    area.add_argument("--donor-manifest", type=_path, required=True)
    area.add_argument("--timeout-seconds", type=_positive_timeout, default=3600)
    return parser


def _artifact_input(artifact_root: Path, path: Path) -> Path:
    if path.is_absolute():
        return path
    return artifact_root.expanduser().resolve(strict=False) / path


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "attribute":
            repository_root = args.repository_root.expanduser()
            if repository_root.is_symlink() or not repository_root.resolve(strict=True).is_dir():
                raise RepairMaterializationPipelineError("repository root must be an existing non-symlink directory")
            direct_inputs: dict[str, Path] = {
                "sourceMap": args.source_map,
                "plan": args.plan,
                "scanner": args.scanner,
                "appearancesIndex": args.appearances_index,
                "itemsXml": args.items_xml,
            }
            if args.rules is not None:
                direct_inputs["runtimeRules"] = args.rules
            if args.review_rules is not None:
                direct_inputs["reviewRules"] = args.review_rules

            def mutation_executor(candidate: Path, evidence: Path):
                return execute_attribute_mutation(
                    artifact_root=args.artifact_root,
                    source_map=args.source_map,
                    plan=args.plan,
                    scanner=args.scanner,
                    appearances_index=args.appearances_index,
                    items_xml=args.items_xml,
                    repository_root=repository_root,
                    script_roots=args.script_roots,
                    candidate_path=candidate,
                    pipeline_evidence_dir=evidence,
                    rules=args.rules,
                    review_rules=args.review_rules,
                    timeout_seconds=args.timeout_seconds,
                )

            mode = ATTRIBUTE_MODE
            source_map = args.source_map
        else:
            plan = _artifact_input(args.artifact_root, args.plan)
            approval = _artifact_input(args.artifact_root, args.approval)
            current_index = _artifact_input(args.artifact_root, args.current_index)
            current_manifest = _artifact_input(args.artifact_root, args.current_manifest)
            donor_index = _artifact_input(args.artifact_root, args.donor_index)
            donor_manifest = _artifact_input(args.artifact_root, args.donor_manifest)
            direct_inputs = {
                "sourceMap": args.current_map,
                "donorMap": args.donor_map,
                "scanner": args.scanner,
                "plan": plan,
                "approval": approval,
                "currentWorldIndex": current_index,
                "currentWorldIndexManifest": current_manifest,
                "donorWorldIndex": donor_index,
                "donorWorldIndexManifest": donor_manifest,
            }

            def mutation_executor(candidate: Path, evidence: Path):
                return execute_area_mutation(
                    artifact_root=args.artifact_root,
                    current_map=args.current_map,
                    donor_map=args.donor_map,
                    scanner=args.scanner,
                    plan=plan,
                    approval=approval,
                    current_index=current_index,
                    current_manifest=current_manifest,
                    donor_index=donor_index,
                    donor_manifest=donor_manifest,
                    candidate_path=candidate,
                    pipeline_evidence_dir=evidence,
                    timeout_seconds=args.timeout_seconds,
                )

            mode = TILE_AREA_MODE
            source_map = args.current_map

        result = run_pipeline(
            mode=mode,
            artifact_root=args.artifact_root,
            source_map=source_map,
            output_map=args.output_map,
            evidence_dir=args.evidence_dir,
            geometry_report=args.geometry,
            reachability_report=args.reachability,
            script_resolution_report=args.script_resolution,
            direct_inputs=direct_inputs,
            mutation_executor=mutation_executor,
            fail_on_severity=args.fail_on_severity,
            fail_on_unresolved=args.fail_on_unresolved,
            sample_limit=args.sample_limit,
        )
        json.dump(
            {
                "ok": result["ok"],
                "mode": result["mode"],
                "sourceSha256": result["source"]["sha256"],
                "outputSha256": result["output"]["sha256"],
                "output": result["output"]["path"],
                "evidenceDir": result["evidence"]["directory"],
                "qualityOutcomeCounts": result["quality"]["outcomeCounts"],
            },
            sys.stdout,
            indent=2,
            sort_keys=True,
        )
        sys.stdout.write("\n")
        return 0
    except (FileNotFoundError, OSError, ValueError, RepairMaterializationPipelineError) as exc:
        parser.error(str(exc))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
