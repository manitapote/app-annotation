"""
Tool: web_search

This calls OpenAI's BUILT-IN web_search tool, combined with structured
output, to check whether an app name has real, verifiable documentation/
presence on the web.

Uses the raw `openai` SDK client (NOT ChatOpenAI/get_admin_model) because
.responses.parse() and the "web_search" tool type are Responses-API-
specific features -- they don't exist on LangChain's ChatOpenAI wrapper
at all, regardless of which credentials it's given. Using OpenAI()
directly also means this reads your regular OPENAI_API_KEY automatically,
removing the need for a separate admin key entirely.
"""

from pydantic import BaseModel, Field
from langchain_core.tools import tool
from openai import OpenAI

from app_annotation.prompts_loader import load_prompt

WEB_SEARCH_PROMPT_FILE = "web_search.md"
WEB_SEARCH_MODEL = "gpt-5.5"


class _WebSearchResult(BaseModel):
    """Internal-only schema for parsing the model's judgment."""
    is_well_known: bool
    reasoning: str = Field(description="Brief justification for the judgment")
    evidence_urls: list[str] = []


def web_search(app_name: str) -> tuple[bool, str, list[str]]:
    """
    Real web search (OpenAI's built-in web_search tool) combined with a
    structured judgment, in one call.

    Returns the raw (is_well_known, reasoning, evidence_urls) tuple --
    NOT a pre-formatted string -- so callers (search_node) can both
    format it for search_results AND use the structured fields to update
    the Result object directly.
    """
    client = OpenAI()
    prompt_template = load_prompt(WEB_SEARCH_PROMPT_FILE)
    response = client.responses.parse(
        model=WEB_SEARCH_MODEL,
        tools=[{"type": "web_search"}],
        input=prompt_template.format(app_name=app_name),
        text_format=_WebSearchResult,
        prompt_cache_key="call_web_search_v1"
    )
    result = response.output_parsed
    return result.is_well_known, result.reasoning, result.evidence_urls


def _format_for_search_results(is_well_known: bool, reasoning: str, urls: list[str]) -> str:
    """Plain-text rendering for the search_results evidence log."""
    lines = [f"Well-known: {is_well_known}", f"Reasoning: {reasoning}"]
    if urls:
        lines.append("Sources:")
        lines.extend(f"- {url}" for url in urls)
    return "\n".join(lines)


@tool
def web_search_tool(query: str) -> str:
    """Search the web for information about an app, brand, or topic."""
    is_well_known, reasoning, urls = web_search(query)
    return _format_for_search_results(is_well_known, reasoning, urls)


if __name__ == "__main__":
    # Quick manual sanity check: python -m app_annotation.tools.web_search
    test_queries = [
        "Instagram",
        "Twitter For Iphone",
    ]
    for q in test_queries:
        is_well_known, reasoning, urls = web_search(q)
        print(_format_for_search_results(is_well_known, reasoning, urls))
        print("\n" + "=" * 60 + "\n")