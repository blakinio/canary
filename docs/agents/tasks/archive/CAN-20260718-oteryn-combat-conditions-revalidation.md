---
task_id: CAN-20260718-oteryn-combat-conditions-revalidation
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-014
status: completed
agent: "GPT-5.5 Thinking"
branch: docs/oam-014-combat-conditions-lifecycle
base_branch: main
created: 2026-07-18
updated: 2026-07-18T14:04:00+02:00
completed: 2026-07-18T14:04:00+02:00
last_verified_commit: "c9ba742731ebea2ccaf73b8b7ae78ee855ad9109"
risk: high
related_issue: "blakinio/Otheryn#34"
related_pr: "539"
depends_on:
  - OAM-013
blocks:
  - OAM-015
modules_touched:
  - combat-conditions
---

# Goal

Revalidate canonical `combat-conditions` against immutable task-start baselines and accept only the smallest coherent evidence-backed adaptation required for condition lifecycle correctness.

# Final disposition

```text
combat-conditions → ADAPT
```

# Immutable task-start baselines

- governance/legacy Canary: `blakinio/canary@0253b712cd4275e8ad72d5bca7020d1f4a2246b7`
- Oteryn target: `blakinio/Otheryn@3628effc5f22e7edbdc66dc5f514e4df5c9f0cda`
- upstream evidence: `opentibiabr/canary@e0ac98e399d0f7e483f3668f57b78fcc45b6e53f`
- maintained OTClient: `blakinio/otclient@2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`

# Accepted boundary

Reviewed donor: Canary PR #297 final head `b7f5de1f04cd3b521ee9621a0f001f0ced5e6c39`.

Exact donor blobs:

```text
src/creatures/combat/condition.cpp
26a1cf0c9e01f4ab162438e8284f5cc73d129d11

tests/unit/players/condition/condition_light_test.cpp
ee2f185042cdb359aac1a752dce971ec76c38f8d

tests/unit/players/condition/CMakeLists.txt
b224d4eb1eb15eb92ca4a26f214c0764b82b03c3
```

Accepted behavior:

- normalize zero `ConditionLight` level before start-condition fade-interval division;
- normalize deserialized persisted zero light level to minimum valid level `1`;
- preserve valid nonzero light behavior.

No second coupled delivered `condition.cpp` runtime fix was identified in reviewed legacy history.

# Target proof

```text
Otheryn issue #34: CLOSED / completed
Otheryn PR #35 final head: f4044811f2b930318ec6541a51e73a9a1b6fdce0
target squash merge: 9d797b547c3f85f6d210c6123202c7cae32d5133
CI #117: 29642976283 SUCCESS
Required #108: 29642976213 SUCCESS
autofix.ci #101: 29642976219 SUCCESS
Linux debug build: PASS
Canary runtime smoke: PASS
database schema import: PASS
full CTest: 351/351 PASS
ConditionLightTest: 3/3 PASS
primary artifact: 8429300008
digest: sha256:328f60045be1d42e4fba0c6b80aa64a3b8e767553808d7c47119750922cc2e36
```

Final target scope was exactly three accepted paths. The temporary fail-closed materializer removed itself before review. Target comments, reviews and review threads were all empty, and target `main` had no task-start drift before expected-head squash merge.

# Canary governance proof

```text
governance PR #539 final head: 9c806ec8524d59430395173d8187ef90d8b2e64d
Agent Task Ownership #2305: 29643562904 SUCCESS
ready-state CI #3449: 29643583135 SUCCESS
Required: PASS
comments: 0
reviews: 0
review threads: 0
Canary main drift before merge: none
governance feature merge: c9ba742731ebea2ccaf73b8b7ae78ee855ad9109
```

# Explicit exclusions

- no generic combat formula or target-selection change;
- no spell registration/cooldown migration;
- no vocation-specific state migration;
- no protocol/client/map/asset changes;
- no broad persistence redesign;
- no SQL/KV atomicity claim;
- no automatic persisted-data rewrite;
- no exhaustive condition timing/stacking/persistence correctness claim;
- no full Real Tibia condition formula/value parity claim.

OAM-004 SQL/KV non-atomicity remains authoritative.

# Lifecycle state

Feature and governance work is complete. This lifecycle-only archive records target merge `9d797b547c3f85f6d210c6123202c7cae32d5133` and Canary governance merge `c9ba742731ebea2ccaf73b8b7ae78ee855ad9109`.

Durable program reconciliation remains pending and must merge before OAM-015 may start.
