# nodes/spoof_check_node.py
from app_annotation.state import AnnotationState
from app_annotation.tools.spoof_check import spoof_check


def spoof_check_node(state: AnnotationState) -> dict:
    is_spoof, confidence, reasoning, urls = spoof_check(state["app_name"])
    return {
        "spoof_check": is_spoof,
        "spoof_confidence": confidence,
        "reasoning": reasoning,
        "spoof_evidence_urls": urls,
    }