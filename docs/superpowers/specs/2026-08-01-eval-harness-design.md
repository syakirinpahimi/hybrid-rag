# Design: Eval Harness

Date: 2026-08-01
Status: Approved (design)

## Goal

Give the hybrid Graph-RAG pipeline measurable quality claims instead of
"we eyeballed it": a golden-set evaluation that reports retrieval hit-rate,
graph coverage, and answer accuracy as percentages. The resulting table is
meant to be pasted into the README as portfolio evidence.

## Scope

One new root-level script `run_eval.py` (~60 lines) + one data file
`golden_qa.json`. No new dependencies. `app/` code is reused untouched
(`app/retrieve.py::retrieve` is the only entry point called).

## Metrics (per question)

All three are deterministic case-insensitive substring checks against the
question's expected keywords. No LLM-as-judge: the local 2B model grading
itself would be circular and non-reproducible.

| Metric | Definition |
|---|---|
| Retrieval hit-rate | expected fact appears in any top-k retrieved chunk text |
| Graph coverage | expected fact appears in any surfaced triple (the hybrid-specific metric; quantifies what the graph adds over pure vector search) |
| Answer accuracy | expected fact appears in the final generated answer |

## Golden set

`golden_qa.json`: 10 entries derived from `sample/industry_report.pdf`, each
`{"question": str, "expected": [str, ...]}` where a hit means ANY expected
keyword matches. Covers all major entities: founders (Elena Vasquez, Marcus
Webb, David Chen, Raj Mehta), headquarters (Austin), acquisition price
(1.2 billion), CEO (Amara Okafor), lead investor (Polaris Capital), cloud
provider (Bluefin Cloud), 2026 revenue target (800 million).

## Flow

1. For each golden question: call `retrieve(question)` once (single LLM call).
2. Run the three checks against `chunks`, `triples`, `answer`.
3. Print a per-question row (question, hit/graph/answer pass-fail).
4. Print a summary table with the three percentages.
5. Preconditions: Qdrant + Neo4j populated (run `app.ingest` first) and the
   configured LLM provider reachable. The run is wrapped in a single try/except
   that exits with a message listing these prerequisites on any connection
   error.

## Explicitly out of scope

- LLM-as-judge scoring (upgrade path if an OpenAI key is configured)
- MRR / precision-at-k (hit-rate suffices for a 10-question golden set)
- CI integration, multi-document golden sets, regression tracking

## Verification

Run `python run_eval.py` against the populated stores; expect a printed
per-question table plus summary percentages. Paste the summary table into the
README under a new "Evaluation" section.
