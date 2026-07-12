# Canary Build and Test Matrix

Always verify current `CMakePresets.json` and workflows.

| Change | Minimum local validation | Additional validation |
|---|---|---|
| Documentation | Markdown/path review, `git diff --check` | Relevant docs/fast checks |
| Python tool | Focused unit tests and bytecode compilation | Dedicated workflow and broader tool suite |
| Lua/XML/datapack | Validator/Lua tests and syntax/format checks | Runtime smoke when behavior changes |
| C++ | Appropriate preset build and focused tests | Required Linux plus affected Windows/macOS |
| DB/schema/migration | Import/parser, migration tests, rollback review | Temporary MariaDB integration and clean schema import |
| Protocol/cross-repo | Server tests plus linked OTClient validation | Compatible client/server integration |
| Deployment | Unit path/symlink/hash/rollback tests | Real Canary staging smoke |
| CI workflow | YAML validation and exact check-name analysis | Observe emitted checks on PR |

## Known Windows release command

```bat
cmake --preset windows-release
cmake --build --preset windows-release --target canary
```

Record exact commands and commit SHA; one platform does not prove another.
