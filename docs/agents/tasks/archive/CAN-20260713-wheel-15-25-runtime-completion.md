---
task_id: CAN-20260713-wheel-15-25-runtime-completion
program_id: CAN-PROGRAM-WHEEL-OF-DESTINY-PARITY
coordination_id: ""
status: superseded
agent: GPT-5.6 Thinking
branch: feat/wheel-15-25-runtime-completion
base_branch: main
created: 2026-07-13T06:22:00Z
updated: 2026-07-14T09:00:00+02:00
completed: 2026-07-13T18:57:15Z
last_verified_commit: "f1f884bfa72807b28dbe9d69e2b3ebb07c23d7c2"
risk: high
related_issue: ""
related_pr: "#230"
depends_on:
  - PR #220
  - PR #229
blocks: []
owned_paths:
  exclusive:
    - data/modules/scripts/taskboard/taskboard.lua
    - src/creatures/players/components/wheel/player_wheel.cpp
    - src/creatures/players/components/wheel/player_wheel.hpp
    - src/lua/functions/creatures/player/player_functions.cpp
    - src/lua/functions/creatures/player/player_functions.hpp
    - tests/unit/players/wheel_validation_test.cpp
    - tools/ai-agent/test_wheel_task_shop_validation.py
    - docs/lua-api/lua_api.d.lua
    - docs/lua-api/lua_api.json
    - docs/ai-agent/OTS_AI_WHEEL_OF_DESTINY_VALIDATION.md
    - docs/agents/tasks/archive/CAN-20260713-wheel-15-25-runtime-completion.md
  read_only:
    - AGENTS.md
    - docs/agents/ACTIVE_WORK.md
    - docs/agents/MODULE_CATALOG.md
    - docs/agents/CHANGELOG.md
modules_touched:
  - Wheel of Destiny runtime
  - Taskboard official packet shim
  - Wheel point persistence and protocol payload
reuses:
  - PlayerWheel
  - official Taskboard packet shim
  - Wheel validation scanners
public_interfaces:
  - persisted purchased Hunting Task Shop Wheel points
  - official-client Wheel Task Shop point field
cross_repo_tasks: []
---

# Goal and final disposition

The task was originally created with the broad goal of completing every explicitly tracked Tibia 15.25 Wheel gap: vocation stances, replacement spells, passive/Revelation behavior, Blessing critical healing, Strong Ice Wave geometry, Hunting Task Shop points and end-to-end coverage.

PR #230 delivered one bounded, useful package — Hunting Task Shop promotion points — and was merged. The remaining independent packages were not implemented. The broad task is therefore archived as `superseded`, not falsely marked fully completed. Remaining work is decomposed in:

`docs/agents/programs/WHEEL_OF_DESTINY_PARITY_PROGRAM.md`

Do not reopen PR #230 or continue its historical branch.

# Delivered package

PR #230 implemented:

- official Taskboard `BONUS_PROMOTION` offer;
- exact escalating cost formula for purchases 1–50;
- persisted maximum of 50 purchased Wheel points;
- bounded `PlayerWheel` cache loaded during the established Wheel KV/login phase;
- immediate cache synchronization after purchase;
- inclusion in authoritative Wheel point accounting;
- correction of the `u16` Wheel payload field interpreted by the maintained client as Hunting Task Shop points;
- focused repository and deterministic audit coverage.

# Not delivered by this task

The following remain separate queue items and must not be described as merged through #230:

- vocation stance state and restrictions;
- Shield Bash and Shield Slam;
- Divine Barrage and Ethereal Barrage;
- Death Echo, Forked Glacier and Forked Thorns;
- Thousand Fist Blows replacement behavior;
- remaining passive/Revelation reworks;
- Blessing of the Grove critical healing;
- authoritative Strong Ice Wave geometry;
- complete DB/KV round-trip and failure injection;
- complete protocol malformed-input and profile tests;
- gameplay and physical-client E2E.

