# Canary Fork Agent Instructions

## Instruction order

1. This root `AGENTS.md`.
2. The nearest nested `AGENTS.md`, when present.
3. `docs/agents/REPOSITORY_MAP.md` and `docs/agents/CONTEXT_ROUTING.md`.
4. The active task checkpoint and live PR for the current task, when present.
5. Only the task-routed documentation and source evidence required by `CONTEXT_ROUTING.md`.

When rules conflict, follow the more restrictive safety rule.

## Repository Allowlist — Highest Priority

- The only repository where write operations are allowed is `blakinio/canary`.
- Treat `opentibiabr/canary` as read-only upstream.
- Never create, update, reopen, close, comment on, label, review, merge, branch, tag, release, commit, or change workflows in `opentibiabr/canary`.
- Never perform a GitHub mutation in another repository unless the user explicitly names and authorizes it.
- Before every GitHub write operation, verify that `repository_full_name` is exactly `blakinio/canary`.
- A pull request is valid only when both its base repository and head repository are `blakinio/canary`.
- Do not use GitHub's fork `Contribute` flow when it targets upstream.
- Treat the `upstream` remote as fetch-only. Never push to it.

## Mandatory lean startup protocol

Before implementation:

1. Read this file.
2. Read `docs/agents/REPOSITORY_MAP.md` and `docs/agents/CONTEXT_ROUTING.md`.
3. If continuing existing work, read its active task `## Context checkpoint` and current live PR/head before any broad discovery.
4. Classify the task into one or more routes from `CONTEXT_ROUTING.md` and load only the matching documentation.
5. Search active task records and open PRs narrowly for overlapping paths, modules, identifiers, or contracts. Do not preload all tasks or all PRs.
6. Search `MODULE_CATALOG.md`, `KNOWN_RISKS.md`, `BUILD_TEST_MATRIX.md`, and `CROSS_REPO_CONTRACTS.md` before opening them in full; read only matching entries/sections unless the task genuinely spans many systems.
7. Search the repository for reusable code before designing a new reusable module.
8. Check `git status --short --branch`, `git branch -vv`, `git remote -v`, and `git worktree list` when a local checkout is available.
9. Record uncertainty instead of inventing repository or cross-repository state.

Do not recursively follow documentation links without evidence that they are relevant to the current task.

## Low-noise progress and preflight reuse — mandatory

- Run the full lean startup preflight once per bounded task or continuation session. After that, verify only the Git/PR/CI/files whose state may have changed.
- Repeat a full preflight only after a material external repository-state change, a long interruption/session replacement, or evidence that the checkpoint and live state conflict.
- Do not narrate routine file reads, searches, tool calls, commands, or unchanged checks to the user.
- Send a user-facing progress update only for a material milestone, a blocker, a required user decision, or a material change in scope/risk. Do not send repetitive "still working" messages.
- Keep progress updates to at most three short sentences and prefer exact identifiers over pasted logs, diffs, or command transcripts.
- When the next action is safe and autonomous, continue without waiting for acknowledgement.

## Context pressure and continuation — mandatory

- Chat history is disposable and never authoritative.
- The active task record, Git state, live PR and deterministic evidence must be sufficient for a new agent to continue without the previous conversation.
- Follow `docs/agents/CONTEXT_HANDOFF.md` when the session becomes slow, context grows materially, the agent starts rereading or repeating work, earlier facts become difficult to retain, or the context window is approaching exhaustion.
- Maintain a compact `## Context checkpoint` in every substantial active task.
- Update the checkpoint after material discoveries, proven/rejected hypotheses, patches, test/CI changes, review changes, head changes, blockers, and before context exhaustion.
- When context pressure appears: stop broad exploration, verify current Git/PR state, write the checkpoint, preserve coherent work, record uncommitted paths if any, and leave exactly one concrete `next_action`.
- A continuation agent starts from root `AGENTS.md`, `REPOSITORY_MAP.md`, `CONTEXT_ROUTING.md`, the checkpoint, current Git state and current PR. It must not reconstruct state from old chat history.
- Use evidence states consistently: `PROVEN`, `DERIVED`, `UNKNOWN`, `CONFLICT`. Never convert `UNKNOWN` into an assumption.

## Work visibility and reuse — mandatory

Every agent must make substantial work discoverable:

- create `docs/agents/tasks/active/CAN-YYYYMMDD-short-slug.md` before substantial implementation;
- declare owned paths, modules touched, reuse, dependencies, blockers, and cross-repository task IDs;
- publish the branch and open a draft PR early;
- do not manually edit `docs/agents/ACTIVE_WORK.md` from a normal feature/fix/docs task branch;
- treat the individual task file and live draft PR as the source of truth;
- update `MODULE_CATALOG.md` only when adding/changing/deprecating a reusable interface or integration point;
- update `CHANGELOG.md` for completed behavior-level or architecture-level changes;
- create an ADR for decisions that outlive one task.

Before creating a helper, service, manager, parser, deployment tool, Lua library, protocol abstraction, or test utility, search the module catalogue, open PRs, task records, and repository. Prefer reuse or extension. If reuse is rejected, record the concrete reason.

