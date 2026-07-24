# Real Tibia Evidence Collector Prompts

These prompts are reusable task starters. Replace placeholders with exact values. They do not override `AGENTS.md`, live task ownership, programme records, PR state or repository safety rules.

---

# 1. Coordinator prompt

```text
Continue CAN-PROGRAM-REAL-TIBIA-EVIDENCE-COLLECTION in repository blakinio/canary.
Repository writes are allowed only in blakinio/canary.
Do not rely on previous chat history.

MISSION
Coordinate a bounded version-aware Real Tibia evidence-collection wave across the canonical module registry without duplicating Universal E2E, OTBM/OWA, TCR, protocol/client or feature-programme ownership.

REQUIRED STARTUP
1. Read AGENTS.md.
2. Read docs/agents/REPOSITORY_MAP.md and docs/agents/CONTEXT_ROUTING.md.
3. Read docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md.
4. Read docs/ai-agent/REAL_TIBIA_EVIDENCE_COLLECTOR_ARCHITECTURE.md.
5. Read docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md and docs/agents/REAL_TIBIA_PARITY_PLAYBOOK.md.
6. Re-fetch current main, open PRs, active tasks and exact programme state.
7. Validate the canonical registry and inspect the selected module records.
8. Search for existing dossiers, evidence records, requests, validation reports and merged PRs before creating new work.

COORDINATOR RESPONSIBILITIES
- Select one bounded wave based on module dependencies, source availability, freshness, owner-request queues, current Canary priorities and repository CI/review capacity.
- Use at most 8 simultaneous Collector workers and at most 4 open Collector worker PRs.
- Start smaller when the data model, CI or review capacity is not yet proven.
- Give each worker exactly one module dossier or one non-overlapping behavior package.
- Ensure each worker has a unique branch, task, PR and exclusive dossier paths.
- Keep shared programme, schema, template, glossary, baseline and generated-index paths coordinator-only.
- Serialize tightly coupled protocol, persistence, map-region, identifier and shared-formula work unless exact independence is proven.
- Deduplicate claims and owner requests before assigning work.
- Do not schedule a second request for the same behavior/identifier/version tuple while one is active.
- Preserve exact source and version baselines for the entire wave.
- Review and integrate worker outputs only after source, proof-level and ownership checks pass.

EVIDENCE POLICY
For every claim require:
- canonical module ID;
- bounded claim key and statement;
- authority dimension;
- exact source URL/path/SHA/build/date;
- what the source proves and does not prove;
- version applicability: announced, introduced, observed, changed, deprecated, removed, effective interval;
- separate official release, client build, protocol profile, Canary commit, map hash, datapack, appearances and schema axes;
- strongest proof level actually reached;
- PROVEN, DERIVED, UNKNOWN, CONFLICT, STALE, SUPERSEDED or REJECTED state;
- current Canary comparison;
- freshness and invalidation triggers.

Never infer an exact Tibia version from filenames, donor branches, OTBM labels or directory names.
Never convert lower proof into gameplay or physical-client proof.
Never choose a convenient source when sources conflict.

OWNER BOUNDARIES
Universal E2E owns physical execution, controlled OTClient, runtime/SQL/UI assertions, result envelopes and reusable lifecycle.
OTBM/OWA owns OTBM parsing, World Index, Script Resolution, Reachability, Semantic Diff, factual rendering and certification.
TCR owns official-client package parsing, normalization and identifier correlation.
Feature programmes own feature-specific fixtures, expected values, gameplay implementation and scenarios.

Collector workers may create structured requests to those owners and consume stable outputs. They must not edit owner implementation paths or create substitute infrastructure.

WAVE OUTPUT
Produce:
- exact worker assignments and ownership paths;
- shared version/source baselines;
- dependency/serialization decisions;
- list of active owner requests;
- merged/reviewed evidence coverage;
- conflicts and unknowns;
- factual progress by module and evidence dimension;
- exact next wave.

Do not use an opaque percentage or parity score as a release claim.
Do not claim faithful whole-game reproduction merely because dossiers exist.
Deliver through bounded tasks, draft PRs, current-head validation, review and normal repository lifecycle.
```

---

# 2. Collector worker prompt

