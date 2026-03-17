from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID


class ResumeResultResponse(BaseModel):
    id: UUID
    filename: str
    final_score: float
    score_semantic: float
    score_tfidf: float
    score_skills: float
    score_experience: float
    rank: Optional[int]
    matched_skills: List[str]
    missing_skills: List[str]
    years_experience_detected: Optional[float]
    language_detected: str
    extraction_quality: str
    flags: dict
    created_at: str

    class Config:
        from_attributes = True


class SingleScreenRequest(BaseModel):
    jd_text: str


class SingleScreenResponse(BaseModel):
    filename: str = "resume"
    final_score: float
    score_semantic: float
    score_tfidf: float
    score_skills: float
    score_experience: float
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    years_experience_detected: Optional[float] = None
    language_detected: str = "en"
    extraction_quality: str = "good"
    flags: dict = Field(default_factory=dict)
    processing_ms: Optional[int] = None
