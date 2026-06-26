"""
Tool: web_search

This call web search tool of OpenAI with the app name to check the app has documentation.
"""
from pydantic import BaseModel, Field
from langchain_core.tools import tool
from app_annotation.models import get_admin_model

from openai import OpenAI
from app_annotation.prompts_loader import load_prompt

WEB_SEARCH_PROMPT_FILE = "web_search.md"


class _WebSearchResult(BaseModel):
    """Internal-only schema for parsing the model's judgment."""
    is_well_known: bool
    reasoning: str = Field(description="Brief justification for the judgment")
    evidence_urls: list[str] = []


def web_search(app_name: str) -> str:
    """
    Real web search (OpenAI's built-in web_search tool) combined with a
    structured judgment.
    """
    client = get_admin_model()
    prompt_template = load_prompt(WEB_SEARCH_PROMPT_FILE)
    response = client.responses.parse(
        tools=[{"type": "web_search"}],
        input=prompt_template.format(app_name=app_name),
        text_format=_WebSearchResult,
    )
    result = response.output_parsed

    lines = [
        f"Well-known: {result.is_well_known}",
        f"Reasoning: {result.reasoning}",
    ]
    if result.evidence_urls:
        lines.append("Sources:")
        lines.extend(f"- {url}" for url in result.evidence_urls)
    return "\n".join(lines)

@tool
def web_search_tool(query: str) -> str:
    """Search the web for information about an app, brand, or topic."""
    return web_search(query)


if __name__ == "__main__":
    # Quick manual sanity check: python -m app_annotation.tools.web_search
    test_queries = [
        'Instagram',
        'Twitter For Iphone',
    ]
    for q in test_queries:
        print(web_search(q))
        print("\n" + "=" * 60 + "\n")
