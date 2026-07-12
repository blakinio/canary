# Atomic content deployment engine

Stage → atomic switch → health check → automatic rollback, with an audit
manifest and constant-time-safe path handling scoped to a single configured
deployment root.

See `docs/systems/ai-content-deployment.md` for the full design, current
scope, and usage. Run the tests with:

```bash
python -m unittest discover -s tools/deploy -p "test_*.py" -v
```
