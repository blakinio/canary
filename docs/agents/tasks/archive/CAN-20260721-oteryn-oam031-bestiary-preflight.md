---
task_id: CAN-20260721-oteryn-oam031-bestiary-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-031
status: archived
created: 2026-07-21
updated: 2026-07-21
related_pr: "675"
modules_touched:
  - bestiary
---

# OAM-031 Bestiary preflight — archived

Final disposition: `bestiary → ADAPT`.

Task-start baselines: Canary `9aa582eb6b8ab9444294e08798f628cd053d2428`, Otheryn `6a7e54ee3c9597e3ab265a14c2b783631ef3776f`, upstream `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`, maintained OTClient `a6868920443dc285656bd016acdb2c1ea566e511`.

The accepted target boundary was exactly two Bestiary-owned corrections from merged legacy PR #188: null-safety before `mtype` dereference in `addBestiaryKill`, and non-truncating fractional difficulty calculation. Charm reset pricing and PR #192 monster-definition data were excluded.

Otheryn PR #63 final head `c49796d696448aa168c34629dc9ebcd9fd7a9465` passed autofix.ci #187, CI #226, Required #211 and Linux debug full `Run Tests`; artifact `8493329878` digest is `sha256:e99f341683bc432512ddd0dc235204f8b13510cd48eaf9f06c9cdf53d7dbc432`. It merged by expected-head squash as `86e4b08c28ede2f35c215a7c2327a579f4a61419`.

Canary governance PR #675 final head `1ce09da615e703ff72062c60093ae8b5173cf80b` passed Agent Task Ownership #3069 and final-gate CI #4222, had exactly two governance paths and zero comments/reviews/threads, then merged by expected-head squash as `e55e0d548d6013da6676cc7b06cbb8d459ccdd1f`.

A separate one-file durable program reconciliation remains required before OAM-032 may start.
