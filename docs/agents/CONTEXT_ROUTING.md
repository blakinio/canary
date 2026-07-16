# Agent Context Routing

This document defines the default context-loading strategy for autonomous agents.

## Goal

Load the smallest authoritative context required to complete the current task. Do not preload broad repository documentation when targeted search can identify the relevant records.

## Human and machine contracts

- This Markdown file is the human-readable routing contract.
- `docs/agents/CONTEXT_ROUTES.json` is the machine-readable routing profile used by `tools/agents/context.py` and `tools/agents/resume.py`.
- The machine profile may narrow or automate context selection but must not weaken repository safety or ownership rules.
- When a machine route and a more restrictive human safety rule disagree, follow the more restrictive human rule and record the conflict.

## Core startup context

Every agent reads only:

1. root `AGENTS.md`;
2. `docs/agents/REPOSITORY_MAP.md`;
3. the active task record, when one already exists;
4. the live PR for that task, when one already exists;
5. the nearest nested `AGENTS.md`, when the paths being inspected are covered by one.

Then classify the task and load only the matching routed context below.

When the task record already has a `## Context checkpoint`, the deterministic resolver is preferred:

```sh
python tools/agents/context.py --task <active-task-path> --task-text "<bounded task>"
```

The output is a bounded working set, not permission to skip required evidence or validation.

## Routing table

| Route | Trigger | Load/search |
|---|---|---|
| `agent-governance` | `AGENTS.md`, `docs/agents/**`, `tools/agents/**`, ownership/context/handoff tooling | Read the context/handoff/execution-mode contracts relevant to the task. Search shared indexes before full reads. |
| `cpp-runtime` | `src/**`, runtime, protocol, ownership, concurrency | Search `MODULE_CATALOG.md`; read matching entries only. Read `BUILD_TEST_MATRIX.md` sections relevant to affected targets. Read system/architecture docs only when referenced by matching code or catalogue entries. |
| `lua-data` | `data/**`, `data-otservbr-global/**`, Lua/XML gameplay behavior | Search catalogue, identifier registries, and relevant script paths. Load identifier/storage policy only when IDs or storages are involved. |
| `otbm` | OTBM, map mechanics, AID/UID, teleport, house door, reachability | Read the relevant `docs/ai-agent/OTBM_*` contract(s) and reuse the unified world index/script-resolution tooling. Never preload unrelated AI validation docs. |
| `universal-e2e` | physical client, login/relog, scenario execution, E2E artifacts | Read `docs/agents/programs/E2E_AUTOMATION_PROGRAM.md`, the scenario/task record, current PR, workflow, and relevant runner code. Do not load unrelated module programs. |
| `real-tibia-parity` | explicit comparison with Real Tibia, TibiaWiki/Fandom, packet capture, official-client observation, donor servers | Read `REAL_TIBIA_EVIDENCE_SOURCES.md`, `REAL_TIBIA_PARITY_PLAYBOOK.md`, relevant registry module and program. This route is not loaded for ordinary implementation work. |
| `upstream-intelligence` | claims that the fork is behind, donor/upstream candidate triage | Read the upstream intelligence program/policies and latest bounded report. Do not load for ordinary local bug fixing. |
| `cross-repo` | Canary change may require OTClient/protocol/client payload compatibility | Search `CROSS_REPO_CONTRACTS.md` for the affected contract/key first; read only the matching section unless a new contract must be created. |
| `ci-repair` | required GitHub check fails | Read the failing workflow/job/step and relevant task record. Do not load the entire build matrix unless failure classification requires it. |

Multiple routes may apply, but each route must be justified by the task scope or observed evidence.

## Execution-mode routing

Context routing and execution-mode routing are separate decisions.

Use `docs/agents/EXECUTION_MODE_ROUTING.md` and the deterministic advisor:

```sh
python tools/agents/execution_mode.py --task-text "<bounded task>"
```

Default budget policy is `minimize_agentic_usage`:

- prefer CHAT for analysis, planning, connector-based repository/GitHub/PR/CI work and coordination;
- use CODEX only when a bounded local edit/build/test/runtime loop or isolated coding worker materially helps;
- use WORK only for broad multi-source research or a large deliverable;
- return coordination to CHAT after the bounded CODEX or WORK package finishes.

Do not infer exact remaining platform tokens/credits when they are not exposed. Optimize through context bounds and capability-based escalation instead.

## Search before read

For large shared indexes, use targeted search before opening the whole document:

- `MODULE_CATALOG.md`: search by module ID, symbol, path, protocol field, subsystem, or responsibility;
- `KNOWN_RISKS.md`: search by affected path/subsystem/risk keyword;
- `BUILD_TEST_MATRIX.md`: search by changed path, target, suite, or workflow;
- `CROSS_REPO_CONTRACTS.md`: search by protocol field, feature, task ID, or affected client surface;
- `ACTIVE_WORK.md`: use only as a convenience index; confirm with task records and live PR state.

Reading a full large index is justified only when the task genuinely spans many unrelated systems or targeted search fails to locate the required entry.

## Context expansion rule

Expand context only when one of these is true:

- a tool/search result points to another authoritative document;
- a required fact remains `UNKNOWN` after targeted search;
- a conflict between sources must be resolved;
- a validation or safety gate explicitly requires the document.

Do not recursively follow every link in documentation.

## Working-set discipline

Keep the active working set limited to:

- current task goal and acceptance criteria;
- current head/branch/PR state;
- affected paths and ownership claims;
- proven facts and unresolved questions;
- currently relevant source excerpts;
- latest test/CI evidence;
- next concrete action.

Move historical discoveries, rejected hypotheses, and completed substeps into the task checkpoint instead of keeping full chat history active.

For CODEX or WORK escalation, generate the bounded handoff instead of copying the conversation:

```sh
python tools/agents/resume.py --task <active-task-path> [capability flags]
```

The bundle must not include full logs, full diffs, whole source trees or unrelated optional documentation.

## Reuse discovery

Before creating a new reusable abstraction, search:

1. `MODULE_CATALOG.md` for matching responsibility/symbols;
2. active task records and open PRs for overlapping paths or intent;
3. repository source/tests for existing implementations.

Do not read the complete catalogue by default.
