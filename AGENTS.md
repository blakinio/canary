# Canary Fork Agent Instructions

## Instruction order

1. This root `AGENTS.md`.
2. The nearest nested `AGENTS.md`, when present.
3. `docs/agents/**`.
4. Relevant system documentation under `docs/**`.
5. The active task record and linked ADRs.

When rules conflict, follow the more restrictive safety rule.

## Repository Allowlist — Highest Priority

- The only repository where write operations are allowed is `blakinio/canary`.
- Treat `opentibiabr/canary` as read-only upstream.
- Never create, update, reopen, close, comment on, label, review, or merge a pull request in `opentibiabr/canary`.
- Never create issues, branches, tags, releases, commits, or workflow changes in `opentibiabr/canary`.
- Never perform a GitHub mutation in another repository unless the user explicitly names and authorizes it.
- Before every GitHub write operation, verify that `repository_full_name` is exactly `blakinio/canary`.
- If the target repository differs, stop before the write and report a repository safety violation.
- A pull request is valid only when both its base repository and head repository are `blakinio/canary`.
- Do not use GitHub's fork `Contribute` flow when it targets upstream.
- Treat the `upstream` remote as fetch-only. Never push to it.

## Mandatory startup protocol

Before implementation:

1. Read this file and `docs/agents/README.md`.
2. Read `docs/agents/ACTIVE_WORK.md` and inspect all open PRs; GitHub state is authoritative when the index is stale.
3. Read `docs/agents/MODULE_CATALOG.md` and search the repository for reusable code before designing a new module.
4. Read `docs/agents/REPOSITORY_MAP.md`, `KNOWN_RISKS.md`, and `BUILD_TEST_MATRIX.md`.
5. Read relevant contracts in `docs/agents/CROSS_REPO_CONTRACTS.md`.
6. Open active task records whose paths, modules, identifiers, or contracts overlap the task.
7. Check `git status --short --branch`, `git branch -vv`, `git remote -v`, and `git worktree list`.
8. Record uncertainty instead of inventing repository or cross-repository state.

## Work visibility and reuse — mandatory

Every agent must make its work discoverable:

- create `docs/agents/tasks/active/CAN-YYYYMMDD-short-slug.md` before substantial implementation;
- declare `owned_paths`, `modules_touched`, `reuses`, `depends_on`, `blocks`, and cross-repository task IDs;
- publish the branch and open a draft PR early;
- add the task to `docs/agents/ACTIVE_WORK.md` in the same early commit when practical;
- update the task record after discoveries, decisions, failures, tests, review changes, and before context exhaustion;
- update `docs/agents/MODULE_CATALOG.md` in the same PR that adds a reusable module, changes a public interface, deprecates a module, or introduces a new integration point;
- update `docs/agents/CHANGELOG.md` for completed behavior-level or architecture-level changes;
- create an ADR under `docs/agents/decisions/` for decisions that outlive one task.

Before creating a helper, service, manager, parser, deployment tool, Lua library, protocol abstraction, or test utility, search the module catalogue, open PRs, task records, and repository. Prefer reuse or extension. If reuse is rejected, record the concrete reason.

A new agent must be able to continue from Git, the PR, and the task record without the previous chat.

## Multi-agent concurrency

- One agent uses one branch and one worktree.
- Never share a branch or worktree between agents.
- `owned_paths` are advisory locks; resolve overlaps before editing.
- Do not perform unrelated cleanup or broad refactors.
- Edit shared indexes narrowly and resolve conflicts from current `main`.

## Autonomous delivery policy

Agents are expected to finish routine repository work end to end without waiting for approval at each step. Default workflow:

1. inspect repository and open PR state;
2. claim the task and affected paths;
3. create a branch and task record;
4. implement the smallest complete change;
5. run relevant validation;
6. create or update the PR;
7. inspect CI results and logs;
8. fix root causes and repeat until required checks pass;
9. resolve addressed review threads and update the PR body;
10. mark ready and squash-merge.

Agents may create branches, commits and PRs; update and discuss their own PRs; rerun a failed job once when it may be transient; repair CI; enable auto-merge; and merge their own PR without separate user confirmation.

### Autonomous merge gate

Merge only when all are true:

- base/head repositories are the approved user-owned repository;
- base is `main` and head is a task branch;
- the full changed-file list and diff were reviewed and contain no unrelated or forbidden files;
- task acceptance criteria are satisfied;
- required local checks ran, or the exact unavailable environment is documented;
- all required GitHub checks pass on the current head;
- the PR is mergeable with no unresolved requested changes or review threads;
- no blocker, cross-repository ordering hold, migration hold, or manual production gate remains;
- task record, module catalogue, changelog, docs, and compatibility notes are current when applicable.

Use squash merge unless repository policy requires another method. Never bypass branch protection, dismiss valid failures, weaken tests, remove safety checks, or mark failing checks successful.

### CI repair loop

When CI fails:

