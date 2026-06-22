"""Prometheus metrics exporter for the AI observability layer."""

from __future__ import annotations

import argparse
import os
import time

from prometheus_client import start_http_server


def main() -> None:
    parser = argparse.ArgumentParser(description="Start Prometheus metrics server")
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("METRICS_PORT", "8000")),
        help="Port to expose /metrics",
    )
    args = parser.parse_args()

    start_http_server(args.port)
    print(f"Prometheus metrics server started at http://0.0.0.0:{args.port}/metrics")
    while True:
        time.sleep(60)


if __name__ == "__main__":
    main()