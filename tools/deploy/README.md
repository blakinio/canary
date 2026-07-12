# Canary atomic content deployment

The deployment tools provide two layers:

- `run_deployment.py` — generic stage → atomic switch → health check → rollback;
- `run_canary_deployment.py` — assemble a complete datapack, run real Canary
  preflight, deploy atomically, then run Canary again from the published
  release.

Key modules:

- `release_manager.py` — release publication, switching and rollback;
- `canary_staging.py` — safe overlay assembly and real runtime smoke adapter;
- `manifest.py` — SHA-256 audit manifest;
- `path_policy.py` — deployment-root confinement and escape rejection.

See `docs/systems/ai-content-deployment.md` for the design and operator usage.

Run all deployment tests with:

```bash
python -m unittest discover -s tools/deploy -p "test_*.py" -v
```
