from pydantic import BaseModel, Field
from typing import List, Optional

class RAGResponse(BaseModel):
    answer: str
    contexts: List[str]
    source_documents: Optional[List[str]] = None
    latency_ms: Optional[float] = None

class GuardResult(BaseModel):
    is_safe: bool
    reason: str
    confidence: float = 1.0
    latency_ms: float = 0.0

class JudgePairwiseResult(BaseModel):
    winner: str = Field(description="'A', 'B', or 'tie'")
    reason: str

class JudgeAbsoluteResult(BaseModel):
    accuracy: int = Field(ge=1, le=5)
    relevance: int = Field(ge=1, le=5)
    conciseness: int = Field(ge=1, le=5)
    helpfulness: int = Field(ge=1, le=5)
    reason: str
