---
task_id: CAN-20260722-oteryn-oam037-preflight
program_id: CAN-PROGRAM-OTERYN-ARCHITECTURE-AND-MIGRATION
coordination_id: OAM-037
status: archived
created: 2026-07-22
updated: 2026-07-23
related_pr: "750"
modules_touched:
  - raids
---

# OAM-037 Raids governance — archived

Final disposition: `raids → REUSE`.

Canary preflight PR #733 merged as `8bdeb2747356727df80a3b95073aa29a4dca7818`. Canary bounded target-proof plan PR #745 merged as `817da293a141880f7090194699a4ac38e567a2fb`. Immutable Otheryn target task-start main was `3aaf77fe27600b274d2b9c9e6bd30d887e0afd0e`.

Otheryn target proof PR #77 final head `133c12f61a1e5e392be9ee7faa9236755cbe0225` changed exactly four proof/task paths and no production path. Exact-head autofix `29988627793`, CI `29988627932`, Required `29988627768`, Linux-debug full `Run Tests`, Linux release, both Windows build paths and macOS succeeded. Comments, reviews and review threads were empty. PR #77 squash-merged as `d896141d084d381d12cc328d4b920c698eb1d55c`.

Canary governance PR #750 final head `63bd6f684e4d88c5dfe4dfbb79ec86dd01210d5f` changed exactly the two governance paths. Agent Task Ownership run `29990517255` and full final-gate CI run `29990517385` succeeded on the exact head after an unchanged-head failed-job retry; Linux-debug full tests, Linux release, both Windows build paths, macOS and Docker succeeded. Comments, reviews and review threads were empty. Canary main drift was limited to an unrelated E2E task archive with no OAM-037 path overlap. PR #750 squash-merged as `841053a1800f4e8fdb338c31bac0534ae264dabd`.

A separate one-file durable program reconciliation and separate Otheryn target-task archive remain required before OAM-038 may start.
