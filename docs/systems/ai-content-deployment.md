# Atomic AI content deployment

## What this is

`tools/deploy/` is a small, dependency-free (stdlib only) Python engine that
takes a directory of already-reviewed content and deploys it as an
atomically-switchable "release", with automatic rollback on a failed
post-switch health check. It sits *after* the existing
`tools/ai-agent/` content-authoring pipeline (task validation → planning →
preview rendering → `build_promotion_handoff.py`'s human-approved,
manual-copy-only handoff bundle - see `docs/ai-agent/CONTENT_AUTHORING_PIPELINE.md`)
and *before* anything touches a real running server.

## Target pipeline and current scope

The full target pipeline this is part of:

1. generate content,
2. validate schemas,
3. validate dependencies/identifiers,
4. create a staging datapack,
5. run the real binary server against staging,
6. verify Lua/datapack loading,
7. smoke test startup,
8. prepare a release directory,
9. atomically switch the active version,
10. health check after the switch,
11. automatic rollback on a failed health check,
12. retain the previous version,
13. audit manifest with checksums.

Steps 1-3 already exist (`tools/ai-agent/`, unchanged by this work). **This
first PR builds steps 8-13 - the deployment mechanics** - as a standalone,
fully unit-tested engine that operates on any directory of files, deliberately
decoupled from step 4-7's real-server integration so each piece can be
reviewed independently. Steps 4-7 (building an actual staging datapack
overlay and running the real compiled `canary_server` binary against it,
reusing `.github/scripts/smoke_test_canary.py`'s already-proven
start/wait-for-online/check-clean-logs/stop sequence) are a planned,
separate follow-up that plugs into this engine as the health check run
*before* `deploy()` is called, not a replacement for anything here.

## How it works

```
releases_root/
  releases/
    <release_id>/           # fully-populated release; only ever appears atomically
  active   -> releases/<release_id>       # symlink, atomically repointed
  previous -> releases/<old_release_id>   # symlink, updated just before active moves
  manifests/
    <release_id>.json       # audit manifest: files, checksums, outcome
```

- **Staging** (`stage_release`) copies the source directory's content into a
  hidden temp directory under `releases_root/releases/`, then
  `os.replace()`s it into its final `<release_id>` name in one step. The
  final path either doesn't exist yet or is fully populated - there is no
  in-between state a health check or another process could observe.
- **Switching** (`switch_active`) creates a new symlink under a temp name and
  `os.replace()`s it onto `active` - again a single atomic rename. Nothing
  ever copies into `active` directly.
- **Health check** (`health_check.py`) is pluggable and defaults to a real
  process-liveness probe (`kill(pid, 0)` against a PID file), not a file
  existence check.
- **Rollback** (`rollback`) is idempotent: pointing `active` back at a
  release it's already pointing at is a reported no-op, not an error.
- **Retention** is "never delete a release directory" - there is no separate
  cleanup mechanism in this PR.
- Every path operation is checked against the configured `releases_root` (or
  the source directory, for staging) via `path_policy.resolve_within_root`,
  which resolves `..` and follows symlinks *before* checking containment, so
  it catches both traversal and symlink escape with one mechanism. Source
  content containing any symlink at all is rejected outright, rather than
  trying to distinguish "safe" from "unsafe" ones.
- `deploy()` orchestrates all of the above and always returns a manifest,
  including on failure - staging, switching, and health-check-with-rollback
  each have distinct, tested failure paths (see `test_release_manager.py`).

## Safety defaults

- `--dry-run` performs every validation a real deploy would, without writing
  anything or touching `active`/`previous`.
- `--environment` defaults to `staging`. Reaching `production` additionally
  requires `--confirm-production` - there is no default or single flag that
  reaches production by accident.
- Without `--pid-file`, the CLI's health check trivially passes. That's only
  appropriate for staging/dry-run validation of the mechanics themselves;
  the real-server follow-up will make a genuine health check a hard
  requirement before production is reachable at all.

## Usage

```bash
# Validate only, touches nothing:
python tools/deploy/run_deployment.py \
  --source /path/to/reviewed-content \
  --releases-root /path/to/deploy-root \
  --release-id 2026-07-12-abc123 \
  --dry-run

# Real deploy to staging, with a real health check:
python tools/deploy/run_deployment.py \
  --source /path/to/reviewed-content \
  --releases-root /path/to/deploy-root \
  --release-id 2026-07-12-abc123 \
  --pid-file /path/to/deploy-root/active/server.pid \
  --source-description "task-id or commit sha"

# Manual rollback:
python -c "
import sys; sys.path.insert(0, 'tools/deploy')
from release_manager import rollback
rollback('/path/to/deploy-root', 'previous-release-id')
"
```

## Known limitations

- No real server is started or checked by this PR's CLI by default - only a
  PID file, if you supply one. The real-server smoke test (steps 5-7) is a
  separate follow-up.
- No automatic pruning of old releases; disk usage grows with every deploy
  until an operator removes old `releases/<id>` directories by hand.
- Not wired into `tools/ai-agent/build_promotion_handoff.py`'s output format
  yet - this engine takes a plain source directory, which today means a
  human has already copied the approved content there per the handoff
  bundle's own manual integration steps.
