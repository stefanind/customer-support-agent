from functools import lru_cache
from typing import NotRequired, TypedDict

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.documents import Document
from langgraph.graph import END, START, StateGraph

from knowledge import search_knowledge
from tracking import track_step


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
    timings_ms: NotRequired[dict[str, float]]
    model_called: NotRequired[bool]


# cache the model to remove repetitive function calls
@lru_cache(maxsize=1)
def get_answer_model():
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

        timings = dict(state.get("timings_ms", {}))

        with track_step(timings, "retrieval"):

            chunks = search_knowledge(
                state["question"], 
                vector_store=vector_store
                )

        # if search_knowledge dn get a chunk
        # chunks will equal []
        return {"chunks": chunks, "timings_ms": timings}

    def answer(state: RAGState) -> dict:

        timings = dict(state["timings_ms"])

        # state["chunks"] can equal []
        if not state["chunks"]:
            timings["generation"] = 0.0
            return {
                "answer": FALLBACK_ANSWER,
                "timings_ms": timings,
                "model_called": False,
            }


        with track_step(timings, "generation"):

            answer_model = model or get_answer_model()

            response = answer_model.invoke(
                [
                    ("system", SYSTEM_PROMPT),
                    (
                        "human",
                        f"Question: {state['question']}\n\n"
                        # format_context adds doc_id and section headers
                        f"Context:\n{format_context(state['chunks'])}", 
                    ),
                ]
            )

            answer_text = response.text.strip() or FALLBACK_ANSWER


        return {
            "answer": answer_text,
            "timings_ms": timings,
            "model_called": True,
        }

    graph = StateGraph(RAGState)
    graph.add_node("retrieve", retrieve)
    graph.add_node("answer", answer)
    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "answer")
    graph.add_edge("answer", END)
    return graph.compile()


rag_graph = build_rag_graph()
