from unittest.mock import patch
from app_annotation.graph import app

with patch("app_annotation.nodes.spoof_check_node.spoof_check") as mock_spoof_check:
    mock_spoof_check.return_value = (False, 0.2, "simulated low confidence", [])

    final_state = app.invoke({
        "app_name": "test app",
        "search_results": [],
        "result": None,
    })

print(final_state["result"])
print("web_search ran:", final_state["result"].is_well_known is not None)