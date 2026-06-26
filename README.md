# App Spoof Classifier

LangGraph agent that classifies app names as well_known, hobby_no_docs,
spoofed, or uncertain (escalated to human review).

## Layout
- `src/spoof_classifier/` -- the package: graph, state, nodes, tools, cache
- `evals/` -- gold-set test cases and eval run results
- `tests/` -- unit + integration tests
- `scripts/` -- batch-run entrypoints
- `data/` -- input dataset / output annotations (not committed)
