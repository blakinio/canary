# Canary Known Risks

- `opentibiabr/canary` is read-only; fork/contribute UI can target it accidentally.
- Branch protection may wait forever when a required nested check is not emitted; inspect PR #132 and exact check names.
- `.otbm`, `items.otb`, client assets, dumps, and generated reports may be destructive/proprietary; forbidden unless explicitly authorized with safe tooling.
- New C++ files must be registered in all maintained build entry points, including tracked Visual Studio projects.
- PCH-only includes can hide missing dependencies.
- Shared Lua userdata ownership mistakes can leak or double-own objects.
- Dynamic Lua registrations and OTBM-only identifiers cannot be guessed safely.
- Account-wide quest changes cross Lua, DB, schema, migration, config, administration, and concurrency.
- Deployment tooling must preserve path/symlink confinement, hashes, atomic switching, and rollback.
- Multi-channel and instance work overlap scheduler/map/player/session/persistence ownership assumptions.
- Open PRs can be superseded while still open; verify successor notes and current base/head.
