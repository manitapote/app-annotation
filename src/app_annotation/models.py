"""
Centralized model client setup.
"""

from typing import Optional
import os
from langchain_openai import ChatOpenAI
from app_annotation.config import CLASSIFY_TEMPERATURE


def _check_api_key() -> str:
    """
    Check if necessary APIs are present.
    """
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Add it to .env file."
        )

    admin_key = os.environ.get("OPENAI_ADMIN_KEY", "")
    if not admin_key:
        raise RuntimeError(
            "OPENAI_ADMIN_KEY is not set. Add it to .env file."
        )
    return admin_key


def get_model(temperature: Optional[float] = None):
    """
    Returns the chat model used throughout the project.
    """
    if temperature is None:
        temperature = CLASSIFY_TEMPERATURE
    return ChatOpenAI(model="gpt-4o-mini", temperature=temperature)


def get_admin_model(temperature: Optional[float] = None):
    """
    Returns a ChatOpenAI instance for gpt-5.5-mini, authenticated via
    OPENAI_ADMIN_KEY.
    """
    if temperature is None:
        temperature = CLASSIFY_TEMPERATURE
    
    admin_key = os.environ.get("OPENAI_API_KEY")
    if not admin_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Add it to .env file."
        )
    return ChatOpenAI(model="gpt-5.4-mini", temperature=temperature, api_key=admin_key)

