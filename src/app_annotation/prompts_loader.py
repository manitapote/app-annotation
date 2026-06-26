"""
Loads prompt templates from PROMPTS_DIR as plain text.
"""

from functools import lru_cache
from app_annotation.config import PROMPTS_DIR


@lru_cache(maxsize=None)
def load_prompt(filename: str) -> str:
    """
    Load a prompt template by filename, e.g. load_prompt("spoof_check.md").

    Cached so repeated calls (e.g. once per spoof_check invocation) don't
    re-read the same file from disk every single time -- the file is only
    read once per process, not once per call.
    """
    path = PROMPTS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {path}. Check that '{filename}' "
            f"actually exists under PROMPTS_DIR ({PROMPTS_DIR})."
        )
    return path.read_text()