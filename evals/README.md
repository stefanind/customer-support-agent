# Evaluation suite

`cases.jsonl` is the single product evaluation suite. Its 50 cases describe the
customer-support behavior we want, including behavior the current agent cannot
handle yet. Each iteration is evaluated against the whole suite; cases are not
split into passing and future files.

Each case contains:

- `case_id`, `category`, and `priority` for grouping results.
- `messages`, which always contains one or more customer turns.
- `customer_id`, representing identity supplied by a trusted session.
- `expected`, containing the desired outcome and its evaluation rubric.

The outcome vocabulary is deliberately small: `answered`, `clarify`, `fallback`,
`not_found`, `refused`, and `handoff`. Optional rubric fields describe expected
documents, order statuses, facts to mention, and claims that must not be made.
Those rubrics are meaning-based rather than exact string matches.

## Running the suite

Target one category while developing a capability:

```powershell
python -m evals.run --category routing_clarification
```

Run every case before completing an iteration:

```powershell
python -m evals.run
```

The runner prints the expected rubric beside the actual result for manual review.
It does not score or save results.

## Iteration loop

1. Run the whole suite to establish the current baseline.
2. Choose one important category and implement the smallest useful change.
3. Run that category while developing.
4. Run the whole suite before completing the new version.
5. Add newly discovered real-world scenarios to this same suite.

Unit tests remain separate because they verify deterministic code behavior and
must stay green. The evaluation suite measures product quality and is allowed to
expose failures. `tests/test_evals.py` only validates the dataset structure.

DeepEval is not installed yet. The consistent `messages` format can later be
converted into conversation turns, while the expected rubrics can feed its
evaluators. Actual agent outputs should be generated during each evaluation run,
not stored as part of the source dataset.
