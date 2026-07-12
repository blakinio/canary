# Canary Repository Map

Navigation map, not an exhaustive inventory. Confirm current paths before editing.

| Area | Typical paths | Responsibility/cautions |
|---|---|---|
| Engine/runtime | `src/**` | C++ server, protocol, Lua bindings, database, configuration, map, services. |
| Instance architecture | `src/game/instance/**` | Existing manager and region pool; read catalogue/docs before extending. |
| Datapacks | `data/**`, `data-otservbr-global/**` | Scripts, XML, migrations, world definitions. Avoid invented IDs. |
| AI/map tools | `tools/ai-agent/**`, `docs/ai-agent/**` | Deterministic dry-run tools, schemas, review rules. Binary map writes restricted. |
| Deployment | `tools/deploy/**`, deploy workflows/docs | Canonical staging, manifests, atomic release/rollback. |
| Analytics | `tools/analytics/**`, analytics workflows/docs | Analytics validation, maintenance, reporting, hunt areas. |
| Account quests | `tools/account-quests/**`, related scripts/docs | Validation, migration, account-shared access. |
| Tests | `tests/**` | Unit/integration tests and focused CMake entries. |
| Build | CMake files, `CMakePresets.json`, `cmake/**`, `vcpkg.json`, `vcproj/**` | Use presets; maintain CMake and VS entries. |
| CI | `.github/workflows/**` | Required checks and subsystem workflows. Inspect active CI PRs first. |
| Docs | `docs/systems/**`, `docs/architecture/**` | Durable behavior, deployment, architecture, handoffs. |
| Agent memory | `AGENTS.md`, `docs/agents/**` | Coordination, catalogue, tasks, ADRs, changelog. |

## Discovery commands

```sh
find . -name AGENTS.md -print
rg -n "<symbol|config key|opcode|storage|module>" src data data-otservbr-global tools tests docs
rg -n "add_(executable|library)|target_sources|CANARY_BUILD_TESTS" CMakeLists.txt src tests cmake
find docs/agents/tasks/active -maxdepth 1 -type f -print
```
