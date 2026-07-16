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

## Incremental pull-request validation

Heavy validation may reuse only the immediate parent's latest successful same-workflow pull-request run when `tools/agents/ci_incremental_validation.py` proves the newest single-commit delta is non-impacting. Missing or non-successful parent evidence, an unresolvable delta, an impacting path, or a validation workflow/helper change fails closed to full applicable validation.

Current-head focused validation and stable `Required` aggregators remain active when heavy jobs are reused. Batch checkpoint and shared-document changes before the final gate. Apply the `ci:final-gate` PR label before the final task/checkpoint commit so that final `synchronize` event forces the full applicable validation set on the exact final head. Do not commit after that gate is green; a later commit invalidates the evidence and must run the final gate again.

## Known Windows release command

```bat
cmake --preset windows-release
cmake --build --preset windows-release --target canary
```

Record exact commands and commit SHA; one platform does not prove another.