import json
import sys
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from analyze_rightsizing import recommend_from_measurement


def test_recommend_guaranteed_qos_for_medium_profile() -> None:
    config = yaml.safe_load((PROJECT_ROOT / "config" / "workload-profiles.yaml").read_text())
    measurement = {"latency_p95_ms": 145.0}

    rec = recommend_from_measurement(
        measurement=measurement,
        observed_cpu_millicores=380,
        observed_memory_mi=410,
        config=config,
        profile_name="medium",
    )

    assert rec.qos_class == "Guaranteed"
    assert rec.cpu_request == rec.cpu_limit
    assert rec.memory_request == rec.memory_limit
    assert rec.cpu_request == "500m"
    assert rec.memory_request == "512Mi"


def test_recommend_burstable_profile_allows_higher_limits() -> None:
    config = yaml.safe_load((PROJECT_ROOT / "config" / "workload-profiles.yaml").read_text())
    measurement = {"latency_p95_ms": 90.0}

    rec = recommend_from_measurement(
        measurement=measurement,
        observed_cpu_millicores=100,
        observed_memory_mi=100,
        config=config,
        profile_name="small",
    )

    assert rec.qos_class == "Burstable"
    assert rec.cpu_limit != rec.cpu_request or rec.memory_limit != rec.memory_request