# Shared E2E Ownership Model

A full one-shot environment that starts MySQL, builds or launches Canary, loads the global datapack, starts an automated client, performs login, and executes UI scenarios is shared test infrastructure. It must not be owned exclusively by one gameplay program such as Cyclopedia.

## Required split

### E2E platform program

Recommended ID: `CAN-PROGRAM-E2E-PLATFORM`

Owns reusable infrastructure such as:

- isolated database/bootstrap orchestration;
- server build and startup wrappers;
- test account provisioning;
- client build/startup and virtual-display integration;
- automated login/session establishment;
- common screenshot, trace, timeout, cleanup, and artifact handling;
- generic scenario runner interfaces.

This program must not encode Cyclopedia-specific expected values or repair Cyclopedia gameplay behavior.

### Feature program

Example ID: `CAN-PROGRAM-CYCLOPEDIA`

Owns feature-specific scenario definitions and assertions such as:

- opening Cyclopedia sections;
- Items, Bestiary, Charms, Bosstiary, Houses, Map, Titles, and Character flows;
- server/client contract expectations specific to Cyclopedia;
- fixtures that are meaningful only to Cyclopedia;
- evidence reports and remediation tasks derived from failed scenarios.

The feature program consumes the E2E platform as a read-only dependency unless a separate E2E-platform task explicitly coordinates a shared interface change.

## Task ownership example

```yaml
program_id: CAN-PROGRAM-CYCLOPEDIA
owned_paths:
  exclusive:
    - tests/e2e/scenarios/cyclopedia/**
    - docs/ai-agent/*CYCLOPEDIA*E2E*
  shared:
    - tests/e2e/scenario_registry.*
  read_only:
    - tools/e2e/**
    - tests/e2e/runtime/**
    - tests/e2e/client/**
depends_on:
  - CAN-E2E-PLATFORM-BOOTSTRAP
```

A platform task would instead claim only the common runner paths it actually changes and list Cyclopedia scenarios as read-only compatibility inputs.

## Interface rule

When a feature needs a new generic E2E capability:

1. the feature task records the missing capability and expected interface;
2. a separate E2E-platform task owns the reusable implementation;
3. the platform PR adds focused generic tests;
4. the feature PR consumes the released interface without duplicating orchestration;
5. ordering is recorded with `depends_on` and `blocks`.

## Why this separation is mandatory

Without it, a Cyclopedia agent could silently alter database bootstrap, client automation, login, global timeouts, or cleanup behavior used by quest, Wheel, Forge, or other future E2E suites. Separating platform ownership from scenario ownership keeps autonomous programs fast while preventing cross-program regressions and file overwrites.