1. identify workflow, job, step, commit SHA, and exact error;
2. decide whether the cause is the PR, stale base, CI configuration, or external infrastructure;
3. inspect logs before rerunning;
4. fix the root cause in the same PR when it belongs to the task;
5. use a separate narrow PR when an unrelated CI repair would obscure the change;
6. rerun only failed jobs when appropriate;
7. record failure and fix in the task record.

A second identical failure must be investigated, not repeatedly rerun. Do not silence, skip, loosen, or delete a check to obtain green CI.

### Mandatory stop conditions

Stop automatic merge and document the blocker for:

- any write to `opentibiabr/*`;
- secrets, private data, proprietary assets, database dumps, or credentials;
- destructive production migration without tested rollback;
- production deployment or irreversible external action outside the repository PR;
- unresolved overlapping path ownership;
- an `atomic-required` cross-repository contract without both sides ready;
- forbidden binary/map asset changes without explicit authorization and safety tooling.

## Pull Request Safety

- Never push directly to `main`.
- Use a dedicated branch for every task. Prefer branch names under `ai/`, `feat/`, `fix/`, `docs/`, `test/`, `refactor/`, `ci/`, or `chore/`.
- Pull requests must target `blakinio/canary:main`.
- Create draft PRs early for discoverability; mark them ready after acceptance criteria and local validation are complete.
- Agents may autonomously merge only after the autonomous merge gate is satisfied.
- Before creating a pull request, perform and report this preflight:
  - target repository: `blakinio/canary`
  - base branch: `main`
  - head repository: `blakinio/canary`
  - head branch: current working branch
  - upstream target: `NO`
- After creating a pull request, verify its URL begins with `https://github.com/blakinio/canary/pull/`.
- If a pull request URL points to any other repository, close it immediately and report the mistake.

## AI Content Project Safety

- The AI tooling lives under `tools/ai-agent/**` and `docs/ai-agent/**` unless a task explicitly requires another location.
- Keep generated content in `artifacts/**` or another explicitly approved temporary output directory.
- Do not write generated previews directly into an active datapack.
- Do not modify `.otbm` files.
- Do not modify `items.otb`.
- Do not create or replace binary map assets.
- Do not change production server configuration unless explicitly requested.
- Content generation must default to `dry-run` and produce a reviewable plan or diff.
- Any future map-writing feature must remain disabled until format detection, backup, round-trip validation, and bounded-area checks are implemented.
- New AI-agent tools must be deterministic where practical and must include unit tests.
- Prefer Python 3.12 standard-library implementations unless a dependency is clearly justified.
- Do not weaken or remove existing tests merely to make CI pass.

## Data and Identifier Safety

- Distinguish identifier definitions from references. Reuse is not automatically a conflict when it is only a reference.
- Before proposing storage, action ID, unique ID, or item ID ranges, inspect the generated registry and active reservations.
- Never overwrite an active reservation silently.
- Item IDs that require `items.xml` or `items.otb` changes must be reported as manual integration work unless explicitly approved.
- Missing monsters, NPCs, items, spells, or event registrations must be surfaced as warnings or blockers rather than silently invented.

## Change Scope and Validation

- Inspect existing Canary conventions before generating Lua, XML, C++, workflow, schema, SQL, or configuration changes.
- Keep changes limited to the user-requested scope.
- Do not perform unrelated cleanup or broad refactors.
- Review `git diff --stat`, the full diff, and the full changed-file list before readiness and merge.
- Explicitly confirm that no forbidden paths were changed:
  - `**/*.otbm`
  - `**/items.otb`
  - active datapack content unless requested
  - production secrets or credentials
- Run relevant tests and report exact commands/outcomes honestly.
- Do not claim CI passed unless the corresponding workflow result was verified on the current head.

## Secrets and Sensitive Data

- Never commit tokens, passwords, private keys, connection strings, cookies, or personal data.
- Treat `.env`, secret configuration, database dumps, backups, and private logs as sensitive.
- If sensitive data is discovered, stop and report it without reproducing the secret in output or comments.
- Do not post repository comments or reviews containing local paths, credentials, internal URLs, or private diagnostic data.

## Git Safety

- Before committing or pushing, always check `git status --short --branch` and `git branch -vv`.
- Never push directly to `origin/main`, including from the local `main` branch.
- A working branch must not track `origin/main` unless the current branch is exactly `main`.
- For feature/fix branches, the upstream must point to the same remote branch name.
- If a branch tracks the wrong upstream:
  - `git branch --unset-upstream <branch>`
  - then publish with `git push -u origin <branch>` only when appropriate.
- Prefer explicit push targets: `git push origin HEAD:<branch>`.
- The repository may allow bypassing main protections, so the direct-push check is mandatory.
- Before rewriting published history, check remote state and use `--force-with-lease`, never plain `--force`.

## Commit Policy

- Use Conventional Commit style: `<type>(optional-scope): <summary>`.
- Preferred types: `feat`, `fix`, `perf`, `refactor`, `test`, `docs`, `build`, `ci`, `chore`, `revert`.
- Keep titles concise, imperative, lowercase after the type, and without a trailing period.
- Use a scope when it adds context.
- For release-only changes, use `chore: update release version to X.Y.Z`.
- Do not mix unrelated changes in the same commit.

