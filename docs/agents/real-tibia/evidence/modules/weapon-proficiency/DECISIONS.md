# Weapon Proficiency evidence decisions

## RTEC-WP-DEC-0001 — keep manipulation separate from static tree selection

**Decision:** treat the Summer Update 2026 modified-slot lifecycle as a separate bounded claim from Canary's existing original-tree perk selection.

**Evidence:** `RT-WEAPON-PROFICIENCY-0001` and `RT-WEAPON-PROFICIENCY-0002`.

**Reason:** the official feature adds modified slots, resources and operations not represented by the selected static-tree selection state. Collapsing both concepts would overstate correspondence.

**Rejected alternative:** call `setSelectedPerk()` equivalent to official manipulation. It selects one original perk for an unlocked level and does not establish modified-slot state, dust settlement, rolling, refinement, maximisation or reshaping.

**Revisit trigger:** exact implementation-owner evidence or a stable owner result demonstrating the official manipulation lifecycle.

## RTEC-WP-DEC-0002 — do not infer character-switch UI isolation

**Decision:** preserve the official fix as `UNKNOWN` for current Canary conformance.

**Evidence:** `RT-WEAPON-PROFICIENCY-0003`.

**Reason:** Player ownership in the selected server component does not prove maintained-client pending-notification state, packet/session behavior or reset on character switch.

**Rejected alternative:** infer isolation from object lifetime. That would promote a server source observation into client behavior proof.

**Revisit trigger:** exact maintained-client/protocol trace or a controlled character-switch result.
