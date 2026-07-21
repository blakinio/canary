---
task_id: CAN-20260721-oteryn-oam033-charms-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-033
status: archived
created: 2026-07-21
updated: 2026-07-21
related_pr: "696"
modules_touched:
  - charms
---

# OAM-033 Charms preflight — archived

Final disposition: `charms → ADAPT`.

Task-start baselines: Canary `f05ea5e916af00ab1469a2332aaec2d3c9df7478`, Otheryn `1a4bbceda2c805bc69c68c1592e04e63d7e9a269`, upstream `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`, maintained OTClient `a6868920443dc285656bd016acdb2c1ea566e511`.

Canonical `charms` selected two bounded PR #188 corrections: category registration now gates on `mask.category`, and all-Charm reset pricing charges the `11,000` surcharge only for levels above 100. Bestiary, Bosstiary, Cyclopedia Character, monster-data and maintained-client work remained outside OAM-033. The initial target full suite passed 421/422; its sole failure was a superseded OAM-031 old-formula boundary assertion, retired without further production change.

Otheryn PR #67 final head `e1fca0b372173db335118735f501f315d442888f` changed exactly seven intended paths. Autofix.ci #192 run `29867543037`, Repository Audit #27 run `29867542987`, CI #233 run `29867543182`, Required #218 run `29867542998`, and Linux-debug full `Run Tests` succeeded; test-log artifact `8510218346` digest is `sha256:1bc7425f036bb5f39c19539590da0704f026718e4bbd54ad2ede79c023300cbc`. It merged by expected-head squash as `c887318a676998da5ef3224a3aa8d1e0df75e607`.

Canary governance PR #696 final head `34ca59c5ca53e7082d4e1ced1428b745bb8e91e1` passed Agent Task Ownership #3213 run `29868982754` and final-gate CI #4369 run `29868983212`, had exactly two governance paths and zero comments/reviews/threads, with no Canary main drift, then merged by expected-head squash as `5ecc72762feb6bda8f6549ac4238a75247752449`.

A separate one-file durable program reconciliation remains required before OAM-034 may start.
