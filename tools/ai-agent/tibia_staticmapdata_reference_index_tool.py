from __future__ import annotations

import argparse
from pathlib import Path

from tibia_staticmapdata_reference_index import (
    DEFAULT_MAX_DECLARED_CELLS,
    DEFAULT_MAX_DECOMPRESSED_BYTES,
    DEFAULT_MAX_HOUSES,
    DEFAULT_MAX_MANIFEST_BYTES,
    DEFAULT_MAX_ROWS,
    DEFAULT_MAX_SOURCE_BYTES,
    DEFAULT_MAX_TILE_RECORDS,
    StaticMapDataReferenceError,
    build_index,
    write_index,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build a deterministic, read-only Tibia StaticMapData house-layout reference index from one explicit "
            "source file whose exact size and SHA-256 are pinned by a stable client-reference manifest."
        )
    )
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--input-id", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-source-bytes", type=int, default=DEFAULT_MAX_SOURCE_BYTES)
    parser.add_argument("--max-decompressed-bytes", type=int, default=DEFAULT_MAX_DECOMPRESSED_BYTES)
    parser.add_argument("--max-manifest-bytes", type=int, default=DEFAULT_MAX_MANIFEST_BYTES)
    parser.add_argument("--max-houses", type=int, default=DEFAULT_MAX_HOUSES)
    parser.add_argument("--max-rows", type=int, default=DEFAULT_MAX_ROWS)
    parser.add_argument("--max-tile-records", type=int, default=DEFAULT_MAX_TILE_RECORDS)
    parser.add_argument("--max-declared-cells", type=int, default=DEFAULT_MAX_DECLARED_CELLS)
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
            max_houses=args.max_houses,
            max_rows=args.max_rows,
            max_tile_records=args.max_tile_records,
            max_declared_cells=args.max_declared_cells,
        )
        write_index(
            args.output,
            payload,
            protected_inputs=protected_inputs,
            overwrite=args.overwrite,
        )
    except (StaticMapDataReferenceError, OSError, ValueError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
