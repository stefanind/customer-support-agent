import re
from functools import lru_cache
from typing import Literal, NotRequired, TypedDict

from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel

from database import get_order
from rag import build_rag_graph, get_model, rag_graph


ORDER_ID_PATTERN = re.compile(r"\bord_\d+\b", re.IGNORECASE)
ORDER_NOT_FOUND = "I couldn't find that order."
ROUTER_PROMPT = """Classify the customer message as faq or order.
Use order for help with a specific customer order, even when its ID is missing.
Use faq for general policies, shipping, returns, warranties, or product help."""


class RouteDecision(BaseModel):
    route: Literal["faq", "order"]


class SupportResult(TypedDict):
    route: Literal["faq", "order"]
    outcome: Literal["answered", "clarify", "fallback", "handoff", "not_found"]
    answer: str
    sources: list[str]


class SupportState(TypedDict):
    message: str
    customer_id: str | None
    route: NotRequired[Literal["faq", "order"]]
    order_id: NotRequired[str]
    outcome: NotRequired[
        Literal["answered", "clarify", "fallback", "handoff", "not_found"]
    ]
    answer: NotRequired[str]
    sources: NotRequired[list[str]]


@lru_cache(maxsize=1)
def get_router():
    return get_model().with_structured_output(RouteDecision)


def build_support_graph(vector_store=None, model=None, router=None):
    """Build the FAQ-or-order support graph."""

    faq_graph = (
        rag_graph
        if vector_store is None and model is None
        else build_rag_graph(vector_store=vector_store, model=model)
    )

    def route(state: SupportState):
        decision = (router or get_router()).invoke(
            [("system", ROUTER_PROMPT), ("human", state["message"])]
        )
        match = ORDER_ID_PATTERN.search(state["message"])
        return {
            "route": decision.route,
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
        if not state["order_id"]:
            return {
                "answer": "What is your order ID?",
                "outcome": "clarify",
                "sources": [],
            }

        if not state["customer_id"]:
            return {
                "answer": (
                    "Please complete secure verification before I can look up "
                    "that order."
                ),
                "outcome": "handoff",
                "sources": ["KB-ORD-001"],
            }

        order = get_order(state["customer_id"], state["order_id"])

        if not order:
            return {
                "answer": ORDER_NOT_FOUND,
                "outcome": "not_found",
                "sources": [],
            }

        answer = f"Order {state['order_id']} is {order['status']}."
        if order["estimated_delivery_date"]:
            answer += (
                f" Its estimated delivery date is {order['estimated_delivery_date']}."
            )

        return {
            "answer": answer,
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
