"""
Computes Cohen's Kappa from an ALREADY-SAVED search results.
By default, it will find the most recent eval_websearch_only_*.csv in
evals/results/ and use that, but you can also pass a specific path to a
results CSV file as an argument.

Usage:
    python evals/run_eval_cohens_kappa.py [path/to/results.csv]
    (defaults to the most recently saved eval_websearch_only_*.csv in
    evals/results/ if no path is given)
"""

import sys
import ast
import glob
from pathlib import Path

import pandas as pd
from sklearn.metrics import cohen_kappa_score

from app_annotation.config import EVAL_RESULTS_DIR


def find_latest_results_file() -> Path:
    pattern = str(EVAL_RESULTS_DIR / "eval_websearch_only_*.csv")
    matches = glob.glob(pattern)
    if not matches:
        raise FileNotFoundError(
            f"No saved results found matching {pattern}. "
            f"Run run_eval_web_search_only.py first to generate one, "
            f"or pass a specific file path as an argument."
        )
    return Path(sorted(matches)[-1])


def parse_urls(val) -> list:
    """
    The saved CSV stores `urls` as the string repr of a Python list
    (e.g. "['https://...']" or "[]") since CSV is flat text. Parse it
    back into a real list -- ast.literal_eval is safe here (no eval()),
    it only parses Python literals, not arbitrary code.
    """
    if pd.isna(val):
        return []
    if isinstance(val, list):
        return val
    try:
        parsed = ast.literal_eval(str(val))
        return parsed if isinstance(parsed, list) else []
    except (ValueError, SyntaxError):
        return []


def report(gold_col: pd.Series, pred_col: pd.Series, label: str):
    mask = gold_col.notna() & pred_col.notna()
    g, p = gold_col[mask], pred_col[mask]

    if len(g) == 0:
        print(f"\n{label}: no scoreable rows -- skipped")
        return

    accuracy = (g == p).mean()
    kappa = cohen_kappa_score(g, p)

    print(f"\n--- {label} ({len(g)} rows) ---")
    print(f"Accuracy:      {accuracy:.2%}")
    print(f"Cohen's Kappa: {kappa:.3f}  {_interpret_kappa(kappa)}")
    print("Confusion matrix (rows=gold, columns=predicted):")
    print(pd.crosstab(g, p, dropna=False))


def _interpret_kappa(kappa: float) -> str:
    if kappa < 0:
        return "(less than chance agreement)"
    elif kappa < 0.20:
        return "(slight agreement)"
    elif kappa < 0.40:
        return "(fair agreement)"
    elif kappa < 0.60:
        return "(moderate agreement)"
    elif kappa < 0.80:
        return "(substantial agreement)"
    else:
        return "(almost perfect agreement)"


def main():
    if len(sys.argv) > 1:
        results_path = Path(sys.argv[1])
    else:
        results_path = find_latest_results_file()
        print(f"No path given -- using most recent saved results: {results_path}\n")

    if not results_path.exists():
        raise FileNotFoundError(f"Results file not found: {results_path}")

    df = pd.read_csv(results_path)

    required = {"gold_category", "predicted_category"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(
            f"{results_path} is missing required columns {missing}. "
            f"Found columns: {list(df.columns)}."
        )

    if "urls" not in df.columns:
        raise ValueError(
            f"{results_path} has no 'urls' column, so the gold-trust "
            f"adjustment can't be computed. Re-run run_eval_web_search_only.py "
            f"with urls saved in its output, then re-run this script."
        )

    n_total = len(df)
    n_failed = df["predicted_category"].isna().sum()
    if n_failed:
        print(f"[warning] {n_failed}/{n_total} row(s) have a missing prediction "
              f"(failed during the original run) -- excluded from all calculations below.")

    df["url_list"] = df["urls"].apply(parse_urls)
    df["has_urls"] = df["url_list"].apply(len) > 0
    n_with_urls = df["has_urls"].sum()
    print(f"{n_with_urls}/{n_total} rows had real evidence URLs from web_search.")

    # The actual adjustment: trust the prediction over gold ONLY where
    # web_search found real evidence. 
    # Rows with no urls keep their original gold label unchanged.
    df["corrected_gold_category"] = df["gold_category"].where(
        ~df["has_urls"], df["predicted_category"]
    )

    n_overridden = (
        df["has_urls"] & (df["gold_category"] != df["predicted_category"])
    ).sum()
    print(f"{n_overridden} row(s) had a gold/prediction disagreement AND real "
          f"urls -- gold is treated as wrong for those rows in the CORRECTED metrics.\n")

    report(df["gold_category"], df["predicted_category"], "ORIGINAL (gold trusted as-is)")
    report(df["corrected_gold_category"], df["predicted_category"],
           "CORRECTED (web_search trusted when it found real urls)")

    out_path = results_path.with_name(results_path.stem + "_with_correction.csv")
    df.drop(columns=["url_list"]).to_csv(out_path, index=False)
    print(f"\nSaved annotated results (with has_urls / corrected_gold_category "
          f"columns) to {out_path}")


if __name__ == "__main__":
    main()