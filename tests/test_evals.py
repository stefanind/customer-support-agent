import json
import unittest
from pathlib import Path

from knowledge import load_public_sections


CASES_PATH = Path(__file__).parents[1] / "evals" / "cases.jsonl"
REQUIRED_CATEGORIES = {
    "action_boundary",
    "conversation_handling",
    "faq_retrieval",
    "human_handoff",
    "input_robustness",
    "multi_turn",
    "order_lookup",
    "routing_clarification",
    "unsupported_grounding",
    "privacy_authorization",
    "prompt_injection",
    "safety",
    "multi_intent",
}
VALID_OUTCOMES = {
    "answered",
    "clarify",
    "fallback",
    "handoff",
    "not_found",
    "refused",
}


class EvalDatasetTests(unittest.TestCase):
    def test_eval_cases_are_valid(self):
        cases = [
            json.loads(line)
            for line in CASES_PATH.read_text(encoding="utf-8").splitlines()
        ]
        case_ids = [case["case_id"] for case in cases]
        public_doc_ids = {
            section.metadata["doc_id"] for section in load_public_sections()
        }

        self.assertGreaterEqual(len(cases), 40)
        self.assertLessEqual(len(cases), 50)
        self.assertEqual(len(case_ids), len(set(case_ids)))
        self.assertTrue(REQUIRED_CATEGORIES.issubset({case["category"] for case in cases}))

        for case in cases:
            with self.subTest(case=case["case_id"]):
                self.assertTrue(case["messages"])
                self.assertTrue(
                    all(isinstance(message, str) for message in case["messages"])
                )
                self.assertIn("customer_id", case)
                self.assertIn(case["priority"], {"critical", "core", "extended"})
                self.assertIn(case["expected"]["outcome"], VALID_OUTCOMES)
                self.assertTrue(
                    {"documents", "must_mention", "must_not_claim", "order_statuses"}
                    & case["expected"].keys()
                )
                self.assertTrue(
                    set(case["expected"].get("documents", [])).issubset(public_doc_ids)
                )


if __name__ == "__main__":
    unittest.main()
