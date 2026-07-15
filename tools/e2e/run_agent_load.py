#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import json
import math
import os
import struct
import sys
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
STATUS_REQUEST = struct.pack("<H", 5) + b"\xffinfo"
LOOPBACK_HOSTS = {"127.0.0.1", "::1"}


class LoadConfigError(ValueError):
    pass


@dataclass(frozen=True)
class Thresholds:
    max_error_rate: float
    max_p95_ms: float
    min_successes: int


@dataclass(frozen=True)
class Stage:
    name: str
    requests: int
    concurrency: int
    request_timeout_seconds: float
    thresholds: Thresholds


@dataclass(frozen=True)
class Profile:
    profile_id: str
    mode: str
    protocol: str
    host: str
    port: int
    gate: bool
    sample_interval_ms: int
    stages: tuple[Stage, ...]
    source: Path


def _require_mapping(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise LoadConfigError(f"{path} must be an object")
    return value


def _require_list(value: Any, path: str) -> list[Any]:
    if not isinstance(value, list) or not value:
        raise LoadConfigError(f"{path} must be a non-empty array")
    return value


def _require_string(mapping: dict[str, Any], key: str, path: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise LoadConfigError(f"{path}.{key} must be a non-empty string")
    return value.strip()


def _require_positive_int(mapping: dict[str, Any], key: str, path: str) -> int:
    value = mapping.get(key)
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise LoadConfigError(f"{path}.{key} must be a positive integer")
    return value


def _require_positive_number(mapping: dict[str, Any], key: str, path: str) -> float:
    value = mapping.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        raise LoadConfigError(f"{path}.{key} must be a positive number")
    return float(value)


def _validate_loopback(host: str) -> None:
    if host not in LOOPBACK_HOSTS:
        raise LoadConfigError(
            f"load target host must be a literal loopback address ({', '.join(sorted(LOOPBACK_HOSTS))}); got {host!r}"
        )


def _parse_thresholds(value: Any, path: str, requests: int) -> Thresholds:
    data = _require_mapping(value, path)
    max_error_rate = data.get("max_error_rate")
    if isinstance(max_error_rate, bool) or not isinstance(max_error_rate, (int, float)):
        raise LoadConfigError(f"{path}.max_error_rate must be a number between 0 and 1")
    max_error_rate = float(max_error_rate)
    if not 0.0 <= max_error_rate <= 1.0:
        raise LoadConfigError(f"{path}.max_error_rate must be between 0 and 1")
    max_p95_ms = _require_positive_number(data, "max_p95_ms", path)
    min_successes = data.get("min_successes", requests)
    if not isinstance(min_successes, int) or isinstance(min_successes, bool) or min_successes < 0:
        raise LoadConfigError(f"{path}.min_successes must be a non-negative integer")
    if min_successes > requests:
        raise LoadConfigError(f"{path}.min_successes cannot exceed stage requests")
    return Thresholds(
        max_error_rate=max_error_rate,
        max_p95_ms=max_p95_ms,
        min_successes=min_successes,
    )


def load_profile(path: Path) -> Profile:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise LoadConfigError(f"{path}: invalid JSON: {exc}") from exc
    except OSError as exc:
        raise LoadConfigError(f"{path}: cannot read profile: {exc}") from exc

    if not isinstance(data, dict):
        raise LoadConfigError(f"{path}: profile root must be an object")
    if data.get("schema_version") != SCHEMA_VERSION:
        raise LoadConfigError(
            f"{path}: schema_version must be {SCHEMA_VERSION}, got {data.get('schema_version')!r}"
        )

    profile_id = _require_string(data, "id", "profile")
    mode = _require_string(data, "mode", "profile")
    if mode not in {"load", "stress"}:
        raise LoadConfigError("profile.mode must be 'load' or 'stress'")
    protocol = _require_string(data, "protocol", "profile")
    if protocol != "status-xml":
        raise LoadConfigError("profile.protocol must be 'status-xml'")

    target = _require_mapping(data.get("target"), "profile.target")
    host = _require_string(target, "host", "profile.target")
    _validate_loopback(host)
    port = _require_positive_int(target, "port", "profile.target")
    if port > 65535:
        raise LoadConfigError("profile.target.port must be <= 65535")

    policy = _require_mapping(data.get("policy"), "profile.policy")
    gate = policy.get("gate")
    if not isinstance(gate, bool):
        raise LoadConfigError("profile.policy.gate must be a boolean")
    sample_interval_ms = _require_positive_int(policy, "sample_interval_ms", "profile.policy")

    raw_stages = _require_list(data.get("stages"), "profile.stages")
    stages: list[Stage] = []
    seen_names: set[str] = set()
    for index, raw_stage in enumerate(raw_stages):
        stage_path = f"profile.stages[{index}]"
        stage_data = _require_mapping(raw_stage, stage_path)
        name = _require_string(stage_data, "name", stage_path)
        if name in seen_names:
            raise LoadConfigError(f"{stage_path}.name duplicates an earlier stage: {name}")
        seen_names.add(name)
        requests = _require_positive_int(stage_data, "requests", stage_path)
        concurrency = _require_positive_int(stage_data, "concurrency", stage_path)
        if concurrency > requests:
            raise LoadConfigError(f"{stage_path}.concurrency cannot exceed requests")
        timeout = _require_positive_number(stage_data, "request_timeout_seconds", stage_path)
        thresholds = _parse_thresholds(stage_data.get("thresholds"), f"{stage_path}.thresholds", requests)
        stages.append(
            Stage(
                name=name,
                requests=requests,
                concurrency=concurrency,
                request_timeout_seconds=timeout,
                thresholds=thresholds,
            )
        )

    if mode == "load" and len(stages) != 1:
        raise LoadConfigError("load profiles must define exactly one stage")
    if mode == "stress" and len(stages) < 2:
        raise LoadConfigError("stress profiles must define at least two stages")

    return Profile(
        profile_id=profile_id,
        mode=mode,
        protocol=protocol,
        host=host,
        port=port,
        gate=gate,
        sample_interval_ms=sample_interval_ms,
        stages=tuple(stages),
        source=path,
    )


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, math.ceil((percentile / 100.0) * len(ordered)) - 1)
    return round(ordered[index], 3)


async def _status_exchange(host: str, port: int) -> tuple[float, float, int]:
    started = time.perf_counter()
    reader, writer = await asyncio.open_connection(host, port)
    connected = time.perf_counter()
    try:
        writer.write(STATUS_REQUEST)
        await writer.drain()
        payload = await reader.read(1024 * 1024)
    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except (ConnectionError, OSError):
            pass
    finished = time.perf_counter()
    if b"<tsqp" not in payload or b"<serverinfo" not in payload:
        raise RuntimeError("status endpoint returned an invalid XML info response")
    return (
        (connected - started) * 1000.0,
        (finished - started) * 1000.0,
        len(payload),
    )


async def _one_request(host: str, port: int, timeout: float) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        connect_ms, total_ms, bytes_received = await asyncio.wait_for(
            _status_exchange(host, port),
            timeout=timeout,
        )
        return {
            "ok": True,
            "connect_ms": connect_ms,
            "total_ms": total_ms,
            "bytes_received": bytes_received,
            "error": None,
        }
    except asyncio.TimeoutError:
        return {
            "ok": False,
            "connect_ms": None,
            "total_ms": (time.perf_counter() - started) * 1000.0,
            "bytes_received": 0,
            "error": "timeout",
        }
    except (ConnectionError, OSError, RuntimeError) as exc:
        return {
            "ok": False,
            "connect_ms": None,
            "total_ms": (time.perf_counter() - started) * 1000.0,
            "bytes_received": 0,
            "error": f"{type(exc).__name__}: {exc}",
        }


def _read_process_sample(pid: int) -> tuple[int, int] | None:
    try:
        stat_fields = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8").split()
        status_lines = Path(f"/proc/{pid}/status").read_text(encoding="utf-8").splitlines()
        cpu_ticks = int(stat_fields[13]) + int(stat_fields[14])
        rss_kb = 0
        for line in status_lines:
            if line.startswith("VmRSS:"):
                rss_kb = int(line.split()[1])
                break
        return cpu_ticks, rss_kb
    except (OSError, ValueError, IndexError):
        return None


class ProcessSampler:
    def __init__(self, pid: int | None, interval_ms: int) -> None:
        self.pid = pid
        self.interval = interval_ms / 1000.0
        self.samples = 0
        self.peak_rss_kb = 0
        self.start_ticks: int | None = None
        self.end_ticks: int | None = None
        self.started_at: float | None = None
        self.ended_at: float | None = None
        self._stop = asyncio.Event()

    async def run(self) -> None:
        if self.pid is None:
            return
        self.started_at = time.perf_counter()
        while not self._stop.is_set():
            sample = _read_process_sample(self.pid)
            if sample is not None:
                ticks, rss_kb = sample
                if self.start_ticks is None:
                    self.start_ticks = ticks
                self.end_ticks = ticks
                self.peak_rss_kb = max(self.peak_rss_kb, rss_kb)
                self.samples += 1
            try:
                await asyncio.wait_for(self._stop.wait(), timeout=self.interval)
            except asyncio.TimeoutError:
                pass
        self.ended_at = time.perf_counter()
        sample = _read_process_sample(self.pid)
        if sample is not None:
            ticks, rss_kb = sample
            if self.start_ticks is None:
                self.start_ticks = ticks
            self.end_ticks = ticks
            self.peak_rss_kb = max(self.peak_rss_kb, rss_kb)
            self.samples += 1

    def stop(self) -> None:
        self._stop.set()

    def result(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "pid": self.pid,
            "samples": self.samples,
            "peak_rss_kb": self.peak_rss_kb if self.samples else None,
            "cpu_percent": None,
        }
        if (
            self.pid is not None
            and self.start_ticks is not None
            and self.end_ticks is not None
            and self.started_at is not None
            and self.ended_at is not None
            and self.ended_at > self.started_at
        ):
            clock_ticks = os.sysconf(os.sysconf_names["SC_CLK_TCK"])
            cpu_seconds = (self.end_ticks - self.start_ticks) / float(clock_ticks)
            elapsed = self.ended_at - self.started_at
            payload["cpu_percent"] = round((cpu_seconds / elapsed) * 100.0, 3)
        return payload


def _summarize(results: list[dict[str, Any]], duration_seconds: float) -> dict[str, Any]:
    successes = [item for item in results if item["ok"]]
    failures = [item for item in results if not item["ok"]]
    connect_latencies = [float(item["connect_ms"]) for item in successes]
    total_latencies = [float(item["total_ms"]) for item in successes]
    attempts = len(results)
    success_count = len(successes)
    failure_count = len(failures)
    error_rate = (failure_count / attempts) if attempts else 1.0
    errors = Counter(str(item["error"]) for item in failures)
    return {
        "attempts": attempts,
        "successes": success_count,
        "failures": failure_count,
        "error_rate": round(error_rate, 6),
        "throughput_rps": round(success_count / duration_seconds, 3) if duration_seconds > 0 else 0.0,
        "bytes_received": sum(int(item["bytes_received"]) for item in successes),
        "connect_ms": {
            "p50": _percentile(connect_latencies, 50),
            "p95": _percentile(connect_latencies, 95),
            "p99": _percentile(connect_latencies, 99),
            "max": round(max(connect_latencies), 3) if connect_latencies else 0.0,
        },
        "round_trip_ms": {
            "p50": _percentile(total_latencies, 50),
            "p95": _percentile(total_latencies, 95),
            "p99": _percentile(total_latencies, 99),
            "max": round(max(total_latencies), 3) if total_latencies else 0.0,
        },
        "errors": dict(sorted(errors.items())),
    }


def _threshold_result(summary: dict[str, Any], thresholds: Thresholds) -> dict[str, Any]:
    checks = {
        "max_error_rate": summary["error_rate"] <= thresholds.max_error_rate,
        "max_p95_ms": summary["round_trip_ms"]["p95"] <= thresholds.max_p95_ms,
        "min_successes": summary["successes"] >= thresholds.min_successes,
    }
    return {
        "limits": {
            "max_error_rate": thresholds.max_error_rate,
            "max_p95_ms": thresholds.max_p95_ms,
            "min_successes": thresholds.min_successes,
        },
        "checks": checks,
        "passed": all(checks.values()),
    }


async def _run_stage(profile: Profile, stage: Stage) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    counter = 0
    counter_lock = asyncio.Lock()
    results: list[dict[str, Any]] = []

    async def worker() -> None:
        nonlocal counter
        while True:
            async with counter_lock:
                if counter >= stage.requests:
                    return
                counter += 1
            results.append(
                await _one_request(
                    profile.host,
                    profile.port,
                    stage.request_timeout_seconds,
                )
            )

    started = time.perf_counter()
    await asyncio.gather(*(worker() for _ in range(stage.concurrency)))
    duration = time.perf_counter() - started
    summary = _summarize(results, duration)
    threshold = _threshold_result(summary, stage.thresholds)
    return (
        {
            "name": stage.name,
            "requests": stage.requests,
            "concurrency": stage.concurrency,
            "request_timeout_seconds": stage.request_timeout_seconds,
            "duration_seconds": round(duration, 6),
            "metrics": summary,
            "thresholds": threshold,
        },
        results,
    )


async def run_profile(profile: Profile, server_pid: int | None = None) -> dict[str, Any]:
    sampler = ProcessSampler(server_pid, profile.sample_interval_ms)
    sampler_task = asyncio.create_task(sampler.run())
    all_results: list[dict[str, Any]] = []
    stages: list[dict[str, Any]] = []
    started = time.perf_counter()
    try:
        for stage in profile.stages:
            stage_result, request_results = await _run_stage(profile, stage)
            stages.append(stage_result)
            all_results.extend(request_results)
    finally:
        sampler.stop()
        await sampler_task
    duration = time.perf_counter() - started

    aggregate = _summarize(all_results, duration)
    thresholds_passed = all(stage["thresholds"]["passed"] for stage in stages)
    gate_passed = thresholds_passed or not profile.gate
    status = "success" if thresholds_passed else ("threshold-failure" if profile.gate else "completed")

    return {
        "schema_version": SCHEMA_VERSION,
        "profile": profile.profile_id,
        "profile_source": profile.source.as_posix(),
        "mode": profile.mode,
        "protocol": profile.protocol,
        "target": {"host": profile.host, "port": profile.port},
        "policy": {
            "gate": profile.gate,
            "sample_interval_ms": profile.sample_interval_ms,
        },
        "status": status,
        "thresholds_passed": thresholds_passed,
        "gate_passed": gate_passed,
        "duration_seconds": round(duration, 6),
        "stages": stages,
        "aggregate": aggregate,
        "server_process": sampler.result(),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run loopback-only lightweight Canary status-protocol load/stress profiles."
    )
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--host")
    parser.add_argument("--port", type=int)
    parser.add_argument("--server-pid", type=int)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        profile = load_profile(args.profile.resolve())
        if args.host is not None:
            _validate_loopback(args.host)
            profile = Profile(
                profile_id=profile.profile_id,
                mode=profile.mode,
                protocol=profile.protocol,
                host=args.host,
                port=profile.port,
                gate=profile.gate,
                sample_interval_ms=profile.sample_interval_ms,
                stages=profile.stages,
                source=profile.source,
            )
        if args.port is not None:
            if not 1 <= args.port <= 65535:
                raise LoadConfigError("--port must be between 1 and 65535")
            profile = Profile(
                profile_id=profile.profile_id,
                mode=profile.mode,
                protocol=profile.protocol,
                host=profile.host,
                port=args.port,
                gate=profile.gate,
                sample_interval_ms=profile.sample_interval_ms,
                stages=profile.stages,
                source=profile.source,
            )
        if args.server_pid is not None and args.server_pid <= 0:
            raise LoadConfigError("--server-pid must be a positive integer")

        result = asyncio.run(run_profile(profile, args.server_pid))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(
            json.dumps(
                {
                    "profile": result["profile"],
                    "status": result["status"],
                    "gate_passed": result["gate_passed"],
                    "attempts": result["aggregate"]["attempts"],
                    "successes": result["aggregate"]["successes"],
                    "error_rate": result["aggregate"]["error_rate"],
                    "throughput_rps": result["aggregate"]["throughput_rps"],
                    "p95_ms": result["aggregate"]["round_trip_ms"]["p95"],
                    "peak_rss_kb": result["server_process"]["peak_rss_kb"],
                    "cpu_percent": result["server_process"]["cpu_percent"],
                },
                sort_keys=True,
            )
        )
        return 0 if result["gate_passed"] else 1
    except (LoadConfigError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
