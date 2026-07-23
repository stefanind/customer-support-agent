# Customer Support Bot

This is a small read-only customer-support agent built with LangGraph.

The project is being built iteratively around the realistic support scenarios in
[`evals/cases.jsonl`](evals/cases.jsonl). That suite describes the customer
questions and safety, privacy, routing, and order-handling problems the agent
should eventually handle. Some cases intentionally fail today. Each iteration
targets one category, adds the smallest useful capability, and then checks the
whole suite for regressions.

It currently handles two kinds of requests:

- FAQ and product questions using RAG over Markdown documents.
- Order-status questions using an authenticated customer ID and SQLite.

## Flow

```text
customer message
      |
    router
   /      \
 FAQ      order
  |         |
 RAG      SQLite
   \       /
     answer
```

The router treats a message containing an ID such as `ord_1002` as an order
question. All other messages use the FAQ path.

## Setup

Install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

Create a `.env` file containing your Anthropic API key:

```text
ANTHROPIC_API_KEY=your-key-here
```

MiniLM runs locally. Its model files are downloaded on first use if they are not
already available on your computer.

## Run the bot

`run_support()` is the application entry point:

```python
from support import run_support

result = run_support(
    message="Is standard shipping free when my cart is exactly $75?",
    customer_id=None,
)

print(result["answer"])
print(result["outcome"])
print(result["sources"])
```

An authenticated order lookup looks like this:

```python
result = run_support(
    message="Where is order ord_1002?",
    customer_id="cus_001",
)
```

In a real application, `customer_id` must come from the authenticated session,
not from the customer's message.

Every request returns the same four fields: `route`, `outcome`, `answer`, and
`sources`. The controller uses this shared result regardless of which path ran.

## Run the tests

```powershell
python -m unittest discover -s tests -v
```

The tests cover document retrieval, the shared support-result contract, SQLite
ownership checks, evaluation-dataset structure, and eval-runner message order.
Claude is replaced with a fake model so tests do not require network access or
spend API credits.

## Run evaluations

Run one category while developing a capability:

```powershell
python -m evals.run --category routing_clarification
```

Run the complete suite before finishing an iteration:

```powershell
python -m evals.run
```

The runner prints the expected behavior beside the actual result for manual
review. Evaluation runs can call the real model and use API credits. See
[`evals/README.md`](evals/README.md) for the evaluation workflow.

## Main files

- `support.py`: unified router and public `run_support()` entry point.
- `rag.py`: FAQ retrieval-and-answer subgraph.
- `knowledge.py`: Markdown chunking, MiniLM, and semantic search.
- `database.py`: customer-owned order lookup.
- `evals/cases.jsonl`: the single 50-case product evaluation suite.
- `evals/run.py`: category-filterable evaluation runner.

## Current limitations

- An order question must include an ID such as `ord_1002`.
- There is no conversation memory, API, or user interface.
- The agent cannot cancel orders, create returns, or perform other writes.
