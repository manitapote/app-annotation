from pydantic import BaseModel, Field
from typing import Optional

class Result(BaseModel):
    spoof_check: bool
    spoof_confidence: float = Field(ge=0, le=1)
    reasoning: str
    spoof_evidence: list[str] = [] 
    is_well_known: Optional[bool] = None
    urls: list[str] = []