# MVP evaluation examples

`cases.jsonl` contains four examples we will use while building the first graph:

1. Answer a shipping-policy question from the knowledge documents.
2. Answer a return-policy question from the knowledge documents.
3. Look up an order owned by the signed-in customer.
4. Do not reveal an order owned by a different customer.

`tests/test_support.py` runs all four examples through the unified support graph.
