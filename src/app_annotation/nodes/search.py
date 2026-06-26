# nodes/search.py
from app_annotation.state import AnnotationState
from app_annotation.tools.web_search import web_search


def search_node(state: AnnotationState) -> dict:
    evidence = web_search(state["app_name"])
    return {
        "search_results": [evidence],
        "attempts": state["attempts"] + 1,
    }