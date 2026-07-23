from __future__ import annotations

import argparse
from pathlib import Path

from tibia_staticdata_reference_index import (
    DEFAULT_MAX_DECOMPRESSED_BYTES,
    DEFAULT_MAX_MANIFEST_BYTES,
    DEFAULT_MAX_RECORDS,
    DEFAULT_MAX_SOURCE_BYTES,
    StaticDataReferenceError,
    build_index,
    write_index,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build a deterministic, read-only Tibia StaticData reference index from one explicit source file "
            "whose exact size and SHA-256 are pinned by a stable client-reference manifest."
        )
    )
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--input-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-source-bytes", type=int, default=DEFAULT_MAX_SOURCE_BYTES)
    parser.add_argument("--max-decompressed-bytes", type=int, default=DEFAULT_MAX_DECOMPRESSED_BYTES)
    parser.add_argument("--max-manifest-bytes", type=int, default=DEFAULT_MAX_MANIFEST_BYTES)
    parser.add_argument("--max-records", type=int, default=DEFAULT_MAX_RECORDS)
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
            max_records=args.max_records,
        )
        write_index(
            args.output,
            payload,
            protected_inputs=protected_inputs,
            overwrite=args.overwrite,
        )
    except (StaticDataReferenceError, OSError, ValueError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
