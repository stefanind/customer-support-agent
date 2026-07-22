import json
import unittest
from pathlib import Path

from langchain_core.messages import AIMessage

from support import build_support_graph, run_support


CASES_PATH = Path(__file__).parents[1] / "evals" / "cases.jsonl"


class EvaluationModel:
    def __init__(self):
        self.calls = []

    def invoke(self, messages):
        prompt = str(messages)
        self.calls.append(prompt)

        if "exactly $75" in prompt:
            return AIMessage(content="At exactly $75, you receive free standard shipping.")
        if "30 days" in prompt:
            return AIMessage(content="A return requested on day 30 is eligible.")
        raise AssertionError("Unexpected FAQ question")


class SupportGraphTests(unittest.TestCase):
    def test_all_evaluation_cases(self):
        cases = [json.loads(line) for line in CASES_PATH.read_text().splitlines()]
        model = EvaluationModel()
        graph = build_support_graph(model=model)
        saved_runs = []

        for case in cases:
            with self.subTest(case=case["case_id"]):
                run = run_support(
                    case["message"],
                    case["customer_id"],
                    graph=graph,
                    saver=saved_runs.append,
                )

                self.assertEqual(run["metadata"]["route"], case["expected_route"])
                self.assertIn("routing", run["timings_ms"])
                self.assertIn("total", run["timings_ms"])

                if case["expected_route"] == "faq":
                    self.assertEqual(
                        run["metadata"]["retrieved_sections"][0]["doc_id"],
                        case["expected_document"],
                    )
                    self.assertIn("retrieval", run["timings_ms"])
                    self.assertIn("generation", run["timings_ms"])
                    for expected_text in case["expected_answer_contains"]:
                        self.assertIn(expected_text, run["answer"])
                elif "expected_status" in case:
                    self.assertIn("order_lookup", run["timings_ms"])
                    self.assertIn(case["expected_status"], run["answer"])
                else:
                    self.assertIn("order_lookup", run["timings_ms"])
                    self.assertEqual(run["status"], case["expected_result"])

        self.assertEqual(len(model.calls), 2)
        self.assertEqual(len(saved_runs), 4)
