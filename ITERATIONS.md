# Iteration Log

Each entry describes the code after evaluation and corresponds to a Git version.

## v001 — Initial unified agent

### What led to this version

The project needed one entry point for FAQ and customer-owned order questions.

### What changed

- Added the unified FAQ-or-order LangGraph.
- Routed messages containing an order ID to SQLite.
- Routed all other messages to RAG.

### Outcome

`routing_clarification`: 1 of 2 cases passed.

`missing_order_id` failed because an order request without an ID was sent to RAG.

## v002 — LLM intent routing and clarification

### What led to this version

The v001 router could not recognize an order lookup unless the message contained
an ID.

### What changed

- Added structured LLM routing between `faq` and `order`.
- Kept regex responsible only for extracting an order ID.
- Added the `clarify` outcome when the order ID is missing.
- Added fake-router unit tests so tests do not call Claude.

### Outcome

- All 11 unit tests passed.
- `order_lookup`: 5 of 7 cases passed.
- All seven order requests were routed correctly.
- `order_without_trusted_customer` still needs secure verification.
- `order_eta_request` still needs the estimated delivery date.
