from langgraph.graph import StateGraph, START, END

from app_annotation.state import AnnotationState
from app_annotation.nodes.spoof_check_node import spoof_check_node
from app_annotation.nodes.search import search_node


def route_after_spoof_check(state: AnnotationState) -> str:
    if state["result"].spoof_confidence < 0.5:
        return "search"
    return "end"


graph = StateGraph(AnnotationState)

graph.add_node("spoof_check", spoof_check_node)
graph.add_node("web_search", search_node)

graph.add_edge(START, "spoof_check")
graph.add_conditional_edges(
    "spoof_check",
    route_after_spoof_check,
    {
        "search": "web_search",
        "end": END,
    },
)
graph.add_edge("web_search", END)

app = graph.compile()

print(app.get_graph().draw_mermaid())