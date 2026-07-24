---
task_id: CAN-20260724-oteryn-oam043-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-043
status: review
agent: "GPT-5.6 Thinking"
branch: dudantas/oam-043-quests-revalidation
base_branch: main
created: 2026-07-24
updated: 2026-07-24
last_verified_commit: "5641a7ac2420f5a3d512325423088890e92ac3cb"
risk: high
related_issue: ""
related_pr: ""
depends_on:
  - Canary OAM-043 preflight merged as df7abb0cfe4b05ed11da7b3a6a0dcddbefb62375
  - Otheryn OAM-043 feature merged as 6512d78004ae2540784b3e67592a92a903554cf6
  - Otheryn OAM-043 lifecycle archived as 3f3c15917610e45430aa3902d110806dd25e10a8
blocks:
  - Canary OAM-043 lifecycle archive
  - durable program reconciliation
  - OAM-044 start
owned_paths:
  exclusive:
    - docs/agents/tasks/active/CAN-20260724-oteryn-oam043-preflight.md
    - docs/agents/OTERYN_OAM_043_QUESTS_REVALIDATION.md
  shared: []
  read_only:
    - docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md
    - docs/agents/OTERYN_TARGET_ARCHITECTURE_CONTRACT.md
    - docs/agents/real-tibia/registry/modules/quests.yaml
    - docs/oam-043-quests-adapt.md
modules_touched:
  - oteryn-architecture-migration
  - quests
cross_repo_tasks:
  - OTH-20260724-oam043-quests-adapt
---

# OAM-043 quests revalidation

## Goal

Reconcile the completed Otheryn OAM-043 target adaptation into Canary governance without mutating Canary runtime, datapack, map, protocol, client, schema or deployment paths. Preserve the bounded `quests → ADAPT` disposition, exact delivery evidence, rejected donor hypotheses and unresolved source/map boundaries before lifecycle archive and durable program reconciliation.

## Acceptance criteria

- [x] Otheryn target feature and lifecycle merges are exact and current.
- [x] Final `quests → ADAPT` is supported by complete inventory, source and configured-map evidence.
- [x] Six accepted source changes and rejected donor hypotheses are explicitly bounded.
- [x] Exact-head Otheryn gates, clean discussions and no target-main drift are recorded.
- [x] Dynamic expressions, shared script-only findings and storage-graph limits remain unresolved.
- [ ] Canary governance PR passes exact-head ownership and final-gate CI.
- [ ] Separate Canary lifecycle/archive PR merges.
- [ ] Durable program reconciliation records OAM-043 before any OAM-044 implementation starts.

## Context checkpoint

