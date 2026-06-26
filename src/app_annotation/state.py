from typing import Annotated, Optional
from typing_extensions import TypedDict
import operator
from app_annotation.schemas import AppClassification

class AnnotationState(TypedDict):
    app_name: str                                          # <-- here
    search_results: Annotated[list[str], operator.add]
    attempts: int
    result: Optional[AppClassification]
    spoof_check: Optional[bool]