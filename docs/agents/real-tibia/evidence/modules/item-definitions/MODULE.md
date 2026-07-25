# Item Definitions evidence dossier — Cloud in a Bottle

## Status and scope

- Module: `item-definitions`.
- Campaign: RTEC-004 wave 1.
- Canary baseline: `8ef88972fd1c473b9f3c0a5cfb9bed98c78bdbc9`.
- Exact selected-path scan: run `30171827237`, artifact `8623126188`.
- Official-source verification date: `2026-07-25`.
- Dossier state: `blocked-by-owner-request`.

This package covers only the official 2026-07-21 Cloud in a Bottle difficulty/description correction and the exact current Canary item-definition loader boundary. It does not claim broad item-catalogue coverage.

## Official visible correction

The official fix states that the description was wrong: Cloud in a Bottle becomes available at difficulty `10`, not `15`.

This proves the visible correction and item name. It does not prove an item/client/server ID, exact client build, acquisition implementation, authorization, runtime behavior or Canary correspondence.

## Current Canary selected-path evidence

The exact scan found no official name, bounded spelling variant, `Radiant Nimbus`, `Moonsilver` or discovery-only candidate ID `54651` in the selected XML/item-loader/parser paths. `data/items/items.xml` contains no exact `id="54651"` entry.

The scan is bounded. Search misses are not proof that the item is absent under another name or identifier.

## Loader boundary

Current Canary loads base item IDs, names and descriptions from `data/items/appearances.dat` through `Items::loadFromProtobuf()`. XML loading can overlay names and description attributes through `Items::loadFromXml()`, `Items::parseItemNode()` and `ItemParse::parseDescription()`.

Therefore the selected textual definitions cannot resolve whether Cloud in a Bottle exists in the exact appearances package. The binary/proprietary reference remains outside Collector authority.

## Owner request

`RTREQ-TCR-CLOUD-IN-A-BOTTLE-0001` requests exact user-supplied official-client reference evidence from the existing OTBM Tibia Client Reference Programme. It must identify the exact object/name/description/build and compare that reference with the pinned Canary appearances revision without importing or mutating assets.

## Evidence records

| ID | Claim | State | Proof |
|---|---|---|---|
| `RT-ITEM-DEFINITIONS-0001` | official difficulty/description correction | `PROVEN` | `definition-found` |
| `RT-ITEM-DEFINITIONS-0002` | exact selected-path scan and appearances loader boundary | `PROVEN` | `definition-found` |

## Nonclaims

This dossier does not prove item absence, item ID `54651`, appearance identity, exact client build, unlock authorization, acquisition, runtime behavior, maintained-client behavior, physical-client behavior or full item-definition parity.
