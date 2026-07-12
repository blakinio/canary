#!/usr/bin/env python3
"""CLI entry point for the atomic content deployment engine.

Safety policy, enforced here rather than in the library:

* ``--environment`` defaults to ``staging``. Deploying to ``production``
  additionally requires ``--confirm-production`` - there is no default or
  single flag that reaches production by accident.
* ``--dry-run`` performs every validation the real deploy would (source
  files exist and are within the source root, release id not already
  taken, releases root is a real provisioned directory) without writing
  anything or touching the active/previous symlinks.

This CLI only performs the mechanics (stage / switch / health-check /
rollback / manifest). It does not run the actual Canary binary yet - see
docs/systems/ai-content-deployment.md for the current scope and the planned
follow-up that wires in a real server smoke test before the switch.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from health_check import HealthCheckResult, make_pid_file_health_check
from release_manager import deploy


def _no_health_check(_release_dir: Path) -> HealthCheckResult:
    return HealthCheckResult(healthy=True, detail="no health check configured")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--source", required=True, type=Path, help="Directory containing the fully-reviewed content to deploy.")
    parser.add_argument("--releases-root", required=True, type=Path, help="Configured, pre-provisioned deployment root.")
    parser.add_argument("--release-id", required=True, help="Unique identifier for this release (e.g. a timestamp or content hash).")
    parser.add_argument("--environment", choices=["staging", "production"], default="staging")
    parser.add_argument("--confirm-production", action="store_true", help="Required in addition to --environment production.")
    parser.add_argument("--pid-file", type=Path, help="PID file to health-check after switching. Without this, the health check trivially passes - only use that for staging/dry runs.")
    parser.add_argument("--source-description", default="", help="Free-text note recorded in the manifest (e.g. task id, commit sha).")
    parser.add_argument("--manifest-output", type=Path, help="Where to write the JSON manifest. Defaults to <releases-root>/manifests/<release-id>.json")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.environment == "production" and not args.confirm_production and not args.dry_run:
        print("refusing production deployment: pass --confirm-production explicitly (or --dry-run to validate only)", file=sys.stderr)
        return 2

    health_checker = make_pid_file_health_check(args.pid_file) if args.pid_file else _no_health_check

    manifest = deploy(
        args.source,
        args.releases_root,
        args.release_id,
        health_checker,
        source_description=args.source_description,
        dry_run=args.dry_run,
    )

    manifest_output = args.manifest_output or (Path(args.releases_root) / "manifests" / f"{args.release_id}.json")
    if not args.dry_run:
        manifest.write(manifest_output)

    print(json.dumps(manifest.to_json(), indent=2, ensure_ascii=False))
    return 0 if manifest.outcome in {"deployed", "dry-run-ok"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
