# Item instances evidence module

## Boundary

This dossier covers the selected current-Canary source path for runtime item creation, instance subtype state, integer/string/custom attributes, clone/equality behavior, transformations and item serialization boundaries.

## Authoritative current-Canary paths

- `src/items/item.cpp`
- `src/items/item.hpp`
- `src/items/functions/item/attribute.cpp`
- `src/items/functions/item/attribute.hpp`
- `src/items/functions/item/custom_attribute.cpp`
- `src/items/functions/item/custom_attribute.hpp`

## In scope

- Item factory and subclass dispatch from ItemType flags.
- Count, charge and fluid subtype state.
- Integer, string and custom attribute representation.
- Clone, equality and ID transformation paths.
- Owner GUID/runtime-ID attributes and owner checks.
- Attribute and item-node serialization/deserialization boundaries.

## Explicitly out of scope

- Static ItemType registry correctness or source-data completeness.
- Containers and movement orchestration.
- Scheduled decay execution.
- Serialization round-trip completeness or compatibility.
- Ownership security, gameplay behavior and Real Tibia parity.

## Evidence posture

Static current-Canary source inspection can establish only a bounded runtime path. Candidate records remain unpublished until coordinator adjudication and generated-index inclusion.
