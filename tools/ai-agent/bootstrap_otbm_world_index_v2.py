#!/usr/bin/env python3
from __future__ import annotations

import base64
import zlib
from pathlib import Path

# One-shot branch bootstrap; the workflow removes this file after validation.
FILES = (
    "otbm_item_audit_scan.cpp",
    "otbm_world_index.py",
    "otbm_world_index_tool.py",
    "test_otbm_world_index.py",
)


def main() -> None:
    module = Path(__file__).resolve().parent
    payloads = module / ".otbm_world_bootstrap"
    for name in FILES:
        encoded = (payloads / f"{name}.zlib.b64").read_text(encoding="ascii")
        (module / name).write_bytes(zlib.decompress(base64.b64decode(encoded)))


if __name__ == "__main__":
    main()
