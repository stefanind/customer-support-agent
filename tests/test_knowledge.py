import unittest

from langchain_core.documents import Document
from langchain_core.messages import AIMessage

from knowledge import load_public_sections, search_knowledge
from rag import FALLBACK_ANSWER, build_rag_graph


class FakeVectorStore:
    def __init__(self, matches):
        self.matches = matches
        self.k = None

    def similarity_search_with_score(self, _question, k):
        self.k = k
        return self.matches[:k]


class FakeModel:
    def __init__(self, answer="Grounded answer"):
        self.answer = answer
        self.calls = []

    def invoke(self, messages):
        self.calls.append(messages)
        return AIMessage(content=self.answer)


def make_chunk(doc_id, section, content):
    return Document(
        page_content=content,
        metadata={"doc_id": doc_id, "section": section},
    )


class KnowledgeTests(unittest.TestCase):
    def test_loads_only_public_markdown_sections(self):
        sections = load_public_sections()
        doc_ids = {document.metadata["doc_id"] for document in sections}

        self.assertTrue(sections)
        self.assertNotIn("KB-SEC-001", doc_ids)
        self.assertTrue(
            all("title" in doc.metadata and "section" in doc.metadata for doc in sections)
        )

    def test_minilm_finds_the_shipping_section(self):
        results = search_knowledge(
            "Is standard shipping free when my cart is exactly $75?"
        )

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].metadata["doc_id"], "KB-SHIP-001")
        self.assertEqual(
            results[0].metadata["section"], "Shipping Services and Charges"
        )

    def test_search_returns_two_chunks(self):
        chunks = [
            make_chunk("KB-1", "One", "First result"),
            make_chunk("KB-2", "Two", "Second result"),
            make_chunk("KB-3", "Three", "Third result"),
        ]
        store = FakeVectorStore([(chunk, 0.9) for chunk in chunks])

        results = search_knowledge("shipping question", vector_store=store)

        self.assertEqual(results, chunks[:2])
        self.assertEqual(store.k, 2)

    def test_weak_match_returns_fallback_without_model_call(self):
        chunk = make_chunk("KB-1", "One", "Unrelated text")
        store = FakeVectorStore([(chunk, 0.1)])
        model = FakeModel()
        graph = build_rag_graph(vector_store=store, model=model)

        result = graph.invoke({"question": "What is the capital of France?"})

        self.assertEqual(result["answer"], FALLBACK_ANSWER)
        self.assertEqual(result["outcome"], "fallback")
        self.assertEqual(len(model.calls), 0)

    def test_answer_prompt_uses_two_chunks_and_one_model_call(self):
        chunks = [
            make_chunk("KB-SHIP", "Cost", "Standard shipping is free at $75."),
            make_chunk("KB-SHIP", "Timing", "Standard shipping takes 3-5 days."),
        ]
        store = FakeVectorStore([(chunks[0], 0.9), (chunks[1], 0.8)])
        model = FakeModel("Standard shipping is free at $75. [KB-SHIP - Cost]")
        graph = build_rag_graph(vector_store=store, model=model)

        result = graph.invoke({"question": "Is shipping free at $75?"})

        self.assertIn("free at $75", result["answer"])
        self.assertEqual(result["outcome"], "answered")
        self.assertEqual(len(result["chunks"]), 2)
        self.assertEqual(len(model.calls), 1)
        prompt = str(model.calls[0])
        self.assertIn("Is shipping free at $75?", prompt)
        self.assertIn("Standard shipping is free at $75.", prompt)
        self.assertIn("Standard shipping takes 3-5 days.", prompt)


if __name__ == "__main__":
    unittest.main()
