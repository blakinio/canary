# Weapon Proficiency behavior model

## Actors and boundaries

- **Player:** gains proficiency progress, selects static tree perks and may use official manipulation features.
- **Current Canary server component:** owns selected source-defined proficiency state for one Player.
- **Maintained client/protocol owners:** own packet and UI behavior.
- **Feature owner:** owns implementation and deterministic runtime proof.
- **Collector:** records evidence and gaps only.

## Selected current Canary state model

```text
no stored weapon state
  -- valid proficiency experience --> tracked weapon state
tracked weapon state
  -- threshold reached --> level unlocked
unlocked level without selected perk
  -- valid level and perk index --> one original-tree perk selected
stored state
  -- load --> invalid, locked and duplicate-level selections removed
valid selected perks
  -- applyPerks --> production stat/augment effects updated
```

State is serialised per weapon in the Player-scoped `weapon-proficiency` KV namespace with experience, mastered flag and selected perk fields.

## Official manipulation state model

```text
original perk slot
  -- modify + resource/progression/PZ guards --> modified slot with rolled effect
modified slot
  -- refine --> higher effect step
  -- maximise + item --> highest effect value
  -- reshape --> three candidate effects; choose replacement or retain current
  -- clear + confirmation --> original perk restored
```

The official model is not mapped to current Canary storage, authorization, packets or UI by the selected evidence.

## Failure and edge cases

Selected current source rejects invalid weapons, missing proficiency state, locked levels, out-of-range perk indexes and duplicate selection for one level. Stored state is filtered against current definitions. Runtime persistence failure, concurrent mutation, dust settlement, manipulation rollback, disconnect, relog and character-switch UI isolation remain unproven.

## Security and abuse boundary

Official manipulation has resource, progression and protection-zone guards. This dossier does not prove server-side authorization, replay resistance, atomic dust settlement or client-trust behavior in Canary.
