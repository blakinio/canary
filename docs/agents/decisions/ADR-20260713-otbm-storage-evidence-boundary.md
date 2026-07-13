# ADR-20260713: OTBM storage graph evidence boundary

## Status

Accepted for Phase 5.

## Context

Quest progression is distributed across Actions, MoveEvents, NPC dialogue, creature events, global systems, KV stores and database-backed helpers. A static scanner can inventory many exact operations, but it cannot safely infer callback order, branch execution, current persisted values or dynamic Lua expressions.

Phase 2 already owns explicit quest-source selection and hashing. Phase 4 already owns NPC/monster definition and placement evidence. Creating another broad source crawler in Phase 5 would duplicate policy and could silently mix active and inactive datapacks.

## Decision

1. Phase 5 requires `canary-quest-map-evidence-v1` and reads only its selected, SHA-256-verified source files.
2. Optional Phase 2 validation, Phase 4 spawn/NPC, and Phase 3 reachability reports provide context only.
3. Namespace identity is part of every node key. Player, account, KV, global and database state are never merged.
4. An explicit stage edge requires one enclosing branch with one exact same-key equality prerequisite and one literal/delete/same-key-delta write.
5. Inequalities, `else` branches, dynamic expressions and lexical proximity do not create exact edges.
6. Missing selected-scope writers/readers and unproduced prerequisites are informational scope findings, not automatic defects.
7. Incompatible outputs are called conflicting only when they share the same exact namespace/key/prerequisite.
8. Lua is never executed and generated reports remain external artifacts.

## Consequences

- The graph has fewer edges than a speculative control-flow engine, but every emitted edge has direct source evidence.
- Dynamic helper abstractions remain unresolved until a reviewed parser extension or runtime test proves their semantics.
- External initialization and cross-quest dependencies remain visible as unproven instead of being mislabeled as broken.
- Future Phase 6/7 tooling may consume graph nodes and transitions without treating them as live gameplay proof.
- Gameplay repairs require a separate focused task with runtime/evidence review.
