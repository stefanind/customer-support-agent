from functools import lru_cache
from typing import Literal, NotRequired, TypedDict

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.documents import Document
from langgraph.graph import END, START, StateGraph

from knowledge import search_knowledge


FALLBACK_ANSWER = "I couldn't find that in the support knowledge base OR an issue went wrong."

SYSTEM_PROMPT = f"""You are an Acme Audio customer-support assistant.
Answer using only the supplied knowledge-base context.
If the context does not answer the question, reply exactly:
{FALLBACK_ANSWER}
Otherwise, finish with the document ID and section you used."""


class RAGState(TypedDict):
    question: str
    chunks: NotRequired[list[Document]]
    answer: NotRequired[str]
    outcome: NotRequired[Literal["answered", "fallback"]]


# Load the model once, then reuse it.
@lru_cache(maxsize=1)
def get_model():
    load_dotenv()
    return ChatAnthropic(model="claude-haiku-4-5", temperature=0)


def format_context(chunks: list[Document]) -> str:
    return "\n\n".join(
        f"[{chunk.metadata['doc_id']} - {chunk.metadata['section']}]\n"
        f"{chunk.page_content}"
        for chunk in chunks
    )


def build_rag_graph(vector_store=None, model=None):
    """Build the deterministic retrieve-then-answer graph."""

    def retrieve(state: RAGState) -> dict:
        chunks = search_knowledge(state["question"], vector_store=vector_store)
        return {"chunks": chunks}

    def answer(state: RAGState) -> dict:
        if not state["chunks"]:
            return {
                "answer": FALLBACK_ANSWER,
                "outcome": "fallback",
            }

        answer_model = model or get_model()
        response = answer_model.invoke(
            [
                ("system", SYSTEM_PROMPT),
                (
                    "human",
                    f"Question: {state['question']}\n\n"
                    f"Context:\n{format_context(state['chunks'])}",
                ),
            ]
        )
        answer_text = response.text.strip() or FALLBACK_ANSWER

        return {
            "answer": answer_text,
            "outcome": "fallback" if answer_text == FALLBACK_ANSWER else "answered",
        }

    graph = StateGraph(RAGState)
    graph.add_node("retrieve", retrieve)
    graph.add_node("answer", answer)
    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "answer")
    graph.add_edge("answer", END)
    return graph.compile()


rag_graph = build_rag_graph()
