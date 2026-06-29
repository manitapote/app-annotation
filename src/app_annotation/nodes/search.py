from app_annotation.state import AnnotationState
from app_annotation.tools.web_search import web_search, _format_for_search_results


def search_node(state: AnnotationState) -> dict:
    """
    Runs web_search and updates Result with its findings.
    """
    is_well_known, reasoning, urls = web_search(state["app_name"])

    existing_result = state["result"]
    updated_result = existing_result.model_copy(update={
        "is_well_known": is_well_known,
        "reasoning": reasoning,
        "urls": urls,
    })

    evidence_text = _format_for_search_results(is_well_known, reasoning, urls)

    return {
        "search_results": [evidence_text],
        "result": updated_result,
    }