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
STATUS_REQUEST_BODY = b"\xff\xffinfo"
STATUS_REQUEST = struct.pack("<H", len(STATUS_REQUEST_BODY)) + STATUS_REQUEST_BODY
LOOPBACK_HOSTS = {"127.0.0.1", "::1"}
SOURCE_IP_STRATEGIES = {"single", "unique-loopback-v4"}
MAX_RESPONSE_BYTES = 1024 * 1024
MAX_UNIQUE_LOOPBACK_SOURCES = (1 << 24) - 2


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
    timeout_seconds: float
    thresholds: Thresholds


@dataclass(frozen=True)
class Profile:
    profile_id: str
    mode: str
    host: str
    port: int
    gate: bool
    sample_interval_ms: int
    source_ip_strategy: str
    stages: tuple[Stage, ...]
    source: Path


def _mapping(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise LoadConfigError(f"{name} must be an object")
    return value


def _string(data: dict[str, Any], key: str, name: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise LoadConfigError(f"{name}.{key} must be a non-empty string")
    return value.strip()


def _positive_int(data: dict[str, Any], key: str, name: str) -> int:
    value = data.get(key)
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise LoadConfigError(f"{name}.{key} must be a positive integer")
    return value


def _positive_number(data: dict[str, Any], key: str, name: str) -> float:
    value = data.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
        raise LoadConfigError(f"{name}.{key} must be a positive number")
    return float(value)


def _validate_loopback(host: str) -> None:
    if host not in LOOPBACK_HOSTS:
        raise LoadConfigError(f"target host must be a literal loopback address, got {host!r}")


def load_profile(path: Path) -> Profile:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LoadConfigError(f"cannot read profile {path}: {exc}") from exc
    data = _mapping(raw, "profile")
    if data.get("schema_version") != SCHEMA_VERSION:
        raise LoadConfigError(f"profile.schema_version must be {SCHEMA_VERSION}")
    profile_id = _string(data, "id", "profile")
    mode = _string(data, "mode", "profile")
    if mode not in {"load", "stress"}:
        raise LoadConfigError("profile.mode must be 'load' or 'stress'")
    if _string(data, "protocol", "profile") != "status-xml":
        raise LoadConfigError("profile.protocol must be 'status-xml'")

    target = _mapping(data.get("target"), "profile.target")
    host = _string(target, "host", "profile.target")
    _validate_loopback(host)
    port = _positive_int(target, "port", "profile.target")
    if port > 65535:
        raise LoadConfigError("profile.target.port must be <= 65535")

    policy = _mapping(data.get("policy"), "profile.policy")
    gate = policy.get("gate")
    if not isinstance(gate, bool):
        raise LoadConfigError("profile.policy.gate must be a boolean")
    sample_interval_ms = _positive_int(policy, "sample_interval_ms", "profile.policy")
    source_ip_strategy = str(policy.get("source_ip_strategy", "single"))
    if source_ip_strategy not in SOURCE_IP_STRATEGIES:
        raise LoadConfigError(f"unsupported source_ip_strategy {source_ip_strategy!r}")
    if source_ip_strategy == "unique-loopback-v4" and host != "127.0.0.1":
        raise LoadConfigError("unique-loopback-v4 requires target host 127.0.0.1")

    raw_stages = data.get("stages")
    if not isinstance(raw_stages, list) or not raw_stages:
        raise LoadConfigError("profile.stages must be a non-empty array")
    stages: list[Stage] = []
    names: set[str] = set()
    total_requests = 0
    for index, raw_stage in enumerate(raw_stages):
        name_path = f"profile.stages[{index}]"
        stage_data = _mapping(raw_stage, name_path)
        name = _string(stage_data, "name", name_path)
        if name in names:
            raise LoadConfigError(f"duplicate stage name {name!r}")
        names.add(name)
        requests = _positive_int(stage_data, "requests", name_path)
        concurrency = _positive_int(stage_data, "concurrency", name_path)
        if concurrency > requests:
            raise LoadConfigError(f"{name_path}.concurrency cannot exceed requests")
        timeout_seconds = _positive_number(stage_data, "request_timeout_seconds", name_path)
        threshold_data = _mapping(stage_data.get("thresholds"), f"{name_path}.thresholds")
        max_error_rate = threshold_data.get("max_error_rate")
        if isinstance(max_error_rate, bool) or not isinstance(max_error_rate, (int, float)):
            raise LoadConfigError(f"{name_path}.thresholds.max_error_rate must be numeric")
        max_error_rate = float(max_error_rate)
        if not 0.0 <= max_error_rate <= 1.0:
            raise LoadConfigError(f"{name_path}.thresholds.max_error_rate must be between 0 and 1")
        max_p95_ms = _positive_number(threshold_data, "max_p95_ms", f"{name_path}.thresholds")
        min_successes = threshold_data.get("min_successes", requests)
        if not isinstance(min_successes, int) or isinstance(min_successes, bool) or not 0 <= min_successes <= requests:
            raise LoadConfigError(f"{name_path}.thresholds.min_successes must be between 0 and requests")
        stages.append(
            Stage(
                name=name,
                requests=requests,
                concurrency=concurrency,
                timeout_seconds=timeout_seconds,
                thresholds=Thresholds(max_error_rate, max_p95_ms, min_successes),
            )
        )
        total_requests += requests

    if mode == "load" and len(stages) != 1:
        raise LoadConfigError("load profiles must define exactly one stage")
    if mode == "stress" and len(stages) < 2:
        raise LoadConfigError("stress profiles must define at least two stages")
    if source_ip_strategy == "unique-loopback-v4" and total_requests > MAX_UNIQUE_LOOPBACK_SOURCES:
        raise LoadConfigError("profile exceeds unique loopback source capacity")

    return Profile(profile_id, mode, host, port, gate, sample_interval_ms, source_ip_strategy, tuple(stages), path)


def _percentile(values: list[float], percentile: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = max(0, math.ceil(percentile / 100.0 * len(ordered)) - 1)
    return round(ordered[index], 3)


def _source_ip(index: int) -> str:
    if not 0 <= index < MAX_UNIQUE_LOOPBACK_SOURCES:
        raise LoadConfigError("unique loopback source index out of range")
    value = index + 1
    return f"127.{(value >> 16) & 0xFF}.{(value >> 8) & 0xFF}.{value & 0xFF}"


async def _exchange(host: str, port: int, source_ip: str | None) -> tuple[float, float, int]:
    started = time.perf_counter()
    reader, writer = await asyncio.open_connection(host, port, local_addr=(source_ip, 0) if source_ip else None)
    connected = time.perf_counter()
    try:
        writer.write(STATUS_REQUEST)
        await writer.drain()
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = await reader.read(65536)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_RESPONSE_BYTES:
                raise RuntimeError("status response exceeded 1 MiB")
            chunks.append(chunk)
        payload = b"".join(chunks)
    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except (ConnectionError, OSError):
            pass
    finished = time.perf_counter()
    if b"<tsqp" not in payload or b"<serverinfo" not in payload:
        raise RuntimeError(f"invalid status XML response ({len(payload)} bytes)")
    return (connected - started) * 1000.0, (finished - started) * 1000.0, len(payload)


async def _request(profile: Profile, stage: Stage, index: int) -> dict[str, Any]:
    source = _source_ip(index) if profile.source_ip_strategy == "unique-loopback-v4" else None
    started = time.perf_counter()
    try:
        connect_ms, total_ms, bytes_received = await asyncio.wait_for(
            _exchange(profile.host, profile.port, source), timeout=stage.timeout_seconds
        )
        return {"ok": True, "connect_ms": connect_ms, "total_ms": total_ms, "bytes_received": bytes_received, "error": None}
    except asyncio.TimeoutError:
        error = "timeout"
    except (ConnectionError, OSError, RuntimeError) as exc:
        error = f"{type(exc).__name__}: {exc}"
    return {"ok": False, "connect_ms": None, "total_ms": (time.perf_counter() - started) * 1000.0, "bytes_received": 0, "error": error}


def _process_sample(pid: int) -> tuple[int, int] | None:
    try:
        fields = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8").split()
        ticks = int(fields[13]) + int(fields[14])
        rss_kb = 0
        for line in Path(f"/proc/{pid}/status").read_text(encoding="utf-8").splitlines():
            if line.startswith("VmRSS:"):
                rss_kb = int(line.split()[1])
                break
        return ticks, rss_kb
    except (OSError, ValueError, IndexError):
        return None


class ProcessSampler:
    def __init__(self, pid: int | None, interval_ms: int) -> None:
        self.pid = pid
        self.interval = interval_ms / 1000.0
        self.samples: list[tuple[float, int, int]] = []
        self.stop_event = asyncio.Event()

    async def run(self) -> None:
        if self.pid is None:
            return
        while not self.stop_event.is_set():
            sample = _process_sample(self.pid)
            if sample:
                self.samples.append((time.perf_counter(), sample[0], sample[1]))
            try:
                await asyncio.wait_for(self.stop_event.wait(), timeout=self.interval)
            except asyncio.TimeoutError:
                pass
        sample = _process_sample(self.pid)
        if sample:
            self.samples.append((time.perf_counter(), sample[0], sample[1]))

    def stop(self) -> None:
        self.stop_event.set()

    def result(self) -> dict[str, Any]:
        if not self.samples:
            return {"pid": self.pid, "samples": 0, "peak_rss_kb": None, "cpu_percent": None}
        peak_rss = max(sample[2] for sample in self.samples)
        cpu_percent = None
        if len(self.samples) >= 2 and self.samples[-1][0] > self.samples[0][0]:
            ticks_per_second = os.sysconf(os.sysconf_names["SC_CLK_TCK"])
            cpu_seconds = (self.samples[-1][1] - self.samples[0][1]) / float(ticks_per_second)
            elapsed = self.samples[-1][0] - self.samples[0][0]
            cpu_percent = round(cpu_seconds / elapsed * 100.0, 3)
        return {"pid": self.pid, "samples": len(self.samples), "peak_rss_kb": peak_rss, "cpu_percent": cpu_percent}


def _summary(results: list[dict[str, Any]], duration: float) -> dict[str, Any]:
    successes = [item for item in results if item["ok"]]
    failures = [item for item in results if not item["ok"]]
    connect = [float(item["connect_ms"]) for item in successes]
    total = [float(item["total_ms"]) for item in successes]
    attempts = len(results)
    return {
        "attempts": attempts,
        "successes": len(successes),
        "failures": len(failures),
        "error_rate": round(len(failures) / attempts, 6) if attempts else 1.0,
        "throughput_rps": round(len(successes) / duration, 3) if duration > 0 else 0.0,
        "bytes_received": sum(int(item["bytes_received"]) for item in successes),
        "connect_ms": {"p50": _percentile(connect, 50), "p95": _percentile(connect, 95), "p99": _percentile(connect, 99), "max": round(max(connect), 3) if connect else 0.0},
        "round_trip_ms": {"p50": _percentile(total, 50), "p95": _percentile(total, 95), "p99": _percentile(total, 99), "max": round(max(total), 3) if total else 0.0},
        "errors": dict(sorted(Counter(str(item["error"]) for item in failures).items())),
    }


async def _run_stage(profile: Profile, stage: Stage, offset: int) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    queue: asyncio.Queue[int] = asyncio.Queue()
    for index in range(stage.requests):
        queue.put_nowait(offset + index)
    results: list[dict[str, Any]] = []

    async def worker() -> None:
        while True:
            try:
                index = queue.get_nowait()
            except asyncio.QueueEmpty:
                return
            try:
                results.append(await _request(profile, stage, index))
            finally:
                queue.task_done()

    started = time.perf_counter()
    await asyncio.gather(*(worker() for _ in range(stage.concurrency)))
    duration = time.perf_counter() - started
    metrics = _summary(results, duration)
    checks = {
        "max_error_rate": metrics["error_rate"] <= stage.thresholds.max_error_rate,
        "max_p95_ms": metrics["round_trip_ms"]["p95"] <= stage.thresholds.max_p95_ms,
        "min_successes": metrics["successes"] >= stage.thresholds.min_successes,
    }
    return {
        "name": stage.name,
        "requests": stage.requests,
        "concurrency": stage.concurrency,
        "request_timeout_seconds": stage.timeout_seconds,
        "duration_seconds": round(duration, 6),
        "metrics": metrics,
        "thresholds": {
            "limits": {
                "max_error_rate": stage.thresholds.max_error_rate,
                "max_p95_ms": stage.thresholds.max_p95_ms,
                "min_successes": stage.thresholds.min_successes,
            },
            "checks": checks,
            "passed": all(checks.values()),
        },
    }, results


async def run_profile(profile: Profile, server_pid: int | None = None) -> dict[str, Any]:
    sampler = ProcessSampler(server_pid, profile.sample_interval_ms)
    sampler_task = asyncio.create_task(sampler.run())
    stages: list[dict[str, Any]] = []
    all_results: list[dict[str, Any]] = []
    offset = 0
    started = time.perf_counter()
    try:
        for stage in profile.stages:
            stage_result, results = await _run_stage(profile, stage, offset)
            stages.append(stage_result)
            all_results.extend(results)
            offset += stage.requests
    finally:
        sampler.stop()
        await sampler_task
    duration = time.perf_counter() - started
    thresholds_passed = all(stage["thresholds"]["passed"] for stage in stages)
    gate_passed = thresholds_passed or not profile.gate
    return {
        "schema_version": SCHEMA_VERSION,
        "profile": profile.profile_id,
        "profile_source": profile.source.as_posix(),
        "mode": profile.mode,
        "protocol": "status-xml",
        "target": {"host": profile.host, "port": profile.port},
        "policy": {"gate": profile.gate, "sample_interval_ms": profile.sample_interval_ms, "source_ip_strategy": profile.source_ip_strategy},
        "status": "success" if thresholds_passed else ("threshold-failure" if profile.gate else "completed"),
        "thresholds_passed": thresholds_passed,
        "gate_passed": gate_passed,
        "duration_seconds": round(duration, 6),
        "stages": stages,
        "aggregate": _summary(all_results, duration),
        "server_process": sampler.result(),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run loopback-only Canary status-protocol load/stress profiles.")
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--host")
    parser.add_argument("--port", type=int)
    parser.add_argument("--server-pid", type=int)
    args = parser.parse_args(argv)
    try:
        profile = load_profile(args.profile.resolve())
        if args.host is not None:
            _validate_loopback(args.host)
            if profile.source_ip_strategy == "unique-loopback-v4" and args.host != "127.0.0.1":
                raise LoadConfigError("unique-loopback-v4 requires 127.0.0.1")
            profile = Profile(profile.profile_id, profile.mode, args.host, profile.port, profile.gate, profile.sample_interval_ms, profile.source_ip_strategy, profile.stages, profile.source)
        if args.port is not None:
            if not 1 <= args.port <= 65535:
                raise LoadConfigError("--port must be between 1 and 65535")
            profile = Profile(profile.profile_id, profile.mode, profile.host, args.port, profile.gate, profile.sample_interval_ms, profile.source_ip_strategy, profile.stages, profile.source)
        result = asyncio.run(run_profile(profile, args.server_pid))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({
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
        }, sort_keys=True))
        return 0 if result["gate_passed"] else 1
    except (LoadConfigError, OSError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