# Final repository state

- PR: #230 — `feat(wheel): complete Tibia 15.25 runtime parity`.
- Historical branch: `feat/wheel-15-25-runtime-completion`.
- Final feature head: `f1f884bfa72807b28dbe9d69e2b3ebb07c23d7c2`.
- Squash merge: `d4e8933b78587445afd9347a6d05b6e715c6c0e4`.
- Merged at: 2026-07-13T18:57:15Z.
- Changed files: 12.
- Review/merge state: merged; do not reopen.

# Final changed files

1. `data/modules/scripts/taskboard/taskboard.lua`
2. `docs/agents/ACTIVE_WORK.md` — historical branch-era change; later removed from current coordination state by dedicated governance cleanup
3. `docs/agents/tasks/active/CAN-20260713-wheel-15-25-runtime-completion.md` — moved to archive by governance cleanup
4. `docs/ai-agent/OTS_AI_WHEEL_OF_DESTINY_VALIDATION.md`
5. `docs/lua-api/lua_api.d.lua`
6. `docs/lua-api/lua_api.json`
7. `src/creatures/players/components/wheel/player_wheel.cpp`
8. `src/creatures/players/components/wheel/player_wheel.hpp`
9. `src/lua/functions/creatures/player/player_functions.cpp`
10. `src/lua/functions/creatures/player/player_functions.hpp`
11. `tests/unit/players/wheel_validation_test.cpp`
12. `tools/ai-agent/test_wheel_task_shop_validation.py`

# Validation evidence

Final head `f1f884bfa72807b28dbe9d69e2b3ebb07c23d7c2`:

| Workflow/run | Result | Evidence boundary |
|---|---|---|
| Wheel of Destiny Validation `29275338619` | success | deterministic Wheel/Task Shop validation on final head |
| Agent Task Ownership `29275338554` | success | task/ownership policy checks executed by that workflow |
| AI Agent Tools `29275338528` | success | AI-agent tool tests for changed scope |
| autofix.ci `29275338557` | success | formatting workflow completed without changing final head |
| repository CI `29275338698` | success | Fast Checks, Lua, Linux debug/release, Windows, macOS, Docker and Required completed |

The final CI run included:

- Fast Checks;
- Lua Tests;
- Linux debug build, schema import and C++ unit tests;
- Linux release and runtime smoke;
- Windows CMake build/runtime smoke;
- macOS build/runtime smoke;
- Docker image build and validation;
- Required.

This proves the executed automated checks on the final head. It does not prove a real-client purchase/relogin scenario or every remaining Wheel 15.25 feature.

# Failure found and repaired during delivery

An intermediate implementation read player KV from every `getWheelPoints()` call. Lightweight player tests do not initialize the full KV service, and Linux debug tests failed. The production repair moved the purchased count into bounded `PlayerWheel` state, loaded it during the established KV/login phase and synchronized the cache after purchase. The corrected final head passed the full matrix.

# Local environment limitation

The previous execution environment could not resolve `github.com` for local Git operations. The task did not claim a local repository build. GitHub Actions on the final head is the recorded execution evidence.

# Rollback

Revert squash merge `d4e8933b78587445afd9347a6d05b6e715c6c0e4`. The persisted purchased-point counter defaults to zero when absent. Review compatibility for players who purchased points before rollback; a rollback must not silently reinterpret the existing KV value as another field.

# Remaining work

Use the bounded queue in `WHEEL_OF_DESTINY_PARITY_PROGRAM.md`. The preferred next candidate is Blessing of the Grove critical healing only after current-main and multi-source revalidation.

# Handoff

- Do not reopen #230.
- Do not continue `feat/wheel-15-25-runtime-completion`.
- Do not reuse technical staging PR #279.
- Do not create another broad “complete Wheel” task.
- Read the Real Tibia parity playbook, Wheel program and validation report.
- Create a fresh task/branch/PR from current main for exactly one still-valid queue item.
