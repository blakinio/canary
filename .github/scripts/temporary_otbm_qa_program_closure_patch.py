from pathlib import Path

catalog = Path("docs/agents/MODULE_CATALOG.md")
catalog_text = catalog.read_text(encoding="utf-8")
status_replacements = {
    "| OTBM World Health Aggregator | active (#672) |": "| OTBM World Health Aggregator | merged (#672) |",
    "| OTBM Map Change Regression Guard | active (#679) |": "| OTBM Map Change Regression Guard | merged (#679) |",
    "| OTBM Repair Recommendation Orchestrator | active (#681) |": "| OTBM Repair Recommendation Orchestrator | merged (#681) |",
    "| OTBM Reviewed Candidate Repair Orchestrator | active (#684) |": "| OTBM Reviewed Candidate Repair Orchestrator | merged (#684) |",
    "| OTBM Coverage Dashboard | active (#688) |": "| OTBM Coverage Dashboard | merged (#688) |",
    "| OTBM Quest State Reachability | active (#709) |": "| OTBM Quest State Reachability | merged (#709) |",
    "| OTBM Connectivity Resilience | active (#713) |": "| OTBM Connectivity Resilience | merged (#713) |",
    "| OTBM Critical Access Integrity | active (#717) |": "| OTBM Critical Access Integrity | merged (#717) |",
    "| OTBM Asset and Appearance Compatibility | active (#734) |": "| OTBM Asset and Appearance Compatibility | merged (#734) |",
    "| OTBM Static Map Performance Hotspots | active (#735) |": "| OTBM Static Map Performance Hotspots | merged (#735) |",
    "| OTBM Release Provenance and Certification Freshness | active (#737) |": "| OTBM Release Provenance and Certification Freshness | merged (#737) |",
    "| OTBM Deterministic Change Risk | active (#739) |": "| OTBM Deterministic Change Risk | merged (#739) |",
    "| OTBM Compact Evidence Gateway | active (#741) |": "| OTBM Compact Evidence Gateway | merged (#741) |",
}
for old, new in status_replacements.items():
    if old in catalog_text:
        catalog_text = catalog_text.replace(old, new, 1)
    elif new not in catalog_text:
        raise SystemExit(f"MODULE_CATALOG status anchor not found: {old}")

qa8 = "| OTBM Dependency and Blast-Radius Graph | merged (#694) | Deterministic read-only `canary-otbm-dependency-blast-radius-v1` computation over explicitly reviewed dependency nodes and directed edges validated against exact compatible QA-001 World Health, QA-002 Map Change Regression and optional QA-005 Coverage Dashboard evidence | `tools/ai-agent/otbm_dependency_graph.py`, CLI, focused tests, `docs/ai-agent/OTBM_DEPENDENCY_GRAPH.md`, manifest/report schemas | The graph never discovers dependencies or infers edges from names, proximity, sprites or source layout. Traverse only current proven reviewer-declared edges; unresolved boundaries remain visible, and absence from the selected graph is never global non-impact proof. |"
qa9 = "| OTBM Dead/Orphaned Content and Completeness Audit | merged (#700) | Deterministic read-only `canary-otbm-content-completeness-audit-v1` selected-scope composition over exact QA-008 Dependency/Blast-Radius evidence and QA-005 Coverage Dashboard evidence for reviewed quest/mechanic stages and counterpart relationships | `tools/ai-agent/otbm_content_completeness.py`, CLI, focused tests, `docs/ai-agent/OTBM_CONTENT_COMPLETENESS.md`, manifest/report schemas | Reuse QA-008/005 only; never discover quest topology, execute scripts, rerun graph traversal, prove runtime completion or declare content globally dead. Confirmed/map-only/script-only/unresolved/conflicting/not-applicable classifications remain explicit and exact-provenance mismatches fail closed. |"
if qa8 not in catalog_text or qa9 not in catalog_text:
    lines = catalog_text.splitlines()
    anchor_index = next((i for i, line in enumerate(lines) if line.startswith("| OTBM Continuous Assurance Gate | merged (#759) |")), None)
    if anchor_index is None:
        raise SystemExit("MODULE_CATALOG QA-007 anchor not found")
    additions = []
    if qa8 not in catalog_text:
        additions.append(qa8)
    if qa9 not in catalog_text:
        additions.append(qa9)
    lines[anchor_index + 1:anchor_index + 1] = additions
    catalog_text = "\n".join(lines) + "\n"
catalog.write_text(catalog_text, encoding="utf-8")

changelog = Path("docs/agents/CHANGELOG.md")
change_text = changelog.read_text(encoding="utf-8")
bullets = [
    "- Adds `canary-otbm-dependency-graph-manifest-v1` and `canary-otbm-dependency-blast-radius-v1` as a deterministic read-only reviewed dependency/blast-radius overlay over exact compatible QA-001 World Health, QA-002 Map Change Regression and optional QA-005 Coverage Dashboard evidence. The graph validates explicit reviewer-declared nodes and directed edges, traverses only current proven edges, exposes unresolved boundaries and never discovers dependencies or infers edges from names, map/source proximity, sprites or chat history; absence from the selected graph is never global non-impact proof.",
    "- Adds `canary-otbm-content-completeness-manifest-v1` and `canary-otbm-content-completeness-audit-v1` as a deterministic selected-scope completeness audit over exact QA-008 dependency evidence and QA-005 coverage evidence. Reviewed quest/mechanic stages and counterpart checks preserve confirmed/map-only/script-only/unresolved/conflicting/not-applicable classifications; the audit never discovers quest topology, executes scripts, reruns dependency traversal, proves runtime completion or declares content globally dead.",
]
if not all(bullet in change_text for bullet in bullets):
    marker = "## Unreleased\n\n"
    if marker not in change_text:
        raise SystemExit("CHANGELOG Unreleased marker not found")
    additions = "\n".join(bullet for bullet in bullets if bullet not in change_text) + "\n"
    change_text = change_text.replace(marker, marker + additions, 1)
    changelog.write_text(change_text, encoding="utf-8")

