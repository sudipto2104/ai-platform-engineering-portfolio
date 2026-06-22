#!/usr/bin/env python3
"""Load-test an inference endpoint and capture latency/resource samples."""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib import error, request

DEFAULT_URL = "http://localhost:8080/predict"


@dataclass
class Sample:
    latency_ms: float
    status_code: int
    success: bool


@dataclass
class MeasurementReport:
    endpoint: str
    concurrency: int
    requests: int
    duration_sec: float
    success_rate: float
    latency_p50_ms: float
    latency_p95_ms: float
    latency_p99_ms: float
    latency_max_ms: float


def _send_request(url: str, payload: dict) -> Sample:
    data = json.dumps(payload).encode()
    req = request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    start = time.perf_counter()
    try:
        with request.urlopen(req, timeout=30) as resp:
            resp.read()
            latency_ms = (time.perf_counter() - start) * 1000
            return Sample(latency_ms=latency_ms, status_code=resp.status, success=True)
    except error.HTTPError as exc:
        latency_ms = (time.perf_counter() - start) * 1000
        return Sample(latency_ms=latency_ms, status_code=exc.code, success=False)
    except error.URLError:
        latency_ms = (time.perf_counter() - start) * 1000
        return Sample(latency_ms=latency_ms, status_code=0, success=False)


def run_load_test(url: str, concurrency: int, total_requests: int) -> MeasurementReport:
    payload = {"input_text": "kubernetes inference workload sample", "max_tokens": 64}
    samples: list[Sample] = []
    start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(_send_request, url, payload) for _ in range(total_requests)]
        for future in as_completed(futures):
            samples.append(future.result())

    duration = time.perf_counter() - start
    latencies = sorted(s.latency_ms for s in samples if s.success)
    successes = sum(1 for s in samples if s.success)

    def percentile(values: list[float], pct: float) -> float:
        if not values:
            return 0.0
        index = int(len(values) * pct / 100)
        index = min(index, len(values) - 1)
        return values[index]

    return MeasurementReport(
        endpoint=url,
        concurrency=concurrency,
        requests=total_requests,
        duration_sec=round(duration, 2),
        success_rate=round(successes / total_requests, 4),
        latency_p50_ms=round(statistics.median(latencies) if latencies else 0.0, 2),
        latency_p95_ms=round(percentile(latencies, 95), 2),
        latency_p99_ms=round(percentile(latencies, 99), 2),
        latency_max_ms=round(max(latencies) if latencies else 0.0, 2),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Measure inference workload characteristics")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--requests", type=int, default=50)
    parser.add_argument("--output", type=Path, default=Path("data/measurements.json"))
    args = parser.parse_args()

    report = run_load_test(args.url, args.concurrency, args.requests)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(asdict(report), indent=2), encoding="utf-8")

    print(json.dumps(asdict(report), indent=2))
    if report.success_rate < 1.0:
        sys.exit(1)


if __name__ == "__main__":
    main()