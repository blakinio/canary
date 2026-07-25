---
task_id: CAN-20260725-rtec-004-weapon-proficiency
program_id: CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION
coordination_id: RTEC-004-W1-WEAPON-PROFICIENCY
status: implementing
agent: "GPT-5.6 Thinking"
branch: feat/rtec-004-weapon-proficiency-20260725
base_branch: main
created: 2026-07-25T20:18:00+02:00
updated: 2026-07-25T20:18:00+02:00
last_verified_commit: "124b029d1a2498a64fa6612b16efa386b8786a83"
risk: medium
related_issue: ""
related_pr: ""
depends_on:
  - RTEC-004-WAVE-1
blocks: []
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260725-rtec-004-weapon-proficiency.md
    - docs/agents/real-tibia/evidence/modules/weapon-proficiency/**
  shared: []
  read_only:
    - docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md
    - docs/agents/real-tibia/evidence/generated/**
    - docs/agents/real-tibia/evidence/requests/**
    - docs/agents/real-tibia/registry/modules/weapon-proficiency.yaml
    - data/items/proficiencies.json
    - src/creatures/players/components/weapon_proficiency.*
    - tests/unit/players/components/weapon_proficiency_test.cpp
    - tools/ai-agent/weapon_proficiency_achievement_audit.py
    - tools/ai-agent/test_weapon_proficiency_achievement_audit.py
    - tools/e2e/**
modules_touched:
  - weapon-proficiency
reuses:
  - canary-real-tibia-evidence-record-v1
  - canary-real-tibia-owner-request-v1
  - RTEC-002 vocations dossier structure
public_interfaces: []
cross_repo_tasks: []
---

# Goal

Collect one bounded, version-aware evidence package for Summer Update 2026 weapon-proficiency perk-slot modification and pending-level-up character-isolation behavior without changing gameplay, protocol, client, persistence or E2E owner paths.

# Assignment

- Official target: Summer Update 2026 released 2026-07-13 plus the 2026-07-14 fix statement.
- Canary baseline at task start: `124b029d1a2498a64fa6612b16efa386b8786a83`.
- Module record: `weapon-proficiency`, inventory maturity, fast freshness class, refresh required before task.
- Canonical current paths: proficiency JSON, server component, focused unit test and retained achievement audit/report.
- Dossier root: `docs/agents/real-tibia/evidence/modules/weapon-proficiency/`.

# Boundaries

- Do not modify proficiency implementation, tests, data, protocol/client, persistence, achievement ownership or E2E paths.
- Do not reuse or advance `RTREQ-FEATURE-VOCATIONS-0001`.
- Do not infer perk identifiers, formulas, packet fields, persistence semantics or UI behavior.
- Missing runtime, persistence, protocol or physical-client proof remains `UNKNOWN` or becomes a separately coordinated owner request.

# Acceptance criteria

- [ ] Refresh exact Canary definitions, registration, persistence, tests and retained reports.
- [ ] Pin exact official URLs/dates and selected statements.
- [ ] Decompose perk-slot modification and character-switch isolation into bounded claims.
- [ ] Create only the module-specific dossier, behavior model, version history, decisions, evidence index, records and review material required by the valid v1 contracts.
- [ ] Separate official release, client build, protocol profile, Canary commit, OTClient commit, datapack/assets and schema axes.
- [ ] Record proof and nonproof boundaries, conflicts, unknowns, freshness and invalidation triggers.
- [ ] Create no duplicate owner request for an existing behavior/identifier/version tuple.
- [ ] Pass focused evidence validation, deterministic-index check and ownership/CI gates on the final head.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-25T20:18:00+02:00
head: 124b029d1a2498a64fa6612b16efa386b8786a83
branch: feat/rtec-004-weapon-proficiency-20260725
pr: none
status: implementing
context_routes:
  - agent-governance
  - real-tibia-parity
owned_paths:
  - docs/agents/tasks/active/CAN-20260725-rtec-004-weapon-proficiency.md
  - docs/agents/real-tibia/evidence/modules/weapon-proficiency/**
proven:
  - coordinator assigned one bounded weapon-proficiency package under RTEC-004 wave 1
  - module registry inventory identifies proficiency JSON server component focused unit test and retained achievement audit paths
  - official Summer Update 2026 states that up to two perk slots per weapon can be modified
  - official 2026-07-14 fixes identify pending proficiency level-up display leakage across character switching
  - active vocations owner request addresses level gains and promotion rather than this package
unknown:
  - exact current Canary implementation and registration comparison
  - exact persistence and protocol surfaces
  - exact current maintained-client behavior
  - strongest proof levels attainable from retained evidence
conflicts: []
first_failure:
  marker: dossier-not-started
  evidence: branch and task exist but no module evidence files have been created
rejected_hypotheses:
  - implement or test the feature in this Collector task: owner boundaries make implementation paths read-only
  - infer client or persistence behavior from official release text: official text does not prove hidden state or packet contracts
changed_paths:
  - docs/agents/tasks/active/CAN-20260725-rtec-004-weapon-proficiency.md
validation:
  - command: coordinator ownership and module-registry preflight
    result: PASS
    evidence: exclusive module dossier root and no duplicate RTEC package found
blockers: []
next_action: Inspect the exact current Canary proficiency JSON component unit test and retained audit/report, then define the first bounded evidence claims before creating dossier files.
```
