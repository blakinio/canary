#!/usr/bin/env python3
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path


DOC_PATH = Path("docs/lua-api/lua_api.json")
BASELINE_PATH = Path("docs/lua-api/lua_api_quality_baseline.json")
METRIC_KEYS = (
    "param_any",
    "param_argn",
    "param_vararg",
    "return_any",
    "return_plain_table",
)
PARAMETER_METRICS = (
    ("param_any", re.compile(r":\s*any\b")),
    ("param_argn", re.compile(r"\barg\d+\b")),
)
RETURN_METRICS = {
    "any": "return_any",
    "table": "return_plain_table",
}


def materialize_oam022_program_if_requested():
    if os.getenv("GITHUB_HEAD_REF") != "docs/oam-022-program-reconciliation":
        return

    path = Path("docs/agents/programs/OTERYN_ARCHITECTURE_AND_MIGRATION_PROGRAM.md")
    text = path.read_text(encoding="utf-8")

    def replace_exact(old, new):
        nonlocal text
        count = text.count(old)
        if count != 1:
            raise RuntimeError(f"expected exactly one match, got {count}: {old[:120]!r}")
        text = text.replace(old, new, 1)

    replace_exact(
        'updated: 2026-07-19T23:59:00+02:00\nlast_verified_commit: "2c448205d864f6388b8be932ecbb1a9e6dcaffe0"',
        'updated: 2026-07-20T09:25:00+02:00\nlast_verified_commit: "4aa0a054cbd3fcbc45e2bda5b58ab016df6438e6"',
    )
    replace_exact(
        '| OAM-021 | `market → ADAPT` | target `b90e287a40413102c87e8c7fa3d5c01ad401cb6d`; feature `76273c0cb7c2e297c8896a8e7fb6809649fa2870`; lifecycle `2c448205d864f6388b8be932ecbb1a9e6dcaffe0` |',
        '| OAM-021 | `market → ADAPT` | target `b90e287a40413102c87e8c7fa3d5c01ad401cb6d`; feature `76273c0cb7c2e297c8896a8e7fb6809649fa2870`; lifecycle `2c448205d864f6388b8be932ecbb1a9e6dcaffe0` |\n| OAM-022 | `prey → REUSE` | target proof `50dfa248251f245f5519495a4fbd430b6814ffe4`; feature `e3a5cc7321636270db150d289ba2da9ddb99ef0d`; lifecycle `4aa0a054cbd3fcbc45e2bda5b58ab016df6438e6` |',
    )
    durable = '''# OAM-022 durable completion

Final disposition:

```text
prey REUSE
```

Task-start baselines were Canary `800142e65c2975e57647bf34128ab468532218f0`, Otheryn `b90e287a40413102c87e8c7fa3d5c01ad401cb6d`, fresh upstream Canary `71a0f92b4da3f550b292fa7536a0e35c2769f1ae`, and maintained OTClient `2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f`. Canonical `prey` depends on completed `player-persistence` and `protocol`; `wheel-of-destiny` is an interaction boundary and remains separately owned.

The reviewed classic Prey/Task Hunting core has no stronger independent legacy donor. `src/io/ioprey.cpp` blob `b0e335f5a4f7f9d8a3da75196dedf0d49242ef17`, `src/io/ioprey.hpp` blob `52b5ebf36037e2c9eee8b24741075e24b1680410`, and `src/io/functions/iologindata_save_player.cpp` blob `5bb44a2f2e15c33b39a5b24206440057ded4ab5b` are identical across the pinned target, fresh upstream and legacy baselines; the reviewed Prey/Task Hunting load functions are functionally identical. Maintained OTClient already carries the standard `modules/game_prey/prey.lua` contract, so no client write was required.

Legacy Canary's Taskboard difference was deliberately excluded from the independent Prey reuse boundary: merged Wheel PR #230 consumes Hunting Task points while persisting/applying purchased promotion points under the `wheel-of-destiny` KV scope and changes Wheel-owned components/bindings/tests. That is an explicit Prey↔Wheel integration and remains under the separately active Wheel parity program rather than being copied into OAM-022.

Otheryn PR #46 final head `12d79e4532e5784e9530caf433cdad1c869f0142` changed exactly three proof-only paths and no production runtime/data/persistence/protocol/client/schema/map/asset/deployment path. Autofix.ci #145 run `29723046171`, CI #169 run `29723046359`, and Required #152 run `29723046189` succeeded. Linux debug CTest completed `400/400`, including `Oam022PreyReuseTest` `4/4`; test-log artifact `8453371882` has digest `sha256:23e923635138726a33e7900ff84cd481d2182994cb68020c5d03698e4804886c`. Target comments/reviews/threads were empty, target-main drift was none, and PR #46 merged by expected-head squash as `50dfa248251f245f5519495a4fbd430b6814ffe4`.

Canary governance PR #612 final head `52b27ea5efedab9b0112c7e206e3c697e17a0ac3` changed exactly the OAM-022 report and active-task record. It passed Agent Task Ownership #2754 run `29723974759` and exact-head final-gate CI #3904 run `29723982438`; comments/reviews/threads were empty and Canary `main` had no drift from the immutable task-start baseline. PR #612 merged by expected-head squash as `e3a5cc7321636270db150d289ba2da9ddb99ef0d`.

Authoritative lifecycle PR #613 final head `13531cdab812d169f21a2e724b71b4e157ca93d6` changed exactly the active-delete/archive-add lifecycle paths. It passed Agent Task Ownership #2756 run `29724219954`, draft CI #3905 run `29724220096`, and ready-state CI #3906 run `29724256954`; comments/reviews/threads were empty and Canary `main` had no drift from the governance merge. PR #613 merged by expected-head squash as `4aa0a054cbd3fcbc45e2bda5b58ab016df6438e6`.

OAM-022 does not claim full modern official Hunting Task/Taskboard parity, Wheel Bonus Promotion Shop migration or Wheel allocation ownership, exhaustive Prey formulas/rarity/reroll-price/monster-pool parity, physical-client Prey or Taskboard E2E closure, generic persistence/protocol redesign, or map/OTBM/`items.otb`/asset/schema/deployment changes.

'''
    replace_exact("# Current state\n", durable + "# Current state\n")
    old_state = '''```text
Canary reconciliation base: 2c448205d864f6388b8be932ecbb1a9e6dcaffe0
Otheryn target head after OAM-021: b90e287a40413102c87e8c7fa3d5c01ad401cb6d
maintained OTClient: 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
OAM-001..OAM-021: feature/lifecycle complete
OAM-021 task: archived
OAM-022: NOT STARTED
```

No OAM implementation task is active in this reconciliation record.

# Queue

| Package | Status | Next action |
|---|---|---|
| OAM-001..OAM-021 | completed | preserve durable evidence |
| OAM-022+ | planned, not active | only after this reconciliation merges: perform fresh live-state/open-PR/ownership and exact target/upstream/legacy preflight, then select one dependency-valid canonical package |
'''
    new_state = '''```text
Canary reconciliation base: 4aa0a054cbd3fcbc45e2bda5b58ab016df6438e6
Otheryn target head after OAM-022: 50dfa248251f245f5519495a4fbd430b6814ffe4
maintained OTClient: 2a1b93bcdf6d4317ceeb2254b1e89429453a8e7f
OAM-001..OAM-022: feature/lifecycle complete
OAM-022 task: archived
OAM-023: NOT STARTED
```

No OAM implementation task is active in this reconciliation record.

# Queue

| Package | Status | Next action |
|---|---|---|
| OAM-001..OAM-022 | completed | preserve durable evidence |
| OAM-023+ | planned, not active | only after this reconciliation merges: perform fresh live-state/open-PR/ownership and exact target/upstream/legacy preflight, then select one dependency-valid canonical package |
'''
    replace_exact(old_state, new_state)
    replace_exact(
        "- OAM-021 does not claim crash-safe exactly-once Market create/cancel/accept/expiry, cross-process or multiwriter Market safety, remote-player mutation routing, generic multichannel/economic-ledger/leader-election redesign, exhaustive Real Tibia Market parity, maintained-client changes, or physical-client Market E2E closure.",
        "- OAM-021 does not claim crash-safe exactly-once Market create/cancel/accept/expiry, cross-process or multiwriter Market safety, remote-player mutation routing, generic multichannel/economic-ledger/leader-election redesign, exhaustive Real Tibia Market parity, maintained-client changes, or physical-client Market E2E closure.\n- OAM-022 does not claim full modern Hunting Task/Taskboard parity, Wheel Bonus Promotion Shop or Wheel allocation ownership, exhaustive Prey formulas/rarity/reroll-price/monster-pool parity, physical-client Prey/Taskboard E2E closure, generic persistence/protocol redesign, or map/asset/schema/deployment migration.",
    )
    replace_exact(
        "Merge this program-only OAM-021 completion reconciliation after exact-head Ownership/CI/review gates. Only then may a fresh OAM-022 preflight begin. OAM-022 is NOT STARTED by this record.",
        "Merge this program-only OAM-022 completion reconciliation after exact-head Ownership/CI/review gates. Only then may a fresh OAM-023 preflight begin. OAM-023 is NOT STARTED by this record.",
    )
    path.write_text(text, encoding="utf-8")

    subprocess.run(["git", "fetch", "origin", "main"], check=True)
    subprocess.run(["git", "checkout", "origin/main", "--", ".github/workflows/agent-task-ownership.yml", "tools/check_lua_api_quality.py"], check=True)
    for helper in (
        Path(".github/workflows/oam-022-program-reconciliation-materializer.yml"),
        Path(".github/oam-022-program-reconciliation-trigger"),
    ):
        if helper.exists():
            helper.unlink()
    subprocess.run(["git", "config", "user.name", "github-actions[bot]"], check=True)
    subprocess.run(["git", "config", "user.email", "41898282+github-actions[bot]@users.noreply.github.com"], check=True)
    subprocess.run(["git", "add", "-A"], check=True)
    subprocess.run(["git", "commit", "-m", "docs(oam): reconcile OAM-022 durable completion"], check=True)
    subprocess.run(["git", "push", "origin", "HEAD:docs/oam-022-program-reconciliation"], check=True)


