"""
Batch entrypoint: runs the annotation graph over a list of app names and
saves the concatenated results to a single CSV.
"""

import pandas as pd

from app_annotation.graph import app
from app_annotation.config import INPUT_DIR, OUTPUT_DIR

INPUT_PATH = INPUT_DIR / "app_names.csv" 
OUTPUT_PATH = OUTPUT_DIR / "annotated.csv"


def run_one(app_name: str) -> dict:
    """
    Runs the graph for a single app name and flattens the resulting
    Result object into a plain dict -- one row of the final CSV.
    """
    final_state = app.invoke({
        "app_name": app_name,
        "search_results": [],
        "result": None,
    })
    result = final_state["result"]

    row = result.model_dump()
    row["app_name"] = app_name
    
    return row


def main():
    df_in = pd.read_csv(INPUT_PATH)
    if "app_name" not in df_in.columns:
        raise ValueError(
            f"Expected a column named 'app_name' in {INPUT_PATH}, "
            f"found columns: {list(df_in.columns)}"
        )

    rows = []
    total = len(df_in)
    for i, name in enumerate(df_in["app_name"], start=1):
        print(f"[{i}/{total}] Processing: {name}")
        try:
            rows.append(run_one(name))
        except Exception as e:
            print(f"  [error] {name!r} failed: {e}")
            rows.append({
                "app_name": name,
                "spoof_check": None,
                "spoof_confidence": None,
                "spoof_evidence": None,
                "is_well_known": None,
                "reasoning": f"ERROR: {e}",
                "urls": None,
                "category": None,
            })

    df_out = pd.DataFrame(rows)
    df_out.to_csv(OUTPUT_PATH, index=False)
    print(f"\nSaved {len(df_out)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()