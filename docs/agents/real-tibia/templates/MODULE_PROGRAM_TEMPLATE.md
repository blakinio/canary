---
program_id: CAN-PROGRAM-<MODULE>-PARITY
module_id: <module-id>
name: <Module> Parity Program
status: inventory
owner: unassigned
created: YYYY-MM-DDTHH:MM:SSZ
updated: YYYY-MM-DDTHH:MM:SSZ
last_verified_commit: "<exact Canary SHA>"
primary_paths: []
shared_integration_paths: []
related_programs:
  - CAN-PROGRAM-REAL-TIBIA-PARITY
cross_repo_contracts: []
---

# Mission

Describe the long-lived module outcome without claiming full parity.

# Scope

## Includes

## Excludes

# Required reads

- `AGENTS.md`
- `docs/agents/README.md`
- `docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md`
- `docs/agents/REAL_TIBIA_PARITY_PLAYBOOK.md`
- `docs/agents/real-tibia/registry/modules/<module-id>.yaml`

# Baseline register

| Dimension | Source | Exact version/SHA/date | Evidence path | Notes |
|---|---|---|---|---|
| Canary server | `blakinio/canary` | | | |
| Maintained client | `blakinio/otclient` | | | |
| Official Tibia | | | | |
| Wiki | | capture date | | secondary only |
| OpenTibiaBR | `opentibiabr/canary` | | | read-only |
| CrystalServer | `zimbadev/crystalserver` | | | read-only donor |

# Current implementation and proof matrix

| Mechanic | Definition | Registration | Runtime | Persistence | Protocol | Automated test | Gameplay/E2E | Source agreement | Status |
|---|---|---|---|---|---|---|---|---|---|---|

# Completed packages

| Package | PR | Merge SHA | Proof boundary |
|---|---:|---|---|

# Bounded queue

| ID | Scope | Status | Evidence baseline | Dependencies | Risk | Exact next action |
|---|---|---|---|---|---|---|

# Active task

None.

# Conflicts and blocked references

# Reusable implementation and validators

# Handoff

State the exact next bounded action and what must be re-fetched.
