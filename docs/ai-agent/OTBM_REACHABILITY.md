# OTBM teleport and reachability validation

`tools/ai-agent/otbm_reachability_tool.py` is the Phase 3 consumer of the merged OTBM World Index. It validates bounded teleport and floor-transition evidence and answers a narrower question than the Quest Map Validator:

> Given an explicit map region, explicit origins/routes, real object appearance flags, indexed teleports and reviewed cross-floor transitions, is a path confirmed, only conditionally possible, or unreachable?

The tool is deterministic and read-only. It does not parse OTBM independently, execute Lua, modify the map, write `.widx`, or infer stairs/holes/ladders from sprite imagery.

## Inputs

Required:

- a `canary-otbm-world-index-v1` `.widx` produced by the existing World Index tooling;
- a compatible binary appearances catalogue or a JSON `canary-appearances-index-v1` document;
- one explicit inclusive region through `--from` and `--to`;
- at least one `--origin` or `--route`.

Optional:

- the World Index provenance manifest (`--world-manifest`); when present, its index hash is verified;
- an OTBM script-resolution report (`--script-resolution`);
- a reviewed floor-transition manifest (`--transitions`);
- diagonal movement (`--allow-diagonal`), still with corner cutting forbidden.

Generated `.widx`, map binaries, appearances binaries, client assets and reports remain local or workflow artifacts. They are not committed.

## Run

```bash
PYTHONPATH=tools/ai-agent \
python tools/ai-agent/otbm_reachability_tool.py analyze \
  /path/to/world.widx \
  --world-manifest /path/to/world.widx.json \
  --appearances /path/to/appearances.dat \
  --script-resolution /path/to/OTBM_SCRIPT_RESOLUTION.json \
  --transitions /path/to/OTBM_TRANSITIONS.json \
  --from 32055,32265,7 \
  --to 32090,32295,8 \
  --origin 32062,32271,7 \
  --route 32062,32271,7:32070,32280,8 \
  --output /tmp/OTBM_REACHABILITY.json \
  --fail-on error
```

Multiple `--origin` and `--route` arguments are accepted within the documented bounds.

## Evidence model

### Ground and blockers

Object appearance flags are used as follows:

- `bank` confirms a ground appearance;
- `unpassable` confirms a blocker;
- `avoid` is reported but remains geometrically traversable;
- `usable`, `multiUse` and `forceUse`, together with AID/UID/house-door evidence, distinguish potentially conditional barriers from static blockers.

A tile is **strictly walkable** only when:

- confirmed ground exists;
- no static blocker exists;
- no conditional blocker exists;
- every placed item has appearance evidence.

A tile is **optimistically walkable** when confirmed ground exists and no static blocker exists. Conditional barriers and unknown non-ground appearances remain explicit uncertainty.

This split prevents the tool from silently choosing whether a door is open, a quest gate is satisfied, or a dynamic script transformed an item.

### Movement

Default same-floor movement is four-directional. `--allow-diagonal` enables diagonal edges only when both orthogonal corner tiles are traversable in the same mode. Diagonal corner cutting is never allowed.

Missing coordinates are not traversable. The analysis does not assume that an absent tile is implicit floor.

### Teleports

Every World Index placement in the selected region with `teleportDestination` becomes a transition candidate. The validator checks:

- source tile existence and ground;
- destination tile existence and ground, even when the destination lies outside the selected route region;
- confirmed/conditional/static blocking state;
- optional script-resolution status for placements carrying AID/UID;
- one-way, dead-end and cycle relationships.

A teleport with a conflicting script-resolution placement emits an error and remains conditional rather than being promoted to handled.

### Stairs, holes, ladders, rope spots and other floor changes

The tool does **not** guess destination offsets from item names, sprites or visual memory. Non-teleport floor transitions are supplied through a reviewed manifest:

