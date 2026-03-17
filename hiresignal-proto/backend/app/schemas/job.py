from pydantic import BaseModel, Field, model_validator
from typing import Optional, List
from uuid import UUID


class JobCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    jd_text: Optional[str] = None
    weight_semantic: float = Field(default=0.40, ge=0.0, le=1.0)
    weight_tfidf: float = Field(default=0.30, ge=0.0, le=1.0)
    weight_skills: float = Field(default=0.20, ge=0.0, le=1.0)
    weight_experience: float = Field(default=0.10, ge=0.0, le=1.0)
    top_n: int = Field(default=10, ge=1, le=100)

    @model_validator(mode="after")
    def weights_must_sum_to_one(self) -> "JobCreate":
        total = (
            self.weight_semantic
            + self.weight_tfidf
            + self.weight_skills
            + self.weight_experience
        )
        if abs(total - 1.0) > 0.01:
            raise ValueError(
                f"Weights must sum to 1.0 (got {total:.3f}). "
                f"Received: semantic={self.weight_semantic}, tfidf={self.weight_tfidf}, "
                f"skills={self.weight_skills}, experience={self.weight_experience}"
            )
        return self

    @model_validator(mode="after")
    def jd_must_be_present(self) -> "JobCreate":
        if not self.jd_text or not self.jd_text.strip():
            raise ValueError("Provide either jd_text or jd_file")
        return self


class JobUpdate(BaseModel):
    title: Optional[str] = None
    weight_semantic: Optional[float] = None
    weight_tfidf: Optional[float] = None
    weight_skills: Optional[float] = None
    weight_experience: Optional[float] = None
    top_n: Optional[int] = None


class JDPreviewResponse(BaseModel):
    skills: List[str]
    quality_score: float
    is_vague: bool
    min_yoe: Optional[float]


class JobResponse(BaseModel):
    id: UUID
    title: str
    jd_quality_score: Optional[float]
    jd_is_vague: bool
    status: str
    total_submitted: int
    total_processed: int
    total_failed: int
    started_at: Optional[str]
    completed_at: Optional[str]
    created_at: str

    class Config:
        from_attributes = True
