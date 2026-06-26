from app_annotation.graph import app

ambiguous_names = [
    "TuitValue",
    "erased136949",
    "RTNicolasMaduro1",
    "Hyves",
    "some random app nobody has heard of",
]

for name in ambiguous_names:
    final_state = app.invoke({
        "app_name": name,
        "search_results": [],
        "result": None,
    })
    result = final_state["result"]
    print(f"{name!r}")
    print(f"  spoof_confidence: {result.spoof_confidence}")
    print(f"  is_well_known: {result.is_well_known}  <- not None means web_search ran")
    print("-" * 60)