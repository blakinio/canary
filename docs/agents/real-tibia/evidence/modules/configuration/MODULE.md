# Configuration evidence module

## Boundary

This dossier covers the selected current-Canary source path for loading and exposing typed configuration values, applying defaults, reloading cached values, and discovering the OTC feature list.

## Authoritative current-Canary paths

- `src/config/configmanager.cpp`
- `src/config/configmanager.hpp`
- `config.lua.dist`

## In scope

- Lua configuration-file loading and failure return path.
- Typed string, integer, boolean and floating-point extraction with defaults.
- One-time versus reloadable key loading.
- Cached getter behavior and reload cache invalidation.
- MOTD hash comparison on reload.
- OTC feature table/default discovery.

## Explicitly out of scope

- Production configuration values or deployment correctness.
- Secrets storage, masking, transport or rotation.
- Correct behavior of features controlled by configuration.
- Protocol/client compatibility, runtime feature validation, gameplay and Real Tibia parity.

## Evidence posture

Static current-Canary source inspection can establish a bounded runtime path only. Candidate records remain unpublished until coordinator adjudication and generated-index inclusion.
