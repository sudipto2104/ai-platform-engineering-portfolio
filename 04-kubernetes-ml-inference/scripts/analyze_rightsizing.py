#!/usr/bin/env python3
"""Recommend Kubernetes resource requests/limits from workload measurements."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class ResourceRecommendation:
    profile: str
    cpu_request: str
    cpu_limit: str
    memory_request: str
    memory_limit: str
    qos_class: str
    rationale: str

    def formatted(self) -> str:
        return (
            f"Profile: {self.profile}\n"
            f"  CPU:    request={self.cpu_request}  limit={self.cpu_limit}\n"
            f"  Memory: request={self.memory_request}  limit={self.memory_limit}\n"
            f"  QoS:    {self.qos_class}\n"
            f"  Note:   {self.rationale}"
        )


def _parse_cpu_millicores(value: str) -> int:
    if value.endswith("m"):
        return int(value[:-1])
    return int(float(value) * 1000)


def _format_cpu(millicores: int) -> str:
    if millicores < 1000:
        return f"{millicores}m"
    if millicores % 1000 == 0:
        return str(millicores // 1000)
    return f"{millicores}m"


def _parse_memory_mi(value: str) -> int:
    units = {"Ki": 1 / 1024, "Mi": 1, "Gi": 1024}
    for suffix, factor in units.items():
        if value.endswith(suffix):
            return int(float(value[: -len(suffix)]) * factor)
    return int(value)


def _format_memory(mi: int) -> str:
    if mi >= 1024 and mi % 1024 == 0:
        return f"{mi // 1024}Gi"
    return f"{mi}Mi"


def _load_config(path: Path) -> dict[str, Any]:
    with path.open() as f:
        return yaml.safe_load(f)


def recommend_from_measurement(
    measurement: dict[str, Any],
    observed_cpu_millicores: int,
    observed_memory_mi: int,
    config: dict[str, Any],
    profile_name: str = "medium",
) -> ResourceRecommendation:
    rightsizing = config["rightsizing"]
    profile = config["profiles"][profile_name]

    cpu_request = int(observed_cpu_millicores * rightsizing["cpu_headroom_multiplier"])
    memory_request = int(observed_memory_mi * rightsizing["memory_headroom_multiplier"])

    profile_cpu_req = _parse_cpu_millicores(str(profile["requests"]["cpu"]))
    profile_mem_req = _parse_memory_mi(str(profile["requests"]["memory"]))
    cpu_request = max(cpu_request, profile_cpu_req)
    memory_request = max(memory_request, profile_mem_req)

    if profile["qos"] == "guaranteed":
        cpu_limit = cpu_request
        memory_limit = memory_request
        qos = "Guaranteed"
    else:
        cpu_limit = max(cpu_request * 2, _parse_cpu_millicores(str(profile["limits"]["cpu"])))
        memory_limit = max(memory_request * 2, _parse_memory_mi(str(profile["limits"]["memory"])))
        qos = "Burstable"

    p95 = measurement.get("latency_p95_ms", 0)
    rationale = (
        f"p95 latency {p95}ms with {rightsizing['cpu_headroom_multiplier']}x CPU and "
        f"{rightsizing['memory_headroom_multiplier']}x memory headroom applied"
    )

    return ResourceRecommendation(
        profile=profile_name,
        cpu_request=_format_cpu(cpu_request),
        cpu_limit=_format_cpu(cpu_limit),
        memory_request=_format_memory(memory_request),
        memory_limit=_format_memory(memory_limit),
        qos_class=qos,
        rationale=rationale,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze measurements and recommend resources")
    parser.add_argument("--measurement", type=Path, default=Path("data/measurements.json"))
    parser.add_argument("--config", type=Path, default=Path("config/workload-profiles.yaml"))
    parser.add_argument("--observed-cpu-m", type=int, default=380, help="Observed CPU in millicores")
    parser.add_argument("--observed-memory-mi", type=int, default=410, help="Observed memory in Mi")
    parser.add_argument("--profile", default="medium")
    args = parser.parse_args()

    measurement = json.loads(args.measurement.read_text(encoding="utf-8"))
    config = _load_config(args.config)
    recommendation = recommend_from_measurement(
        measurement=measurement,
        observed_cpu_millicores=args.observed_cpu_m,
        observed_memory_mi=args.observed_memory_mi,
        config=config,
        profile_name=args.profile,
    )
    print(recommendation.formatted())


if __name__ == "__main__":
    main()