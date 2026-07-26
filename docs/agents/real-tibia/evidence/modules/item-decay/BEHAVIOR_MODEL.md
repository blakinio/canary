# Item Decay behavior model

## Selected source flow

```text
item with duration
  -- Decay::startDecay -->
DURATION_TIMESTAMP + ordered decayMap bucket
  -- dispatcher event -->
Decay::checkDecay
  -- elapsed bucket -->
Decay::internalDecayItem
  -- decayTo != 0 --> Game::transformItem
  -- decayTo == 0 and not map-loaded --> Game::internalRemoveItem
```

`Decay::stopDecay()` is a separate cancellation path that removes the item from its timestamp bucket and clears decay state while preserving remaining duration when available.

## Separate questions

- Source registration is distinct from scheduler execution.
- Scheduler execution is distinct from wall-clock accuracy.
- Transform/removal call paths are distinct from item-specific metadata correctness.
- Restart recovery and persistence are not established by the selected files.
- A current Canary source path is not physical gameplay or Real Tibia parity proof.

## Failure boundary

The selected files do not establish behavior after process restart, safe singleton shutdown, correctness of every `decayTo`, or observed client-visible timing.
