# Atomic AI content deployment

## Purpose

`tools/deploy/` turns reviewed content into an atomically switchable Canary
datapack release. The complete Canary path now performs both real-server
validation and filesystem-safe publication:

1. validate the AI-content task and generated files;
2. assemble a full staging datapack from a trusted base plus reviewed overlay;
3. start the real compiled Canary binary against staging;
4. verify datapack/Lua loading, online readiness and clean startup logs;
5. publish the complete release directory atomically;
6. atomically repoint `active`;
7. start Canary again from the published release;
8. roll back `active` automatically if that post-switch smoke fails;
9. retain previous releases and write a SHA-256 audit manifest.

The existing authoring pipeline under `tools/ai-agent/` remains responsible for
generation, schema/dependency checks and the human-reviewed promotion handoff.

## Components

### Generic release engine

`run_deployment.py` and `release_manager.py` implement the reusable mechanics:

- hidden same-filesystem staging directory;
- atomic release publication with `os.replace()`;
- atomic `active` and `previous` symlink updates;
- pluggable health check;
- automatic, idempotent rollback;
- immutable retained release directories;
- per-file SHA-256 manifest;
- dry-run and explicit production confirmation.

### Canary-aware deployment

`run_canary_deployment.py` adds the engine-specific gate:

- copies a trusted full datapack into a temporary workspace;
- applies a symlink-free reviewed overlay;
- removes the entire partial tree if assembly fails;
- reuses `.github/scripts/smoke_test_canary.py` for real startup validation;
- records preflight status and detail in manifest schema `1.1`;
- uses a second database name for post-switch validation;
- deploys only after preflight succeeds;
- runs the same real smoke against the published release.

`canary_staging.py` exposes the assembly and real-smoke helpers for tests and
other tooling.

## Release layout

```text
releases_root/
  releases/
    <release_id>/
  active   -> releases/<release_id>
  previous -> releases/<old_release_id>
  manifests/
    <release_id>.json
```

A release path is never visible half-populated. Content is copied to a hidden
temporary directory under `releases/` and renamed into place only after the
copy completes. `active` is switched by replacing a temporary symlink in one
filesystem operation.

## Safety guarantees

- `releases_root` must already exist and is resolved strictly.
- All release operations are confined to that root.
- Reviewed overlay content may not contain any symlink.
- Traversal and symlink escape are rejected.
- Partial datapack assembly is deleted on every copy/overlay exception.
- Production requires both `--environment production` and
  `--confirm-production`.
- Dry-run never changes `active`, `previous`, release directories or manifests.
  It may create and remove a temporary workspace and run the real preflight
  server because that is part of validation.
- A failed preflight never switches the active release.
- A failed post-switch smoke restores the previous active release when one
  exists.
- Rollback is idempotent.
- Releases are not automatically deleted.

## Real Canary deployment example

```bash
mkdir -p /srv/canary-content

python3 tools/deploy/run_canary_deployment.py \
  --source /srv/reviewed-overlay \
  --base-datapack data-canary \
  --releases-root /srv/canary-content \
  --release-id 2026-07-12-abc123 \
  --binary-path build/linux-release/bin/canary \
  --db-host 127.0.0.1 \
  --db-port 3306 \
  --db-user canary_smoke \
  --db-password '<secret>' \
  --db-name canary_content_validation \
  --login-port 7471 \
  --game-port 7472 \
  --status-port 7471 \
  --source-description 'TASK-123 commit abc123'
```

Production additionally requires:

```bash
  --environment production --confirm-production
```

The base datapack and binary paths may be relative to `--repo-root`. Relative
`--source`, `--workspace-root` and map-cache paths are also resolved from that
root.

## Manifest states

Manifest schema `1.1` includes:

- `preflightStatus` and `preflightDetail`;
- all released files with size and SHA-256;
- previous release id;
- switch status;
- post-switch health status and detail;
- rollback status;
- final outcome.

Important outcomes include:

- `failed-assembly`;
- `failed-preflight`;
- `failed-staging`;
- `failed-switch`;
- `deployed`;
- `rolled-back`;
- `failed-health-check-no-rollback-target`;
- `failed-health-check-rollback-failed`;
- `dry-run-ok`.

## CI validation

Two workflows cover the deployment system:

- `Content Deployment Pipeline` runs unit tests and generic CLI smoke tests,
  including traversal, symlink, dry-run and rollback failures.
- `Canary Staging Deployment` builds the real Linux Canary binary, assembles a
  datapack with an overlay, runs preflight, performs the atomic switch, runs a
  second real server smoke from the published release and validates the
  resulting manifest.

The repository-wide CI also emits the required Linux release check for this
workflow-only change, so branch protection cannot remain waiting for a check
that was intentionally skipped.

## Operational integration

The deployment command intentionally starts short-lived validation processes
and stops them cleanly. It does not replace the host's long-running process
supervisor. After a successful production deployment, systemd, Docker,
Kubernetes or another operator-controlled service must restart/reload the
long-lived server so its configured datapack path resolves through `active`.

That supervisor step must not copy files into `active`; it should only consume
the already-published release.

## Remaining limitation

The promotion handoff generated by `tools/ai-agent/build_promotion_handoff.py`
is not yet converted automatically into the plain overlay directory consumed
by `run_canary_deployment.py`. Until that adapter is added, the reviewed file
mapping must be materialized into an overlay by the operator or orchestration
layer.

Old release pruning is also deliberately manual so rollback targets are never
removed implicitly.
