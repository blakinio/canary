# OTS AI Equipment Upgrade Validation — status, methodology and handoff

> **Status date:** 2026-07-12  
> **Repository:** `blakinio/canary`  
> **Working branch:** `validation/equipment-upgrade`  
> **Baseline main commit observed at start:** `dbcc809bac57bb78425ca39c2523c723cef79bb0`  
> **Primary comparison page:** `https://tibia.fandom.com/wiki/Equipment_Upgrade`  
> **Parent methodology:** `docs/ai-agent/OTS_AI_WORLD_VALIDATION_PROJECT.md`  
> **Current phase:** inventory and evidence collection  
> **Rule:** every implementation change made during this validation must be recorded in this file in the same commit or immediately following commit.

---

## 1. Goal

Validate Canary's complete Equipment Upgrade / Exaltation Forge implementation against documented Tibia behaviour, without assuming that code presence, a passing build, or a successful happy-path test proves gameplay parity.

The validation covers:

1. upgrade classifications and tier limits;
2. upgradable-item metadata;
3. Dust capacity, Dust acquisition and conversions;
4. Slivers and Exalted Cores;
5. influenced and fiendish creature spawning, scaling, rewards and restrictions;
6. regular Fusion;
7. Fusion bonus effects;
8. Convergence Fusion;
9. regular Transfer;
10. Convergence Transfer;
11. Onslaught, Ruse, Momentum, Transcendence and Amplification effects;
12. protocol/UI data sent to the client;
13. persistence, Forge history and resource accounting;
14. malformed/stale packet rejection and transaction safety;
15. focused unit, integration and runtime tests.

---

## 2. Evidence levels

The project-wide validation layers from `OTS_AI_WORLD_VALIDATION_PROJECT.md` are applied here as follows:

- **A — structural:** relevant files/configurations load and compile;
- **B — static references:** classifications, tiers, config keys, item metadata and protocol handlers resolve;
- **C — semantic parity:** formulas, eligibility rules, costs, outcomes and side effects agree with the reference behaviour;
- **D — runtime:** the server starts and Forge-related systems register without critical errors;
- **E — gameplay scenarios:** test characters execute each relevant flow and receive the exact expected result;
- **F — regression:** automated tests preserve confirmed behaviour.

A lower layer must not be reported as proof of a higher layer.

---

## 3. Safety and scope rules

- Do not modify map files, client assets or binary item files as part of an unproven hypothesis.
- Do not change price tables or probabilities without evidence.
- Do not infer official behaviour solely from variable names or existing tests.
- Separate documented Tibia behaviour from Canary-specific configuration choices.
- Prefer the smallest independently testable fix.
- Preserve unrelated work already merged to `main`.
- Record unresolved questions rather than guessing.

---

## 4. Existing baseline work that must be preserved

### PR #89 — normal transfer rules, costs and history

Already merged before this validation. It introduced or corrected:

- normal-transfer compatibility based on matching upgrade classification rather than equipment slot;
- server-side validation of matching classifications and valid donor tiers;
- donor-tier-based regular price/core lookup;
- correct resulting tier calculation;
- actual Dust/core/gold values in history;
- correct donor/receiver rendering;
- focused transfer policy and integration tests.

### PR #110 — Forge history item identity

Already merged before this validation. It introduced or corrected:

- storing first and second item IDs in in-memory Forge history;
- resolving item types by ID instead of ambiguous name-only lookup;
- fallback name lookup for older call sites.

These changes are baseline evidence, not proof that the full Equipment Upgrade system is correct.

---

## 5. Reference behaviour inventory

Initial facts extracted from the comparison page; each row still requires implementation evidence and, where possible, corroboration from official release notes/protocol behaviour.

| Area | Reference behaviour to validate | Status |
|---|---|---|
| Classification | Class 1/2/3/4 tier caps are 1/2/3/10 | not started |
| Eligibility | Forge equipment cannot be imbued during the process | not started |
| Dust capacity | Starts at 100; upgrade cost is current limit minus 75; maximum 325 | not started |
| Dust conversion | 60 Dust creates 3 Slivers | not started |
| Core conversion | 50 Slivers creates 1 Exalted Core | not started |
| Influenced creatures | 1–5 stacks; stack-dependent HP/damage/XP/Dust | not started |
| Fiendish creatures | Equivalent strength/reward to 15 stacks; world cap and lifecycle rules | not started |
| Premium restriction | Dust is not awarded without Premium | not started |
| Fusion | Two identical items of equal tier; base success 50%; optional core raises to 65% | not started |
| Failure | Default 100% tier loss/destruction chance; optional core reduces it to 50% | not started |
| Fusion costs | Class/tier-specific gold plus Dust and optional cores | not started |
| Fusion bonuses | Eight documented bonus outcomes | not started |
| Convergence Fusion | Class 4 only; different items in same body slot and equal tier; guaranteed; no bonus | not started |
| Transfer | Same classification; receiver tier 0; source destroyed; result donor tier minus one | partially covered by PR #89 |
| Convergence Transfer | Class 4 only; no tier loss; may cross body slots; source destroyed | not started |
| Onslaught | Weapon effect and exact chance/damage rules | not started |
| Ruse | Armor effect and exact dodge rules | not started |
| Momentum | Helmet effect and exact cooldown rules | not started |
| Transcendence | Legs effect and exact avatar trigger/duration rules | not started |
| Amplification | Boots modify other Forge effects according to documented rules | not started |
| History | Exact partners, results, costs, bonus and success state | partially covered by PRs #89/#110 |
| Transaction safety | No partial item/resource loss after a rejected or failed server operation | not started |

---

## 6. Validation workflow

For each area:

1. capture the exact documented rule and date/version context;
2. locate all server, datapack, configuration, persistence, protocol and test code involved;
3. identify trusted inputs and packet-controlled inputs;
4. trace validation before mutation;
5. compare formulas, table indexing, caps and rounding;
6. test success, failure, boundary and malformed-packet cases;
7. classify the result as `confirmed`, `mismatch`, `incomplete`, `configurable divergence` or `unknown`;
8. implement only evidence-backed fixes;
9. update this file with files changed, rationale, tests and remaining risks.

---

## 7. Work log

### 2026-07-12 — validation initialized

- Read the parent methodology and adopted its layered evidence model.
- Created branch `validation/equipment-upgrade` from current `main`.
- Created this dedicated validation/handoff document beside the parent project file.
- Identified merged Forge baseline fixes in PRs #89 and #110.
- Began source inventory and external behaviour extraction.

No production code was changed in this step.

---

## 8. Current next actions

1. inventory every Forge-related source/config/test file;
2. reconstruct the exact cost/probability/classification tables used at runtime;
3. compare Fusion and both Convergence flows first, because normal Transfer already has focused baseline coverage;
4. inspect mutation ordering and rollback guarantees;
5. add failing tests before behavioural fixes;
6. continue with influenced/fiendish creatures and item effects;
7. perform runtime and protocol validation after static/semantic issues are resolved.

---

## 9. Handoff

The next agent must continue on `validation/equipment-upgrade`, read this file and the parent methodology first, and preserve PR #89/#110 behaviour. No claim of full Equipment Upgrade parity has been made yet. The current work is at evidence-inventory stage.