# ADR-20260718: Separate static world intelligence from physical E2E execution

- Status: proposed
- Date: 2026-07-18
- Task/PR: `CAN-20260718-universal-e2e-gameplay-roadmap` / PR #563
- Supersedes:
- Superseded by:

## Context

The repository now has a merged Universal Physical E2E platform and physical proofs for login/relog, movement, non-teleport floor change and teleport. It also has a mature static OTBM evidence stack with World Index, Reachability and Script Resolution.

Future gameplay tests need to navigate real maps, interact with mechanics, validate feature outcomes and prove persistence without forcing feature agents to hand-author long directional sequences or duplicate map/pathfinding logic.

At the same time, static map evidence and runtime gameplay evidence answer different questions:

- OTBM/static tools can prove map structure, graph reachability and handler correlation;
- only a real controlled OTClient against the exact Canary runtime can prove that the physical gameplay action actually succeeds.

Draft PR #562 separately owns the detailed OTBM-to-E2E routing bridge. The broader E2E programme needs a durable responsibility boundary that future agents cannot accidentally bypass.

## Decision

Adopt a layered validation architecture with one Universal Physical E2E platform:

1. deterministic disposable runtime environment;
2. static OTBM/world/mechanic evidence;
3. OTBM-to-E2E route/landmark/interaction bridge;
4. generic physical action execution through the controlled real OTClient;
5. feature-owned scenario suites and expected values;
6. shared assertion/persistence interfaces;
7. common evidence and diagnostics;
8. advanced multi-client and fault/recovery orchestration added only through bounded platform tasks.

Static OTBM route planning remains outside the E2E runner. E2E consumes a validated executable route plan and proves physical execution. It must not implement an independent map parser or pathfinder.

Feature suites consume platform infrastructure read-only. When a feature requires a new generic client action, assertion, multi-client capability or recovery seam, that capability is implemented first in a separate bounded Universal E2E platform task with focused tests.

Nontrivial map navigation should migrate to OTBM-aware route execution once the routing programme is stable. Tiny bounded directional probes may remain only when the movement itself is the subject under test.

## Alternatives considered

| Alternative | Benefits | Costs/reason rejected |
|---|---|---|
| Keep hand-authored movement sequences in every feature scenario | simple manifests and no integration contract | brittle, blind to map structure, duplicates knowledge, difficult to diagnose and maintain |
| Add a new pathfinder directly inside Universal E2E | E2E could plan and execute autonomously | duplicates existing Reachability/World Index logic and creates competing map truth |
| Let each feature own its own physical workflow/runner | local autonomy | duplicates lifecycle, client setup, cleanup and evidence; violates the existing platform contract |
| Treat static Reachability success as sufficient feature validation | fast and cheap | does not prove real OTClient behavior, runtime conditions, feature outcome or persistence |
| Build a single giant end-to-end journey first | broad visible coverage | difficult fault isolation, hidden missing capabilities, high flakiness and poor ownership boundaries |

## Consequences

- Positive:
  - one canonical runtime lifecycle and evidence format;
  - OTBM knowledge can improve navigation without leaking pathfinding into E2E;
  - feature scenarios become intent- and assertion-focused;
  - failures can be classified by static preflight, route execution, feature action, assertion, persistence or infrastructure layer;
  - new capabilities can be added incrementally and reused across suites.
- Negative:
  - some feature work must wait for explicit platform or OTBM bridge dependencies;
  - route-plan and assertion interfaces require stable contracts between programmes;
  - a scenario may need both static preflight evidence and physical runtime evidence.
- Follow-up:
  - complete and merge the OTBM-aware routing programme from PR #562;
  - implement `E2E-GAMEPLAY-002` route consumption;
  - add quest/NPC, combat, persistence, multi-client, resilience and cross-system work packages in the order recorded by the E2E programme.
- Rollback/reversal:
  - supersede this ADR with a new accepted architecture decision; existing Universal E2E remains usable because this ADR does not change runtime code.

## Validation

The decision is based on the current repository architecture and merged proof history:

- PR #245 established one reusable Universal Physical E2E platform;
- PR #446 added generic declarative physical gameplay actions;
- PR #477 added generic changed-scenario selection;
- PRs #481, #512 and #525 proved real physical movement, floor change and teleport;
- the existing OTBM World Index, Reachability and Script Resolution tools already own static map/mechanic evidence;
- draft PR #562 explicitly defines the OTBM-aware route-integration programme without adding a second parser/pathfinder/orchestrator.

This ADR is documentation-only and does not claim that the future work packages are already implemented or runtime-proven.
