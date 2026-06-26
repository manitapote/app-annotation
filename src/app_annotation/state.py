from typing import Annotated, Optional
from typing_extensions import TypedDict
import operator
from app_annotation.schemas import Result
from pydantic import Field

class AnnotationState(TypedDict):
    app_name: str
    search_results: Annotated[list[str], operator.add]
    attempts: int
    result: Optional[Result]
    spoof_check: Optional[bool]
    spoof_confidence: Optional[float]
    reasoning: Optional[str]
    spoof_evidence_urls: Optional[list[str]]