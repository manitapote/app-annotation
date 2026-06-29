"""
Eval: tests web_search() ALONE against the gold-standard dataset --
bypasses spoof_check and the graph/routing entirely. Every row gets
web_search called directly, regardless of what spoof_check would have
said.

Since web_search only answers True/False (is_well_known), its output is
mapped to a category for comparison against the gold Category column:
    is_well_known=True  -> "Popular"
    is_well_known=False -> "Others"
(Same mapping used elsewhere in this project -- web_search alone can
never produce "Native", so those rows are excluded same as in run_eval.py.)

Usage:
    python evals/run_eval_web_search_only.py [path/to/gold.csv]
"""

import sys
import datetime
from pathlib import Path

import pandas as pd

from app_annotation.tools.web_search import web_search
from app_annotation.config import ANNOTATED_DIR, EVAL_RESULTS_DIR

def load_gold(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Gold standard file not found: {path}")
    df = pd.read_csv(path)
    if "app_names" in df.columns and "app_name" not in df.columns:
        df = df.rename(columns={"app_names": "app_name"})
    required = {"app_name", "Category"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Gold file missing required columns {missing}. Found: {list(df.columns)}")
    return df

def predict_one(app_name: str) -> dict:
    """Calls web_search directly -- no spoof_check, no graph, no routing."""
    is_well_known, reasoning, urls = web_search(app_name)
    return {
        "predicted_category": "Popular" if is_well_known else "Others",
        "is_well_known": is_well_known,
        "reasoning": reasoning,
        "urls": urls,
    }


def main():
    gold_path = Path(sys.argv[1]) if len(sys.argv) > 1 else ANNOTATED_DIR / "gold_standard.csv"
    df_gold = load_gold(gold_path)

    n_total = len(df_gold)
    df_testable = df_gold[df_gold["Category"] != "Native"].copy()
    n_excluded = n_total - len(df_testable)
    print(f"Loaded {n_total} gold rows from {gold_path}")
    print(f"Excluding {n_excluded} 'Native' rows (web_search alone can never "
          f"predict this) -> {len(df_testable)} rows to score\n")

    predictions = []
    total = len(df_testable)
    for i, row in enumerate(df_testable.itertuples(index=False), start=1):
        name = getattr(row, "app_name")
        gold_category = getattr(row, "Category")
        print(f"[{i}/{total}] {name!r} (gold={gold_category})")
        try:
            pred = predict_one(name)
        except Exception as e:
            print(f"  [error] {e}")
            pred = {"predicted_category": None, "is_well_known": None,
                     "reasoning": f"ERROR: {e}", "urls": []}
        predictions.append({
            "app_name": name,
            "gold_category": gold_category,
            "predicted_category": pred["predicted_category"],
            "is_well_known": pred["is_well_known"],
            "correct": pred["predicted_category"] == gold_category,
            "reasoning": pred["reasoning"],
            "urls": pred["urls"],
        })

    df_results = pd.DataFrame(predictions)

    accuracy = df_results["correct"].mean()
    print(f"\nweb_search-ONLY accuracy: {accuracy:.2%} "
          f"({int(df_results['correct'].sum())}/{len(df_results)})")

    print("\nPer-category accuracy (based on GOLD label):")
    for cat in sorted(df_results["gold_category"].dropna().unique()):
        subset = df_results[df_results["gold_category"] == cat]
        cat_acc = subset["correct"].mean()
        print(f"  {cat}: {cat_acc:.2%} ({int(subset['correct'].sum())}/{len(subset)})")

    print("\nConfusion matrix (rows=gold, columns=predicted):")
    print(pd.crosstab(
        df_results["gold_category"], df_results["predicted_category"], dropna=False
    ))

    EVAL_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_path = EVAL_RESULTS_DIR / f"eval_websearch_only_{timestamp}.csv"
    df_results.to_csv(out_path, index=False)
    print(f"\nSaved detailed per-row results to {out_path}")


if __name__ == "__main__":
    main()