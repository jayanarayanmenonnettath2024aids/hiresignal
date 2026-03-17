from enum import Enum
from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class FeedbackAction(str, Enum):
    shortlisted = "shortlisted"
    rejected = "rejected"
    interviewed = "interviewed"
    hired = "hired"
    ghosted = "ghosted"


class FeedbackCreate(BaseModel):
    result_id: UUID
    action: FeedbackAction
    notes: Optional[str] = None

    model_config = {"use_enum_values": True}


class FeedbackResponse(BaseModel):
    id: UUID
    result_id: UUID
    job_id: Optional[UUID] = None
    action: FeedbackAction
    notes: Optional[str] = None

    model_config = {"from_attributes": True, "use_enum_values": True}
