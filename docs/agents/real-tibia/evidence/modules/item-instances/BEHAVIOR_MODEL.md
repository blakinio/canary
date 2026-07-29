# Item instances behavior model

## Creation

1. `createItemBatch` delegates each requested instance to `CreateItem`, optionally with an explicit subtype.
2. `CreateItem` consults the selected static type descriptor and dispatches to specialized runtime subclasses where flags require them.
3. The base constructor initializes count, charges or fluid subtype state and materializes default duration when applicable.

## State and attributes

- Integer, string and custom attributes are stored through the item attribute container.
- Custom-attribute keys are normalized to lowercase and values support integer, string, double and boolean variants.
- Count, charges and fluids are exposed through subtype getters/setters.
- Owner GUID and runtime-ID attributes participate in owner checks.

## Copy, comparison and transformation

- `clone` creates an item of the same ID/count and deep-copies attributes.
- `equals` compares ID/store/owner state and selected integer/string attributes while excluding the store marker.
- `setID` applies ID-transition rules including duration/decay-related state.

## Serialization boundary

- Attribute readers and writers dispatch known attribute tags.
- Item-node deserialization and attribute serialization define selected persistence boundaries.

## Failure and uncertainty

The selected path does not prove type-registry correctness, container/movement behavior, scheduled decay, complete round trips, ownership safety, gameplay or parity.
