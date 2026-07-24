from __future__ import annotations

import argparse
from pathlib import Path

from tibia_proficiency_reference_index import (
    DEFAULT_MAX_DECOMPRESSED_BYTES,
    DEFAULT_MAX_LEVELS,
    DEFAULT_MAX_MANIFEST_BYTES,
    DEFAULT_MAX_PERKS,
    DEFAULT_MAX_PROFICIENCIES,
    DEFAULT_MAX_SOURCE_BYTES,
    ProficiencyReferenceError,
    build_index,
    write_index,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build a deterministic, read-only Tibia proficiency definition reference index from one explicit "
            "JSON source whose exact size and SHA-256 are pinned by a stable client-reference manifest."
        )
    )
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--input-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-source-bytes", type=int, default=DEFAULT_MAX_SOURCE_BYTES)
    parser.add_argument("--max-decompressed-bytes", type=int, default=DEFAULT_MAX_DECOMPRESSED_BYTES)
    parser.add_argument("--max-manifest-bytes", type=int, default=DEFAULT_MAX_MANIFEST_BYTES)
    parser.add_argument("--max-proficiencies", type=int, default=DEFAULT_MAX_PROFICIENCIES)
    parser.add_argument("--max-levels", type=int, default=DEFAULT_MAX_LEVELS)
    parser.add_argument("--max-perks", type=int, default=DEFAULT_MAX_PERKS)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    try:
        payload, protected_inputs = build_index(
            manifest_path=args.manifest,
            source_path=args.source,
            input_id=args.input_id,
            max_source_bytes=args.max_source_bytes,
            max_decompressed_bytes=args.max_decompressed_bytes,
            max_manifest_bytes=args.max_manifest_bytes,
            max_proficiencies=args.max_proficiencies,
            max_levels=args.max_levels,
            max_perks=args.max_perks,
        )
        write_index(
            args.output,
            payload,
            protected_inputs=protected_inputs,
            overwrite=args.overwrite,
        )
    except (ProficiencyReferenceError, OSError, ValueError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