## Multi-agent concurrency

- One agent uses one branch and one worktree.
- Never share a branch or worktree between agents.
- `owned_paths` are advisory locks; resolve overlaps before editing.
- Do not perform unrelated cleanup or broad refactors.
- Do not use `ACTIVE_WORK.md` as a writable shared lock or per-PR checklist.
- If an existing PR conflicts only in `ACTIVE_WORK.md`, take current `main` for that file and preserve the PR's own task record.
- Edit other shared indexes narrowly and resolve conflicts from current `main`.

## Autonomous delivery policy

Default workflow:

1. inspect current repository/task/PR state using the lean startup protocol;
2. claim the task and affected paths;
3. create a branch and task record;
4. implement the smallest complete change;
5. run relevant validation;
6. create or update the PR;
7. inspect CI results and logs;
8. fix root causes and repeat until required checks pass;
9. resolve addressed review threads and update the PR body;
10. mark ready and squash-merge when the merge gate is satisfied.

Agents may create branches, commits and PRs; update and discuss their own PRs; rerun a failed job once when it may be transient; repair CI; enable auto-merge; and merge their own PR without separate user confirmation.

### Autonomous merge gate

Merge only when all are true:

- base/head repositories are the approved user-owned repository;
- base is `main` and head is a task branch;
- the full changed-file list and diff contain no unrelated or forbidden files;
- acceptance criteria are satisfied;
- required local checks ran, or the exact unavailable environment is documented;
- all required GitHub checks pass on the current head;
- the PR is mergeable with no unresolved requested changes or review threads;
- no blocker, ownership conflict, cross-repository ordering hold, migration hold, or manual production gate remains;
- task record and relevant catalogue/changelog/docs/contracts are current.

Use squash merge unless repository policy requires another method. Never bypass branch protection, dismiss valid failures, weaken tests, remove safety checks, or mark failing checks successful.

### Incremental validation and final-head gate

- Heavy PR validation may reuse evidence only when the canonical incremental-validation helper proves the newest single-commit delta is non-impacting for that workflow and the immediate parent's latest same-workflow pull-request run completed successfully.
- Missing, failed, cancelled or in-progress parent evidence; an unresolved or empty delta; an impacting path; or a validation workflow/helper change fails closed to full applicable validation.
- Reuse may skip expensive build/runtime jobs, but current-head focused validation and stable required-check aggregators must remain active and fail closed.
- Batch task checkpoint and shared-document mutations instead of committing after every evidence update.
- Before the final task/checkpoint commit, apply the PR label `ci:final-gate`. The final commit's normal `pull_request synchronize` event must force the full applicable validation set on that exact final head.
- Do not create a commit after a green final-head gate. Any later commit invalidates the final evidence and must pass the final gate again before merge.

### CI repair loop

When CI fails:

1. identify workflow, job, step, current commit SHA and exact error;
2. inspect logs/artifacts before rerunning;
3. classify the cause as PR, stale base, CI configuration, or external infrastructure;
4. fix the root cause in the same PR when it belongs to the task;
5. use a separate narrow PR when an unrelated CI repair would obscure the change;
6. rerun only failed jobs when appropriate;
7. record failure and fix in the task checkpoint.

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
- Use a dedicated task branch.
- Pull requests must target `blakinio/canary:main` and use a head branch in `blakinio/canary`.
- Create draft PRs early; mark ready only after acceptance criteria and validation are complete.
- Before creating a PR, verify: target `blakinio/canary`, base `main`, head repository `blakinio/canary`, current task branch, upstream target `NO`.
- Verify the resulting PR URL begins with `https://github.com/blakinio/canary/pull/`; otherwise close it immediately and report the mistake.

## AI Content Project Safety

- AI tooling lives under `tools/ai-agent/**` and `docs/ai-agent/**` unless a task explicitly requires another location.
- Keep generated content in `artifacts/**` or another approved temporary output directory.
- Do not write generated previews directly into an active datapack.
- Do not modify `.otbm` files or `items.otb`, create/replace binary map assets, or change production server configuration unless explicitly authorized.
- Content generation defaults to `dry-run` and produces a reviewable plan or diff.
- Future map-writing remains disabled until format detection, backup, round-trip validation, and bounded-area checks exist.
- New AI-agent tools should be deterministic where practical and include unit tests.
- Prefer Python 3.12 standard-library implementations unless a dependency is justified.
- Do not weaken or remove tests merely to make CI pass.

## Data and Identifier Safety

- Distinguish identifier definitions from references.
- Before proposing storage, action ID, unique ID, or item ID ranges, inspect generated registry and active reservations.
- Never overwrite an active reservation silently.
- Item IDs requiring `items.xml` or `items.otb` changes are manual integration work unless explicitly approved.
- Missing monsters, NPCs, items, spells, event registrations, handlers, or evidence must be surfaced as warnings/blockers rather than invented.

## Change Scope and Validation

