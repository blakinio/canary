#!/usr/bin/env python3
from __future__ import annotations

import base64
import zlib
from pathlib import Path

# One-shot bootstrap; the workflow removes this file after validation.
FILES = (
    "quest_map_validation.py",
    "quest_map_validation_tool.py",
    "test_quest_map_validation.py",
)


def main() -> None:
    module = Path(__file__).resolve().parent
    payloads = module / ".quest_map_bootstrap"
    for name in FILES:
        encoded = (payloads / f"{name}.zlib.b64").read_text(encoding="ascii")
        (module / name).write_bytes(zlib.decompress(base64.b64decode(encoded)))


if __name__ == "__main__":
    main()