```json
{
  "format": "canary-otbm-transition-manifest-v1",
  "transitions": [
    {
      "id": "zirella-ladder-up",
      "kind": "ladder",
      "source": [32070, 32280, 8],
      "delta": [0, 0, -1],
      "expectedItemIds": [1948],
      "bidirectional": false,
      "uncertainties": ["requires-use"],
      "evidence": {
        "source": "reviewed bounded map export",
        "note": "destination offset verified manually"
      }
    }
  ]
}
```

`destination` and `delta` are mutually exclusive. `expectedItemIds` is optional but recommended; when present, the source tile must contain at least one expected item.

`bidirectional: true` creates both graph directions from one reviewed rule. Otherwise the transition is one-way unless another explicit reverse edge exists.

Useful uncertainty tags include:

- `requires-use` — interaction is required but does not by itself block strict graph use;
- `door-state`;
- `quest-state`;
- `dynamic-script`;
- `runtime-condition`;
- `one-way-intended`;
- `unknown`.

Door/quest/dynamic/runtime/unknown tags prevent strict eligibility while retaining optimistic eligibility when geometry permits.

The manifest contract is `docs/ai-agent/OTBM_TRANSITIONS.schema.json`.

## Route statuses

- `confirmed` — a strict path exists;
- `conditional` — no strict path exists, but an optimistic path exists;
- `unreachable` — neither path exists inside the explicit region;
- `invalid` — the request itself is invalid, for example the goal lies outside the explicit region.

Routes include distances, a bounded path sample and transition IDs used. Long paths are deterministically represented by a head/tail sample and `pathTruncated: true`.

## Mechanic reachability

AID, UID, house-door and teleport placements inside the region are classified from the union of all supplied origins:

- `confirmed` — reachable in strict mode;
- `conditional` — reachable only optimistically;
- `unreachable` — unreachable in both modes.

This is geometry evidence, not gameplay proof. It does not prove that a handler succeeds, a storage value is correct, an NPC is in the expected state or a client can complete the route.

## Transition graph findings

The validator reports:

- missing source or destination tiles;
- destinations without confirmed ground;
- confirmed static blocking;
- conditional transition use;
- expected source item mismatches;
- script-resolution conflicts/unresolved state;
- missing reverse edges;
- destinations with no optimistic movement/transition exit inside the region;
- transition cycles and closed cycles;
- mechanics unreachable from every supplied origin.

A one-way edge is a warning unless it carries `one-way-intended`, in which case it is informational. A cycle is not automatically a defect; closed cycles are highlighted separately.

## Output and limits

Report contract: `canary-otbm-reachability-v1`  
Schema: `docs/ai-agent/OTBM_REACHABILITY.schema.json`

Hard bounds:

- region coordinate volume: 1,000,000;
- distinct route starts/origins: 16;
- routes: 32;
- total transitions: 10,000;
- sample output: 10,000;
- path sample: 10,000 positions.

Exact totals remain in `summary` when samples are truncated.

Output is written through a temporary file and atomically replaced. Existing output requires `--overwrite`. Symlink output targets are rejected.

## Failure policy

`--fail-on` accepts:

- `none` — always return zero after a valid report is written;
- `warning` — return nonzero for warnings or errors;
- `error` — return nonzero only for errors (default).

`ok` means no error-severity finding. It does not mean every route is confirmed or that live gameplay was tested.

## Rendering reported locations

Use the existing factual renderer separately when visual review is needed:

```bash
PYTHONPATH=tools/ai-agent \
python tools/ai-agent/otbm_render_tool.py \
  /path/to/world.otbm \
  /path/to/client-assets \
  --from 32055,32265,7 \
  --to 32090,32295,7 \
  --output /tmp/reachability-context.png \
  --report /tmp/reachability-context.json
```

Run one render per floor. Do not use AI image generation to represent map evidence.

## Limitations

The validator does not model:

- creatures, players or movable-item occupancy;
- door open/closed state at a specific runtime instant;
- quest/account/storage/database state;
- dynamic Lua execution;
- action timing, cooldowns or combat restrictions;
- directional one-way floor semantics unless present in the reviewed transition manifest;
- physical-client behavior.

A green report is static bounded evidence. Live quest completion and physical-client behavior require separate runtime/E2E validation.
