import re
from typing import Literal, NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph

from database import get_order
from rag import build_rag_graph, rag_graph


ORDER_ID_PATTERN = re.compile(r"\bord_\d+\b", re.IGNORECASE)
ORDER_NOT_FOUND = "I couldn't find that order."





class SupportResult(TypedDict):
    route: Literal["faq", "order"]
    outcome: Literal["answered", "fallback", "not_found"]
    answer: str
    sources: list[str]


class SupportState(TypedDict):
    message: str
    customer_id: str | None
    route: NotRequired[Literal["faq", "order"]]
    order_id: NotRequired[str]
    outcome: NotRequired[Literal["answered", "fallback", "not_found"]]
    answer: NotRequired[str]
    sources: NotRequired[list[str]]


def build_support_graph(vector_store=None, model=None):
    """Build the FAQ-or-order support graph."""

    faq_graph = (
        rag_graph
        if vector_store is None and model is None
        else build_rag_graph(vector_store=vector_store, model=model)
    )

    def route(state: SupportState):
        match = ORDER_ID_PATTERN.search(state["message"])
        return {
            "route": "order" if match else "faq",
            "order_id": match.group(0).lower() if match else "",
        }

    def answer_faq(state: SupportState):
        result = faq_graph.invoke({"question": state["message"]})
        return {
            "answer": result["answer"],
            "outcome": result["outcome"],
            "sources": sorted(
                {chunk.metadata["doc_id"] for chunk in result["chunks"]}
            ),
        }

    def answer_order(state: SupportState):
        order = (
            get_order(state["customer_id"], state["order_id"])
            if state["customer_id"]
            else None
        )

        if not order:
            return {
                "answer": ORDER_NOT_FOUND,
                "outcome": "not_found",
                "sources": [],
            }

        return {
            "answer": f"Order {state['order_id']} is {order['status']}.",
            "outcome": "answered",
            "sources": [],
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


def run_support(message: str, customer_id: str | None, graph=None) -> SupportResult:
    """Run one support request and return the shared result."""

    result = (graph or support_graph).invoke(
        {"message": message, "customer_id": customer_id}
    )
    return {
        "route": result["route"],
        "outcome": result["outcome"],
        "answer": result["answer"],
        "sources": result["sources"],
    }
