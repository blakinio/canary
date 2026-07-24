from pathlib import Path

merge_sha = "78b3435510c7e09d10a87ca2338bef59a24475bb"
feature_head = "4ba3ff2f56ffa369c1274060cb16f22c9dba9b1e"
merged_at = "2026-07-24T16:58:27Z"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


active = Path("docs/agents/tasks/active/CAN-20260724-tcr-006-content-reference-correlation.md")
archive = Path("docs/agents/tasks/archive/CAN-20260724-tcr-006-content-reference-correlation.md")
task = active.read_text(encoding="utf-8")
task = replace_once(task, "status: implementing\n", "status: completed\n", "task frontmatter status")
task = replace_once(task, "updated: 2026-07-24T18:15:59+02:00\n", f"updated: {merged_at}\n", "task frontmatter updated")
task = replace_once(task, 'last_verified_commit: "fcb8edf1be084511b4e4926808009b54884b597a"\n', f'last_verified_commit: "{merge_sha}"\n', "task frontmatter head")
task = replace_once(task, "cross_repo_tasks: []\n---\n", f"cross_repo_tasks: []\ncompleted: {merged_at}\n---\n", "task completed field")
task = replace_once(task, "updated_at: 2026-07-24T18:15:59+02:00\n", f"updated_at: {merged_at}\n", "checkpoint updated")
task = replace_once(task, "head: fcb8edf1be084511b4e4926808009b54884b597a\n", f"head: {merge_sha}\n", "checkpoint head")
task = replace_once(task, "status: implementing\n", "status: ready\n", "checkpoint status")
task = replace_once(
    task,
    "  - PR 880 remains the sole open TCR-006 owner; it is draft, mergeable and targets blakinio/canary main from feat/tcr-006-content-reference-correlation.\n",
    f"  - PR 880 squash-merged into blakinio/canary main as {merge_sha} at {merged_at}; feature head was {feature_head}.\n",
    "checkpoint merged fact",
)
task = replace_once(
    task,
    "  - The implementation acceptance surface is complete; only the final task-checkpoint head validation and PR lifecycle action remain.\n",
    "  - TCR-006 is stable/merged within its exact read-only provenance and identifier-resolution boundaries.\n",
    "checkpoint derived",
)
task = replace_once(
    task,
    "unknown:\n  - Exact workflow conclusions on the task-checkpoint commit created after fcb8edf1be084511b4e4926808009b54884b597a.\n  - Final squash-merge commit SHA.\n",
    "unknown: []\n",
    "checkpoint unknowns",
)
task = replace_once(
    task,
    "next_action: Verify the ci:final-gate workflows on the task-checkpoint commit, then mark PR 880 ready and squash-merge it if all required checks remain green.\n",
    "next_action: No further action in TCR-006; select the next dependency-satisfied programme package through a fresh task and PR.\n",
    "checkpoint next action",
)
task += (
    "\n## Automated lifecycle completion\n\n"
    "- Feature PR: #880.\n"
    f"- Feature head: `{feature_head}`.\n"
    f"- Merge commit: `{merge_sha}`.\n"
    f"- Merged at: `{merged_at}`.\n"
    "- This record was moved from `tasks/active` by the post-merge lifecycle closeout.\n"
)
archive.write_text(task, encoding="utf-8")
active.unlink()