roadmap = Path("docs/ai-agent/OTBM_WORLD_QUALITY_REPAIR_ROADMAP.md")
roadmap_text = roadmap.read_text(encoding="utf-8")
old_status = "> Status: planning / consolidated successor roadmap  "
new_status = "> Status: complete / OTBM-QA-001..018 delivered and lifecycle-closed  "
if old_status in roadmap_text:
    roadmap_text = roadmap_text.replace(old_status, new_status, 1)
elif new_status not in roadmap_text:
    raise SystemExit("roadmap status anchor not found")

closure_heading = "# Programme closure reconciliation — 2026-07-23"
if closure_heading not in roadmap_text:
    marker = "# Proposal-to-package inventory"
    if marker not in roadmap_text:
        raise SystemExit("roadmap proposal inventory marker not found")
    closure = '''# Programme closure reconciliation — 2026-07-23

> Delivery status: **COMPLETE — OTBM-QA-001..018 delivered**
>
> This closes the consolidated successor roadmap as a tooling/governance programme. It does **not** certify that an arbitrary or current world is globally healthy or gameplay-correct. Every health, regression, certification, repair, risk and evidence claim still requires the exact compatible inputs and proof level required by its own contract.

## Delivery ledger

| Package | Delivered feature PR | Lifecycle closure PR | Durable capability |
|---|---:|---:|---|
| OTBM-QA-001 | #672 | #678 | World Health Aggregator |
| OTBM-QA-002 | #679 | #680 | Map Change Regression Guard |
| OTBM-QA-003 | #681 | #682 | Repair Recommendation Orchestrator |
| OTBM-QA-004 | #684 | #686 | Reviewed Candidate Repair Orchestration |
| OTBM-QA-005 | #688 | #689 | Coverage Dashboard |
| OTBM-QA-006 | #759 | #767 | Region and Quest Certification |
| OTBM-QA-007 | #759 | #767 | Continuous World Assurance Gate |
| OTBM-QA-008 | #694 | #698 | Dependency and Blast-Radius Graph |
| OTBM-QA-009 | #700 | #704 | Dead/Orphaned Content and Completeness Audit |
| OTBM-QA-010 | #709 | #710 | Quest State Reachability |
| OTBM-QA-011 | #713 | #716 | Connectivity Resilience |
| OTBM-QA-012 | #717 | #721 | Critical Access Integrity |
| OTBM-QA-013 | #724 | #731 | Identifier and Selector Integrity |
| OTBM-QA-014 | #734 | #752 | Asset and Appearance Compatibility |
| OTBM-QA-015 | #735 | #752 | Static Map Performance Hotspots |
| OTBM-QA-016 | #737 | #752 | Release Provenance and Certification Freshness |
| OTBM-QA-017 | #739 | #752 | Deterministic Change Risk |
| OTBM-QA-018 | #741 | #752 | Compact Evidence Gateway |

Shared public-interface governance for QA-014..018 was reconciled in #743. QA-006/007 shared catalogue/changelog registration was reconciled in #768. Closure PR #773 also restores the previously missing shared discovery entries for QA-008 and QA-009.

## Completion-definition reconciliation

The sixteen programme completion conditions are satisfied by the delivered contracts as follows:

1. Deterministic current-world health composition: QA-001.
2. Fail-closed impacted static and represented Physical E2E selection for exact map changes: QA-002.
3. Explicit proven dependency/blast-radius paths without invented edges: QA-008.
4. Conservative dead/orphaned-content and selected quest/mechanic completeness auditing: QA-009.
5. Selected quest-state reachability without dynamic Lua execution: QA-010.
6. Connectivity fragility, reviewed transition/teleport topology and static entrapment candidates through the canonical Reachability graph: QA-011.
7. Bounded critical-access, identifier, asset/appearance and static-hotspot evidence: QA-012..015.
8. Reviewable repair recommendations without automatic mutation: QA-003.
9. Reviewed candidate repair orchestration restricted to existing approved bounded mutation contracts: QA-004.
10. Candidate evidence chains retain native reparse/reindex, Semantic Diff, quality and impacted Physical E2E boundaries through QA-004 and the existing OTBM-E2E candidate-validation stack.
11. Exact release BOM/provenance, upgrade comparison and dependency-scoped certification freshness: QA-016.
12. Explicit target coverage dimensions and bounded C0-C7 certification with stale-state handling: QA-005/006.
13. Transparent evidence-derived change-risk classification: QA-017.
14. Compact exact downstream evidence without transferring E2E/feature ownership: QA-018.
15. Exact provenance and source-map immutability remain mandatory across the programme.
16. The programme reuses the canonical World Index, Script Resolution, Reachability, Semantic Diff, renderer, bounded mutation pipeline and Universal Physical E2E; it introduces no parallel parser/pathfinder/writer/renderer/E2E stack.

## Closure boundary

Future work may consume or extend these stable contracts through new bounded tasks, but it does not reopen OTBM-QA-001..018. New Real Tibia/client-reference, parity, content-reconstruction or feature-runtime programmes remain separate ownership domains and must preserve the reuse and proof-level rules above.

'''
    roadmap_text = roadmap_text.replace(marker, closure + marker, 1)
roadmap.write_text(roadmap_text, encoding="utf-8")