```text
Collect and normalize Real Tibia evidence for one bounded module/package in blakinio/canary.
Repository writes are allowed only in blakinio/canary.
Do not rely on previous chat history.

ASSIGNMENT
Module: <module-id>
Bounded package/question: <exact behavior package>
Official target baseline: <release/client build/date or UNKNOWN>
Canary baseline: <exact commit plus separate protocol/map/datapack/assets/schema revisions>
Owned dossier paths: <exact paths>
Coordinator task/coordination ID: <id>

REQUIRED STARTUP
1. Read AGENTS.md.
2. Read docs/agents/REPOSITORY_MAP.md and docs/agents/CONTEXT_ROUTING.md.
3. Read docs/agents/programs/REAL_TIBIA_EVIDENCE_COLLECTION_PROGRAM.md.
4. Read docs/ai-agent/REAL_TIBIA_EVIDENCE_COLLECTOR_ARCHITECTURE.md.
5. Read docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md and docs/agents/REAL_TIBIA_PARITY_PLAYBOOK.md.
6. Read the canonical registry record for <module-id> and its linked module programme/validation reports.
7. Re-fetch current main, active tasks, open PRs and source baselines.
8. Search existing evidence, requests, reports and PRs for the exact claim/package before collecting anything new.
9. Create one task, branch and early draft PR with exclusive module-specific paths.

SCOPE RULE
Work on exactly one module dossier or one independently reviewable behavior package. Do not attempt to complete the whole module when it contains several independent findings.

COLLECTION METHOD
A. Decompose the package into bounded claims.
B. For each claim select the correct authority dimension.
C. Check every applicable source class:
   - official Tibia news/update/guide;
   - official staff clarification;
   - reproducible official-client observation;
   - maintained wiki as secondary evidence;
   - current exact Canary source/registrations/tests/runtime;
   - maintained OTClient/protocol evidence when relevant;
   - pinned upstream Canary/CrystalServer as implementation candidates only;
   - stable OTBM/OWA evidence when map mechanics matter;
   - stable TCR evidence when official-client reference data matters;
   - existing Universal E2E results when physical/runtime proof matters.
D. Pin exact URLs, dates, SHAs, builds, paths, symbols, report IDs and external artifact hashes.
E. Record what each source proves and does not prove.
F. Preserve missing, conflicting, stale or inaccessible evidence explicitly.

DETAILED BEHAVIOR DESCRIPTION
Document applicable:
- purpose and exclusions;
- actors and authority boundaries;
- inputs and outputs;
- states and every known transition;
- triggers, guards, authorization and preconditions;
- resources consumed/produced;
- formulas, values, units, rounding, caps and selection rules;
- cooldown/time/server-save behavior;
- account/character/world scope;
- persistence, migration, rollback, exactly-once and recovery;
- protocol fields, capability gates and client UI behavior;
- map, NPC, spawn, boss, quest, item and route dependencies;
- concurrency, repeated requests and multi-client behavior;
- disconnect, relog, death, restart, stale state and malformed input;
- security and abuse boundaries.

VERSION HISTORY IS MANDATORY
For every behavior/value record, where evidence permits:
- announced_in;
- introduced_in;
- observed_in with exact build/date;
- changed_in;
- deprecated_in;
- removed_in;
- effective_from/effective_until;
- confidence: proven-official, proven-observation, supported-secondary, derived-range, conflicting or unknown.

Keep official release, client build, protocol profile, Canary commit, OTClient commit, map hash, datapack revision, appearances revision, spawn/NPC sidecar revision and database schema revision separate.
Use derived-range when only bounds are known. Never invent an exact first version.

CANARY COMPARISON
Prove separately:
- definition;
- registration;
- runtime path;
- persistence;
- protocol;
- deterministic behavior test;
- gameplay;
- physical-client result.

Classify only the bounded claim/package. Do not call a fix missing until both target and current Canary behavior are sufficiently proven.

RATIONALE
Record durable decision rationale:
- selected option;
- factual constraints;
- evidence IDs;
- trade-offs;
- compatibility effect;
- rejected alternatives and concrete reasons;
- remaining unknowns;
- revisit trigger.

Do not store hidden chain-of-thought or narrative about the agent's internal deliberation.

OWNER REQUESTS
When proof is missing, create a structured request instead of crossing ownership boundaries.

For Universal E2E requests specify:
- exact observable behavior;
- setup/action/assertions;
- required server/client/SQL/UI/persistence checks;
- minimum M0-M5 maturity and quality dimensions;
- version/capability cells;
- evidence already available;
- generic platform gap only as a suggestion.

For OTBM/OWA requests specify:
- exact map/index provenance;
- requested World Index/Script Resolution/Reachability/Semantic Diff/certification dimensions;
- positions/bounds only when reviewed;
- runtime proof still needed after static evidence.

For TCR requests specify:
- missing client-reference dimension;
- expected normalized output;
- identifier namespace and mapping requirements;
- external/proprietary-data boundary;
- downstream consumer claim.

You must not implement E2E, OTBM/OWA or TCR capabilities in a Collector task.

OUTPUT
Update only your owned module/package dossier, records, decisions, requests and task file.
Do not edit shared programme/schema/template/generated-index paths.
Do not commit raw pages, copied wiki prose, videos, screenshots, maps, client packages, captures, binaries or large reports.

COMPLETION
A dossier/package can complete with explicit UNKNOWN, CONFLICT, STALE or blocked-by-owner-request states.
Report the strongest proof actually reached and all nonclaims.
Run applicable validation, review the exact diff, keep the task checkpoint current and deliver through the normal PR lifecycle.
```

---

# 3. Evidence reviewer prompt

```text
Review one Real Tibia Collector worker PR in blakinio/canary without expanding its scope.

Verify:
- exact task/branch/PR ownership;
- one bounded module/package only;
- canonical module IDs and claim IDs;
- source provenance, dates, SHAs/builds and selected sections;
- correct authority dimension;
- complete proves/does-not-prove boundaries;
- no source conflict hidden or resolved by convenience;
- no guessed values, formulas, IDs, coordinates, packet fields or versions;
- mandatory version history with separate version axes;
- accurate current Canary baseline and proof-level decomposition;
- detailed behavior/state/persistence/protocol/map/edge-case coverage where applicable;
- rationale contains decisions/evidence/trade-offs/rejections, not private chain-of-thought;
- owner requests target the correct programme and do not smuggle implementation into Collector scope;
- no edits to E2E, OTBM/OWA, TCR, feature or another worker's paths;
- no proprietary, binary, captured or large external material committed;
- freshness and supersession are explicit;
- completion statement does not overclaim module or whole-game parity.

Accept explicit UNKNOWN or CONFLICT when honest and complete.
Request changes when uncertainty is guessed away, a weak source is promoted, historical versions are invented, ownership is crossed or a parity claim exceeds the evidence.
```
