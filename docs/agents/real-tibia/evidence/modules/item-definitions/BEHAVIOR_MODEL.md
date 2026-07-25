# Cloud in a Bottle behavior model

## Evidence actors

- **Official service:** publishes the visible item name and difficulty correction.
- **Canary item registry:** loads client-derived appearances, then XML overlays and parsed attributes.
- **TCR owner:** may inspect an exact user-supplied official-client package outside Git.
- **Collector:** records source boundaries and owner requests; it does not parse proprietary assets or implement item behavior.

## Current Canary definition flow

```text
exact appearances package
  -- Items::loadFromProtobuf --> base item id, name, description, flags
items.xml
  -- Items::loadFromXml / parseItemNode --> XML id/name/attribute overlays
XML description attribute
  -- ItemParse::parseDescription --> itemType.description overlay
loaded non-empty name
  -- lower-case registration --> Items::getItemIdByName lookup
```

A missing textual XML/name match cannot establish absence because the base identity may originate from `appearances.dat`.

## Requested TCR resolution flow

```text
exact official client package + provenance
  -- read-only TCR index --> exact object id, name, description, build
exact Canary appearances revision
  -- read-only comparison --> matching, conflicting or unresolved identity
Collector consumption
  -- reviewed result --> evidence update without asset import
```

## Separate questions

- The official difficulty value is visible documentation evidence.
- Description display is distinct from item identity.
- Item identity is distinct from unlock authorization.
- Unlock authorization is distinct from acquisition and runtime behavior.
- A matching client object would not prove Canary gameplay or availability.

## Failure boundary

Until exact client-reference evidence exists, identity and Canary correspondence remain blocked. Candidate ID `54651` and secondary related names remain discovery leads only.
