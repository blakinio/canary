from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Callable

from otbm_repair_materialization_pipeline import TILE_AREA_MODE, execute_area_mutation
from otbm_repair_pipeline_raw_tile_contracts import (
    TILE_DELETION_MODE,
    TILE_INSERTION_MODE,
    TILE_REPLACEMENT_MODE,
    TILE_TYPE_CONVERSION_MODE,
)
from otbm_repair_pipeline_raw_tile_executors import (
    execute_tile_deletion_mutation,
    execute_tile_insertion_mutation,
    execute_tile_replacement_mutation,
    execute_tile_type_conversion_mutation,
)

STRUCTURAL_MODES = {
    TILE_AREA_MODE,
    TILE_REPLACEMENT_MODE,
    TILE_INSERTION_MODE,
    TILE_DELETION_MODE,
    TILE_TYPE_CONVERSION_MODE,
}


def add_structural_parsers(
    subparsers: argparse._SubParsersAction[argparse.ArgumentParser],
    add_common: Callable[[argparse.ArgumentParser], None],
    path_type: Callable[[str], Path],
    timeout_type: Callable[[str], int],
) -> None:
    specs = (
        (TILE_AREA_MODE, True, True, "Approved zero-translation complete TILE_AREA materialization."),
        (TILE_REPLACEMENT_MODE, True, False, "Approved same-coordinate complete raw tile replacement."),
        (TILE_INSERTION_MODE, True, False, "Approved same-coordinate complete raw tile insertion."),
        (TILE_DELETION_MODE, False, False, "Approved complete raw tile deletion."),
        (TILE_TYPE_CONVERSION_MODE, True, False, "Approved same-coordinate TILE/HOUSETILE conversion."),
    )
    for mode, donor, plan in specs:
        parser = subparsers.add_parser(mode, help=specs[0][3] if mode == TILE_AREA_MODE else specs[[s[0] for s in specs].index(mode)][3])
        add_common(parser)
        parser.add_argument("--current-map", type=path_type, required=True)
        if donor:
            parser.add_argument("--donor-map", type=path_type, required=True)
        parser.add_argument("--scanner", type=path_type, required=True)
        if plan:
            parser.add_argument("--plan", type=path_type, required=True)
        parser.add_argument("--approval", type=path_type, required=True)
        parser.add_argument("--current-index", type=path_type, required=True)
        parser.add_argument("--current-manifest", type=path_type, required=True)
        if donor:
            parser.add_argument("--donor-index", type=path_type, required=True)
            parser.add_argument("--donor-manifest", type=path_type, required=True)
        parser.add_argument("--timeout-seconds", type=timeout_type, default=3600)


def artifact_input(artifact_root: Path, path: Path) -> Path:
    return path if path.is_absolute() else artifact_root.expanduser().resolve(strict=False) / path


def prepare_structural(args: argparse.Namespace) -> tuple[str, Path, dict[str, Path], Callable[[Path, Path], Any]]:
    donor = args.command != TILE_DELETION_MODE
    paths = {
        "approval": artifact_input(args.artifact_root, args.approval),
        "current_index": artifact_input(args.artifact_root, args.current_index),
        "current_manifest": artifact_input(args.artifact_root, args.current_manifest),
    }
    if args.command == TILE_AREA_MODE:
        paths["plan"] = artifact_input(args.artifact_root, args.plan)
    if donor:
        paths["donor_index"] = artifact_input(args.artifact_root, args.donor_index)
        paths["donor_manifest"] = artifact_input(args.artifact_root, args.donor_manifest)

    direct_inputs = {
        "sourceMap": args.current_map,
        "scanner": args.scanner,
        "approval": paths["approval"],
        "currentWorldIndex": paths["current_index"],
        "currentWorldIndexManifest": paths["current_manifest"],
    }
    if donor:
        direct_inputs.update({
            "donorMap": args.donor_map,
            "donorWorldIndex": paths["donor_index"],
            "donorWorldIndexManifest": paths["donor_manifest"],
        })
    if args.command == TILE_AREA_MODE:
        direct_inputs["plan"] = paths["plan"]

    def executor(candidate: Path, evidence: Path):
        common = dict(
            artifact_root=args.artifact_root,
            current_map=args.current_map,
            scanner=args.scanner,
            approval=paths["approval"],
            current_index=paths["current_index"],
            current_manifest=paths["current_manifest"],
            candidate_path=candidate,
            pipeline_evidence_dir=evidence,
            timeout_seconds=args.timeout_seconds,
        )
        if args.command == TILE_DELETION_MODE:
            return execute_tile_deletion_mutation(**common)
        donor_args = dict(
            donor_map=args.donor_map,
            donor_index=paths["donor_index"],
            donor_manifest=paths["donor_manifest"],
        )
        if args.command == TILE_AREA_MODE:
            return execute_area_mutation(**common, plan=paths["plan"], **donor_args)
        if args.command == TILE_REPLACEMENT_MODE:
            return execute_tile_replacement_mutation(**common, **donor_args)
        if args.command == TILE_INSERTION_MODE:
            return execute_tile_insertion_mutation(**common, **donor_args)
        return execute_tile_type_conversion_mutation(**common, **donor_args)

    return args.command, args.current_map, direct_inputs, executor