## Build Policy

- Compile when a change is critical, complex, or likely to break compilation. Avoid wasteful builds for clearly non-build-affecting docs/scripts unless they add validation value.
- Use the correct known workflow instead of guessing commands or creating new build trees.
- When adding/removing/renaming C++ source/header files, update every maintained build entry point, normally relevant `CMakeLists.txt`, `vcproj/canary.vcxproj`, and test CMake files.
- Before building on Windows, inspect `CMakePresets.json`, `CMakeLists.txt`, existing solutions, and preset caches.
- Prefer CMake presets over generated Visual Studio solutions unless explicitly required or unusable.
- Prefer normal release validation:

```bat
cmake --preset windows-release
cmake --build --preset windows-release --target canary
```

- Run Windows builds from a Visual Studio Developer Command Prompt or Developer PowerShell.
- Initialize `VsDevCmd.bat` when needed; ensure `cl.exe` and Ninja are available.
- If Ninja is absent, use the copy bundled with Visual Studio CMake tools instead of switching generators.
- Treat `CMakeCache.txt`, `CMakeFiles/`, `build.ninja`, `.ninja_deps`, `.ninja_log`, `cmake_install.cmake`, `compile_commands.json`, `vcpkg-manifest-install.log`, and `VSInheritEnvironments.txt` as active-cache markers.
- If compiler variables, `CMAKE_MAKE_PROGRAM`, or cache compatibility fail, remove only the affected verified directory under `build/` and rerun the same preset.
- Do not switch from presets to a generated `.sln` merely because configure failed.
- Use `docs/agents/BUILD_TEST_MATRIX.md` for focused validation.

## Precompiled Header Policy

- The project uses `src/pch.hpp` for common standard/library headers.
- Do not add unguarded standard/library includes already provided by `src/pch.hpp`.
- For non-PCH builds, wrap local fallback includes:

```cpp
#ifndef USE_PRECOMPILED_HEADERS
	#include <memory>
#endif
```

- Add broadly used headers to `src/pch.hpp` and retain guarded local fallbacks where needed.

## Lua Shared Userdata Gate

- Treat Lua bindings that store `std::shared_ptr<T>` in userdata as high-risk ownership code.
- Before changing shared userdata bindings, read `docs/systems/lua-shared-userdata.md`.
- New shared userdata types must define `LuaUserdataTraits<T>::name` and use `Lua::registerSharedClass<T>`, `Lua::pushSharedUserdata<T>`, or `Lua::pushBorrowedSharedUserdata<T>`.
- Do not add new uses of `Lua::pushUserdata<T>(..., std::shared_ptr<T>)` followed by manual `Lua::setMetatable`.
- Do not use `Lua::setWeakMetatable` for userdata storing `std::shared_ptr<T>`; it removes `__gc` and can leak the object.
- Do not wrap borrowed objects as `std::shared_ptr<T>(&object)` without a no-op deleter. Prefer `Lua::pushBorrowedSharedUserdata<T>`.
- Run and investigate every match:

```sh
rg -n "pushUserdata<.*std::shared_ptr|setWeakMetatable|std::shared_ptr<[^>]+>\(&" src/lua
rg -n "registerSharedClass\(L," src/lua
```

## Docker Quickstart Policy

- The Docker quickstart is intended for non-expert users to run a local Canary stack with minimal setup.
- Keep CI/build Docker, local development Docker, and user-facing quickstart Docker separate unless a change documents why they overlap.
- `docker/docker-compose.yml` must keep `login-server` as the default client login webservice.
- Do not point clients to MyAAC `login.php`.
- The MyAAC quickstart image must not include or expose `login.php`; MyAAC is website/admin only.
- Default client login URL: `http://localhost:8088/login`.
- Default web/admin URL: `http://localhost:8080`.
- MyAAC must build from the `slawkens/myaac` `develop` branch unless a compatibility reason is documented.
- Public Docker env vars use `CANARY_*`; avoid new public `MYSQL_*`, `OT_*`, or raw Lua config variable names.
- Quickstart must use the published Canary runtime image and must not require local compilation.

## Cross-repository changes

When a Canary change affects OTClient protocol parsing, feature flags, protobuf, assets, identifiers, login, or payload-dependent UI:

- create or link an `OTC-*` task and one shared `OTS-*` coordination ID;
- record both PRs in each task and in `docs/agents/CROSS_REPO_CONTRACTS.md`;
- define compatibility, capability/version gates, rollout order, one-sided failure behavior, and validation on both sides;
- do not merge an `atomic-required` contract until both PRs satisfy their merge gates.

## PR Communication Policy

- Agents may autonomously update and discuss their own PRs, reply to review feedback, and resolve threads after fixes.
- Do not comment on unrelated PRs unless needed to coordinate overlapping paths or dependencies.
- All PR comments and reviews must be in English.
