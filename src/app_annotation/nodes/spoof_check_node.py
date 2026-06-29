from app_annotation.state import AnnotationState
from app_annotation.schemas import Result
from app_annotation.tools.spoof_check import spoof_check


def spoof_check_node(state: AnnotationState) -> dict:
    is_spoof, confidence, reasoning, urls, category = spoof_check(state["app_name"])
    result = Result(
        spoof_check=is_spoof,
        spoof_confidence=confidence,
        spoof_evidence=urls,
        reasoning=reasoning,
        urls=urls,
        category=category,
    )
    print(f"[DEBUG] spoof_check_node returning result: {result}")
    return {"result": result}