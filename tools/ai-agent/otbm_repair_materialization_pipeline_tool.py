#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from otbm_repair_materialization_pipeline import (
    ATTRIBUTE_MODE,
    RepairMaterializationPipelineError,
    execute_attribute_mutation,
    run_pipeline,
)
from otbm_repair_pipeline_structural_cli import STRUCTURAL_MODES, add_structural_parsers, prepare_structural


def _path(value: str) -> Path:
    return Path(value)


def _bounded_int(value: str, *, label: str, minimum: int, maximum: int | None = None) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{label} must be an integer") from exc
    if parsed < minimum or (maximum is not None and parsed > maximum):
        suffix = f"..{maximum}" if maximum is not None else " or greater"
        raise argparse.ArgumentTypeError(f"{label} must be in {minimum}{suffix}")
    return parsed


def _sample_limit(value: str) -> int:
    return _bounded_int(value, label="sample limit", minimum=1, maximum=10_000)


def _positive_timeout(value: str) -> int:
    return _bounded_int(value, label="timeout", minimum=1)


def _add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--artifact-root", type=_path, required=True)
    parser.add_argument("--output-map", type=_path, required=True, help="Create-new final map path relative to artifact root.")
    parser.add_argument("--evidence-dir", type=_path, required=True, help="Create-new pipeline evidence directory relative to artifact root.")
    parser.add_argument("--geometry", type=_path, required=True)
    parser.add_argument("--reachability", type=_path, required=True)
    parser.add_argument("--script-resolution", type=_path, required=True)
    parser.add_argument("--fail-on-severity", choices=("error", "warning"), default="error")
    parser.add_argument("--fail-on-unresolved", action="store_true")
    parser.add_argument("--sample-limit", type=_sample_limit, default=500)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Finalize exactly one reviewed OTBM fixed-width, complete TILE_AREA, or bounded raw-tile mutation "
            "through the canonical repair/materialization pipeline and explicit compatible Map Quality evidence."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    attribute = subparsers.add_parser("attribute", help="Re-run a reviewed Phase 8 plan through the repair sandbox verifier.")
    _add_common(attribute)
    attribute.add_argument("--source-map", type=_path, required=True)
    attribute.add_argument("--plan", type=_path, required=True)
    attribute.add_argument("--scanner", type=_path, required=True)
    attribute.add_argument("--appearances-index", type=_path, required=True)
    attribute.add_argument("--items-xml", type=_path, required=True)
    attribute.add_argument("--repository-root", type=_path, required=True)
    attribute.add_argument("--script-root", action="append", dest="script_roots", required=True)
    attribute.add_argument("--rules", type=_path)
    attribute.add_argument("--review-rules", type=_path)
    attribute.add_argument("--timeout-seconds", type=_positive_timeout, default=3600)
    add_structural_parsers(subparsers, _add_common, _path, _positive_timeout)
    return parser


def _prepare_attribute(args: argparse.Namespace):
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

    def executor(candidate: Path, evidence: Path):
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

    return ATTRIBUTE_MODE, args.source_map, direct_inputs, executor


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == ATTRIBUTE_MODE:
            mode, source_map, direct_inputs, mutation_executor = _prepare_attribute(args)
        elif args.command in STRUCTURAL_MODES:
            mode, source_map, direct_inputs, mutation_executor = prepare_structural(args)
        else:
            raise RepairMaterializationPipelineError(f"unsupported mutation command: {args.command}")
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
