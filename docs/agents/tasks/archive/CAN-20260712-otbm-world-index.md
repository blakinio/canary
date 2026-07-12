---
task_id: CAN-20260712-otbm-world-index
coordination_id: "OTS-OTBM-VALIDATION"
status: completed
agent: "GPT-5.6 Thinking"
branch: feat/otbm-world-index-v2
base_branch: main
created: 2026-07-12T22:16:00+02:00
updated: 2026-07-13T00:12:00+02:00
last_verified_commit: "97ff786663b30cafbd933799d8549a6dd3e3370b"
risk: medium
related_issue: ""
related_pr: "#219"
depends_on:
  - "merged OTBM item audit"
  - "merged OTBM script-resolution audit #104"
  - "merged factual OTBM renderer and HD pipeline #154/#161"
  - "merged roadmap-only PR #190"
blocks:
  - "Quest Map Validator phase"
  - "teleport/pathfinding validation phase"
  - "OTBM semantic diff phase"
owned_paths:
  - tools/ai-agent/otbm_item_audit_scan.cpp
  - tools/ai-agent/otbm_world_index.py
  - tools/ai-agent/otbm_world_index_tool.py
  - tools/ai-agent/test_otbm_world_index.py
  - docs/ai-agent/OTBM_WORLD_INDEX.md
  - docs/ai-agent/OTBM_WORLD_INDEX.schema.json
  - docs/ai-agent/OTS_OTBM_TOOLING_ROADMAP.md
  - .github/workflows/otbm-world-index.yml
modules_touched:
  - OTBM item audit native scanner
  - OTBM script-resolution input foundation
  - factual OTBM renderer evidence
public_interfaces:
  - "OTSWIDX1 binary layout version 1"
  - "canary-otbm-world-index-v1 manifest"
  - "canary-otbm-world-query-v1 query result"
  - "OTBM world index CLI"
cross_repo_tasks: []
---

# Goal

Create a deterministic read-only full-world OTBM index so agents can query items, mechanics, positions, regions and teleport destinations without rescanning or modifying the map.

# Result

Completed and squash-merged in PR #219 as commit `97ff786663b30cafbd933799d8549a6dd3e3370b`.

The existing native item-audit scanner now supports:

```text
otbm_item_audit_scan --world-index MAP OUTPUT.widx
```

The implementation preserves the legacy JSON scan mode and adds:

- deterministic `OTSWIDX1` little-endian binary postings;
- memory-mapped Python validation and queries;
- item ID, AID, UID, house-door and teleport-destination lookups;
- exact-position and inclusive 3D-region queries;
- bounded pagination with exact total counts;
- source/scanner/index hashes;
- duplicate-position detection;
- atomic output and symlink/overwrite safety;
- focused tests, schema, documentation and dedicated CI.

# Real-map evidence

```text
map SHA-256: a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2
source size: 184,776,037 bytes
index size: 842,280,592 bytes
build time: 32.72 s
peak RSS: 419,140 KiB
tiles: 17,972,761
placements: 23,359,571
used item IDs: 23,852
mechanics: 9,339
canonical areas: 1,171
raw area nodes: 1,175,983
unknown attribute tails: 0
maximum item depth: 2
Cobra bounds: 33377,32631,7 -> 33417,32671,7
Cobra tiles: 1,681
Cobra placements: 2,627
```

Generated map, client and `.widx` artifacts stayed outside Git.

# Validation

## Local

```text
native C++ compile: passed with -Wall -Wextra -Wpedantic -Werror
focused unit tests: 10 passed in 3.015 s
Python bytecode compilation: passed
real-map build and bounded query smoke: passed
```

## GitHub final head

Validated head: `452cdc6aaa183a7b4ce05ea83a013046764ecdb1`.

- OTBM World Index run `29210711531`: success.
- OTBM Map Tools run `29210711521`: success.
- AI Agent Tools run `29210711515`: success.
- ready-for-review CI run `29210760673`: success.
- nested required check `Required`: success.
- review threads: none.
- mergeability before auto-merge: true.

# Decisions and failed approaches

- Extended the existing native scanner instead of creating a second parser.
- Used deterministic binary postings because NDJSON/SQLite exceeded five minutes on the real map.
- Merged 1,175,983 raw tile-area nodes into 1,171 canonical query areas with postings.
- Kept Phase 1 strictly read-only; safe map writing remains a later gated phase.
- Closed conflicted PR #211 and replaced it with clean current-main PR #219 rather than overwriting concurrent shared documentation.

# Compatibility and rollback

- No runtime, database, protocol, datapack, map or OTClient behavior changed.
- Legacy item-audit scanner invocation and JSON format remain supported.
- Generated `.widx` files are local cache artifacts and must not be committed or shipped as client assets.
- Rollback: revert merge commit `97ff786663b30cafbd933799d8549a6dd3e3370b`; no persistent cleanup is required.

# Handoff

The next phase should implement Quest Map Validator on a new branch and reuse:

- `tools/ai-agent/otbm_world_index.py` for map evidence;
- `tools/ai-agent/otbm_script_resolution.py` for runtime-handler evidence;
- the factual renderer for bounded visual confirmation.

Do not create another OTBM parser, commit `.widx`, or add map-writing behavior to the validator.

# Completion

- Final status: completed and merged
- PR: #219
- Merge commit: `97ff786663b30cafbd933799d8549a6dd3e3370b`
- Catalogue updated: yes
- Changelog updated: yes
- Archived at: `docs/agents/tasks/archive/CAN-20260712-otbm-world-index.md`
