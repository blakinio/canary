# Real Tibia Module Maturity Model

Maturity is multidimensional. A module with substantial code may still lack current evidence, persistence proof, protocol proof or gameplay E2E. Never collapse these dimensions into one optimistic status.

## Lifecycle

- `inventory`: registered for discovery; no claim of completeness;
- `active`: currently maintained or governed by a program/queue;
- `paused`: intentionally not progressing, with preserved state;
- `historical`: retained for compatibility/history, not current parity work;
- `deprecated`: being replaced or no longer recommended.

## Maturity dimensions

### Implementation

- `not-assessed`: not inventoried;
- `inventory`: implementation locations identified;
- `partial`: some required behavior exists, gaps remain or are unverified;
- `verified`: implementation matches the currently established contract;
- `not-applicable`: dimension does not apply.

### Evidence

- `not-assessed`: no controlled comparison;
- `inventory`: likely sources identified;
- `mapped`: source roles and implementation surfaces mapped;
- `audited`: required sources compared with explicit conclusions;
- `verified`: current evidence supports the required contract;
- `not-applicable`.

### Persistence and protocol

- `not-assessed`;
- `missing`;
- `partial`;
- `verified`;
- `not-applicable`.

`verified` requires the relevant boundary tests, not merely a serializer, database column or parser definition.

### Automated tests

- `not-assessed`;
- `missing`;
- `unit`;
- `integration`;
- `verified` — required focused and integration contracts are covered for the audited scope;
- `not-applicable`.

### Runtime validation

- `not-assessed`;
- `missing`;
- `limited` — controlled runtime proof exists for only part of the contract;
- `verified`;
- `not-applicable`.

### Gameplay E2E

- `not-assessed`;
- `missing`;
- `limited`;
- `verified`;
- `not-applicable`.

Physical-client E2E is a separate proof level. CI compilation or unit tests do not satisfy it.

## Promotion rules

A maturity value may only be raised when the module program, validation report, task or merged PR contains exact evidence. Lower it when a previously trusted source is stale, a regression is found, or the required contract expands.

`conforming` is deliberately not a registry maturity value. It is a conclusion for a specific versioned scope after all required dimensions are proven.