```yaml
checkpoint_version: 1
updated_at: 2026-07-24T14:28:00+02:00
head: 5641a7ac2420f5a3d512325423088890e92ac3cb
branch: dudantas/oam-043-quests-revalidation
pr: none
status: validating
context_routes:
  - agent-governance
  - otbm
  - cross-repo
owned_paths:
  - docs/agents/tasks/active/CAN-20260724-oteryn-oam043-preflight.md
  - docs/agents/OTERYN_OAM_043_QUESTS_REVALIDATION.md
proven:
  - Canary preflight PR 866 selected quests with REVALIDATE and merged as df7abb0cfe4b05ed11da7b3a6a0dcddbefb62375; post-preflight PR 872 merged as 13ec3077babba0ac81bb1e30e79f0ea4827ae2fe.
  - Exact task-start baselines were Otheryn 3a37f3d5e4c01ddf4469f1c71461c40ca749142f, upstream 7323503b3dc61ed86bf1f04a611b2d0aec64b35a and legacy 13ec3077babba0ac81bb1e30e79f0ea4827ae2fe.
  - Inventory manifest 391e38d963b1a791e4fd59edf8ce6adbb4a75dfc8e8a34da351c50f080267925 records target/upstream 978 files, legacy 981, 973 all-identical, five target/upstream-identical divergences and three legacy-only paths.
  - Complete source digest a97442a2e77aee6cd02ba094a8158965a1da9681d0426114c7cd1c3546e3ef40 covers 978 files and 12027 evidence entries while preserving 1045 dynamic expressions unresolved.
  - Configured map a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2 produced World Index 6c22cd26d4414aa094af1d00be7f62190a441e270ee7a478b55449bf92e55e7a with zero unknown tails.
  - Complete map correlation records 8860 confirmed, 484 script-only, 2683 unresolved, zero map-only and zero conflicting findings.
  - Accepted adaptation corrects Hero of Rathleton achievement lookup, Soulpit receiver and Ancient Tomb timed door closure.
  - Three legacy-only The Beginning handlers produced 47 confirmed and zero script-only map findings and were restored, leaving 981 quest files.
  - Legacy AID 12108 was script-only with zero map placements; account-wide Ape City/Wrath donor calls lacked prerequisite target APIs; redundant Soulpit counter was also rejected.
  - Otheryn ready head 7a783c65e83a9fead651e38f336b10cbffe7a19b and sync head 333b7047f8ecc660a84b215e9a4149b10d083c35 passed autofix, CI, Required and Repository Audit matrices.
  - Otheryn PR 98 had no comments, reviews or threads, no target-main drift, and merged as 6512d78004ae2540784b3e67592a92a903554cf6.
  - Otheryn lifecycle PR 99 changed only the lifecycle task path, Required 30093061770 succeeded, discussions were empty, no main drift occurred, and it merged as 3f3c15917610e45430aa3902d110806dd25e10a8.
  - Revalidation report records exact accepted changes, source/map provenance, target gates, rejected hypotheses and nonclaims.
derived:
  - Canonical quests is ADAPT rather than REUSE because concrete source defects and map-backed missing handlers were proven.
  - Remaining shared script-only and dynamic findings are explicit evidence boundaries rather than broad remediation scope.
  - No maintained-client, protocol, map, schema or deployment mutation is justified by the accepted package.
unknown:
  - Exact gameplay impact and ownership of each of the 484 shared script-only findings.
  - Runtime values and execution paths of the 1045 unresolved dynamic expressions.
  - Exhaustive stage ordering, reachability and scope for all 2016 storage references.
  - Full factual correctness of every quest family, reward, NPC/spawn dependency and access gate.
  - Physical-client and production gameplay parity.
conflicts: []
first_failure:
  marker: candidate donor AID 12108
  evidence: Otheryn run 30089559964 rejected dual registration; run 30089658579 retained diagnostics classifying AID 12108 as script-only with map count zero.
rejected_hypotheses:
  - Finalize quests as REUSE from target/upstream inventory identity alone.
  - Bulk-copy the legacy quest tree or all five divergent legacy variants.
  - Import account-wide quest-access calls without prerequisite target APIs.
  - Restore the redundant Soulpit-local countMonsters override.
  - Register Ancient Tomb AID 12108 despite zero configured-map placements.
  - Treat unresolved dynamic expressions or lexical storage references as proven runtime progression.
changed_paths:
  - docs/agents/tasks/active/CAN-20260724-oteryn-oam043-preflight.md
  - docs/agents/OTERYN_OAM_043_QUESTS_REVALIDATION.md
validation:
  - command: exact Otheryn delivery and evidence audit
    result: PASS
    evidence: Feature PR 98 merged as 6512d78004ae2540784b3e67592a92a903554cf6 and lifecycle PR 99 merged as 3f3c15917610e45430aa3902d110806dd25e10a8 after exact-head gates and clean discussion/drift audits.
  - command: Canary governance exact-head ownership and CI
    result: NOT_RUN
    evidence: A governance PR must be opened and synchronized to its exact final head.
blockers: []
next_action: Open the bounded Canary governance PR, synchronize related PR/head metadata, require exact-head Agent Task Ownership and final-gate CI, audit discussions and Canary-main drift, then squash-merge with the expected head.
```
