# ADR-20260723: Evolve Universal E2E through orthogonal quality dimensions and tiered execution

- Status: proposed
- Date: 2026-07-23
- Task/PR: `CAN-20260723-e2e-quality-resilience-roadmap` / PR #797
- Supersedes:
- Superseded by:

## Context

The Universal Physical E2E platform has moved beyond bootstrap. The repository has delivered the E2E-GAMEPLAY-001..008 foundation, including canonical login/relog, physical movement and route execution, typed persistence, deterministic combat and NPC promotion slices, bounded two-client orchestration, fixed-purpose client-disconnect recovery and one representative cross-system journey.

The next useful work is broader than adding another isolated scenario. The platform now needs to answer additional engineering questions:

- does a real player-to-player transaction remain correct and durable?
- does Canary recover safely after restart or an isolated infrastructure interruption?
- does retry/reconnect create exactly one durable effect?
- do concurrent actors preserve ownership and conservation invariants?
- can a failure be replayed and minimized deterministically?
- is a scenario stable across repeated clean runs?
- did a candidate revision change runtime behavior relative to an approved baseline?
- did performance, compatibility, migration or cleanup regress?
- which E2E proofs are current, stale, missing or unstable?

The existing M0-M5 evidence maturity model answers how strong a gameplay/runtime proof is. It does not naturally encode stability, performance, compatibility or diagnostic quality, and extending it to M6/M7-style levels would conflate different questions.

Running every expensive test on every pull request would also create excessive cost and increase noise. Soak, fuzzing, compatibility matrices and repeated stability runs need a different execution cadence from deterministic impacted PR gates.

## Decision

Adopt a post-008 Universal E2E architecture with four coordinated workstreams:

1. **Gameplay coverage** — real two-player trade, broader representative journeys and deterministic UI evidence where server/SQL evidence is insufficient.
2. **Reliability and resilience** — Canary restart recovery, fixture snapshot/restore, exactly-once, concurrency, controlled DB interruption, save/restart consistency, time-dependent behavior and cleanup certification.
3. **Test intelligence and diagnostics** — standard result envelope, factual coverage dashboard, differential runtime comparison, deterministic replay, failure minimization, explicit invariants, seeded reproducible fuzzing, state-machine misuse validation, dependency-driven selection and crash bundles.
4. **Operational and release confidence** — flake/stability certification, soak, performance regression, Canary/OTClient compatibility, datapack compatibility, migration E2E and a reviewed release gold suite.

Keep M0-M5 unchanged as the evidence maturity scale. Report these orthogonal quality dimensions separately:

- determinism;
- stability;
- resilience;
- exactly-once;
- concurrency;
- cleanup;
- performance;
- compatibility;
- diagnostics.

Use states such as `not-evaluated`, `pass`, `fail`, `unstable` and `blocked` rather than promoting an unrelated quality result into a higher M-level.

Introduce execution tiers:

- **PR-required** for deterministic impacted scenarios;
- **scheduled/nightly** for repeated stability, soak, fuzzing and broad matrices;
- **release certification** for reviewed gold scenarios, migration and supported compatibility cells;
- **on-demand investigation** for replay, minimization, differential expansion and controlled fault analysis.

All packages continue to reuse one canonical Universal E2E lifecycle. Fault/stress work must use isolated disposable targets and fixed-purpose code-owned seams. No arbitrary command, SQL, packet, host or external-target interface is authorized by this ADR.

## Alternatives considered

| Alternative | Benefits | Costs/reason rejected |
|---|---|---|
| Continue adding isolated feature scenarios without a successor architecture | minimal planning overhead | leaves resilience, reproducibility, diagnostics, performance and release confidence fragmented and difficult to prioritize |
| Add M6/M7/M8 levels for determinism, resilience and performance | one linear scale | conflates gameplay evidence maturity with orthogonal quality properties and makes claims misleading |
| Run every new suite on every PR | simple policy | excessive cost, long feedback loops and high noise from soak/fuzz/matrix workloads |
| Add separate runners for soak, resilience or differential testing | local implementation freedom | duplicates lifecycle, cleanup and evidence; violates the existing single-platform decision |
| Rely on automatic retries to remove flakiness | superficially greener CI | hides instability and destroys useful failure evidence |
| Allow generic arbitrary fault commands in scenario manifests | flexible fault coverage | unsafe, difficult to audit and unnecessary for bounded deterministic recovery proofs |
| Build one giant release journey instead of focused suites | one visible end-to-end signal | poor fault isolation, fragile ownership, high flakiness and inability to reuse focused scenarios selectively |

## Consequences

- Positive:
  - the post-008 roadmap is explicit and dependency-aware;
  - expensive validation can be scheduled according to cost and purpose;
  - M0-M5 claims remain semantically clean;
  - stability and failures become measurable evidence instead of hidden retry behavior;
  - replay, minimization and standardized result envelopes improve autonomous debugging;
  - exactly-once, concurrency and recovery become first-class E2E concerns;
  - release certification can assemble focused proven scenarios without creating a monolithic test.
- Negative:
  - the platform needs additional evidence contracts before some advanced packages become useful;
  - scheduled/nightly infrastructure and artifact retention may increase CI operational cost;
  - compatibility/performance claims require controlled baselines and careful threshold policies;
  - fault-injection work must wait for safe explicit seams rather than using convenient arbitrary commands.
- Follow-up:
  - publish `docs/architecture/universal-e2e-quality-resilience-roadmap.md`;
  - update `E2E_AUTOMATION_PROGRAM.md` so 001..008 are the delivered foundation and the successor roadmap owns future prioritization;
  - start future implementation packages only as separate bounded tasks after live dependency/ownership checks;
  - prefer the roadmap's first wave: result envelope, cleanup certification, real trade, Canary restart recovery, broader Journey 002 and factual coverage reporting.
- Rollback/reversal:
  - supersede this ADR with a later accepted decision; existing E2E scenarios and the canonical lifecycle remain valid because this ADR is documentation/architecture only.

## Validation

This decision is grounded in the current merged Universal E2E architecture and delivery history:

- one canonical physical lifecycle is already authoritative;
- E2E-GAMEPLAY-006 delivered bounded two-client orchestration;
- E2E-GAMEPLAY-007 delivered fixed-purpose client-disconnect recovery;
- E2E-GAMEPLAY-008 delivered one representative M4 cross-system journey;
- the existing architecture already requires deterministic first-failure evidence and separates M0-M5 proof levels;
- OTBM-aware route planning/execution is already a separate reuse boundary and is not duplicated here.

This ADR does not claim that any `E2E-QRI-*` package is implemented or runtime-proven.
