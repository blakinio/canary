# Cloud in a Bottle evidence decisions

## RTEC-CLOUD-DEC-0001 — do not promote candidate ID 54651

**Decision:** retain `54651` as discovery-only.

**Reason:** no official-client or current Canary identity evidence links that value to Cloud in a Bottle. The selected XML paths contain no exact entry.

**Rejected alternative:** use the secondary community value as a Canary or official ID. That would cross identifier namespaces and invent correspondence.

**Revisit trigger:** accepted TCR result with exact package provenance, object identity and comparison evidence.

## RTEC-CLOUD-DEC-0002 — classify current correspondence as blocked by reference

**Decision:** do not classify the item as absent or present in Canary.

**Reason:** names and descriptions may originate from `appearances.dat`; the bounded textual scan cannot inspect that proprietary binary reference.

**Rejected alternative:** infer absence from `items.xml` and code-search misses. This ignores `Items::loadFromProtobuf()`.

**Revisit trigger:** `RTREQ-TCR-CLOUD-IN-A-BOTTLE-0001` reaches a stable reviewed result.

## RTEC-CLOUD-DEC-0003 — keep visible difficulty separate from runtime availability

**Decision:** record the official `10`, not `15`, correction only as visible documentation evidence.

**Reason:** the official fix does not expose authorization, acquisition, storage, runtime or client implementation.
