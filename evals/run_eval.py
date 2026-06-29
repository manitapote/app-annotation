"""
Eval: compares the app's predicted `category` against a gold-standard
annotated dataset (data/annotated/).
"""

import sys
import datetime
from pathlib import Path

import pandas as pd

from app_annotation.graph import app
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
        raise ValueError(
            f"Gold file missing required columns {missing}. "
            f"Found columns: {list(df.columns)}"
        )
    return df


def predict_one(app_name: str) -> str | None:
    """Runs the graph for one app name, returns its predicted category."""
    final_state = app.invoke({
        "app_name": app_name,
        "search_results": [],
        "result": None,
    })
    return final_state["result"]


def main():
    gold_path = Path(sys.argv[1]) if len(sys.argv) > 1 else ANNOTATED_DIR / "gold_standard.csv"
    df_gold = load_gold(gold_path)
    df_gold = df_gold.head()
    total = len(df_gold)
    predictions = []
    for i, row in enumerate(df_gold.itertuples(index=False), start=1):
        name = getattr(row, "app_name")
        gold_category = getattr(row, "Category")
        print(f"[{i}/{total}] {name!r} (gold={gold_category})")
        try:
            predicted = predict_one(name)
        except Exception as e:
            print(f"  [error] {e}")
            predicted = None
        predictions.append({
            "app_name": name,
            "gold_category": gold_category,
            "predicted_category": predicted.category,
            "correct": predicted.category == gold_category,
            "reasoning": predicted.reasoning,
            "spoof_confidence": predicted.spoof_confidence,
            "is_well_known": predicted.is_well_known,
            "urls": predicted.urls,
        })

    df_results = pd.DataFrame(predictions)

    EVAL_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_path = EVAL_RESULTS_DIR / f"eval_{timestamp}.csv"
    df_results.to_csv(out_path, index=False)
    print(f"\nSaved detailed per-row results to {out_path}")


if __name__ == "__main__":
    main()