program_path = Path("docs/agents/programs/OTBM_TIBIA_CLIENT_REFERENCE_PROGRAM.md")
program = program_path.read_text(encoding="utf-8")
program = replace_once(program, "updated: 2026-07-24T16:05:00+02:00\n", f"updated: {merged_at}\n", "program updated")
program = replace_once(program, 'last_verified_commit: "5641a7ac2420f5a3d512325423088890e92ac3cb"\n', f'last_verified_commit: "{merge_sha}"\n', "program head")
program = replace_once(
    program,
    "| TCR-006 | Global Content Registry Correlation | planned (next candidate) | staticdata index + existing subsystem evidence | TCR-002/TCR-002A | medium | After fresh ownership/reuse/identifier-resolution preflight, add only read-only monster/boss/quest/achievement registry correlation routed to existing subsystem owners. |",
    "| TCR-006 | Global Content Registry Correlation | merged | `canary-tibia-content-reference-resolver-v1` + `canary-tibia-content-reference-correlation-v1`; PR #880; merge `78b34355...` | TCR-002/TCR-002A | medium | Complete. Exact reviewed cross-namespace resolution and read-only content registry correlation are stable/merged; runtime/gameplay parity and mutation remain unproven. |",
    "queue TCR-006",
)
program = replace_once(
    program,
    "TCR-001, TCR-002, TCR-003, TCR-004 and TCR-005 stabilize these reference and parity contracts:",
    "TCR-001, TCR-002, TCR-003, TCR-004, TCR-005 and TCR-006 stabilize these reference, resolver and correlation contracts:",
    "stable contract intro",
)
program = replace_once(
    program,
    "canary-otbm-house-reference-parity-v1\n```",
    "canary-otbm-house-reference-parity-v1\ncanary-tibia-content-reference-resolver-v1\ncanary-tibia-content-reference-correlation-v1\n```",
    "stable contract list",
)
house_paragraph = "The house-ID resolver and house reference parity contracts are `stable/merged` as of PR #868 / merge `5641a7ac2420f5a3d512325423088890e92ac3cb`. They provide exact provenance-pinned reviewed house-ID mappings and deterministic comparison of StaticData registry, StaticMapData layout and canonical World Index house evidence. They preserve unresolved `staticmapdata.object_id`, keep evidence dimensions separate and emit review findings only; they do not prove runtime ownership, rent, access or gameplay parity."
program = replace_once(
    program,
    house_paragraph,
    house_paragraph
    + "\n\nThe content-reference resolver and correlation contracts are `stable/merged` as of PR #880 / merge `78b3435510c7e09d10a87ca2338bef59a24475bb`. They consume exact manifest-bound StaticData evidence and explicit reviewed mappings to existing creature/spawn, boss, quest/storage and achievement owners while preserving source-family vocabulary and unresolved joins. They emit review evidence only and do not prove runtime behavior, gameplay parity or authorize mutation.",
    "TCR-006 stable paragraph",
)
program = replace_once(
    program,
    "The following remain planned and **not stable/merged**: TCR-006/TCR-007 correlation reports, optional TCR-008 minimap reference, `canary-tibia-client-reference-drift-v1`, gateway integration and adoption routing.",
    "The following remain planned and **not stable/merged**: TCR-007 proficiency correlation, optional TCR-008 minimap reference, `canary-tibia-client-reference-drift-v1`, gateway integration and adoption routing.",
    "remaining planned",
)
program = replace_once(
    program,
    "OWA-003 may later consume `canary-tibia-client-reference-manifest-v1`, `canary-tibia-staticdata-index-v1`, `canary-tibia-staticmapdata-index-v1`, `canary-tibia-proficiency-index-v1`, `canary-otbm-house-id-resolver-v1` and `canary-otbm-house-reference-parity-v1` only within their exact stable provenance/reference boundaries where that dependency is required. It must not infer map authority, `staticmapdata.object_id` equivalence, cross-namespace proficiency-ID equivalence, gameplay/runtime parity or any still-planned TCR correlation, minimap, drift, gateway or routing output before the owning bounded package merges.",
    "OWA-003 may later consume `canary-tibia-client-reference-manifest-v1`, `canary-tibia-staticdata-index-v1`, `canary-tibia-staticmapdata-index-v1`, `canary-tibia-proficiency-index-v1`, `canary-otbm-house-id-resolver-v1`, `canary-otbm-house-reference-parity-v1`, `canary-tibia-content-reference-resolver-v1` and `canary-tibia-content-reference-correlation-v1` only within their exact stable provenance/reference boundaries where that dependency is required. It must not infer map authority, `staticmapdata.object_id` equivalence, cross-namespace proficiency-ID equivalence, gameplay/runtime parity or any still-planned TCR proficiency correlation, minimap, drift, gateway or routing output before the owning bounded package merges.",
    "OWA consumption",
)
program = replace_once(
    program,
    "## TCR-006 — Global Content Registry Correlation\n\nPlanned public format:\n\n```text\ncanary-tibia-content-reference-correlation-v1\n```",
    "## TCR-006 — Global Content Registry Correlation\n\nStable public formats:\n\n```text\ncanary-tibia-content-reference-resolver-v1\ncanary-tibia-content-reference-correlation-v1\n```",
    "TCR-006 contract state",
)
program = replace_once(
    program,
    "# Last completed task\n\n- Task: `docs/agents/tasks/archive/CAN-20260724-tcr-005-house-reference-parity.md`\n- PR: `#868` — merged.\n- Merge commit: `5641a7ac2420f5a3d512325423088890e92ac3cb`.\n- Scope: TCR-005 exact reviewed house-ID resolver and read-only StaticData/StaticMapData/World Index house parity only; no object-ID equivalence, OTBM mutation, runtime or gameplay claim.",
    "# Last completed task\n\n- Task: `docs/agents/tasks/archive/CAN-20260724-tcr-006-content-reference-correlation.md`\n- PR: `#880` — merged.\n- Merge commit: `78b3435510c7e09d10a87ca2338bef59a24475bb`.\n- Scope: TCR-006 exact reviewed content-reference resolver and read-only StaticData-to-existing-owner correlation only; no runtime/gameplay parity, source/datapack/map mutation or automatic repair.",
    "last completed task",
)
program = replace_once(
    program,
    "# Exact next action after TCR-005\n\nTCR-005 is merged. After this lifecycle/discovery closure lands, perform a fresh ownership/PR/reuse/identifier-resolution preflight and start **only TCR-006 — Global Content Registry Correlation** if it remains the first unowned, unblocked, dependency-satisfied queue item.\n\nDo not start TCR-007 or another TCR package in the TCR-006 task or PR.",
    "# Exact next action after TCR-006\n\nTCR-006 is merged. After this lifecycle closure lands, perform a fresh ownership/PR/reuse/identifier-resolution preflight and start **only TCR-007 — Proficiency Reference Correlation** if it remains the first unowned, unblocked, dependency-satisfied queue item.\n\nDo not start TCR-008 or another TCR package in the TCR-007 task or PR.",
    "program next action",
)
program = replace_once(
    program,
    "11. treat `canary-tibia-client-reference-manifest-v1`, `canary-tibia-staticdata-index-v1`, `canary-tibia-staticmapdata-index-v1`, `canary-tibia-proficiency-index-v1`, `canary-otbm-house-id-resolver-v1` and `canary-otbm-house-reference-parity-v1` as stable/merged only within their exact provenance/reference boundaries; do not upgrade planned correlation, minimap, drift, gateway or routing contracts to stable without their own merged packages.",
    "11. treat `canary-tibia-client-reference-manifest-v1`, `canary-tibia-staticdata-index-v1`, `canary-tibia-staticmapdata-index-v1`, `canary-tibia-proficiency-index-v1`, `canary-otbm-house-id-resolver-v1`, `canary-otbm-house-reference-parity-v1`, `canary-tibia-content-reference-resolver-v1` and `canary-tibia-content-reference-correlation-v1` as stable/merged only within their exact provenance/reference boundaries; do not upgrade planned proficiency correlation, minimap, drift, gateway or routing contracts to stable without their own merged packages.",
    "handoff stable contracts",
)
program = replace_once(
    program,
    "3. The next candidate is TCR-006 Global Content Registry Correlation only if it remains unowned, unblocked and dependency-satisfied.",
    "3. The next candidate is TCR-007 Proficiency Reference Correlation only if it remains unowned, unblocked and dependency-satisfied.",
    "kickoff candidate",
)
program = replace_once(
    program,
    "TCR-006 TARGET CONTRACT:\n- canary-tibia-content-reference-correlation-v1;\n- consume exact stable TCR-001 manifest and TCR-002/TCR-002A StaticData provenance;\n- keep monster, boss, quest and achievement registry records as separate evidence dimensions;\n- route each correlation to existing creature/spawn, boss, quest/storage and achievement subsystem owners instead of duplicating validators;\n- require explicit reviewed identifier-space joins and fail closed on ambiguous, conflicting or unavailable mappings;\n- emit read-only correlation findings only, with no map/datapack mutation, runtime claim or gameplay conclusion.\n\nBefore implementation, prove that no equivalent canonical content-reference correlation consumer already exists, that no active task/PR owns TCR-006 and that each selected subsystem join has an explicit evidence owner and identifier-resolution decision. If any condition fails, stop duplication and update the programme with the reuse/ownership/resolver decision instead.",
    "TCR-007 TARGET CONTRACT:\n- canary-tibia-proficiency-reference-correlation-v1;\n- consume exact stable TCR-001 manifest and TCR-004 proficiency provenance;\n- keep definition, appearance binding, Canary item binding, runtime, persistence, protocol and E2E as separate evidence dimensions;\n- reuse the canonical appearances index and existing item/runtime/persistence/protocol/E2E owners instead of duplicating validators;\n- require explicit reviewed cross-namespace joins and fail closed on ambiguous, conflicting or unavailable mappings;\n- emit read-only correlation findings only, with no items.xml/datapack/runtime/protocol mutation or gameplay conclusion.\n\nBefore implementation, prove that no equivalent canonical proficiency-reference correlation consumer already exists, that no active task/PR owns TCR-007 and that each selected join has an explicit evidence owner and identifier-resolution decision. If any condition fails, stop duplication and update the programme with the reuse/ownership/resolver decision instead.",
    "kickoff target contract",
)
program_path.write_text(program, encoding="utf-8")

catalog_path = Path("docs/agents/MODULE_CATALOG.md")
catalog = catalog_path.read_text(encoding="utf-8")
catalog = replace_once(
    catalog,
    "| Tibia content reference correlation | active TCR-006 (#880) |",
    "| Tibia content reference correlation | merged TCR-006 (#880) |",
    "module catalogue state",
)
catalog_path.write_text(catalog, encoding="utf-8")
