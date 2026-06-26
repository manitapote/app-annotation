# App Spoof Classifier

LangGraph agent that classifies whether the app is well documented, spoofed or unknown apps.

- Spoofed apps: Apps are mimick the names of well known apps.
- Well documented apps: Apps whose purpose is well documented
- Unknown: Apps that lack documentation.

## Layout
- `src/app_annotation/` -- the package: graph, state, nodes, tools, cache
- `evals/` -- gold-set test cases and eval run results
- `tests/` -- unit + integration tests
- `scripts/` -- batch-run entrypoints
- `data/` -- input dataset / output annotations (not committed)
