# Canary Fork Agent Instructions

## Instruction order

1. This root `AGENTS.md`.
2. The nearest nested `AGENTS.md`, when present.
3. `docs/agents/**`.
4. Relevant system documentation under `docs/**`.
5. The active task record and linked ADRs.

When rules conflict, follow the more restrictive safety rule.

## Repository allowlist — highest priority

- Routine write operations are allowed only in `blakinio/canary`.
- `opentibiabr/canary` is read-only upstream.
- Never mutate upstream issues, pull requests, branches, tags, releases, files, workflows, comments, or reviews.
- Before every GitHub write, verify `repository_full_name` is exactly `blakinio/canary`.
- A valid PR has both base and head repositories equal to `blakinio/canary` and targets `main`.
- Treat an `upstream` Git remote as fetch-only.

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

## Git and commit policy

- Never push directly to `main`.
- Use a dedicated branch under `ai/`, `feat/`, `fix/`, `docs/`, `test/`, `refactor/`, `ci/`, or `chore/`.
- Track the matching remote branch, never `origin/main`.
- Prefer `git push origin HEAD:<branch>`.
- Use Conventional Commits and one logical change per PR.
- Use `--force-with-lease`, never plain `--force`, when history rewrite is necessary.

## Change scope and evidence

- Inspect existing Canary conventions before changing C++, Lua, XML, SQL, workflows, schemas, or configuration.
- Review `git diff --stat`, the full diff, and every changed path before readiness and merge.
- Record exact commands, outcomes, and validation commit SHA.
- Never claim CI, build, test, runtime, or migration success without evidence.
- Preserve failed approaches so another agent does not repeat them.

## AI content and binary safety

- AI tooling belongs under `tools/ai-agent/**` and `docs/ai-agent/**` unless the task requires another location.
- Generated output belongs under `artifacts/**` or an approved temporary directory.
- Default generation to dry-run and reviewable plans/diffs.
- Do not modify `.otbm`, `items.otb`, binary map assets, or production configuration unless explicitly authorized by the task.
- Map writing remains disabled until format detection, backup, round-trip validation, bounded-area checks, and rollback exist.
- New AI tools should be deterministic where practical and include tests.
- Prefer Python 3.12 standard library unless a dependency is justified.
- Never weaken tests to make CI pass.

## Data and identifier safety

- Distinguish definitions from references.
- Before allocating storage, action, unique, or item IDs, inspect definitions, registries, reservations, and active tasks.
- Never overwrite an active reservation silently.
- Missing monsters, NPCs, items, spells, handlers, migrations, or registrations must be surfaced, not invented.

## Build policy

- Use current CMake presets; do not guess build directories.
- Normal Windows validation:

```bat
cmake --preset windows-release
cmake --build --preset windows-release --target canary
```

- Run Windows builds from a Visual Studio Developer shell.
- Recover caches by removing only the verified affected preset directory under `build/`.
- When adding/removing/renaming C++ files, update CMake, `vcproj/canary.vcxproj`, and test CMake entries as applicable.
- Use `docs/agents/BUILD_TEST_MATRIX.md` for focused validation.

## Precompiled headers

- Common headers are supplied by `src/pch.hpp`.
- Do not add unguarded includes already supplied by the PCH.
- Preserve non-PCH builds with guarded local includes where needed.

## Lua shared userdata gate

- Treat Lua bindings storing `std::shared_ptr<T>` as high-risk ownership code.
- Read `docs/systems/lua-shared-userdata.md` before changing them.
- Use project shared/borrowed userdata traits and helpers.
- Do not combine shared-pointer userdata with weak or manually assigned metatables.

## Docker quickstart gate

- Keep CI/build Docker, development Docker, and user quickstart responsibilities separate.
- `docker/docker-compose.yml` keeps `login-server` as the client login service.
- MyAAC remains website/admin only.
- Public Canary Docker variables use `CANARY_*`.
- Quickstart uses the published runtime image and does not require local compilation.

## Cross-repository changes

When a Canary change affects OTClient protocol parsing, feature flags, protobuf, assets, identifiers, login, or payload-dependent UI:

- create or link an `OTC-*` task and one shared `OTS-*` coordination ID;
- record both PRs in each task and in `CROSS_REPO_CONTRACTS.md`;
- define compatibility, gates, rollout order, failure behavior, and validation on both sides;
- do not merge an `atomic-required` contract until both PRs satisfy their merge gates.

## PR communication

Agents may autonomously update and discuss their own PRs, reply to review feedback, and resolve threads after fixes. Do not comment on unrelated PRs unless needed for overlap/dependency coordination. All PR communication must be in English.
