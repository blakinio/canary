# Real Tibia Registry Source and Baseline Policy

This document explains how structured registry records refer to evidence. The detailed authority rules remain in `docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md` and the parity playbook.

## Stable source identities

`registry/sources.yaml` gives each source a stable ID, type, write policy, immutable-reference requirement and question-specific authority dimensions. Module records reference those IDs with modes such as `required`, `required-when-related`, `secondary` or `comparison-only`.

No source has universal precedence:

- current Canary source/tests/runtime are authoritative for what Canary currently does;
- official Tibia material is strongest for announced existence, names and visible intended behavior;
- maintained OTClient is authoritative for its own packet/UI interpretation;
- packet captures can prove byte shape when versioned and controlled;
- TibiaWiki/Fandom is secondary gameplay reference;
- OpenTibiaBR and CrystalServer are read-only implementation comparisons, never official behavior authorities.

## Baselines

`registry/versions.yaml` stores named immutable snapshots. A baseline separates:

- Canary repository SHA;
- maintained client SHA when used;
- upstream/donor SHA when used;
- protocol version;
- official client build or publication date;
- datapack/map revision when applicable;
- capture timestamp and notes.

Never store a moving external `main` as proof. Module files hold freshness metadata, not moving repository heads. Each new task must re-fetch live state and record exact SHAs in its task/program evidence.

## Captures and quotations

Registry records link sources and roles; they do not archive copied wiki pages, proprietary client assets, packet secrets, maps or large reports. Store only the minimum lawful evidence required by the relevant validation workflow and keep protected/transient artifacts outside Git.

## Conflicts

When sources disagree, record the conflict in the module program or task evidence matrix. Do not resolve it by averaging values, choosing the donor with the most complete code, or silently treating secondary material as official.
