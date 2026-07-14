# Real Tibia Crystal global-map snapshot audit

## Pinned sources

- Canary commit: `bd5c7bee5a0524dedcd786ef52152f475dd424a6`
- Baseline OTBM: `a80de1dda6a9aca3956a9d5b7fb2e0caebb451570d26853fc21beb40d5f31da2` (184,776,037 bytes)
- CrystalServer commit: `fc0d53b9f9965463b6082c07e6d3d482294541a7`
- Crystal repository blob: `3bd40d14fefec41f24c4b3ae879e420be1a831ef55b95dcbec721e587a09b034` (52,836,960 bytes), encoded as **gzip** despite the `.otbm` extension.
- Decompressed Crystal OTBM: `4b2099f38df05d4be68d1ba1265754e9fd6da09742025d92644fa4b1a12eb120` (186,660,172 bytes)

Both maps use OTBM version **4**, item major/minor **4/4**, dimensions **35143×34812**, maximum item depth **2**, and report zero unknown attribute tails.

## Executive conclusion

**Do not replace the complete Canary map with the Crystal map.** This is not a small Targuna-only update. The exact comparison found **1,884,169 changed coordinates** across **19,099,041 coordinates present in either snapshot** (9.87%). Crystal contains **1,126,280 tiles absent from the baseline**, while the baseline contains **101,373 tiles absent from Crystal**.

The snapshots still share **17,871,388 coordinates**, of which **17,214,872 are identical**. At shared coordinates, however, **639,821 item stacks**, **19,531 tile metadata records**, and **382 mechanic payloads** differ. One-sided changes also occur at coordinates far outside the principal global-map cluster, proving that wholesale replacement would import unrelated or custom content together with newer Real Tibia regions.

The safe strategy is bounded extraction and validation of Targuna and Newhaven, not a global swap.

## World-index summary

| Metric | Canary baseline | Crystal | Delta |
|---|---:|---:|---:|
| Tiles | 17,972,761 | 18,997,668 | +1,024,907 |
| Item placements | 23,359,571 | 24,504,223 | +1,144,652 |
| Mechanic placements | 9,339 | 9,323 | -16 |
| Query areas | 1,171 | 1,197 | +26 |
| Raw OTBM area nodes | 1,175,983 | 167,838 | -1,008,145 |

The raw area-node count reflects OTBM serialization/editor structure and is not a semantic map-difference metric. Exact coordinate and query-area results are the relevant evidence.

## Exact coordinate comparison

| Category | Count |
|---|---:|
| Shared coordinates | 17,871,388 |
| Identical shared coordinates | 17,214,872 |
| Changed shared coordinates | 656,516 |
| Canary-only tiles | 101,373 |
| Crystal-only tiles | 1,126,280 |
| Shared tile metadata changed | 19,531 |
| Shared item stacks changed | 639,821 |
| Shared mechanic payloads changed | 382 |
| Any changed coordinate | 1,884,169 |

## Largest changed 256×256 regions

| Base X | Base Y | Z | Changed coordinates |
|---:|---:|---:|---:|
| 33280 | 32768 | 7 | 59,637 |
| 33792 | 32000 | 7 | 55,247 |
| 33536 | 32768 | 7 | 47,595 |
| 33792 | 32256 | 7 | 46,792 |
| 33792 | 32768 | 7 | 44,699 |
| 33536 | 30976 | 7 | 43,739 |
| 33792 | 32512 | 7 | 34,751 |
| 31744 | 32256 | 7 | 32,533 |
| 33792 | 31744 | 7 | 31,309 |
| 33792 | 30976 | 7 | 29,740 |
| 31744 | 31744 | 7 | 29,579 |
| 31744 | 32000 | 7 | 28,946 |
| 33536 | 32000 | 7 | 25,328 |
| 33280 | 32512 | 7 | 23,853 |
| 31744 | 30976 | 7 | 23,626 |
| 32512 | 30976 | 7 | 22,730 |
| 32768 | 31488 | 11 | 22,118 |
| 33536 | 32512 | 7 | 22,092 |
| 32512 | 32256 | 7 | 21,455 |
| 33280 | 30976 | 7 | 20,950 |
| 32512 | 32512 | 11 | 20,577 |
| 33024 | 32768 | 7 | 20,139 |
| 31744 | 31488 | 7 | 19,187 |
| 31744 | 32768 | 7 | 19,074 |
| 32768 | 31232 | 9 | 18,744 |

## Houses and sidecars

- Canary houses: **993**
- Crystal houses: **995**
- Crystal-only houses:
  - **3701 — Targuna Cottage 1**, entry `31962,31911,7`, size 118, three beds.
  - **3702 — Targuna Cottage 2**, entry `31940,31890,7`, size 89, two beds.
- Removed houses: none.
- Changed shared house IDs: `[2819, 3205, 3654, 3660]`.
- NPC sidecar records: Canary **1007**, Crystal **1043** (+36).
- Zone sidecars are byte-identical by SHA-256: `137c6d87018f03eb0dc83b9be7f0f80955bccbeee1184c56f3d1b00e097c34a5`.
- Monster/spawn sidecars differ:
  - Canary Git blob: `65e87a4134a320d28b2270fa5a17917fc7b513a1`.
  - Crystal Git blob: `3829f7dcd9091ace8549bfb36a00186726076898`.

## Targuna and Newhaven source evidence

Crystal contains **15 Targuna quest scripts** absent from Canary:

- `actions_herald_lever.lua`
- `actions_reliable_ram.lua`
- `actions_three_fold_path_shrine_targuna.lua`
- `actions_tortoise_eggs.lua`
- `actions_treasure_chest.lua`
- `creaturescripts_herald_of_fire.lua`
- `creaturescripts_lizard_commander.lua`
- `creaturescripts_pirates.lua`
- `eventcallbacks_secondary_tasks.lua`
- `movements_aragonia.lua`
- `movements_crimson_court.lua`
- `movements_herald_red_floors.lua`
- `movements_main_continent_hint.lua`
- `movements_sandcastles.lua`
- `movements_temple_teleport.lua`

Crystal contains **seven Newhaven quest scripts** absent from Canary:

- `#ondroploot_the_corruptor.lua`
- `movement_init_newhaven.lua`
- `movement_select_vocation.lua`
- `movement_update_tutorial_hunting.lua`
- `on_death_newhaven.lua`
- `on_login_newhaven.lua`
- `on_use_newhaven.lua`

These files prove public implementation coverage, not Real Tibia parity. Their storages, NPCs, spawns, transitions, item IDs, assets, engine APIs, reset behavior, and physical-client flows still require bounded validation.

## Recommended next tasks

1. Derive bounded Targuna map coordinates from the Crystal-only houses, quest transitions, NPC/spawn positions, and exact coordinate diff.
2. Run item/mechanic and script-resolution audits only for that bounded region.
3. Resolve the 15 quest scripts, all Targuna NPCs/monsters/bosses, house/PZ/sign changes, teleport destinations, and required item/assets revisions.
4. Repeat independently for Newhaven; do not assume its map area or tutorial engine behavior is transferable with the scripts alone.
5. Prepare an evidence-backed region patch plan. Do not write or replace an OTBM until the semantic-diff/map-writing safety phase is separately authorized.

## Evidence boundary

This report is a deterministic static comparison of two exact snapshots. It does not prove live gameplay parity and does not authorize a whole-map replacement, item substitution, `items.otb` change, asset import, or datapack mixing. The companion JSON contains per-floor bounds, top changed regions, exact source/index hashes, sidecar inventories, and quest-file lists.
