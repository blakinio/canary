# CAN-20260721 — OTS future gameplay systems roadmap

## Status

ACTIVE — durable design/handoff record. This task is documentation-only unless a later task explicitly implements one of the systems.

## Goal

Persist the user's OTS gameplay/system redesign discussion so a continuation agent can resume without relying on chat history.

## Owned paths

- `docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md`
- `docs/agents/tasks/active/CAN-20260721-ots-future-gameplay-roadmap.md`

## Live PR

- PR #664 — `docs(ai-agent): persist OTS future gameplay systems roadmap`
- Branch: `docs/ots-future-roadmap-20260721`

## Scope

- Record user-requested future systems, redesign directions, anti-frustration principles, anti-abuse constraints, and open design questions.
- Preserve the RubinOT feature-audit classification discussed with the user as research context, not as implementation truth.
- Do not implement gameplay changes in this task.

## Evidence state

- `PROVEN`: the user explicitly requested the ideas and design directions recorded in the roadmap.
- `DERIVED`: architectural groupings and dependency relationships are organizational conclusions from the discussion.
- `UNKNOWN`: exact balance values, implementation feasibility, current local implementation details, and any external-system behavior not reverified at implementation time.

## Context checkpoint

### User design philosophy

- The game should remain challenging and risky, but avoid legacy friction that mainly causes frustration or player churn.
- Death should be frequent enough to matter and carry loss/risk, but should not erase disproportionate amounts of long-term progression.
- Convenience should generally be earned by engaging with content first rather than granted globally from day one.
- Anti-abuse systems should prefer telemetry, pattern detection, risk scoring, and review over automatic punishment based on one event.
- Money sinks should be desirable/convenient/luxury systems rather than punitive taxes on basic play.
- Modern client/UI work must support large displays, ultrawide, high DPI, 1440p and 4K without creating unfair competitive visibility.

### Durable roadmap

The full backlog and design notes are stored in:

`docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md`

### Important implementation constraint

Every future implementation must independently verify current Canary/OTClient behavior, current Real Tibia behavior when parity is relevant, current repository contracts, and abuse/balance implications. This roadmap is a design source, not proof that a feature already exists or is technically ready.

### next_action

Continue appending newly agreed OTS future-system ideas to `docs/ai-agent/OTS_FUTURE_GAMEPLAY_SYSTEMS.md`. When the user chooses a feature for implementation, create a separate bounded active task, perform the normal live-state preflight, and implement only that selected scope.
