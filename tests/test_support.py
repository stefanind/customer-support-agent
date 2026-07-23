import unittest

from langchain_core.documents import Document
from langchain_core.messages import AIMessage

from support import build_support_graph, run_support


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


class SupportGraphTests(unittest.TestCase):
    def test_faq_returns_shared_result(self):
        model = FakeModel()
        graph = build_support_graph(vector_store=FakeVectorStore(), model=model)

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
        own_order = run_support("Check ord_1002", "cus_001")
        other_order = run_support("Check ord_2001", "cus_001")

        self.assertEqual(own_order["outcome"], "answered")
        self.assertIn("shipped", own_order["answer"])
        self.assertEqual(other_order["outcome"], "not_found")
        self.assertEqual(other_order["answer"], "I couldn't find that order.")
