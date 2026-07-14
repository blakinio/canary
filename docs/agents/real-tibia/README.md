# Real Tibia Module Registry

This directory is the machine-readable discovery layer for evidence-based Real Tibia parity work. It complements, and does not replace, the repository's agent governance, source policy, module catalogue, technical validation reports, program records, active task records, source code, tests, and live GitHub state.

## Start here

For any Real Tibia comparison or parity task, read in this order:

1. `AGENTS.md` and `docs/agents/README.md`;
2. `docs/agents/REAL_TIBIA_EVIDENCE_SOURCES.md`;
3. `docs/agents/REAL_TIBIA_PARITY_PLAYBOOK.md`;
4. `docs/agents/programs/REAL_TIBIA_PARITY_PROGRAM.md`;
5. this README and the generated `MODULE_INDEX.md`;
6. the selected module record under `registry/modules/`;
7. the module program and validation reports linked by that record;
8. current open PRs and active task records.

Registry metadata is an inventory and navigation contract. It never proves that gameplay matches Real Tibia.

## Layout

```text
docs/agents/real-tibia/
├── README.md
├── TAXONOMY.md
├── MATURITY_MODEL.md
├── SOURCE_POLICY.md
├── registry/
│   ├── categories.yaml
│   ├── sources.yaml
│   ├── versions.yaml
│   └── modules/<module-id>.yaml
├── schemas/
├── templates/
└── generated/
```

The `.yaml` records use the YAML 1.2 JSON-compatible subset. They are valid YAML and valid JSON, so the validator remains deterministic and dependency-free. Formal JSON Schema validation is additionally enabled when `jsonschema` is installed, including in CI.

## Source-of-truth boundaries

- One module record owns identity, category, scope boundaries, repository path hints, relationships, documents, source requirements, maturity dimensions and freshness policy.
- A module program owns a long-running queue, completed PRs, blockers, current baselines and the exact next bounded package.
- A validation report owns detailed technical findings and evidence matrices.
- An active task owns current path claims, implementation decisions, failures, tests and handoff.
- GitHub owns live PR, branch, commit, review and CI state.
- `MODULE_CATALOG.md` remains the reusable implementation/tool catalogue.

Do not duplicate detailed gameplay values or copied wiki prose in module records.

## Commands

```bash
python tools/agents/real_tibia_registry.py validate
python tools/agents/real_tibia_registry.py generate --check
python tools/agents/real_tibia_registry.py module wheel-of-destiny
python tools/agents/real_tibia_registry.py lookup-path src/io/io_wheel.cpp
python tools/agents/real_tibia_registry.py stale --only-stale
python tools/agents/real_tibia_registry.py affected --base origin/main --head HEAD
```

`generate` without `--check` rewrites the derived Markdown indexes. The default generation date is the newest pinned baseline date, not wall-clock time, so generated files do not drift every day. The interactive `stale` command defaults to the current date.

## Adding or changing a module

1. Search the generated path index, module catalogue, programs, active tasks and open PRs.
2. Create or edit exactly one `registry/modules/<module-id>.yaml` record.
3. Keep scope concise and describe boundaries rather than full gameplay behavior.
4. Link existing programs and validation reports; do not create empty placeholder programs.
5. Add only known relationships and repository path patterns.
6. Set maturity dimensions conservatively. Existing code is not automatically verified behavior.
7. Pin the inventory date and define freshness thresholds.
8. Run validation and regenerate indexes.
9. Create a bounded task before changing runtime behavior.

## Generated-file policy

Files under `generated/` are derived artifacts. Never edit them manually. CI fails when they differ from registry records or when an unregistered file appears in that directory.

Path matches are discovery hints, not permissions. A module record never overrides an active task's structured ownership claims.
