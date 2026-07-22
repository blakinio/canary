from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

from otbm_evidence_gateway import EvidenceGatewayError, build_evidence_bundle, load_manifest


def _write(path: Path, payload: dict, *, overwrite: bool, manifest_path: Path) -> None:
    target = path.expanduser().resolve()
    manifest = manifest_path.expanduser().resolve()
    if path.is_symlink() or target.is_symlink():
        raise EvidenceGatewayError(f"output must not be a symlink: {path}")
    if target == manifest or (target.exists() and os.path.samefile(target, manifest)):
        raise EvidenceGatewayError("output collides with manifest input")
    if target.exists() and not target.is_file():
        raise EvidenceGatewayError(f"output exists but is not a regular file: {target}")
    if target.exists() and not overwrite:
        raise EvidenceGatewayError(f"output already exists: {target}; pass --overwrite")
    target.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if not overwrite:
        fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text)
        return
    fd, temp_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=target.parent)
    temp = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp, target)
    finally:
        temp.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compose compact exact OTBM evidence extracts from existing JSON reports.")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    try:
        manifest = load_manifest(args.manifest)
        bundle = build_evidence_bundle(args.manifest, manifest)
        _write(args.output, bundle, overwrite=args.overwrite, manifest_path=args.manifest)
    except (EvidenceGatewayError, FileNotFoundError, OSError, ValueError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
