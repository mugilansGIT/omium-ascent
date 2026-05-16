from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class MeetingCreate(BaseModel):
    title: str
    description: Optional[str] = None
    meeting_type: Optional[str] = "general"
    scheduled_at: datetime
    duration_minutes: int = 60
    location: Optional[str] = None
    meeting_url: Optional[str] = None
    attendee_ids: Optional[List[str]] = []

class MeetingTranscriptUpload(BaseModel):
    meeting_id: str
    transcript: str

class MeetingUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    transcript: Optional[str] = None
