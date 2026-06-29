# App Name Annotator

A LangGraph agent that classifies app/client names into **Native**, **Popular**,
or **Others**, combining a fast, knowledge-based spoof/identity check with a
confidence-gated, real web search fallback for cases the model can't confidently
resolve on its own.

Built originally to annotate third-party Twitter client names (the
`tweet_client_name` indicator from a separate coordinated-behavior detection
pipeline), but the agent itself is general-purpose: give it any app/service
name, it tells you what it is.

## What it actually does

```
app_name
   │
   ▼
spoof_check  ──confidently spoofed?──▶ END   (category = "Others")
   │ no / uncertain
   ▼
web_search  ──▶ END   (category = "Popular" or "Others", based on real evidence)
```

1. **`spoof_check`** asks the model (no live search, just its own knowledge) whether
   the name looks like a typosquat/impersonation of a known brand, and separately
   classifies it as `Native` (Twitter/X's own product), `Popular`, or `Others`.
2. If spoof_check is **confidently** sure the name *is* a spoof, that's the final
   answer, there's nothing more to check.
3. Otherwise, **`web_search`** runs a real query (OpenAI's built-in `web_search`
   tool via the Responses API) and overrides the category/reasoning/sources with
   evidence-backed findings.

See `src/app_annotation/schemas.py` for the exact rules on which fields get
overwritten vs. preserved across the two steps.

## Project layout

```
app-annotation/
├── src/app_annotation/
│   ├── graph.py              # StateGraph wiring + routing logic
│   ├── state.py              # AnnotationState (what flows through the graph)
│   ├── schemas.py            # Result (the final, consistent output shape)
│   ├── models.py              # Centralized model/client setup (get_model, call_web_search, etc.)
│   ├── config.py              # Portable path/env config -- no hardcoded machine paths
│   ├── prompts_loader.py      # Loads prompt templates from prompts/*.md
│   ├── api.py                  # FastAPI backend (HTTP endpoints over the graph)
│   ├── nodes/                  # spoof_check_node.py, search.py
│   ├── tools/                  # spoof_check.py, web_search.py
│   └── prompts/                # spoof_check.md, web_search.md
│
├── evals/
│   ├── run_eval.py                    # Full pipeline vs. gold standard (split by decision path)
│   ├── run_eval_web_search_only.py    # web_search alone vs. gold (bypasses spoof_check/routing)
│   ├── run_eval_cohens_kappa.py       # Kappa + gold-correction-via-real-urls logic
│   └── results/                        # Timestamped eval run outputs
│
├── scripts/
│   ├── run_batch.py            # CLI batch entrypoint: CSV in -> CSV out
│   └── app_ui.py                # Streamlit UI (alternative to the FastAPI+HTML frontend)
│
├── index.html                  # Static frontend for api.py ("investigation console" UI)
├── data/
│   ├── input/                   # app_names.csv goes here
│   ├── output/                  # run_batch.py writes here
│   └── annotated/               # gold_standard.csv (your hand-labeled eval set) goes here
└── tests/
```

## Setup

```bash
git clone <this-repo>
cd app-annotation
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env   # then fill in OPENAI_API_KEY
```

**Required in `.env`:**
```
OPENAI_API_KEY=sk-...          # regular API key -- NOT an Admin key
WEB_SEARCH_MODEL=gpt-5.5        # must support the built-in web_search tool
```

Verify the install:
```bash
python -c "import app_annotation; print('ok')"
python -m app_annotation.tools.spoof_check   # runs a few built-in sanity-check names
```

## Usage

**Single name, from Python:**
```python
from app_annotation.graph import app

final_state = app.invoke({"app_name": "Instagram", "search_results": [], "result": None})
print(final_state["result"])
```

**Batch CSV (CLI):**
```bash
# data/input/app_names.csv needs a column called 'app_name'
python scripts/run_batch.py
# -> data/output/annotated.csv
```

**Web UI (FastAPI + static HTML):**
```bash
pip install fastapi "uvicorn[standard]"
uvicorn app_annotation.api:api --reload --port 8000
# in another terminal:
python -m http.server 8080
# visit http://localhost:8080/index.html
```

**Web UI (Streamlit alternative, single process):**
```bash
pip install streamlit
streamlit run scripts/app_ui.py
```

## Evaluating against a gold standard

Put a hand-labeled file at `data/annotated/gold_standard.csv` with columns
`app_names` (or `app_name`), `Category`, `Reasoning`. **`Native` rows are
excluded from scoring**, neither `spoof_check` nor `web_search` can currently
distinguish "Twitter's own product" from anything else, so those rows are
untestable by design, not a bug.

```bash
# Full pipeline accuracy, broken down by which step decided the answer
python evals/run_eval.py

# web_search in isolation (bypasses spoof_check/routing entirely)
python evals/run_eval_web_search_only.py

# Cohen's Kappa + per-class precision/recall, with an optional correction
# that trusts web_search's evidence-backed prediction over a stale/wrong
# gold label when web_search actually found real source URLs
python evals/run_eval_cohens_kappa.py
```

Results are saved with a timestamp under `evals/results/` so you can track
whether a prompt/routing change actually helped, rather than guessing.

## A few design decisions worth knowing if you're extending this

- **`Result`'s fields have different overwrite rules** — `spoof_check`,
  `spoof_confidence`, `spoof_evidence`, and `category` are spoof_check's
  permanent record; `reasoning` and `urls` get overwritten by web_search if it
  runs; `is_well_known` only exists at all if web_search ran. See the
  docstring in `schemas.py` before changing any node's return shape.
- **Routing is "skip web_search only if confidently spoofed,"** not "skip if
  confident" generically — a name confidently judged *not* spoofed still needs
  web_search to actually establish whether it's well-known at all.
- **No app-level cache yet** — repeated app names across batches currently
  re-trigger real API calls every time. Worth building before running large,
  overlapping batches.
- **Metrics on small classes are unreliable** — don't trust a per-category
  score computed from fewer than ~20-30 gold examples; treat it as "not enough
  data yet," not a real number.
