from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

from otbm_change_risk import ChangeRiskError, build_change_risk_report, load_input, load_policy


def _input(path: Path, label: str) -> Path:
    source = path.expanduser().resolve()
    if path.is_symlink() or not source.is_file():
        raise ChangeRiskError(f"{label} must be an existing non-symlink regular file: {path}")
    return source


def _write(path: Path, payload: dict, *, overwrite: bool, inputs: list[Path]) -> None:
    target = path.expanduser().resolve()
    if path.is_symlink() or target.is_symlink():
        raise ChangeRiskError(f"output must not be a symlink: {path}")
    for source in inputs:
        if source == target or (target.exists() and os.path.samefile(source, target)):
            raise ChangeRiskError(f"output collides with input: {source}")
    if target.exists() and not target.is_file():
        raise ChangeRiskError(f"output exists but is not a regular file: {target}")
    if target.exists() and not overwrite:
        raise ChangeRiskError(f"output already exists: {target}; pass --overwrite")
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
    parser = argparse.ArgumentParser(description="Classify deterministic OTBM change risk from explicit evidence-backed factors.")
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    try:
        policy_path = _input(args.policy, "policy")
        input_path = _input(args.input, "risk input")
        report = build_change_risk_report(load_policy(policy_path), load_input(input_path))
        _write(args.output, report, overwrite=args.overwrite, inputs=[policy_path, input_path])
    except (ChangeRiskError, FileNotFoundError, OSError, ValueError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
