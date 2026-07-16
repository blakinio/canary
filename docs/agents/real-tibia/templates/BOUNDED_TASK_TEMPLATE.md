---
task_id: CAN-YYYYMMDD-<module>-<bounded-scope>
program_id: CAN-PROGRAM-<MODULE>-PARITY
coordination_id: <MODULE>-NNN
status: planned
agent: ""
branch: type/<module>-<bounded-scope>
base_branch: main
created: YYYY-MM-DDTHH:MM:SSZ
updated: YYYY-MM-DDTHH:MM:SSZ
last_verified_commit: ""
risk: medium
related_issue: ""
related_pr: ""
depends_on: []
blocks: []
owned_paths:
  exclusive: []
  shared: []
  read_only:
    - docs/agents/ACTIVE_WORK.md
module_ids:
  - <module-id>
primary_module: <module-id>
modules_touched: []
reuses: []
public_interfaces: []
cross_repo_tasks: []
---

# Goal

One exact independently testable outcome.

# Evidence gate

- [ ] Current main, open PRs and active tasks re-fetched.
- [ ] Module record and program read.
- [ ] Exact source/version matrix completed.
- [ ] Current absence/defect proven.
- [ ] Donor code classified rather than copied wholesale.

# Acceptance criteria

- [ ] Focused behavior and deterministic tests.
- [ ] Persistence/protocol/E2E boundaries handled when applicable.
- [ ] Module record/program/validation report updated only when conclusions changed.
- [ ] Full affected CI passes on final head.
- [ ] Separate archive lifecycle after merge.

# Comparison matrix

| Mechanic | Official | Wiki | Canary | OTClient | Upstream | CrystalServer | Tests/runtime | Conclusion |
|---|---|---|---|---|---|---|---|---|

# Plan

# Work log

# Validation and CI

# Handoff