- Inspect existing Canary conventions before generating Lua, XML, C++, workflow, schema, SQL, or configuration changes.
- Keep changes limited to requested scope; no unrelated cleanup or broad refactors.
- Review `git diff --stat`, full diff, and full changed-file list before readiness and merge.
- Confirm no forbidden paths changed: `**/*.otbm`, `**/items.otb`, unrequested active datapack content, production secrets/credentials.
- Run relevant tests and report exact commands/outcomes honestly.
- Do not claim CI passed unless verified on the current head.

## Secrets and Sensitive Data

- Never commit tokens, passwords, private keys, connection strings, cookies, personal data, private logs, database dumps, backups, or secrets.
- If sensitive data is discovered, stop and report it without reproducing the secret.
- Do not post repository comments/reviews containing local paths, credentials, internal URLs, or private diagnostic data.

## Git Synchronization Workflow

- Never assume a local checkout is synchronized with GitHub. Verify the current branch, working-tree state, remotes, and exact local/remote SHAs before starting work.
- Before starting a new task from local `main`, when a local checkout is available:
  1. run `git status --short --branch`, `git branch -vv`, `git remote -v`, and `git worktree list`;
  2. if the working tree is dirty or contains uncommitted/untracked task work, do not automatically reset, stash, clean, or discard it; stop and reconcile ownership/task state first;
  3. run `git fetch origin`;
  4. switch to `main`;
  5. update only with `git pull --ff-only origin main`;
  6. verify local `HEAD` equals `origin/main` before creating a new task branch.
- If an existing task branch is already published, fetch first and inspect ahead/behind/divergence before integrating remote changes. Do not blindly pull, merge, rebase, reset, or force-update it.
- Create or use one dedicated branch per task and keep its upstream on the same-named `origin` branch. Never push task commits directly to `main`.
- Publish commits, branches, and PRs according to the existing Autonomous delivery policy and Pull Request Safety rules; this synchronization section does not add a separate user-confirmation gate.
- After a task PR is merged, before starting the next task in that local checkout: switch to `main`, run `git fetch origin`, then `git pull --ff-only origin main`, and verify `HEAD` equals `origin/main`.
- Treat `upstream` as fetch-only and never use it as a push target.
- Never resolve synchronization by weakening branch protection or using plain `--force`.

## Git Safety

- Before committing or pushing, check `git status --short --branch` and `git branch -vv`.
- Never push directly to `origin/main`.
- A working branch must not track `origin/main` unless the current branch is exactly `main`.
- Feature/fix branch upstream must point to the same remote branch name.
- Prefer explicit push targets: `git push origin HEAD:<branch>`.
- Before rewriting published history use `--force-with-lease`, never plain `--force`.

## Commit Policy

Use Conventional Commit style: `<type>(optional-scope): <summary>`. Preferred types: `feat`, `fix`, `perf`, `refactor`, `test`, `docs`, `build`, `ci`, `chore`, `revert`. Keep commits narrow and unrelated changes separate.

## Build Policy

- Compile when a change is critical, complex, or likely to break compilation; avoid wasteful builds for clearly non-build-affecting docs/scripts.
- Use known workflows and CMake presets instead of guessing commands or creating new build trees.
- When adding/removing/renaming C++ sources/headers, update all maintained build entry points.
- For focused validation, search `docs/agents/BUILD_TEST_MATRIX.md` by affected path/target/suite before reading broader sections.
- Normal Windows release validation is `cmake --preset windows-release` then `cmake --build --preset windows-release --target canary` from an appropriate Visual Studio developer environment.
- Do not switch generators merely because configure failed; repair only the verified affected cache/build directory.

## Precompiled Header Policy

- The project uses `src/pch.hpp` for common standard/library headers.
- Do not add unguarded standard/library includes already provided by `src/pch.hpp`.
- For non-PCH builds, retain guarded local fallback includes.

## Lua Shared Userdata Gate

For Lua bindings that store `std::shared_ptr<T>` in userdata, read `docs/systems/lua-shared-userdata.md` before changes. Do not add unsafe manual shared-pointer userdata/metatable patterns or weak metatables that remove required `__gc` behavior.

## Docker Quickstart Policy

- Keep CI/build Docker, local development Docker, and user-facing quickstart Docker separate unless documented otherwise.
- `docker/docker-compose.yml` keeps `login-server` as the default client login webservice.
- MyAAC is website/admin only and must not expose client `login.php`.
- Default client login URL: `http://localhost:8088/login`; default web/admin URL: `http://localhost:8080`.
- Public Docker env vars use `CANARY_*`.
- Quickstart uses the published Canary runtime image and must not require local compilation.

## Cross-repository changes

When a Canary change affects OTClient protocol parsing, feature flags, protobuf, assets, identifiers, login, or payload-dependent UI, use the `cross-repo` context route, create/link the required counterpart task and coordination ID, record compatibility/rollout/failure behavior, and do not merge an `atomic-required` contract until both sides satisfy their gates.

## PR Communication Policy

Agents may autonomously update and discuss their own PRs, reply to review feedback, and resolve threads after fixes. Do not comment on unrelated PRs unless needed for overlap/dependency coordination. PR comments and reviews must be in English.
