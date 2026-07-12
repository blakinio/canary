# Autonomous Agent Programs

Autonomous programs are long-lived workstreams such as Cyclopedia, quest audits, OTBM tooling, Wheel of Destiny, upstream maintenance, runtime architecture, CI/deployment, or the universal E2E platform.

A program may create and complete many task branches and pull requests. The program record preserves strategy, boundaries, queue, dependencies, and handoff across ChatGPT conversations. It is not a writable global lock.

## Sources of truth

- Git and open pull requests are authoritative for branches, commits, checks, and merge state.
- Individual active task records are authoritative for exact path ownership and current implementation state.
- Program records are authoritative for long-lived scope, sequencing, queue, and handoff.
- Generated ownership indexes are derived views and must not be edited manually.

## Required program record

Create one file under `docs/agents/programs/` from `docs/agents/templates/PROGRAM.md` for every autonomous workstream expected to span multiple tasks or pull requests.

Each program record must declare:

- stable `program_id`;
- logical owner name used by the autonomous chat or agent;
- scope and explicit exclusions;
- primary path families and shared integration points;
- current task queue and active task IDs;
- dependencies, blockers, and cross-repository contracts;
- exact handoff instructions.

## Concurrency rules

- One active task equals one branch, one worktree, and one pull request.
- One autonomous program may execute many tasks, sequentially or in parallel, but each task owns its own Git state.
- Exact path claims belong in task records, not in the program record.
- Program path families describe responsibility and discovery only; they do not override another active task's exclusive claim.
- Before opening each new task, inspect all active task records and open pull requests for overlap.
- Never manually maintain a central ownership table. Generate it from active task records.

## Task ownership modes

New task records use three modes under `owned_paths`:

- `exclusive`: the task may edit the path; another active structured task must not claim an overlapping exclusive path.
- `shared`: the task may need a narrow coordinated edit to a shared index, contract, catalogue, changelog, or registry.
- `read_only`: the task relies on the path but must not edit it.

Legacy flat `owned_paths` lists remain readable as `legacy_exclusive`. During migration they are included in the generated index and produce overlap warnings, but they do not fail default CI because older records may contain intentional broad or stale claims. Run `python tools/agents/task_ownership.py --strict-legacy` for a full migration audit.

## Recommended program files

Typical autonomous workstreams include:

- `E2E_AUTOMATION_PROGRAM.md`
- `cyclopedia.md`
- `quest-audit.md`
- `wheel-of-destiny.md`
- `otbm-tooling.md`
- `upstream-maintenance.md`
- `runtime-architecture.md`
- `ci-deployment.md`

Create only programs that are actually active. Do not add placeholder ownership records for work that has not been assigned.
