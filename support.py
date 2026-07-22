import re
from datetime import datetime, timezone
from typing import Literal, NotRequired, TypedDict
from uuid import uuid4

from langchain_core.documents import Document
from langgraph.graph import END, START, StateGraph

from database import get_order
from rag import FALLBACK_ANSWER, build_rag_graph, rag_graph
from tracking import save_run, track_step


ORDER_ID_PATTERN = re.compile(r"\bord_\d+\b", re.IGNORECASE)
ORDER_NOT_FOUND = "I couldn't find that order."


class SupportState(TypedDict):
    message: str
    customer_id: str | None
    route: NotRequired[Literal["faq", "order"]]
    order_id: NotRequired[str]
    chunks: NotRequired[list[Document]]
    answer: NotRequired[str]
    timings_ms: NotRequired[dict[str, float]]
    model_called: NotRequired[bool]


def build_support_graph(vector_store=None, model=None):
    """Build the FAQ-or-order support graph."""

    faq_graph = (
        rag_graph
        if vector_store is None and model is None
        else build_rag_graph(vector_store=vector_store, model=model)
    )

    def route(state: SupportState):
        timings = {}
        with track_step(timings, "routing"):
            match = ORDER_ID_PATTERN.search(state["message"])
        return {
            "route": "order" if match else "faq",
            "order_id": match.group(0).lower() if match else "",
            "timings_ms": timings,
        }

    def answer_faq(state: SupportState):
        result = faq_graph.invoke({"question": state["message"]})
        return {
            "answer": result["answer"],
            "chunks": result["chunks"],
            "model_called": result["model_called"],
            "timings_ms": {**state["timings_ms"], **result["timings_ms"]},
        }

    def answer_order(state: SupportState):
        timings = dict(state["timings_ms"])
        with track_step(timings, "order_lookup"):
            order = (
                get_order(state["customer_id"], state["order_id"])
                if state["customer_id"]
                else None
            )

        answer = (
            f"Order {state['order_id']} is {order['status']}."
            if order
            else ORDER_NOT_FOUND
        )
        return {
            "answer": answer,
            "chunks": [],
            "model_called": False,
            "timings_ms": timings,
        }

    graph = StateGraph(SupportState)
    graph.add_node("route", route)
    graph.add_node("faq", answer_faq)
    graph.add_node("order", answer_order)
    graph.add_edge(START, "route")
    graph.add_conditional_edges(
        "route", lambda state: state["route"], {"faq": "faq", "order": "order"}
    )
    graph.add_edge("faq", END)
    graph.add_edge("order", END)
    return graph.compile()


support_graph = build_support_graph()


def run_support(message: str, customer_id: str | None, graph=None, saver=save_run):
    """Run one support request, save its trace, and return the trace."""

    total_timing = {}
    with track_step(total_timing, "total"):
        result = (graph or support_graph).invoke(
            {"message": message, "customer_id": customer_id}
        )

    if result["answer"] == ORDER_NOT_FOUND:
        status = "not_found"
    elif result["answer"] == FALLBACK_ANSWER:
        status = "fallback"
    else:
        status = "answered"

    run = {
        "run_id": str(uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "prompt": message,
        "answer": result["answer"],
        "status": status,
        "timings_ms": {**result["timings_ms"], **total_timing},
        "metadata": {
            "route": result["route"],
            "model_called": result["model_called"],
            "retrieved_sections": [
                {
                    "doc_id": chunk.metadata["doc_id"],
                    "section": chunk.metadata["section"],
                }
                for chunk in result["chunks"]
            ],
        },
    }
    saver(run)
    return run
