from __future__ import annotations

import argparse
from pathlib import Path

from tibia_client_reference_manifest import (
    BUILD_EVIDENCE_STATES,
    DEFAULT_MAX_FILE_BYTES,
    ClientReferenceManifestError,
    build_manifest,
    write_manifest,
)


def _assignment(value: str, label: str) -> tuple[str, str]:
    key, separator, item = value.partition("=")
    if not separator or not key or not item:
        raise argparse.ArgumentTypeError(f"{label} must use ID=VALUE")
    return key, item


def _selected(value: str) -> tuple[str, str]:
    return _assignment(value, "--select")


def _generated(value: str) -> tuple[str, str]:
    return _assignment(value, "--generated-index")


def _metadata(value: str) -> tuple[str, str]:
    return _assignment(value, "--metadata")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build a deterministic provenance manifest for explicitly selected Tibia client reference files."
    )
    parser.add_argument("--package-root", type=Path, required=True)
    parser.add_argument("--reference-id", required=True)
    parser.add_argument("--package-label", required=True)
    parser.add_argument("--source-role", required=True)
    parser.add_argument("--observed-at", required=True)
    parser.add_argument("--client-build-evidence", choices=sorted(BUILD_EVIDENCE_STATES), required=True)
    parser.add_argument("--client-build")
    parser.add_argument("--client-build-conflict", action="append", default=[])
    parser.add_argument("--parser-revision", required=True)
    parser.add_argument("--select", type=_selected, action="append", default=[], metavar="ID=RELATIVE_PATH")
    parser.add_argument("--generated-index", type=_generated, action="append", default=[], metavar="ID=SHA256")
    parser.add_argument("--metadata", type=_metadata, action="append", default=[], metavar="KEY=VALUE")
    parser.add_argument("--max-file-bytes", type=int, default=DEFAULT_MAX_FILE_BYTES)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    try:
        manifest, selected_paths = build_manifest(
            package_root=args.package_root,
            reference_id=args.reference_id,
            package_root_label=args.package_label,
            source_role=args.source_role,
            observed_at=args.observed_at,
            client_build_evidence=args.client_build_evidence,
            client_build=args.client_build,
            client_build_conflicts=args.client_build_conflict,
            parser_revision=args.parser_revision,
            selected_inputs=args.select,
            generated_indexes=args.generated_index,
            package_metadata=args.metadata,
            max_file_bytes=args.max_file_bytes,
        )
        write_manifest(args.output, manifest, selected_paths=selected_paths, overwrite=args.overwrite)
    except (ClientReferenceManifestError, OSError, ValueError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
