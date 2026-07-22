# Customer Support Bot

This is a small read-only customer-support agent built with LangGraph.

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
print(result["timings_ms"])
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

Each run is returned as a dictionary and appended to `data/runs.jsonl`. That file
is ignored by Git because it contains raw prompts and answers.

## Run the tests

```powershell
python -m unittest discover -s tests -v
```

The automated tests use real Markdown retrieval and the real SQLite database.
Claude is replaced with a fake model so tests do not require network access or
spend API credits.

## Main files

- `support.py`: unified router and public `run_support()` entry point.
- `rag.py`: FAQ retrieval-and-answer subgraph.
- `knowledge.py`: Markdown chunking, MiniLM, and semantic search.
- `database.py`: customer-owned order lookup.
- `tracking.py`: timings and JSONL run records.
- `evals/cases.jsonl`: the four MVP evaluation examples.

## Current limitations

- An order question must include an ID such as `ord_1002`.
- There is no conversation memory, API, or user interface.
- The agent cannot cancel orders, create returns, or perform other writes.
