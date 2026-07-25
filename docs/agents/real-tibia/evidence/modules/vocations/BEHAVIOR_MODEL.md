# Vocations behavior model

## Authority and baseline

This model describes only transitions visible in current source at Canary commit `930e0a15767b7e5348bb36c679fa5e458a76f184`. It is not a runtime trace.

## Registry lifecycle

```text
UNLOADED
  -- loadFromXml() parses XML successfully --> DEFINITIONS_LOADED
  -- loadFromXml() fails -------------------> LOAD_FAILED

DEFINITIONS_LOADED
  -- reload() clears then successful load --> DEFINITIONS_LOADED
  -- reload() clears then failed load -----> LOAD_FAILED
```

The selected source proves the presence of these control paths. It does not prove their behavior under a running server, concurrent access or existing online players.

## Lookup model

```text
configured id   -> configured Vocation entry
unknown id      -> no entry / warning
base vocation   -> first distinct entry with fromVocation == base id
no such entry   -> VOCATION_NONE
```

The XML snapshot contains these bounded promotion edges:

- Sorcerer `1` → Master Sorcerer `5`;
- Druid `2` → Elder Druid `6`;
- Paladin `3` → Royal Paladin `7`;
- Knight `4` → Elite Knight `8`;
- Monk `9` → Exalted Monk `10`.

## Level-gain transition

Expected player-state transition requested from the feature owner:

```text
(base vocation, level N, configured HP/mana/cap gains)
  -- one controlled level advancement -->
(level N+1, prior maxima/capacity plus configured gains)
```

Status: `UNKNOWN`. Static XML and loader evidence do not prove this executed transition.

## Promotion transition

Expected player-state transition requested from the feature owner:

```text
(base vocation)
  -- authorized promotion owned by feature/runtime paths -->
(configured promoted vocation)
```

Status: `UNKNOWN`. The registry lookup exists; eligibility, payment, persistence and executed character-state mutation are outside Collector ownership.

## Failures and invariants

- An invalid XML document can prevent a successful load.
- An unknown ID does not produce a configured entry.
- Promotion lookup must not return the same entry as the base ID.
- No inference is made about thread safety, transactionality, live reload safety or persistence.
