import unittest

from evals.run import run_case


class EvalRunnerTests(unittest.TestCase):
    def test_run_case_processes_messages_in_order(self):
        calls = []

        def fake_agent(message, customer_id):
            calls.append((message, customer_id))
            return {"answer": message}

        case = {
            "messages": ["Where is my order?", "ORD_1002"],
            "customer_id": "cus_001",
        }

        turns = run_case(case, agent=fake_agent)

        self.assertEqual(
            calls,
            [
                ("Where is my order?", "cus_001"),
                ("ORD_1002", "cus_001"),
            ],
        )
        self.assertEqual(
            [turn["message"] for turn in turns],
            ["Where is my order?", "ORD_1002"],
        )


if __name__ == "__main__":
    unittest.main()
