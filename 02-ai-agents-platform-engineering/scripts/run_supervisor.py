#!/usr/bin/env python3
import argparse
import json

from platform_agents.supervisor import ask_supervisor


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the multi-agent supervisor")
    parser.add_argument("question", help="Question to route to specialists")
    args = parser.parse_args()
    result = ask_supervisor(args.question)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()