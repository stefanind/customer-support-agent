import unittest

from langchain_core.documents import Document
from langchain_core.messages import AIMessage

from support import RouteDecision, build_support_graph, run_support


class FakeVectorStore:
    def similarity_search_with_score(self, _question, k):
        chunk = Document(
            page_content="Standard shipping is free at $75.",
            metadata={"doc_id": "KB-SHIP-001", "section": "Shipping Charges"},
        )
        return [(chunk, 0.9)][:k]


class FakeModel:
    def __init__(self):
        self.calls = []

    def invoke(self, messages):
        self.calls.append(messages)
        return AIMessage(content="Standard shipping is free at $75.")


class FakeRouter:
    def __init__(self, route):
        self.route = route

    def invoke(self, _messages):
        return RouteDecision(route=self.route)


class SupportGraphTests(unittest.TestCase):
    def test_faq_returns_shared_result(self):
        model = FakeModel()
        graph = build_support_graph(
            vector_store=FakeVectorStore(),
            model=model,
            router=FakeRouter("faq"),
        )

        result = run_support("Is shipping free at $75?", None, graph=graph)

        self.assertEqual(
            result,
            {
                "route": "faq",
                "outcome": "answered",
                "answer": "Standard shipping is free at $75.",
                "sources": ["KB-SHIP-001"],
            },
        )
        self.assertEqual(len(model.calls), 1)

    def test_order_lookup_requires_ownership(self):
        graph = build_support_graph(router=FakeRouter("order"))
        own_order = run_support("Check ord_1002", "cus_001", graph=graph)
        other_order = run_support("Check ord_2001", "cus_001", graph=graph)

        self.assertEqual(own_order["outcome"], "answered")
        self.assertIn("shipped", own_order["answer"])
        self.assertEqual(other_order["outcome"], "not_found")
        self.assertEqual(other_order["answer"], "I couldn't find that order.")

    def test_missing_order_id_asks_for_clarification(self):
        graph = build_support_graph(router=FakeRouter("order"))

        result = run_support("Where is my order?", "cus_001", graph=graph)

        self.assertEqual(
            result,
            {
                "route": "order",
                "outcome": "clarify",
                "answer": "What is your order ID?",
                "sources": [],
            },
        )

    def test_order_policy_can_use_faq_path(self):
        graph = build_support_graph(
            vector_store=FakeVectorStore(),
            model=FakeModel(),
            router=FakeRouter("faq"),
        )

        result = run_support(
            "What is your order cancellation policy?", None, graph=graph
        )

        self.assertEqual(result["route"], "faq")

    def test_order_lookup_without_customer_requires_verification(self):
        graph = build_support_graph(router=FakeRouter("order"))

        result = run_support("Check ord_1002", None, graph=graph)

        self.assertEqual(result["outcome"], "handoff")
        self.assertIn("secure verification", result["answer"])
        self.assertNotIn("shipped", result["answer"])
        self.assertEqual(result["sources"], ["KB-ORD-001"])

    def test_order_lookup_includes_delivery_estimate(self):
        graph = build_support_graph(router=FakeRouter("order"))

        result = run_support(
            "When should ord_1002 arrive?", "cus_001", graph=graph
        )

        self.assertIn("2026-07-23", result["answer"])
