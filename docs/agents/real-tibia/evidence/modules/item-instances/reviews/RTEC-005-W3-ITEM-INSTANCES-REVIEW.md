# RTEC-005 wave 3 item-instances candidate review

## Candidate

- Evidence: `RT-ITEM-INSTANCES-0001`
- Worker PR: #1022
- Status: pending coordinator adjudication
- Proposed proof level: `runtime-path-proven`

## Source pins

- `src/items/item.cpp` — `62e8117dc7dcb135d4849c22832a251032420a93`
- `src/items/item.hpp` — `a882313ba808ff0170d5231953694f6345af1399`
- `src/items/functions/item/attribute.cpp` — `715b5ac3e0b231506b338f64bd10074548de0c37`
- `src/items/functions/item/attribute.hpp` — `4f6ca169a47fe6d7b6ff88f286a28e755af0959e`
- `src/items/functions/item/custom_attribute.cpp` — `701a65fa142df5233ee1ad2a25e8b43c25262e07`
- `src/items/functions/item/custom_attribute.hpp` — `54f532fd4e15283f71994884ad71040b090f042f`

## Worker finding

The selected path contains item factory/subclass dispatch, count/charge/fluid subtype state, integer/string/custom attributes, clone/equality/ID-transition behavior, ownership-related attributes and explicit item attribute serialization/deserialization boundaries.

## Required coordinator checks

- Confirm every symbol and observation is present at the pinned baseline.
- Confirm no ItemType-data, container, movement, decay, complete persistence, ownership-safety, gameplay or parity claim escaped the boundary.
- Decide whether to accept as written, narrow, reject or request owner evidence.
- Populate module/global indexes only after acceptance.

## Explicit nonclaims

This review does not establish static ItemType correctness, container/movement behavior, scheduled decay, serialization completeness or compatibility, ownership safety, gameplay or Real Tibia parity.
