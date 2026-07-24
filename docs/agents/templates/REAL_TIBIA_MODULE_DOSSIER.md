# <Module name> — Real Tibia Evidence Dossier

> Module ID: `<module-id>`  
> Dossier status: `planned|collecting|review-needed|dossier-complete|stale`  
> Current official baseline: `<release/client build/date>`  
> Canary baseline: `<commit + separate protocol/map/datapack/assets/schema revisions>`  
> Last reviewed: `<date>`

## 1. Purpose

Describe what the module does for the player and for the server. Keep the statement bounded and distinguish official product purpose from current Canary architecture.

## 2. Scope

### Included

- ...

### Excluded

- ...

### Trust and ownership boundaries

- server-owned decisions:
- client representation:
- map/content dependencies:
- persistence owner:
- protocol owner:
- related feature programmes:

## 3. Actors

| Actor | Role | Authority | Evidence |
|---|---|---|---|
| player | | | |
| server | | | |
| client | | | |
| world/NPC/creature | | | |

## 4. Inputs and outputs

### Inputs

- player actions;
- packets/client requests;
- timers/server save;
- map/item/NPC interactions;
- database/configuration state.

### Outputs

- player-visible result;
- client/UI update;
- server state change;
- persistence change;
- world/economy effect.

## 5. Behavior overview

Describe the full normal flow:

```text
input
  -> authorization and guards
  -> state transition
  -> server mutation
  -> persistence boundary
  -> client response
  -> visible result
```

Every material statement must reference evidence IDs.

## 6. State model

### States

| State | Meaning | Entry conditions | Exit conditions | Evidence |
|---|---|---|---|---|
| | | | | |

### Transitions

| Transition | Trigger | Preconditions/guards | Effects | Failure/rollback | Versions | Evidence |
|---|---|---|---|---|---|---|
| | | | | | | |

For each transition consider authorization, resource consumption, generated resources, repeatability, idempotency, cooldown, concurrency and client synchronization.

## 7. Rules, formulas and values

Each independently changing value should be backed by its own evidence record.

| Rule/value | Current official | Historical changes | Canary | Status | Evidence |
|---|---|---|---|---|---|
| | | | | | |

Document units, rounding, caps, order of operations, selection rules, random distributions and condition-specific modifiers.

## 8. Version history

Do not use one ambiguous version axis. Keep official release, client build, protocol profile, Canary commit, map hash, datapack, appearances and schema revisions separate.

| Event | Official release/build | Behavior change | Applicability | Confidence | Source/evidence |
|---|---|---|---|---|---|
| announced | | | | | |
| introduced | | | | | |
| changed | | | | | |
| deprecated/removed | | | | | |
| current observation | | | | | |

Use `derived-range` when only lower/upper version bounds are known. Never invent an exact first version.

## 9. Persistence and recovery

Document:

- state scope: account/character/world/guild/house/session;
- storage/table/schema or abstract contract;
- load/save timing;
- transaction boundary;
- migration and legacy data;
- retry/exactly-once behavior;
- stale or concurrent writes;
- disconnect/relog/restart/server-save behavior;
- rollback and corruption handling.

| Concern | Real Tibia evidence | Canary evidence | Status | Owner request |
|---|---|---|---|---|
| | | | | |

## 10. Protocol and client

Document applicable messages, fields, ordering, capability gates, UI interpretation, resynchronization and compatibility behavior.

| Surface | Official/client evidence | Canary/OTClient evidence | Status | Evidence/request |
|---|---|---|---|---|
| | | | | |

No packet field or byte may be guessed.

## 11. Map and content dependencies

Document applicable geometry, zones, positions, item namespaces, AID/UID, teleports, houses, NPCs, spawns, bosses, raids, routes and handlers.

| Dependency | Static evidence | Runtime evidence | Proof boundary | Evidence/request |
|---|---|---|---|---|
| | | | | |

Static success is not gameplay success.

## 12. Concurrency and multi-actor behavior

Evaluate:

- repeated requests/double click;
- multiple clients;
- party/guild/world-global state;
- simultaneous settlement;
- stale writers;
- exactly-once behavior;
- ordering and race conditions.

## 13. Failure and edge cases

| Case | Expected Real Tibia behavior | Canary behavior | Status | Evidence/request |
|---|---|---|---|---|
| disconnect | | | | |
| relog | | | | |
| server restart | | | | |
| server save | | | | |
| death | | | | |
| missing capacity/item | | | | |
| unsupported client | | | | |
| malformed/duplicate request | | | | |
| map/datapack mismatch | | | | |

## 14. Security and abuse boundaries

Record server-side authorization, replay protection, economy duplication, cooldown bypass, scope escalation and client-trust assumptions.

## 15. Evidence matrix

Check every applicable source column. `not-applicable` is allowed; silent omission is not.

| Claim/mechanic | Official material | Official observation | Wiki | Canary | Upstream/Crystal | Maintained client | OTBM/TCR | Tests/runtime/E2E | Conclusion |
|---|---|---|---|---|---|---|---|---|---|
| | | | | | | | | | |

## 16. Current Canary comparison

### Conforming

- ...

### Differing

- ...

### Partial or conflicting

- ...

### Blocked by reference

- ...

### Intentionally unsupported

- ...

Do not classify a fix as missing until current Canary behavior and the target behavior are strongly proven.

## 17. Decisions and rationale

| Decision ID | Decision | Evidence/constraints | Trade-offs | Rejected alternatives | Revisit trigger |
|---|---|---|---|---|---|
| | | | | | |

Store auditable rationale, not hidden chain-of-thought.

## 18. Gaps and owner requests

| Request ID | Owner programme | Exact question | Required proof | Status | Blocking |
|---|---|---|---|---|---|
| | | | | | |

The Collector may propose extensions to E2E, OTBM/OWA or TCR but must not implement owner capabilities in this dossier task.

## 19. Freshness

| Dimension | Last verified | Warning threshold | Invalid threshold | Current state | Refresh trigger |
|---|---|---|---|---|---|
| official behavior | | | | | |
| Canary | | | | | |
| maintained client | | | | | |
| map/datapack/assets | | | | | |
| runtime/E2E | | | | | |

## 20. Proof summary

| Dimension | Strongest level | State | Exact evidence | Does not prove |
|---|---|---|---|---|
| definition | | | | |
| registration | | | | |
| runtime | | | | |
| persistence | | | | |
| protocol | | | | |
| behavior test | | | | |
| gameplay | | | | |
| physical client | | | | |

## 21. Completion statement

State only one of:

- dossier incomplete;
- dossier complete with explicit unknowns/conflicts;
- bounded module behavior conforming for the selected baseline;
- bounded module behavior differing for the selected baseline;
- parity blocked by owner request;
- stale and requires refresh.

Never claim whole-game parity from one dossier.
