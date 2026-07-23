import argparse
import json
from pathlib import Path

from support import run_support


CASES_PATH = Path(__file__).with_name("cases.jsonl")


def load_cases(category=None):
    cases = [
        json.loads(line)
        for line in CASES_PATH.read_text(encoding="utf-8").splitlines()
    ]
    if category:
        cases = [case for case in cases if case["category"] == category]
    return cases


def run_case(case, agent=run_support):
    return [
        {
            "message": message,
            "result": agent(message, case["customer_id"]),
        }
        for message in case["messages"]
    ]


def main():
    parser = argparse.ArgumentParser(description="Run the support evaluation suite.")
    parser.add_argument("--category", help="Run only one evaluation category.")
    args = parser.parse_args()

    cases = load_cases(args.category)
    if not cases:
        raise SystemExit("No evaluation cases matched that category.")

    for case in cases:
        print(f"\n=== {case['case_id']} ({case['category']}) ===")
        print("Expected:", json.dumps(case["expected"], indent=2))

        for turn in run_case(case):
            print(f"\nUser: {turn['message']}")
            print("Actual:", json.dumps(turn["result"], indent=2))


if __name__ == "__main__":
    main()