def iter_functions(data):
    for class_name, methods in data.get("classes", {}).items():
        for method in methods:
            yield f"{class_name}.{method.get('name', '')}", method

    for function in data.get("globals", []):
        yield function.get("name", ""), function


def collect_metrics(data):
    metrics = dict.fromkeys(METRIC_KEYS, 0)
    examples = {key: [] for key in METRIC_KEYS}

    for function_name, function in iter_functions(data):
        collect_parameter_metrics(function_name, function.get("params", []), metrics, examples)
        collect_return_metrics(function_name, function.get("return", ""), metrics, examples)

    return metrics, examples


def collect_parameter_metrics(function_name, parameters, metrics, examples):
    for parameter in parameters:
        for metric_key, pattern in PARAMETER_METRICS:
            if pattern.search(parameter):
                increment_metric(metric_key, metrics, examples, function_name, parameter)
        if parameter.startswith("..."):
            increment_metric("param_vararg", metrics, examples, function_name, parameter)


def collect_return_metrics(function_name, return_type, metrics, examples):
    metric_key = RETURN_METRICS.get(return_type)
    if metric_key:
        increment_metric(metric_key, metrics, examples, function_name, return_type)


def increment_metric(metric_key, metrics, examples, function_name, value):
    metrics[metric_key] += 1
    append_example(examples[metric_key], function_name, value)


def append_example(examples, function_name, value):
    if len(examples) < 5:
        examples.append(f"{function_name}: {value}")


def load_json(path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main():
    materialize_oam022_program_if_requested()

    parser = argparse.ArgumentParser(description="Check generated Lua API documentation quality metrics.")
    parser.add_argument(
        "--update-baseline",
        action="store_true",
        help="write the current metrics to docs/lua-api/lua_api_quality_baseline.json",
    )
    args = parser.parse_args()

    current, examples = collect_metrics(load_json(DOC_PATH))
    if args.update_baseline:
        write_json(BASELINE_PATH, current)
        print(f"Updated Lua API quality baseline: {current}")
        return 0

    if not BASELINE_PATH.exists():
        print(f"::error::{BASELINE_PATH} is missing. Run tools/check_lua_api_quality.py --update-baseline and commit it.")
        return 1

    baseline = load_json(BASELINE_PATH)
    failed = False
    for key in METRIC_KEYS:
        value = current[key]
        allowed = baseline.get(key, value)
        if value > allowed:
            print(f"::error::Lua API quality regression: {key} increased from {allowed} to {value}")
            for example in examples[key]:
                print(f"  {example}")
            failed = True

    if failed:
        return 1

    print(f"Lua API quality check passed: {current}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
