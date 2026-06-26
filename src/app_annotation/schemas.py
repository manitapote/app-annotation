from typing import Literal
from pydantic import BaseModel, Field

class AppClassification(BaseModel):
    category: Literal["well_known", "no_docs", "spoofed", "uncertain"]
    confidence: float = Field(ge=0, le=1)
    reasoning: str
    evidence_urls: list[str] = []