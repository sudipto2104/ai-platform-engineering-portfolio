#!/usr/bin/env python3
import argparse

from platform_agents.react_agent import ask_agent


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the basic ReAct agent")
    parser.add_argument("question", help="Question to ask")
    args = parser.parse_args()
    print(ask_agent(args.question))


if __name__ == "__main__":
    main()