# Configuration behavior model

## Load

1. Create a Lua state and open standard libraries.
2. Execute the configured Lua file; return failure when execution fails.
3. Load one-time identity and network keys only before the manager is marked loaded.
4. Load reloadable string, integer, boolean and floating-point keys through typed helpers.
5. Use the declared default when a key is absent or has the wrong Lua type, with a warning.
6. Load the OTC feature table or temporary default feature identifiers when the table is absent.

## Access

- Typed getters read the stored variant, cache successful values and return an empty/zero/false fallback with a warning for absent or mismatched keys.
- Feature checks read the enabled/disabled feature sets materialized during loading.

## Reload

1. Clear typed getter caches.
2. Re-run the load path.
3. Compare the SHA-1 of the previous and current MOTD and increment the MOTD number when it changed.

## Failure and uncertainty

- The selected source proves the control path, not the correctness or safety of any deployed configuration.
- It does not execute a server, validate controlled features or establish protocol/client behavior.
