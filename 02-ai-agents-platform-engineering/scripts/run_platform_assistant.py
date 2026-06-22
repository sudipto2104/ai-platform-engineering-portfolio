#!/usr/bin/env python3
import argparse
import os

from platform_agents.platform_assistant import ask_platform_assistant
from platform_agents.tools.approval import ApprovalGate


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the platform assistant agent")
    parser.add_argument("question", help="Platform engineering question")
    args = parser.parse_args()

    os.environ.setdefault("K8S_DRY_RUN", "true")
    gate = ApprovalGate(auto_approve=True)
    print(ask_platform_assistant(args.question, approval_gate=gate))


if __name__ == "__main__":
    main()