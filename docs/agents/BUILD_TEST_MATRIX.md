# Canary Build and Test Matrix

Always verify current `CMakePresets.json` and workflows. Validation must be proportional to the changed paths, risk and current project milestone; do not compile merely because a commit or small step was created.

## Validation timing and escalation

- During a multi-step task, run cheap focused checks after each step: syntax, formatting, schema, generated-file consistency and directly affected unit tests.
- Defer compilation and other heavy validation until the end of a coherent milestone, phase or implementation package. A five-step OTBM package should normally compile once after the five steps form one reviewable result, not after every step.
- Compile earlier only when a step changes CMake/build manifests, source registration, dependencies, toolchains, generated compile inputs, public headers/ABI, or when later work requires a verified binary or compile breakage is a material risk.
- Documentation, task-checkpoint, comment, metadata and other clearly non-build-affecting commits do not require compilation.
- Run the full applicable final validation once on the exact final head before merge. Any later build-affecting commit invalidates that evidence; a later docs-only commit needs only the checks selected by the canonical incremental-validation rules.
- Record why a heavy build was run early or skipped when the choice is not obvious from changed paths.

| Change | Minimum local validation | Additional validation |
|---|---|---|
| Documentation/task records | Markdown/path review, `git diff --check` | Relevant docs/fast checks; no compilation |
| Python/OTBM tool | Focused unit tests and bytecode compilation | Dedicated workflow and broader tool suite at milestone completion; compile Canary only when compiled integration changed |
| Lua/XML/datapack | Validator/Lua tests and syntax/format checks | Runtime smoke when behavior changes; no C++ build unless compiled integration changed |
| C++ implementation | Focused compile/test at the end of the coherent implementation milestone | Required Linux plus affected Windows validation |
| CMake/dependency/toolchain/public header | Configure/build immediately enough to protect subsequent work | Clean or full affected-platform validation at milestone completion |
| DB/schema/migration | Import/parser, migration tests, rollback review | Temporary MariaDB integration and clean schema import |
| Protocol/cross-repo | Server tests plus linked OTClient validation | Compatible client/server integration |
| Deployment | Unit path/symlink/hash/rollback tests | Real Canary staging smoke |
| CI workflow | YAML validation and exact check-name analysis | Observe emitted checks on PR; build only when the workflow selects it |

## Canary macOS CI status

Canary macOS compilation is temporarily suspended. The reusable macOS workflow may remain in the repository for future re-enablement, but normal CI and the `Required` aggregator must not invoke or require it. Re-enabling macOS requires an explicit CI task that restores the caller, required-check logic and validation evidence.

## Incremental pull-request validation

Heavy validation may reuse only the immediate parent's latest successful same-workflow pull-request run when `tools/agents/ci_incremental_validation.py` proves the newest single-commit delta is non-impacting. Missing or non-successful parent evidence, an unresolvable delta, an impacting path, or a validation workflow/helper change fails closed to full applicable validation.

Current-head focused validation and stable `Required` aggregators remain active when heavy jobs are reused. Batch checkpoint and shared-document changes before the final gate. Apply the `ci:final-gate` PR label before the final task/checkpoint commit so that final `synchronize` event forces the full applicable validation set on the exact final head. Do not commit build-affecting changes after that gate is green; a later build-affecting commit must run the final gate again.

## Known Windows release command

```bat
cmake --preset windows-release
cmake --build --preset windows-release --target canary
```

Record exact commands and commit SHA; one platform does not prove another.