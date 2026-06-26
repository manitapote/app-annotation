"""
Tool: spoof_check

Uses the model's own knowledge of well-known apps/brands to judge whether
an app name looks like it's deliberately imitating one of them
(typosquatting, lookalike spelling, suspicious added words like "Pro"/
"Real", character substitutions, etc.) -- rather than maintaining a
hand-curated list of brand names to compare against.

Returns a plain bool, matching state.py's `spoof_check: Optional[bool]`
field.
"""

from pydantic import BaseModel, Field
from langchain_core.tools import tool

from app_annotation.models import get_model
from app_annotation.prompts_loader import load_prompt


SPOOF_PROMPT_FILE = "spoof_check.md"
class _SpoofCheckResult(BaseModel):
    """
    Internal-only schema for parsing the model's judgment.
    """
    is_likely_spoof: bool
    reasoning: str = Field(description="Brief justification for the judgment")
    confidence: float = Field(ge=0, le=1)
    urls: list[str] = []


def spoof_check(app_name: str) -> bool:
    """
    Returns True if `app_name` appears to be impersonating a specific,
    well-known app/brand name; False otherwise (including when there's
    no clear match to imitate, or genuine ambiguity).
    """
    model = get_model()
    structured_model = model.with_structured_output(_SpoofCheckResult)
    prompt_template = load_prompt(SPOOF_PROMPT_FILE)
    result = structured_model.invoke(prompt_template.format(app_name=app_name))
    return result.is_likely_spoof, result.confidence, result.reasoning, result.urls


@tool
def spoof_check_tool(app_name: str) -> bool:
    """Check whether an app name appears to impersonate a well-known app or brand."""
    return spoof_check(app_name)


if __name__ == "__main__":
    for name in ["Instagram", "Instagrm Pro", "WhatsApp", "Whatsap Plus", "Notion"]:
        print(f"{name!r:25} -> spoof_check = {spoof_check(name)}")
